import pygame
from ui import create_screen
from input_handler import handle_events
from renderer import render

def main():
    pygame.init()

    screen, clock, pixel_array = create_screen()
    running = True
    drawing = False

    while running:
        running, drawing = handle_events(drawing, pixel_array)
        render(screen, pixel_array)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
