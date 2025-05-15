import pygame
import sys
from ui import FluidSimulatorUI  # ui.py'deki arayüz sınıfını import ediyoruz

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))  # Pencere boyutu, istediğin gibi ayarlayabilirsin
    pygame.display.set_caption("2D Fluid Simulator")

    clock = pygame.time.Clock()
    ui = FluidSimulatorUI()  # Arayüz sınıfı örneği

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Dilersen burada ekstra event yönetimi yapılabilir ama
            # ui.handle_events() fonksiyonu zaten bu işi yapacak

        ui.handle_events()  # Kullanıcı girişlerini işle
        ui.draw_obstacles() # Engel çizimlerini güncelle
        ui.update()         # Simülasyon adımı
        ui.render(screen)   # Ekranı güncelle

        pygame.display.flip()
        clock.tick(60)      # 60 FPS sabit hız

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
