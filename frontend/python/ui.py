# fluid_ui.py (Arayüz)
import pygame
import sys
import json
import requests
import numpy as np
from typing import List, Tuple, Optional

class FluidUIApp:
    def __init__(self):
        pygame.init()
        self.width, self.height = 800, 600
        self.cell_size = 4  # Her hücre için piksel boyutu
        self.grid_width = self.width // self.cell_size
        self.grid_height = self.height // self.cell_size
        
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Akışkan Simülasyonu API Arayüzü")
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 16)
        
        # API Bağlantı Ayarları
        self.api_url = "http://localhost:8000"
        
        # Simülasyon parametreleri
        self.dt = 0.1
        self.steps = 10  # Her API çağrısında kaç adım simüle edilecek
        self.fluid_type = "water"
        self.env_type = "bounded"
        self.shape = "circle"
        
        # Simülasyon verisi
        self.density = np.zeros((self.grid_height, self.grid_width), dtype=float)
        
        # Kontrol değişkenleri
        self.paused = False
        self.draw_mode = "density"  # 'density' veya 'velocity'
        self.mouse_down = False
        self.prev_mouse_pos = None
        self.custom_shape = None
        
        # Kontrol panel boyutları
        self.panel_width = 200
        self.panel_height = self.height
        self.panel_x = self.width - self.panel_width
        
        # API durumu
        self.api_status = "Bağlantı Bekleniyor..."
        self.check_api_connection()
        
        # İlk simülasyon çağrısı
        self.reset_simulation()
    
    def check_api_connection(self):
        try:
            response = requests.get(f"{self.api_url}/health", timeout=2)
            if response.status_code == 200 and response.json()["status"] == "ok":
                self.api_status = "API Bağlandı"
            else:
                self.api_status = "API Hatası!"
        except requests.exceptions.RequestException:
            self.api_status = "API Bağlantı Hatası!"
    
    def reset_simulation(self):
        # API'ye istek gönder
        try:
            data = {
                "shape": self.shape,
                "size": self.grid_width,
                "height": self.grid_height,
                "dt": self.dt,
                "steps": self.steps,
                "fluid_type": self.fluid_type,
                "env_type": self.env_type
            }
            
            if self.shape == "custom" and self.custom_shape is not None:
                data["custom_shape"] = self.custom_shape
                
            response = requests.post(f"{self.api_url}/simulate", json=data, timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                self.density = np.array(result["density"])
                self.api_status = "Simülasyon Başarılı"
            else:
                self.api_status = f"API Hatası: {response.status_code}"
                print(response.text)
        except requests.exceptions.RequestException as e:
            self.api_status = "API İsteği Başarısız!"
            print(f"API hatası: {e}")
    
    def update_simulation(self):
        # Eğer özel bir çizim yapıyorsak, daha fazla simülasyon yapma
        if self.mouse_down:
            return
            
        if not self.paused:
            try:
                data = {
                    "shape": "custom",  # Mevcut yoğunluk durumunu kullan
                    "custom_shape": self.density.tolist(),
                    "size": self.grid_width,
                    "height": self.grid_height,
                    "dt": self.dt,
                    "steps": self.steps,
                    "fluid_type": self.fluid_type,
                    "env_type": self.env_type
                }
                
                response = requests.post(f"{self.api_url}/simulate", json=data, timeout=5)
                
                if response.status_code == 200:
                    result = response.json()
                    self.density = np.array(result["density"])
                    self.api_status = "Simülasyon Güncellendi"
                else:
                    self.api_status = f"API Hatası: {response.status_code}"
            except requests.exceptions.RequestException as e:
                self.api_status = "API İsteği Başarısız!"
                print(f"API hatası: {e}")
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r:
                    self.reset_simulation()
                elif event.key == pygame.K_1:
                    self.fluid_type = "water"
                    self.reset_simulation()
                elif event.key == pygame.K_2:
                    self.fluid_type = "oil"
                    self.reset_simulation()
                elif event.key == pygame.K_3:
                    self.fluid_type = "honey"
                    self.reset_simulation()
                elif event.key == pygame.K_4:
                    self.shape = "circle"
                    self.reset_simulation()
                elif event.key == pygame.K_5:
                    self.shape = "square"
                    self.reset_simulation()
                elif event.key == pygame.K_6:
                    self.shape = "triangle"
                    self.reset_simulation()
                elif event.key == pygame.K_7:
                    self.shape = "ellipse"
                    self.reset_simulation()
                elif event.key == pygame.K_b:
                    self.env_type = "bounded"
                    self.reset_simulation()
                elif event.key == pygame.K_p:
                    self.env_type = "periodic"
                    self.reset_simulation()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_down = True
                self.prev_mouse_pos = pygame.mouse.get_pos()
            
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_down = False
                self.prev_mouse_pos = None
                # Mouse işleme bittiyse, simülasyonu güncelle
                self.update_simulation()
    
    def handle_mouse_interaction(self):
        if self.mouse_down and self.prev_mouse_pos:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            # Kontrol paneli dışında mı kontrol et
            if mouse_x < self.panel_x:
                prev_x, prev_y = self.prev_mouse_pos
                
                # Izgara koordinatlarına dönüştür
                grid_x = mouse_x // self.cell_size
                grid_y = mouse_y // self.cell_size
                
                # Sınırlar içinde mi kontrol et
                if (0 <= grid_x < self.grid_width and 
                    0 <= grid_y < self.grid_height):
                    
                    # Yerel density matrisini güncelle
                    self.density[grid_y, grid_x] = 1.0
                    
                    # Komşu hücrelere de etki ekle (yayma)
                    radius = 3
                    for i in range(-radius, radius+1):
                        for j in range(-radius, radius+1):
                            nx, ny = grid_x + i, grid_y + j
                            if 0 <= nx < self.grid_width and 0 <= ny < self.grid_height:
                                dist = np.sqrt(i*i + j*j)
                                if dist <= radius:
                                    intensity = 1.0 * (1 - dist/radius)
                                    self.density[ny, nx] = max(self.density[ny, nx], intensity)
            
            self.prev_mouse_pos = (mouse_x, mouse_y)
    
    def draw_density(self):
        # Yoğunluk alanını görselleştir
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                density = self.density[y, x]
                
                # Yoğunluğa göre renk belirle (mavi tonları)
                color_val = min(255, int(density * 255))
                color = (0, color_val, min(255, int(color_val * 1.5)))
                
                # Hücreyi çiz
                rect = pygame.Rect(
                    x * self.cell_size, 
                    y * self.cell_size, 
                    self.cell_size, 
                    self.cell_size
                )
                pygame.draw.rect(self.screen, color, rect)
    
    def draw_control_panel(self):
        # Panel arkaplanı
        panel_rect = pygame.Rect(self.panel_x, 0, self.panel_width, self.panel_height)
        pygame.draw.rect(self.screen, (30, 30, 30), panel_rect)
        pygame.draw.line(self.screen, (100, 100, 100), (self.panel_x, 0), (self.panel_x, self.height), 2)
        
        # Başlık
        title = self.font.render("AKIŞKAN SİMÜLASYONU", True, (255, 255, 255))
        self.screen.blit(title, (self.panel_x + 10, 20))
        
        # API durumu
        api_status_color = (0, 255, 0) if "Başarılı" in self.api_status or "Bağlandı" in self.api_status else (255, 100, 100)
        api_text = self.font.render(self.api_status, True, api_status_color)
        self.screen.blit(api_text, (self.panel_x + 10, 50))
        
        # Durum bilgileri
        y_pos = 80
        line_height = 25
        
        status_items = [
            f"Sıvı Tipi: {self.fluid_type}",
            f"Çevre Tipi: {self.env_type}",
            f"Şekil: {self.shape}",
            f"Durum: {'Durduruldu' if self.paused else 'Çalışıyor'}",
            "",
            "KONTROLLER:",
            "SPACE: Duraklat/Devam",
            "R: Sıfırla",
            "",
            "SIVI TİPLERİ:",
            "1: Su",
            "2: Yağ",
            "3: Bal",
            "",
            "ŞEKİLLER:",
            "4: Daire",
            "5: Kare",
            "6: Üçgen",
            "7: Elips",
            "",
            "ÇEVRE TİPLERİ:",
            "B: Sınırlı",
            "P: Periyodik",
            "",
            "Fare ile:",
            "- Sıvı ekle (tıkla ve sürükle)"
        ]
        
        for item in status_items:
            text = self.font.render(item, True, (200, 200, 200))
            self.screen.blit(text, (self.panel_x + 10, y_pos))
            y_pos += line_height
    
    def draw(self):
        self.screen.fill((0, 0, 0))
        
        # Simülasyon alanını çiz
        self.draw_density()
        
        # Kontrol panelini çiz
        self.draw_control_panel()
        
        pygame.display.flip()
    
    def run(self):
        frame_count = 0
        update_interval = 5  # Her 5 karede bir API güncellemesi
        
        while True:
            self.handle_events()
            self.handle_mouse_interaction()
            
            # Belirli aralıklarla simülasyonu güncelle
            if not self.paused and not self.mouse_down and frame_count % update_interval == 0:
                self.update_simulation()
            
            self.draw()
            self.clock.tick(60)  # FPS
            frame_count += 1

if __name__ == "__main__":
    app = FluidUIApp()
    app.run()
