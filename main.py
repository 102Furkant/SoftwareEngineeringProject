import pygame
import sys
from frontend.python.basic_test_ui import FluidSimulatorUI

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Navier-Stokes Simülasyonu")

    clock = pygame.time.Clock()
    ui = FluidSimulatorUI()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        ui.handle_events()
        ui.update()
        ui.render(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
