import pygame
import numpy as np

class FluidSimulatorUI:
    def __init__(self, width=200, height=150, scale=4):
        self.width = width
        self.height = height
        self.scale = scale
        
        # akis alani icin numpy dizileri
        self.velocity_x = np.zeros((height, width))
        self.velocity_y = np.zeros((height, width))
        self.density = np.zeros((height, width))
        self.pressure = np.zeros((height, width))
        
        # simulasyon parametreleri
        self.viscosity = 0.1
        self.diffusion = 0.1
        self.dt = 0.1
        
        # engel matrisi
        self.obstacle = np.zeros((height, width), dtype=bool)
        self.set_initial_obstacle()
        
        # mouse kontrolu
        self.drawing = False

    def set_initial_obstacle(self):
        # basit bir kare engel, ben test icin ekledim, gelismis ui ile beraber tekrar sekil sectirilebilir
        size = min(self.width, self.height) // 4
        x0 = (self.width - size) // 2
        y0 = (self.height - size) // 2
        self.obstacle[y0:y0+size, x0:x0+size] = True

    def handle_events(self):
        mouse_buttons = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        
        if mouse_buttons[0]:
            self.drawing = True
            self.set_obstacle_at_pos(mouse_pos)
        else:
            self.drawing = False

    def set_obstacle_at_pos(self, mouse_pos):
        x, y = mouse_pos
        grid_x = x // self.scale
        grid_y = y // self.scale
        
        if 0 <= grid_x < self.width and 0 <= grid_y < self.height:
            self.obstacle[grid_y, grid_x] = True
            self.density[grid_y, grid_x] = 0
            self.velocity_x[grid_y, grid_x] = 0
            self.velocity_y[grid_y, grid_x] = 0

    def update(self):
        # navier-stokes denklemlerinin basitlestirilmis versiyonu
        self.diffuse_velocity()
        self.advect_velocity()
        self.project_velocity()
        self.diffuse_density()
        self.advect_density()
        
        # sol kenardan sürekli akis
        self.density[:, 0] = 1.0
        self.velocity_x[:, 0] = 1.0

    def diffuse_velocity(self):
        # hiz difuzyonu
        a = self.dt * self.viscosity
        for _ in range(20):
            self.velocity_x[1:-1, 1:-1] = (self.velocity_x[1:-1, 1:-1] + 
                a * (self.velocity_x[1:-1, 2:] + self.velocity_x[1:-1, :-2] +
                     self.velocity_x[2:, 1:-1] + self.velocity_x[:-2, 1:-1])) / (1 + 4 * a)
            self.velocity_y[1:-1, 1:-1] = (self.velocity_y[1:-1, 1:-1] + 
                a * (self.velocity_y[1:-1, 2:] + self.velocity_y[1:-1, :-2] +
                     self.velocity_y[2:, 1:-1] + self.velocity_y[:-2, 1:-1])) / (1 + 4 * a)
            
            # engelleri uygula
            self.velocity_x[self.obstacle] = 0
            self.velocity_y[self.obstacle] = 0

    def advect_velocity(self):
        # hiz adveksiyonu
        for y in range(1, self.height-1):
            for x in range(1, self.width-1):
                if not self.obstacle[y, x]:
                    # geriye dogru adveksiyon
                    x0 = x - self.dt * self.velocity_x[y, x]
                    y0 = y - self.dt * self.velocity_y[y, x]
                    
                    # sinirlari kontrol et
                    x0 = max(0.5, min(self.width-1.5, x0))
                    y0 = max(0.5, min(self.height-1.5, y0))
                    
                    # lineer interpolasyon
                    i0, i1 = int(x0), int(x0) + 1
                    j0, j1 = int(y0), int(y0) + 1
                    s1, s0 = x0 - i0, 1 - (x0 - i0)
                    t1, t0 = y0 - j0, 1 - (y0 - j0)
                    
                    self.velocity_x[y, x] = (s0 * (t0 * self.velocity_x[j0, i0] + t1 * self.velocity_x[j1, i0]) +
                                           s1 * (t0 * self.velocity_x[j0, i1] + t1 * self.velocity_x[j1, i1]))
                    self.velocity_y[y, x] = (s0 * (t0 * self.velocity_y[j0, i0] + t1 * self.velocity_y[j1, i0]) +
                                           s1 * (t0 * self.velocity_y[j0, i1] + t1 * self.velocity_y[j1, i1]))

    def project_velocity(self):
        # hiz alanini diverjanssiz yap
        div = np.zeros((self.height, self.width))
        p = np.zeros((self.height, self.width))
        
        # diverjans hesapla
        div[1:-1, 1:-1] = -0.5 * (
            self.velocity_x[1:-1, 2:] - self.velocity_x[1:-1, :-2] +
            self.velocity_y[2:, 1:-1] - self.velocity_y[:-2, 1:-1]
        )
        
        # poisson denklemini coz
        for _ in range(20):
            p[1:-1, 1:-1] = (div[1:-1, 1:-1] +
                            p[1:-1, 2:] + p[1:-1, :-2] +
                            p[2:, 1:-1] + p[:-2, 1:-1]) / 4.0
            
            # engelleri uygula
            p[self.obstacle] = 0
        
        # hiz alanini guncelle
        self.velocity_x[1:-1, 1:-1] -= 0.5 * (p[1:-1, 2:] - p[1:-1, :-2])
        self.velocity_y[1:-1, 1:-1] -= 0.5 * (p[2:, 1:-1] - p[:-2, 1:-1])
        
        # engelleri uygula
        self.velocity_x[self.obstacle] = 0
        self.velocity_y[self.obstacle] = 0

    def diffuse_density(self):
        # yoğunluk difuzyonu
        a = self.dt * self.diffusion
        for _ in range(20):
            self.density[1:-1, 1:-1] = (self.density[1:-1, 1:-1] + 
                a * (self.density[1:-1, 2:] + self.density[1:-1, :-2] +
                     self.density[2:, 1:-1] + self.density[:-2, 1:-1])) / (1 + 4 * a)
            
            # engelleri uygula
            self.density[self.obstacle] = 0

    def advect_density(self):
        # yoğunluk adveksiyonu
        for y in range(1, self.height-1):
            for x in range(1, self.width-1):
                if not self.obstacle[y, x]:
                    # geriye dogru adveksiyon
                    x0 = x - self.dt * self.velocity_x[y, x]
                    y0 = y - self.dt * self.velocity_y[y, x]
                    
                    # sinirlari kontrol et
                    x0 = max(0.5, min(self.width-1.5, x0))
                    y0 = max(0.5, min(self.height-1.5, y0))
                    
                    # lineer interpolasyon
                    i0, i1 = int(x0), int(x0) + 1
                    j0, j1 = int(y0), int(y0) + 1
                    s1, s0 = x0 - i0, 1 - (x0 - i0)
                    t1, t0 = y0 - j0, 1 - (y0 - j0)
                    
                    self.density[y, x] = (s0 * (t0 * self.density[j0, i0] + t1 * self.density[j1, i0]) +
                                        s1 * (t0 * self.density[j0, i1] + t1 * self.density[j1, i1]))

    def render(self, screen):
        screen.fill((0, 0, 0))
        
        # yoğunluk değerlerini normalize et
        normalized_density = np.clip(self.density * 255, 0, 255).astype(np.uint8)
        
        # tum grid hücrelerini çiz
        for y in range(self.height):
            for x in range(self.width):
                px = x * self.scale
                py = y * self.scale
                
                if self.obstacle[y, x]:
                    color = (150, 150, 150)
                else:
                    c = normalized_density[y, x]
                    color = (c, 0, 0)
                
                rect = pygame.Rect(px, py, self.scale, self.scale)
                pygame.draw.rect(screen, color, rect)
