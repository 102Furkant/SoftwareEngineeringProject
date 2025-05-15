import pygame
import numpy as np
from backend import FluidSimulator

class FluidSimulatorUI:
    def __init__(self, width=200, height=150, scale=4):
        self.sim = FluidSimulator(width, height)
        self.scale = scale  # hücre boyutu

        # Başlangıç obstacle'ı belirle
        self.sim.set_obstacle('square', size=min(width, height)//4)

        self.drawing = False  # mouse basılı mı
        self.draw_value = True  # çizilen yerler engel mi

    def handle_events(self):
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        if mouse_buttons[0]:  # Sol tuş basılıyken duvar çiz
            self.drawing = True
            self.set_obstacle_at_pos(mouse_pos)
        else:
            self.drawing = False

        # Space tuşuna basınca soldan sağa yoğunluk ekle
        if keys[pygame.K_SPACE]:
            self.sim.inject(10.0, direction='left')

    def set_obstacle_at_pos(self, mouse_pos):
        x, y = mouse_pos
        grid_x = x // self.scale
        grid_y = y // self.scale

        if 0 <= grid_x < self.sim.width and 0 <= grid_y < self.sim.height:
            # obstacle maskesini güncelle
            self.sim.obstacle[grid_y, grid_x] = True
            # içerideki akışkanı sıfırla
            self.sim.density[grid_y, grid_x] = 0
            self.sim.Vx[grid_y, grid_x] = 0
            self.sim.Vy[grid_y, grid_x] = 0

    def update(self):
        # Simülasyon adımı için dt belirle
        self.sim.step(0.1)

    def draw_obstacles(self):
        # Duvar çizimi arayüzde özel olarak yapılacaksa buraya konulabilir
        pass

    def render(self, screen):
        #ekranı temizle
        screen.fill((0, 0, 0))

        # Tüm grid hücrelerini çiz
        for y in range(self.sim.height):
            for x in range(self.sim.width):
                px = x * self.scale
                py = y * self.scale

                if self.sim.obstacle[y, x]:
                    color = (150, 150, 150)  # gri duvar
                else:
                    d = self.sim.density[y, x]
                    # Yoğunluğu kırmızı tonlarında göster (0-255 arası)
                    c = min(255, int(d * 255))
                    color = (c, 0, 0)

                rect = pygame.Rect(px, py, self.scale, self.scale)
                pygame.draw.rect(screen, color, rect)
