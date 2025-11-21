import pygame
from core.game import Game
from ui.menu import Menu

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Proyecto QUIMERA")

    menu = Menu(screen)
    clock = pygame.time.Clock()

    in_menu = True
    running = True
    game = None  # Inicializar la variable

    while running:
        dt = clock.tick(60) / 1000  # tiempo en segundos
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                running = False

        if in_menu:
            # Delegar eventos al menú
            for event in events:
                result = menu.handle_event(event)
                if result == "Jugar":
                    game = Game()
                    in_menu = False
                elif result == "Salir":
                    running = False

            menu.update(dt)
            menu.draw()
            pygame.display.flip()
        else:
            # Delegar todo al juego
            # Suponiendo que Game.run() acepta dt y lista de eventos
            game.run(dt, events)  # Esto debe contener su propio loop de juego interno
