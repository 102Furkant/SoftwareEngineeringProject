import pygame
import sys
from ui import FluidSimulatorUI  # ui.py'deki arayüz sınıfını import ediyoruz

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))  # Pencere boyutu
    pygame.display.set_caption("2D Fluid Simulator")

    clock = pygame.time.Clock()
    ui = FluidSimulatorUI()  # Arayüz sınıfı

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        ui.handle_events()  # Kullanıcı girişleri
        ui.draw_obstacles() # Engel çizimleri
        ui.update()         # Simülasyon adımı
        ui.render(screen)   # Ekranı güncelle

        pygame.display.flip()
        clock.tick(60)      # 60 FPS

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
