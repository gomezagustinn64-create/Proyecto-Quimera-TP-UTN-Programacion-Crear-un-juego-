# entidades/npc.py
import pygame
import math    # Librería para cálculos matemáticos (distancias, vectores, etc.)

# Clase que representa un NPC en el juego
class NPC:
    def __init__(self, data):
        # Nombre del NPC
        self.name = data["name"]
        
        # Sprite principal del NPC
        self.image = pygame.image.load(data["sprite"]).convert_alpha()

        # Escalado opcional del sprite
        scale = data.get("scale", 1.0)
        if scale != 1.0:
            w = int(self.image.get_width() * scale)
            h = int(self.image.get_height() * scale)
            self.image = pygame.transform.scale(self.image, (w, h))

        # Posición y rectángulo de colisión
        self.rect = self.image.get_rect(topleft=(data.get("x", 0), data.get("y", 0)))
        self.hitbox = self.rect.copy()  # Hitbox separada para colisiones

        # Diálogo del NPC (lista de strings)
        self.dialogue = data.get("dialogue", [])
        self.dialogue_index = 0  # Índice para avanzar en los diálogos
        self.is_interacting = False  # True si el jugador está interactuando

        # 🔥 Opcional: datos del retrato del NPC
        self.portrait_data = data.get("portrait", None)

        # Movimiento opcional
        self.walk_speed = data.get("walk_speed", 0)  # Velocidad de caminata
        self.path = data.get("path", [])             # Lista de puntos a recorrer
        self.path_index = 0                           # Índice del punto actual
        self.target_pos = None                        # Posición objetivo
        if self.walk_speed > 0 and self.path:
            self.target_pos = pygame.Vector2(self.path[0])  # Inicializa el primer objetivo

    def update(self, dt):
        """
        Actualiza el NPC cada frame.
        Solo camina si tiene velocidad y no está interactuando.
        """
        if self.walk_speed > 0 and not self.is_interacting:
            self._walk(dt)

    def _walk(self, dt):
        """
        Lógica de movimiento automático siguiendo la ruta (path).
        """
        if not self.target_pos:
            return
        
        current = pygame.Vector2(self.rect.center)  # Posición actual
        target = pygame.Vector2(self.target_pos)    # Posición objetivo
        vec = target - current                       # Vector hacia el objetivo
        dist = vec.length()                          # Distancia al objetivo
        
        # Si llegó al objetivo, pasar al siguiente punto del path
        if dist < 2:
            self.path_index = (self.path_index + 1) % len(self.path)
            self.target_pos = pygame.Vector2(self.path[self.path_index])
            return

        # Normalizar vector y mover NPC según velocidad y dt
        vec = vec.normalize()
        movement = vec * self.walk_speed * dt
        self.rect.x += movement.x
        self.rect.y += movement.y
        
        # Sincronizar hitbox con rect
        self.hitbox.topleft = self.rect.topleft

    def interact(self):
        """
        Inicia la interacción con el jugador.
        Devuelve la lista de diálogo.
        """
        self.is_interacting = True
        self.dialogue_index = 0
        return self.dialogue

    def end_interaction(self):
        """
        Finaliza la interacción con el jugador.
        """
        self.is_interacting = False
        self.dialogue_index = 0

    def draw(self, screen):
        """
        Dibuja el sprite del NPC en pantalla.
        """
        screen.blit(self.image, self.rect)
