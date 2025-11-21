import pygame 

# Clase base para todas las escenas del juego
class Scene:
    def __init__(self, game):
        self.game = game  # Guarda una referencia al objeto principal del juego
        self.current_scene = None  # Guarda la escena actual si se está cambiando a otra

    # Método que se llama al entrar en la escena
    def on_enter(self):
        pass  # Se puede sobreescribir en subclases para inicializar elementos

    # Método que se llama al salir de la escena
    def on_exit(self):
        pass  # Se puede sobreescribir en subclases para limpiar recursos

    # Maneja eventos básicos de Pygame
    def handle_events(self):
        for event in pygame.event.get():  # Recorre todos los eventos de la cola
            if event.type == pygame.QUIT:  # Si se cierra la ventana
                self.game.running = False  # Detiene el loop principal del juego

    # Cambia a otra escena
    def change_scene(self, new_scene):
        self.current_scene = new_scene  # Guarda la nueva escena como la actual

    # Actualiza la escena (se llama cada frame)
    def update(self, dt):
        if self.current_scene:  # Si hay una escena activa
            self.current_scene.update(dt)  # Llama al update de la escena actual

    # Dibuja la escena en pantalla
    def draw(self, screen):
        if self.current_scene:  # Si hay una escena activa
            self.current_scene.draw(screen)  # Llama al draw de la escena actual
