import pygame  # Librería para gráficos y eventos
import os      # Librería para manejo de rutas de archivos

# Clase que representa al jugador principal
class Player:
    def __init__(self, x, y):
        # Posición visual del sprite
        self.sprite_pos = pygame.Vector2(x, y)

        # Animación
        self.frame_index = 0.0        # Índice del frame actual
        self.animation_speed = 0.1    # Velocidad de animación
        self.direction = "down"       # Dirección inicial
        self.can_move = True          # Indica si puede moverse

        # Cargar sprites del jugador
        base_path = os.path.join("assets", "images", "sprites", "overworld", "lenard")
        def load(img_name):
            """Carga y escala imágenes del jugador"""
            p = os.path.join(base_path, img_name)
            if not os.path.exists(p):
                raise FileNotFoundError(f"Imagen no encontrada: {p}")
            img = pygame.image.load(p).convert_alpha()
            img = pygame.transform.scale_by(img, 2)  # Escalar imagen 2x
            return img

        # Diccionario de animaciones por dirección
        self.animations = {
            "down": [load("id_down.png"), load("down_w1.png"), load("id_down.png"), load("down_w2.png")],
            "up":   [load("id_up.png"), load("up_w1.png"), load("id_up.png"), load("up_w2.png")],
            "left": [load("id_left.png"), load("left_w1.png"), load("id_left.png"), load("left_w2.png")],
            "right":[load("id_right.png"), load("right_w1.png"), load("id_right.png"), load("right_w2.png")]
        }

        # Imagen inicial y rect visual
        self.image = self.animations[self.direction][0]
        self.image_rect = self.image.get_rect(topleft=self.sprite_pos.xy)

        # HITBOX independiente (para colisiones)
        self.hitbox = pygame.Rect(int(x + 46), int(y + 100), 32, 24)  # Ajustar según sprite

        # Offsets opcionales para dibujar sprite relativo a hitbox
        self.draw_offset_x = 0
        self.draw_offset_y = 0

        # Velocidad en píxeles por segundo
        self.speed = 200

        # Estado de movimiento (True si hay tecla mantenida)
        self.is_moving = False

    # ---------- MOVIMIENTOS EXPLÍCITOS ----------
    def move_sprite(self, dx, dy):
        """Mueve solo el sprite visual (no hitbox)"""
        self.sprite_pos.x += dx
        self.sprite_pos.y += dy
        self.image_rect.topleft = (int(self.sprite_pos.x), int(self.sprite_pos.y))

    def move_hitbox(self, dx, dy):
        """Mueve solo la hitbox (no el sprite visual)"""
        self.hitbox.x += int(round(dx))
        self.hitbox.y += int(round(dy))

    def move_both(self, dx, dy, collisions=None):
        """
        Mueve hitbox y sprite juntos.
        Aplica colisiones solo a la hitbox y sincroniza sprite.
        """
        if collisions is None:
            collisions = []

        # Movimiento en eje X con colisiones
        self.hitbox.x += int(round(dx))
        for c in collisions:
            if self.hitbox.colliderect(c):
                if dx > 0:
                    self.hitbox.right = c.left
                elif dx < 0:
                    self.hitbox.left = c.right

        # Movimiento en eje Y con colisiones
        self.hitbox.y += int(round(dy))
        for c in collisions:
            if self.hitbox.colliderect(c):
                if dy > 0:
                    self.hitbox.bottom = c.top
                elif dy < 0:
                    self.hitbox.top = c.bottom

        # Sincronizar sprite visual con hitbox
        self.sprite_pos.x = self.hitbox.x - (self.image_rect.width - self.hitbox.width) // 2
        self.sprite_pos.y = self.hitbox.y - (self.image_rect.height - self.hitbox.height)
        self.image_rect.topleft = (int(self.sprite_pos.x), int(self.sprite_pos.y))

    # ---------- INPUT / UPDATE ----------
    def handle_input(self, dt, collisions):
        """
        Procesa el input del jugador.
        Llamar cada frame para movimiento continuo mientras la tecla esté presionada.
        """
        if not self.can_move:
            # Si está bloqueado (ej. diálogo), no procesar input
            self.is_moving = False
            return

        keys = pygame.key.get_pressed()  # Detecta teclas presionadas
        dx = 0.0
        dy = 0.0
        moving = False

        # Movimiento según teclas
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= self.speed * dt
            self.direction = "left"
            moving = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += self.speed * dt
            self.direction = "right"
            moving = True
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= self.speed * dt
            self.direction = "up"
            moving = True
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += self.speed * dt
            self.direction = "down"
            moving = True

        self.is_moving = moving

        if not moving:
            return

        # Mover con colisiones
        self.move_both(dx, dy, collisions)

    def update_animation(self, dt, moving):
        """Actualiza la animación del jugador"""
        if moving:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(self.animations[self.direction]):
                self.frame_index = 0.0
        else:
            self.frame_index = 0.0

        # Actualizar imagen y rect
        self.image = self.animations[self.direction][int(self.frame_index)]
        self.image_rect = self.image.get_rect(topleft=self.sprite_pos.xy)

    def update(self, dt, collisions):
        """
        Lógica principal de update del jugador.
        Maneja input, animación y movimiento.
        """
        if not self.can_move:
            # Si diálogo activo → animación idle
            self.update_animation(dt, False)
            return

        self.handle_input(dt, collisions)
        self.update_animation(dt, self.is_moving)

    def draw(self, surface):
        """Dibuja el jugador en pantalla"""
        surface.blit(self.image, self.image_rect)
        # pygame.draw.rect(surface, (255,0,0), self.hitbox, 1)  # debug hitbox
