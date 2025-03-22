import pygame

GRID_SIZE = (50, 50)
PIXEL_SIZE = 15

def create_screen():
    screen = pygame.display.set_mode((GRID_SIZE[0] * PIXEL_SIZE, GRID_SIZE[1] * PIXEL_SIZE))
    pygame.display.set_caption("2D Akışkan Simülasyonu")
    clock = pygame.time.Clock()
    pixel_array = [[0 for _ in range(GRID_SIZE[0])] for _ in range(GRID_SIZE[1])]
    return screen, clock, pixel_array
