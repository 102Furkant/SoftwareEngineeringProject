import pygame
import numpy as np
from scipy.ndimage import gaussian_filter

class FluidUI:
    def __init__(self, simulator, width=1000, height=1000):
        self.sim = simulator
        self.width = width
        self.height = height
        self.cell_size_x = width // simulator.nx
        self.cell_size_y = height // simulator.ny
        self.screen = None
        self.font = None
        self.running = True
        self.paused = True
        self.show_pressure = False
        self.drawing_obstacle = False
        self.clearing_obstacle = False
        self.show_stats = False
        self.active_mode = None
        self.circle_radius = int(4 * 1.5)
        self.default_rect_width = int(10 * 1.5)
        self.default_rect_height = int(5 * 1.5)
        self.rect_coords = [0, 0, 0, 0]
        self.GUIDE_HEIGHT = 100 
        self.viscosity_slider_value = 0.5
        self.viscosity_slider_rect = pygame.Rect(20, self.height - self.GUIDE_HEIGHT - 50, 200, 10)
        self.slider_knob_pos = 120
        self.dragging_slider = False
        self.BG_COLOR = (0, 0, 0) 
        self.OBSTACLE_COLOR = (255, 255, 255)
        self.AIR_COLOR = (0, 0, 255)  # Default air color
        self.PRESSURE_COLORS = [(255, 0, 0), (255, 255, 0)]
        self.GUIDE_BG_COLOR = (50, 50, 50)
        self.SEPARATOR_COLOR = (255, 255, 255)

        self.color_options = [
            ((0, 0, 255), pygame.Rect(self.width - 60, self.height - 40, 20, 20)),  # Blue
            ((0, 255, 0), pygame.Rect(self.width - 90, self.height - 40, 20, 20)),  # Green
            ((255, 0, 0), pygame.Rect(self.width - 120, self.height - 40, 20, 20)), # Red
            ((0, 255, 255), pygame.Rect(self.width - 150, self.height - 40, 20, 20)) # Cyan
        ]

    def init_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("2D Fluid Simulation (Admin Panel)")
        self.font = pygame.font.SysFont("arial", 14)

    def draw_grid(self):
        u, v = self.sim.get_velocity()
        p = self.sim.get_pressure()
        obstacle = self.sim.get_obstacle()
        speed = np.sqrt(u**2 + v**2)
        speed_smooth = gaussian_filter(speed, sigma=1.0)
        max_speed = np.max(speed_smooth) if np.max(speed_smooth) > 0 else 1
        max_pressure = np.max(np.abs(p)) if np.max(np.abs(p)) > 0 else 1


        self.screen.fill(self.BG_COLOR)  # (0, 0, 0)

        for i in range(self.sim.ny):
            for j in range(self.sim.nx):
                rect = (j * self.cell_size_x, i * self.cell_size_y,
                        self.cell_size_x, self.cell_size_y)

                if obstacle[i, j]:
                    color = self.OBSTACLE_COLOR  # Engeller beyaz
                elif self.show_pressure:
                    # Basınç görselleştirme
                    p_norm = np.clip(np.abs(p[i, j]) / max_pressure, 0, 1)
                    r = int(self.PRESSURE_COLORS[0][0] * (1 - p_norm) + self.PRESSURE_COLORS[1][0] * p_norm)
                    g = int(self.PRESSURE_COLORS[0][1] * (1 - p_norm) + self.PRESSURE_COLORS[1][1] * p_norm)
                    b = int(self.PRESSURE_COLORS[0][2] * (1 - p_norm) + self.PRESSURE_COLORS[1][2] * p_norm)
                    color = (r, g, b)
                else:
                    # Hava hücreleri için seçilen AIR_COLOR kullanılıyor, yoğunluk hız ile ölçekleniyor
                    s_norm = np.clip(speed_smooth[i, j] / max_speed, 0, 1)
                    r = int(self.AIR_COLOR[0] * s_norm)
                    g = int(self.AIR_COLOR[1] * s_norm)
                    b = int(self.AIR_COLOR[2] * s_norm)
                    color = (r, g, b)

                pygame.draw.rect(self.screen, color, rect)

    def draw_stats(self):
        stats = self.sim.get_statistics()
        stats_text = [
            f"Zaman: {stats['time']:.2f}s",
            f"Adım: {stats['step_count']}",
            f"Max Hız: {stats['max_speed']:.2f}",
            f"Ort Hız: {stats['avg_speed']:.2f}",
            f"Max Basınç: {stats['max_pressure']:.2f}",
            f"Min Basınç: {stats['min_pressure']:.2f}",
            f"Adım Süresi: {stats['avg_step_time']*1000:.1f}ms"
        ]

        for i, text in enumerate(stats_text):
            label = self.font.render(text, True, (255, 255, 255))
            text_width = label.get_width()
            self.screen.blit(label, (self.width - text_width - 10, 10 + i * 20))

    def draw_slider(self):
        pygame.draw.rect(self.screen, (100, 100, 100), self.viscosity_slider_rect)
        knob_rect = pygame.Rect(self.slider_knob_pos, self.viscosity_slider_rect.y - 5, 10, 20)
        pygame.draw.rect(self.screen, (255, 255, 255), knob_rect)
        label = self.font.render(f"Viskozite: {self.viscosity_slider_value:.2f}", True, (255, 255, 255))
        self.screen.blit(label, (20, self.viscosity_slider_rect.y - 25))

    def draw_guide(self):
        guide_rect = pygame.Rect(0, self.height - self.GUIDE_HEIGHT, self.width, self.GUIDE_HEIGHT)
        pygame.draw.rect(self.screen, self.GUIDE_BG_COLOR, guide_rect)
        pygame.draw.rect(self.screen, self.SEPARATOR_COLOR, guide_rect, 2)

        guide_text = [
            "SPACE: Başlat/Durdur", "R: Sıfırla",
            "S: İstatistik", "C: Daire", "X: Dikdörtgen", "H: Yarım Daire", "T: Üçgen", 
            "Sol Tık: Ekle", "Sağ Tık: Sil", "Q: Çık"
        ]

        for i, text in enumerate(guide_text):
            col = i % 3
            row = i // 3
            label = self.font.render(text, True, (255, 255, 255))
            x = 10 + col * (self.width // 3)
            y = self.height - self.GUIDE_HEIGHT + 10 + row * 20
            self.screen.blit(label, (x, y))

    def draw_color_buttons(self):
        for color, rect in self.color_options:
            pygame.draw.rect(self.screen, color, rect)
            if color == self.AIR_COLOR:
                pygame.draw.rect(self.screen, (255, 255, 255), rect, 2)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r:
                    self.sim.reset()
                elif event.key == pygame.K_s:
                    self.show_stats = not self.show_stats
                elif event.key == pygame.K_c:
                    self.active_mode = "circle"
                elif event.key == pygame.K_x:
                    self.active_mode = "rect"
                elif event.key == pygame.K_h:
                    self.active_mode = "semicircle"
                elif event.key == pygame.K_t:
                    self.active_mode = "triangle"
                elif event.key == pygame.K_q:
                    self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                for color, rect in self.color_options:
                    if rect.collidepoint(x, y):
                        self.AIR_COLOR = color
                        break
                if self.viscosity_slider_rect.collidepoint(x, y):
                    self.dragging_slider = True
                    self.slider_knob_pos = min(max(x, self.viscosity_slider_rect.left), 
                                              self.viscosity_slider_rect.right)
                    self.viscosity_slider_value = (self.slider_knob_pos - self.viscosity_slider_rect.left) / self.viscosity_slider_rect.width
                    self.sim.nu = self.viscosity_slider_value * 0.1
                elif event.button == 1:
                    j = x // self.cell_size_x
                    i = y // self.cell_size_y
                    if 0 <= i < self.sim.ny and 0 <= j < self.sim.nx:
                        if self.active_mode == "circle":
                            self.sim.set_obstacle(self.sim.create_circle_obstacle(j, i, int(self.circle_radius)))
                            self.active_mode = None
                        elif self.active_mode == "rect":
                            self.rect_coords[0] = j
                            self.rect_coords[1] = i
                            self.rect_coords[2] = int(j + self.default_rect_width)
                            self.rect_coords[3] = int(i + self.default_rect_height)
                            mask = self.sim.create_rectangle_obstacle(
                                self.rect_coords[0], self.rect_coords[1],
                                self.rect_coords[2], self.rect_coords[3]
                            )
                            self.sim.set_obstacle(mask)
                            self.active_mode = None
                        elif self.active_mode == "semicircle":
                            self.sim.set_obstacle(self.sim.create_semicircle_obstacle(j, i, int(self.circle_radius)))
                            self.active_mode = None
                        elif self.active_mode == "triangle":
                            self.sim.set_obstacle(self.sim.create_triangle_obstacle(j, i, int(self.circle_radius)))
                            self.active_mode = None
                        else:
                            self.drawing_obstacle = True
                elif event.button == 3:
                    self.clearing_obstacle = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.drawing_obstacle = False
                    self.dragging_slider = False
                elif event.button == 3:
                    self.clearing_obstacle = False
            elif event.type == pygame.MOUSEMOTION:
                x, y = event.pos
                if self.dragging_slider:
                    self.slider_knob_pos = min(max(x, self.viscosity_slider_rect.left), 
                                              self.viscosity_slider_rect.right)
                    self.viscosity_slider_value = (self.slider_knob_pos - self.viscosity_slider_rect.left) / self.viscosity_slider_rect.width
                    self.sim.nu = self.viscosity_slider_value * 0.1
                elif self.drawing_obstacle or self.clearing_obstacle:
                    j = x // self.cell_size_x
                    i = y // self.cell_size_y
                    if 0 <= i < self.sim.ny and 0 <= j < self.sim.nx:
                        new_obstacle = self.sim.get_obstacle().copy()
                        new_obstacle[i, j] = self.drawing_obstacle
                        self.sim.set_obstacle(new_obstacle)

    def run(self):
        self.init_pygame()
        clock = pygame.time.Clock()

        while self.running:
            self.handle_events()
            if not self.paused:
                self.sim.step()

            self.screen.fill(self.BG_COLOR)
            self.draw_grid()
            self.draw_slider()
            self.draw_guide()
            self.draw_color_buttons()
            if self.show_stats:
                self.draw_stats()
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
