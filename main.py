import pygame
import numpy as np
from backend.simulation import FluidSimulator

def main():
    # initialize pygame
    pygame.init()
    
    # const initialize
    WINDOW_SIZE = (800, 600)
    GRID_SIZE = (100, 75)  # Reduced grid size for better performance
    CELL_SIZE = (WINDOW_SIZE[0] // GRID_SIZE[0], WINDOW_SIZE[1] // GRID_SIZE[1])
    
    # create window
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Fluid Simulation 2D v.alpha")
    
    # create simulator with more stable parameters
    simulator = FluidSimulator(
        nx=GRID_SIZE[0],
        ny=GRID_SIZE[1],
        dx=1.0,
        dt=0.05,  # Reduced time step for stability, can change later, or create more variations
        viscosity=0.1,  # Increased viscosity for stability, can change later, or create more variations
        u_in=0.5  # Reduced inflow velocity for stability, can change later, or create more variations
    )
    
    # add initial obstacle could've add a button to add or remove later
    obstacle = np.zeros((GRID_SIZE[1], GRID_SIZE[0]), dtype=bool)
    # add a circle obstacle, can change the shape later
    center_x, center_y = GRID_SIZE[0]//2, GRID_SIZE[1]//2
    radius = 10
    y, x = np.ogrid[:GRID_SIZE[1], :GRID_SIZE[0]]
    obstacle[(x-center_x)**2 + (y-center_y)**2 <= radius**2] = True
    simulator.set_obstacle(obstacle)
    
    # main loop
    clock = pygame.time.Clock()
    running = True
    drawing = False
    
    # font for fps display, irrelevant for backend
    font = pygame.font.Font(None, 36)
    
    # initialize velocity field
    u = np.zeros((GRID_SIZE[1], GRID_SIZE[0]))
    v = np.zeros((GRID_SIZE[1], GRID_SIZE[0]))
    
    while running:
        # handle events ; 1 is left click, 2 is right click, 3 is middle click. can add a usage form for right click and middle click later (maybe erase function)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  
                    drawing = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  
                    drawing = False
            elif event.type == pygame.MOUSEMOTION and drawing:
                # convert mouse position to grid coordinates
                grid_x = event.pos[0] // CELL_SIZE[0]
                grid_y = event.pos[1] // CELL_SIZE[1]
                # add obstacle at mouse position
                if 0 <= grid_x < GRID_SIZE[0] and 0 <= grid_y < GRID_SIZE[1]:
                    # create a small 3x3 obstacle at the mouse position
                    obstacle = simulator.get_obstacle()
                    for dy in range(-1, 2):
                        for dx in range(-1, 2):
                            ny, nx = grid_y + dy, grid_x + dx
                            if 0 <= ny < GRID_SIZE[1] and 0 <= nx < GRID_SIZE[0]:
                                obstacle[ny, nx] = True
                    simulator.set_obstacle(obstacle)
        
        # update simulation
        simulator.step()
        
        # get velocity field for visualization
        u, v = simulator.get_velocity()
        
        # handle potential infinite values and smooth the field
        u = np.nan_to_num(u, nan=0.0, posinf=0.5, neginf=-0.5)
        v = np.nan_to_num(v, nan=0.0, posinf=0.5, neginf=-0.5)
        
        # apply smoothing to velocity field, if its too smooth, it can change the range later
        u = np.clip(u, -0.5, 0.5)
        v = np.clip(v, -0.5, 0.5)
        
        # calculate velocity magnitude with smoothing
        velocity_magnitude = np.sqrt(u**2 + v**2)
        velocity_magnitude = np.clip(velocity_magnitude, 0, 0.5)  # Clip to [0, 0.5] range
        
        # draw
        screen.fill((0, 0, 0))
        
        # draw fluid velocity
        for y in range(GRID_SIZE[1]):
            for x in range(GRID_SIZE[0]):
                if not simulator.get_obstacle()[y, x]:
                    # calculate color based on velocity magnitude
                    vel = velocity_magnitude[y, x]
                    color_value = min(255, int(vel * 510))  # scale for visibility
                    color = (0, 0, color_value)
                    pygame.draw.rect(screen, color, 
                                   (x * CELL_SIZE[0], y * CELL_SIZE[1],
                                    CELL_SIZE[0], CELL_SIZE[1]))
        
        # draw obstacles
        for y in range(GRID_SIZE[1]):
            for x in range(GRID_SIZE[0]):
                if simulator.get_obstacle()[y, x]:
                    pygame.draw.rect(screen, (100, 100, 100),
                                   (x * CELL_SIZE[0], y * CELL_SIZE[1],
                                    CELL_SIZE[0], CELL_SIZE[1]))
        
        # draw fps, also irrelevant for backend
        fps = clock.get_fps()
        fps_text = font.render(f"FPS: {fps:.1f}", True, (255, 255, 255))
        screen.blit(fps_text, (10, 10))
        
        pygame.display.flip()
        clock.tick(60)  # cap at 60 fps, we do not need more
    
    pygame.quit()

if __name__ == "__main__":
    main()
