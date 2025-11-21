import pygame
import os

class Prop:
    def __init__(self, x, y, image_path, collision=False, teleport_to=None):
        """
        image_path = ruta al PNG
        collision = True → el player choca
        teleport_to = {"map": "zona2", "spawn": "left"} → cambia de zona
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(image_path)

        self.image = pygame.image.load(image_path).convert_alpha()
        
        # posición donde se dibuja el PNG
        self.rect = self.image.get_rect(topleft=(x, y))

        # colisión opcional (zona de choque)
        self.collision = pygame.Rect(x, y, self.rect.width, self.rect.height) if collision else None

        # cambio de zona opcional
        self.teleport_to = teleport_to

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)
