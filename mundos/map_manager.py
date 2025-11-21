import pygame
import json
import os
from entidades.npc import NPC  # Importa clase NPC para instanciar los personajes

# Clase que maneja los mapas, NPCs, props y teletransportes
class MapManager:
    def __init__(self, game, start_map="zona1"):
        self.game = game
        self.base_path = os.path.dirname(os.path.abspath(__file__))  # Ruta base de este archivo
        self.current_map = None
        self.load_map(start_map)  # Cargar mapa inicial

    def load_map(self, name):
        """
        Carga un mapa desde un archivo JSON, incluyendo background, colisiones, NPCs, props y teletransportes.
        """
        path = os.path.join(self.base_path, "mapas", f"{name}.json")

        if not os.path.exists(path):
            raise FileNotFoundError(f"Mapa no encontrado: {path}")

        with open(path, "r") as f:
            data = json.load(f)

        # cargar background
        bg_path = data.get("background")
        background_image = None
        if bg_path and os.path.exists(bg_path):
            background_image = pygame.image.load(bg_path).convert()

        # Guardar información general del mapa
        self.current_map = {
            "name": data["name"],
            "width": data["width"],
            "height": data["height"],
            "color": tuple(data["color"]),
            "collision": [
                pygame.Rect(c["x"], c["y"], c["w"], c["h"]) for c in data["collision"]
            ],
            "connections": data["connections"],  # mapas conectados
            "background": background_image,
            "spawn_points": data.get("spawn_points", {}),
            "npcs": data.get("npcs", [])
        }

        # --- Instanciar NPCs ---
        self.current_map["npcs"] = [NPC(n) for n in data.get("npcs", [])]

        # --- Cargar props ---
        self.current_map["props"] = []
        for p in data.get("props", []):
            from mundos.prop import Prop
            prop = Prop(
                p["x"],
                p["y"],
                p["image"],
                p.get("collision", False),
                p.get("teleport_to", None)
            )
            self.current_map["props"].append(prop)

        # --- Teletransporte ---
        self.current_map["teleports"] = [
            pygame.Rect(t["x"], t["y"], t["w"], t["h"])
            for t in data.get("teleports", [])
        ]
        self.current_map["teleports_data"] = data.get("teleports", [])

    # ---------- SINCRONIZACIÓN DEL SPRITE ----------
    def sync_player_sprite(self, player):
        """Sincroniza la posición visual del jugador con su hitbox"""
        player.sprite_pos.x = player.hitbox.x - (player.image_rect.width - player.hitbox.width) // 2
        player.sprite_pos.y = player.hitbox.y - (player.image_rect.height - player.hitbox.height)
        player.image_rect.topleft = (int(player.sprite_pos.x), int(player.sprite_pos.y))

    def sync_companion_to_player(self, player):
        """Coloca la compañera en el spawn junto al jugador"""
        comp = self.game.scene.companion
        comp.hitbox.x = player.hitbox.x - 40
        comp.hitbox.y = player.hitbox.y
        comp.sprite_pos.x = comp.hitbox.x
        comp.sprite_pos.y = comp.hitbox.y
        comp.image_rect.topleft = (comp.hitbox.x, comp.hitbox.y)

    def get_spawn(self, direction):
        """Devuelve las coordenadas de spawn según la dirección de entrada"""
        sp = self.current_map.get("spawn_points", {})
        return sp.get(direction, None)

    # ---------- ACTUALIZACIÓN DEL MAPA ----------
    def update(self, player):
        width = self.current_map["width"]
        height = self.current_map["height"]

        # ---------- CONEXIONES ENTRE MAPAS ----------
        # Derecha
        if player.hitbox.right >= width:
            if "right" in self.current_map["connections"]:
                next_map = self.current_map["connections"]["right"]
                self.load_map(next_map)
                spawn = self.get_spawn("right")
                if spawn:
                    player.hitbox.x = spawn["x"]
                    player.hitbox.y = spawn["y"]
                else:
                    player.hitbox.left = 0
                self.sync_player_sprite(player)
                self.sync_companion_to_player(player)
            else:
                player.hitbox.right = width

        # Izquierda
        elif player.hitbox.left <= 0:
            if "left" in self.current_map["connections"]:
                next_map = self.current_map["connections"]["left"]
                self.load_map(next_map)
                spawn = self.get_spawn("left")
                if spawn:
                    player.hitbox.x = spawn["x"]
                    player.hitbox.y = spawn["y"]
                else:
                    player.hitbox.right = width
                self.sync_player_sprite(player)
                self.sync_companion_to_player(player)
            else:
                player.hitbox.left = 0

        # Arriba
        elif player.hitbox.top <= 0:
            if "up" in self.current_map["connections"]:
                next_map = self.current_map["connections"]["up"]
                self.load_map(next_map)
                spawn = self.get_spawn("up")
                if spawn:
                    player.hitbox.x = spawn["x"]
                    player.hitbox.y = spawn["y"]
                else:
                    player.hitbox.bottom = height
                self.sync_player_sprite(player)
                self.sync_companion_to_player(player)
            else:
                player.hitbox.top = 0

        # Abajo
        elif player.hitbox.bottom >= height:
            if "down" in self.current_map["connections"]:
                next_map = self.current_map["connections"]["down"]
                self.load_map(next_map)
                spawn = self.get_spawn("down")
                if spawn:
                    player.hitbox.x = spawn["x"]
                    player.hitbox.y = spawn["y"]
                else:
                    player.hitbox.top = 0
                self.sync_player_sprite(player)
                self.sync_companion_to_player(player)
            else:
                player.hitbox.bottom = height

        # ---------- ACTUALIZAR NPCs ----------
        for npc in self.current_map.get("npcs", []):
            npc.update(self.game.clock.get_time() / 1000)

        # ---------- COLISIONES CON PROPS ----------
        for prop in self.current_map["props"]:
            if prop.collision and player.hitbox.colliderect(prop.collision):
                if player.hitbox.centerx < prop.collision.centerx:
                    player.hitbox.right = prop.collision.left
                else:
                    player.hitbox.left = prop.collision.right
                if player.hitbox.centery < prop.collision.centery:
                    player.hitbox.bottom = prop.collision.top
                else:
                    player.hitbox.top = prop.collision.bottom
                self.sync_player_sprite(player)

        # ---------- TELEPORTES ----------
        for i, tp_rect in enumerate(self.current_map["teleports"]):
            if player.hitbox.colliderect(tp_rect):
                tp = self.current_map["teleports_data"][i]
                self.load_map(tp["to_map"])
                spawn = self.get_spawn(tp["spawn"])
                if spawn:
                    player.hitbox.x = spawn["x"]
                    player.hitbox.y = spawn["y"]
                self.sync_player_sprite(player)
                self.sync_companion_to_player(player)
                break

        # ---------- ACTUALIZAR NPCs nuevamente (por si cambiaron de mapa) ----------
        for npc in self.current_map.get("npcs", []):
            npc.update(self.game.clock.get_time() / 1000)

    # ---------- DIBUJAR MAPA ----------
    def draw(self, screen, player, companion=None):
        # dibujar background
        if self.current_map.get("background"):
            screen.blit(self.current_map["background"], (0, 0))
        else:
            screen.fill(self.current_map["color"])

        # construir lista de objetos dibujables con su "z" (y bottom)
        drawables = []

        # props
        for prop in self.current_map["props"]:
            drawables.append(("prop", prop.rect.bottom, prop))

        # npcs
        for npc in self.current_map.get("npcs", []):
            drawables.append(("npc", npc.rect.bottom, npc))

        # player y companion
        drawables.append(("player", player.hitbox.bottom, player))
        if companion:
            drawables.append(("companion", companion.hitbox.bottom, companion))

        # ordenar por bottom (para que los objetos delante se dibujen encima)
        drawables.sort(key=lambda x: x[1])
        for _, _, obj in drawables:
            obj.draw(screen)

    def draw_props(self, screen):
        """Dibuja solo los props"""
        for prop in self.current_map["props"]:
            prop.draw(screen)
