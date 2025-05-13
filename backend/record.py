import os
import cv2
import glob
from PIL import Image, ImageDraw
from models import CellType
from fastapi import FastAPI
from state import init_grid  # Grid'i başlatmak için

# Konfigurasyonlar
SAVE_PATH = "simulation_frames"  # PNG kayıtlarının tutulacağı klasör
VIDEO_FILENAME = "simulation.mp4"  # Final MP4 dosyası
GRID_WIDTH = 50
GRID_HEIGHT = 50

# Klasörü oluştur
os.makedirs(SAVE_PATH, exist_ok=True)

app = FastAPI()

# Global grid değişkeni
grid = init_grid()  # Simülasyon başladığında grid başlatılır

def save_grid_image(grid, step):
    """ Grid'in mevcut durumunu PNG olarak kaydeder. """
    img_size = (GRID_WIDTH * 10, GRID_HEIGHT * 10)
    img = Image.new("RGB", img_size, "white")
    draw = ImageDraw.Draw(img)

    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            color = "white"
            if grid[y][x].cell_type == CellType.WATER:
                color = "blue"
            elif grid[y][x].cell_type == CellType.AIR:
                color = "gray"
            elif grid[y][x].cell_type == CellType.OBSTACLE:
                color = "black"

            draw.rectangle([x * 10, y * 10, (x + 1) * 10, (y + 1) * 10], fill=color)

    img.save(f"{SAVE_PATH}/frame_{step}.png")

@app.post("/save_frame/{step}")
def capture_frame(step: int):
    """ Belirli bir adım için simülasyonun görselini kaydeder. """
    save_grid_image(grid, step)
    return {"message": f"Frame {step} başarıyla kaydedildi."}

def convert_images_to_video():
    """ Kayıtlı PNG dosyalarını MP4 formatında birleştirir. """
    img_array = []
    for filename in sorted(glob.glob(f"{SAVE_PATH}/frame_*.png")):
        img = cv2.imread(filename)
        height, width, layers = img.shape
        size = (width, height)
        img_array.append(img)

    out = cv2.VideoWriter(VIDEO_FILENAME, cv2.VideoWriter_fourcc(*'mp4v'), 5, size)

    for img in img_array:
        out.write(img)

    out.release()
    return VIDEO_FILENAME

@app.post("/generate_video/")
def create_video():
    """ Tüm kareleri toplayarak MP4 video oluşturur. """
    filename = convert_images_to_video()
    return {"message": "Video başarıyla oluşturuldu.", "video_path": filename}

@app.get("/download_video/")
def download_video():
    """ MP4 dosyasını istemciye sunar. """
    from fastapi.responses import FileResponse
    return FileResponse(VIDEO_FILENAME, media_type="video/mp4", filename=VIDEO_FILENAME)