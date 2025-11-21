import pygame
import math
import os

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.selected_index = 0
        self.font = pygame.font.SysFont("Comicsans", 40)
        self.time_levitation = 0

        self.YELLOW = (255, 255, 0)
        self.BLACK = (0, 0, 0)

        # Cargar imágenes
        base_path = os.path.join("assets", "images")
        self.background = pygame.image.load(os.path.join(base_path, "Cielo_fondo.png")).convert()
        self.background = pygame.transform.scale(self.background, self.screen.get_size())

        self.prota1 = pygame.image.load(os.path.join(base_path, "Lenard.png")).convert_alpha()
        self.prota1 = pygame.transform.scale(self.prota1, (400, 400))  # ajustar tamaño

        self.npc1 = pygame.image.load(os.path.join(base_path, "Pika.png")).convert_alpha()
        self.npc1 = pygame.transform.scale(self.npc1, (300, 300))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_w, pygame.K_UP]:
                self.selected_index = (self.selected_index - 1) % 2  # solo dos opciones
            elif event.key in [pygame.K_s, pygame.K_DOWN]:
                self.selected_index = (self.selected_index + 1) % 2

            elif event.key == pygame.K_RETURN:
                return "Jugar" if self.selected_index == 0 else "Salir"

        return None

    def update(self, dt):
        self.time_levitation += dt * 5  # velocidad levitación

    def draw(self):
        # Dibujar fondo
        self.screen.blit(self.background, (0, 0))

        # Dibujar sprites en posiciones fijas 
        self.screen.blit(self.prota1, (250, 50))
        self.screen.blit(self.npc1, (500, 145))

        opciones_texto = ["Jugar", "Salir"]

        # Dibujar opciones del menú con levitación
        for i, texto in enumerate(opciones_texto):
            color = self.YELLOW if i == self.selected_index else self.BLACK
            base_y = 225 + i * 80

            if i == self.selected_index:
                offset_levitation = math.sin(self.time_levitation) * 5
                y = base_y + offset_levitation
            else:
                y = base_y

            text_surf = self.font.render(texto, True, color)
            rect = text_surf.get_rect(center=(250 // 2, y))
            self.screen.blit(text_surf, rect)
