import pygame

PIXEL_SIZE = 15
GRID_SIZE = (50, 50)

def render(screen, pixel_array):
    screen.fill((0, 0, 0))  

    for y in range(GRID_SIZE[1]):
        for x in range(GRID_SIZE[0]):
            if pixel_array[y][x] == 1:
                pygame.draw.rect(screen, (255, 255, 255), (x * PIXEL_SIZE, y * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))
