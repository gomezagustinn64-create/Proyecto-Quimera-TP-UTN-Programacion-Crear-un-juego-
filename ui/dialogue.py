import pygame
import os

class DialogueSystem:
    def __init__(self, game):
        self.game = game  # Referencia al objeto principal del juego
        self.active = False  # Controla si el diálogo está activo

        # Velocidad a la que se muestra el texto (caracteres por frame)
        self.text_speed = 0.03  
        self.time_acc = 0.0  # Acumulador de tiempo para mostrar progresivamente texto

        self.dialogues = []  # Lista de líneas de diálogo a mostrar
        self.current_index = 0  # Índice de la línea de diálogo actual

        self.full_text = ""  # Texto completo de la línea actual
        self.current_text = ""  # Texto mostrado progresivamente

        # Cajas de diálogo para jugador y NPC
        base = os.path.join("assets", "ui_assets")
        self.box_player = pygame.image.load(os.path.join(base, "textboxplayer.png")).convert_alpha()
        self.box_npc = pygame.image.load(os.path.join(base, "textboxnpc.png")).convert_alpha()

        # Escalar cajas para altura fija
        TARGET_HEIGHT = 450
        SCALE = TARGET_HEIGHT / self.box_player.get_height()
        TARGET_WIDTH = int(self.box_player.get_width() * SCALE)
        self.box_player = pygame.transform.scale(self.box_player, (TARGET_WIDTH, TARGET_HEIGHT))
        self.box_npc = pygame.transform.scale(self.box_npc, (TARGET_WIDTH, TARGET_HEIGHT))

        # Posición de las cajas en pantalla
        self.box_offset_x = -140
        self.box_offset_y = 10

        # Posición del texto dentro de la caja
        self.text_offset_x = 220
        self.text_offset_y = 205
        self.line_spacing = 28  # Espaciado entre líneas

        self.font = pygame.font.Font("assets/fonts/DTM-Sans.otf", 22)  # Fuente del texto
        self.speaker = "npc"  # Quién habla ("npc" o "player")

        # Para mostrar retrato o sprite junto al diálogo
        self.portrait_image = None
        self.portrait_offset_x = 0
        self.portrait_offset_y = 0

        # Variables para secuencia final especial
        self.special_end_sequence = False
        self.sequence_state = "dialogue"
        self.fade_alpha = 0
        self.sequence_timer = 0
        self.final_text_1 = "Tu destino está escrito..."
        self.final_text_2 = "Pero aún puedes cambiarlo."

        # Imagen final opcional
        final_img_path = os.path.join("assets", "images", "Elfinal.png")
        if os.path.exists(final_img_path):
            self.final_image = pygame.image.load(final_img_path).convert_alpha()
        else:
            self.final_image = None

    # -------------------
    # INICIAR UN DIÁLOGO
    # -------------------
    def start(self, dialogue_list, speaker="npc", portrait=None):
        if not dialogue_list:
            return  # No hacer nada si no hay líneas

        self.active = True
        self.dialogues = dialogue_list
        self.current_index = 0
        self.speaker = speaker

        self.full_text = self.dialogues[0]  # Línea completa actual
        self.current_text = ""  # Texto mostrado progresivamente
        self.time_acc = 0.0

        # Cargar retrato opcional
        if portrait:
            img = pygame.image.load(portrait["path"]).convert_alpha()
            scale = portrait.get("scale", 1.0)
            img = pygame.transform.scale(img, (int(img.get_width()*scale), int(img.get_height()*scale)))
            self.portrait_image = img
            self.portrait_offset_x = portrait.get("offset_x", 0)
            self.portrait_offset_y = portrait.get("offset_y", 0)
        else:
            self.portrait_image = None

        # Bloquear movimiento del jugador durante el diálogo
        self.game.scene.player.can_move = False

    # -------------------
    # MANEJAR INPUT PARA AVANZAR EL DIÁLOGO
    # -------------------
    def handle_input(self):
        if not self.active:
            return

        # Mostrar toda la línea si aún no se completó
        if len(self.current_text) < len(self.full_text):
            self.current_text = self.full_text
            return

        # Pasar a la siguiente línea
        self.current_index += 1

        # Si no quedan líneas, terminar diálogo
        if self.current_index >= len(self.dialogues):
            npc = getattr(self.game.scene, "current_npc", None)

            # Secuencia especial si el NPC se llama "muerte"
            if npc and npc.name.lower() == "muerte":
                final_line = "MUERTE: \nY ustedes tambien."
                if self.dialogues[-1].strip() == final_line.strip():
                    self.start_special_sequence()
                    return

            # Permitir que el jugador se mueva
            self.active = False
            self.game.scene.player.can_move = True
            return

        # Actualizar línea y reiniciar texto progresivo
        self.full_text = self.dialogues[self.current_index]
        self.current_text = ""
        self.time_acc = 0.0

    # -------------------
    # INICIAR SECUENCIA FINAL ESPECIAL
    # -------------------
    def start_special_sequence(self):
        self.special_end_sequence = True
        self.sequence_state = "fade_to_black"
        self.fade_alpha = 0
        self.sequence_timer = 0
        self.game.scene.player.can_move = False

    # -------------------
    # ACTUALIZAR CADA FRAME
    # -------------------
    def update(self, dt):
        if not self.active:
            return

        if self.special_end_sequence:
            self.update_special_sequence(dt)
            return

        # Avanzar texto progresivamente
        if len(self.current_text) < len(self.full_text):
            self.time_acc += dt
            while self.time_acc >= self.text_speed:
                self.time_acc -= self.text_speed
                n = len(self.current_text)
                if n < len(self.full_text):
                    self.current_text += self.full_text[n]

    # -------------------
    # ACTUALIZAR SECUENCIA ESPECIAL FINAL
    # -------------------
    def update_special_sequence(self, dt):
        # Fade a negro
        if self.sequence_state == "fade_to_black":
            self.fade_alpha += 120 * dt
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                self.sequence_state = "show_text_1"
            return

        # Mostrar primer texto
        if self.sequence_state == "show_text_1":
            self.sequence_timer += dt
            if self.sequence_timer >= 2.5:
                self.sequence_timer = 0
                self.sequence_state = "show_text_2"
            return

        # Mostrar segundo texto
        if self.sequence_state == "show_text_2":
            self.sequence_timer += dt
            if self.sequence_timer >= 2.5:
                self.sequence_timer = 0
                self.sequence_state = "show_image"
            return

        # Mostrar imagen final
        if self.sequence_state == "show_image":
            self.sequence_timer += dt
            if self.sequence_timer >= 4:
                self.sequence_state = "end_game"
            return

        # Finalizar juego
        if self.sequence_state == "end_game":
            pygame.quit()
            raise SystemExit

    # -------------------
    # DIBUJAR DIÁLOGO
    # -------------------
    def draw(self, screen):
        if not self.active:
            return

        if self.special_end_sequence:
            self.draw_special_sequence(screen)
            return

        # Elegir caja según quién hable
        box = self.box_npc if self.speaker == "npc" else self.box_player

        # Posicionar caja
        box_x = self.box_offset_x
        box_y = screen.get_height() - box.get_height() + self.box_offset_y

        # Dibujar retrato si existe
        if self.portrait_image:
            screen.blit(self.portrait_image,
                        (box_x + self.portrait_offset_x, box_y + self.portrait_offset_y))

        # Dibujar caja
        screen.blit(box, (box_x, box_y))

        # Dibujar texto línea por línea
        text_x = box_x + self.text_offset_x
        text_y = box_y + self.text_offset_y
        for line in self.current_text.split("\n"):
            text_surface = self.font.render(line, True, (255, 255, 255))
            screen.blit(text_surface, (text_x, text_y))
            text_y += self.line_spacing

    # -------------------
    # DIBUJAR SECUENCIA ESPECIAL FINAL
    # -------------------
    def draw_special_sequence(self, screen):
        # Fade negro
        fade_surf = pygame.Surface((screen.get_width(), screen.get_height()))
        fade_surf.fill((0, 0, 0))
        fade_surf.set_alpha(int(self.fade_alpha))
        screen.blit(fade_surf, (0, 0))

        text_color = (255, 255, 255)

        # Mostrar texto o imagen según el estado
        if self.sequence_state == "show_text_1":
            text_surface = self.font.render(self.final_text_1, True, text_color)
            screen.blit(text_surface, ((screen.get_width() - text_surface.get_width()) // 2,
                                       (screen.get_height() - text_surface.get_height()) // 2))
        elif self.sequence_state == "show_text_2":
            text_surface = self.font.render(self.final_text_2, True, text_color)
            screen.blit(text_surface, ((screen.get_width() - text_surface.get_width()) // 2,
                                       (screen.get_height() - text_surface.get_height()) // 2))
        elif self.sequence_state == "show_image" and self.final_image:
            img_rect = self.final_image.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
            screen.blit(self.final_image, img_rect.topleft)
