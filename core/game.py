import pygame
from core import settings  # Importa las configuraciones del juego (título, tamaño de pantalla, FPS, etc.)
from scenes.overworld import OverworldScene  # Importa la escena principal del mundo
from ui.dialogue import DialogueSystem  # Importa el sistema de diálogos

class Game:
    def __init__(self):
        # Configura el título de la ventana usando la constante del settings
        pygame.display.set_caption(settings.TITLE)  # Este se puede usar para establecer un título dinámico
        
        # Crea la ventana con las dimensiones definidas en settings
        self.screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        
        # Sobrescribe el título de la ventana con el nombre del juego
        pygame.display.set_caption("Quimera")
        
        # Reloj para controlar la tasa de actualización (FPS)
        self.clock = pygame.time.Clock()
        
        # Variable de control para el loop principal
        self.running = True

        # Inicializa el sistema de diálogos
        self.dialogue = DialogueSystem(self)
        
        # Crea la escena principal del juego (Overworld)
        self.scene = OverworldScene(self)

    def run(self):
        # Loop principal del juego
        while self.running:
            # Calcula el tiempo entre frames (delta time) para movimiento suave
            dt = self.clock.tick(settings.FPS) / 1000.0
            
            # Obtiene todos los eventos que ocurrieron (teclas, clicks, cierre de ventana, etc.)
            events = pygame.event.get()

            # Manejo básico de eventos de salida
            for e in events:
                if e.type == pygame.QUIT:  # Si se cierra la ventana
                    self.running = False
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:  # Si se presiona ESC
                    self.running = False

            # Actualiza la escena actual, pasando delta time y eventos
            self.scene.update(dt, events)

            # Dibuja la escena en la pantalla
            self.scene.draw(self.screen)

            # Actualiza y dibuja el diálogo si hay alguno activo
            self.dialogue.update(dt)
            self.dialogue.draw(self.screen)

            # Actualiza toda la pantalla con lo dibujado
            pygame.display.flip()
