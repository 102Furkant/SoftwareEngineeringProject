import pygame

PIXEL_SIZE = 15
GRID_SIZE = (50, 50)

def handle_events(drawing, pixel_array):
    running = True
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            drawing = True
        if event.type == pygame.MOUSEBUTTONUP:
            drawing = False

    if drawing:
        mx, my = pygame.mouse.get_pos()
        grid_x = mx // PIXEL_SIZE
        grid_y = my // PIXEL_SIZE
        if 0 <= grid_x < GRID_SIZE[0] and 0 <= grid_y < GRID_SIZE[1]:
            pixel_array[grid_y][grid_x] = 1

    return running, drawing
