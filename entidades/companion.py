import pygame 
import os  # Para manejar rutas de archivos
from entidades.player import Player  # Importa la clase base Player

# Clase Companion que hereda de Player
class Companion(Player):

    # Ruta base donde están los sprites del companion
    BASE_PATH = os.path.join("assets", "images", "sprites", "overworld", "pika")

    @staticmethod
    def load(img_name):
        """
        Carga una imagen del companion desde la carpeta BASE_PATH
        """
        p = os.path.join(Companion.BASE_PATH, img_name)  # Construye la ruta completa
        if not os.path.exists(p):  # Verifica que el archivo exista
            raise FileNotFoundError(f"[Companion] Imagen no encontrada: {p}")
        img = pygame.image.load(p).convert_alpha()  # Carga la imagen con transparencia
        img = pygame.transform.scale_by(img, 1.6)  # Escala la imagen 1.6x
        return img

    def __init__(self, x, y):
        super().__init__(x, y)  # Llama al constructor del Player base

        load = Companion.load  # Alias para facilitar la carga de sprites

        # Diccionario con las animaciones para cada dirección
        self.animations = {
            "down": [
                load("id_down_pika.png"), load("w1_down_pika.png"),
                load("id_down_pika.png"), load("w2_down_pika.png")
            ],
            "up": [
                load("id_up_pika.png"), load("w1_up_pika.png"),
                load("id_up_pika.png"), load("w2_up_pika.png")
            ],
            "left": [
                load("id_left_pika.png"), load("w1_left_pika.png"),
                load("id_left_pika.png"), load("w2_left_pika.png")
            ],
            "right": [
                load("id_right_pika.png"), load("w1_right_pika.png"),
                load("id_right_pika.png"), load("w2_right_pika.png")
            ]
        }

        # Imagen inicial del companion
        self.image = self.animations[self.direction][0]
        self.image_rect = self.image.get_rect(topleft=self.sprite_pos.xy)  # Rect de la imagen

        self.follow_speed = 190  # Velocidad a la que sigue al player

    # ---------- MOVIMIENTOS EXPLÍCITOS ----------
    def move_sprite(self, dx, dy):
        """Mueve solo el sprite visual (no la hitbox). dx,dy en píxeles."""
        self.sprite_pos.x += dx
        self.sprite_pos.y += dy
        # actualizar rect visual
        self.image_rect.topleft = (int(self.sprite_pos.x), int(self.sprite_pos.y))

    def move_hitbox(self, dx, dy):
        """Mueve solo la hitbox (no toca la imagen)."""
        self.hitbox.x += int(round(dx))
        self.hitbox.y += int(round(dy))

    def move_both(self, dx, dy, collisions=None):
        """
        Mueve hitbox y sprite juntos.
        Aplica colisiones solo a la hitbox y sincroniza sprite.
        """
        if collisions is None:
            collisions = []

        # Mover hitbox en eje X
        self.hitbox.x += int(round(dx))
        for c in collisions:
            if self.hitbox.colliderect(c):
                if dx > 0:
                    self.hitbox.right = c.left
                elif dx < 0:
                    self.hitbox.left = c.right

        # Mover hitbox en eje Y
        self.hitbox.y += int(round(dy))
        for c in collisions:
            if self.hitbox.colliderect(c):
                if dy > 0:
                    self.hitbox.bottom = c.top
                elif dy < 0:
                    self.hitbox.top = c.bottom

        # Sincronizar sprite con hitbox
        self.sprite_pos.x = self.hitbox.x - (self.image_rect.width - self.hitbox.width) // 2
        self.sprite_pos.y = self.hitbox.y - (self.image_rect.height - self.hitbox.height)
        self.image_rect.topleft = (int(self.sprite_pos.x), int(self.sprite_pos.y))

    def update_animation(self, dt, moving=True):
        """
        Actualiza la animación del companion.
        Si se mueve → cambia frames; si no → imagen idle.
        """
        if moving:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(self.animations[self.direction]):
                self.frame_index = 0.0
            self.image = self.animations[self.direction][int(self.frame_index)]
        else:
            self.frame_index = 0.0
            self.image = self.animations[self.direction][0]

    def follow(self, target, dt):
        """
        Hace que el companion siga al player.
        target → objeto a seguir
        dt → delta time para movimiento suave
        """
        # Si el player no se mueve → idle
        if not getattr(target, "is_moving", True):
            self.update_animation(dt, moving=False)
            return

        # ------ POSICIÓN IDEAL SEGÚN DIRECCIÓN DEL PLAYER ------
        offset_x = 0
        offset_y = 0

        if target.direction == "down":
            offset_y = -50   # companion detrás del player
        elif target.direction == "up":
            offset_y = 50
        elif target.direction == "left":
            offset_x = 50
        elif target.direction == "right":
            offset_x = -50

        # Punto ideal a seguir
        goal_x = target.hitbox.centerx + offset_x
        goal_y = target.hitbox.centery + offset_y

        dx = goal_x - self.hitbox.centerx
        dy = goal_y - self.hitbox.centery

        dist = (dx*dx + dy*dy)**0.5  # distancia al punto ideal

        # distancia mínima → no moverse si está cerca
        if dist <= 10:
            self.update_animation(dt, moving=False)
            return

        # Normalizar vector de movimiento
        nx = dx / dist
        ny = dy / dist

        # Aplicar movimiento con velocidad
        self.hitbox.x += nx * self.follow_speed * dt
        self.hitbox.y += ny * self.follow_speed * dt

        # Determinar dirección según movimiento
        if abs(dx) > abs(dy):
            self.direction = "right" if dx > 0 else "left"
        else:
            self.direction = "down" if dy > 0 else "up"

        # Actualizar animación según dirección y movimiento
        self.update_animation(dt, moving=True)

        # Sincronizar sprite con hitbox
        self.sprite_pos.x = self.hitbox.x - (self.image_rect.width - self.hitbox.width) // 2
        self.sprite_pos.y = self.hitbox.y - (self.image_rect.height - self.hitbox.height)
        self.image_rect.topleft = (int(self.sprite_pos.x), int(self.sprite_pos.y))
