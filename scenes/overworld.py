import pygame
from entidades.player import Player
from entidades.companion import Companion
from mundos.map_manager import MapManager

class OverworldScene:
    def __init__(self, game):
        self.game = game  # referencia al objeto Game principal
        self.map_manager = MapManager(game)  # administrador de mapas
        self.player = Player(193, 360)  # crear player en coordenadas iniciales
        self.companion = Companion(160, 360)  # crear compañera (seguirá al player)

    def handle_events(self, event_list):
        """
        Maneja eventos recibidos desde Game.run()
        - Si hay diálogo activo -> pasa el input a DialogueSystem
        - Si se presiona Z y no hay diálogo -> inicia diálogo con NPC cercano
        """
        for event in event_list:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_z:
                # 1) Si hay diálogo activo → avanzarlo
                if self.game.dialogue.active:
                    self.game.dialogue.handle_input()
                    return

                # 2) Si no hay diálogo, buscar NPC cercano para interactuar
                for npc in self.map_manager.current_map.get("npcs", []):
                    # Inflar hitbox del NPC para zona de interacción
                    if self.player.hitbox.colliderect(npc.hitbox.inflate(40, 40)):
                        self.player.can_move = False  # bloquear movimiento del player

                        portrait = getattr(npc, "portrait_data", None)  # obtener retrato si existe

                        # guardar referencia al NPC con el que se interactúa
                        self.game.scene.current_npc = npc

                        # iniciar diálogo con el NPC
                        self.game.dialogue.start(
                            npc.dialogue,
                            speaker="npc",
                            portrait=portrait
                        )

                        npc.is_interacting = True  # marcar NPC como en conversación
                        return

    def update(self, dt, events):
        """
        Lógica principal de actualización del overworld:
        - procesar eventos
        - actualizar player y companion
        - actualizar mapa (NPCs, colisiones, teleports)
        """
        self.handle_events(events)  # manejar eventos antes que todo

        collisions = self.map_manager.current_map["collision"]
        # actualizar player (su método se encarga de input y colisiones)
        self.player.update(dt, collisions)
        # companion sigue al player
        self.companion.follow(self.player, dt)
        # actualizar NPCs y colisiones del mapa
        self.map_manager.update(self.player)

    def draw(self, screen):
        """
        Dibuja todo en pantalla, delegando al MapManager
        """
        # MapManager dibuja background, props, NPCs, player y companion en orden correcto
        self.map_manager.draw(screen, self.player, self.companion)
