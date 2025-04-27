from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from state import (
    init_grid,
    inject_water,
    inject_air,
    set_wall,
    print_grid,
    GRID_WIDTH,
    GRID_HEIGHT
)
from sim import spread_water_dynamic
from models import CellType
from utils import grid_to_json
import uvicorn

app = FastAPI()

# Global grid ve mod durumu
grid = init_grid()
current_mode = "none"  # "water", "air", "none"

# Modeller
class WallRequest(BaseModel):
    x: int
    y: int

class WaterRequest(BaseModel):
    x: int

class AirRequest(BaseModel):
    edge: str  # "left" veya "right"
    y: int

class StepRequest(BaseModel):
    time_step: int

@app.get("/")
def read_root():
    return {"message": "Water Simulation API - FastAPI ile"}

@app.post("/mode/{mode_name}")
def set_mode(mode_name: str):
    global current_mode
    if mode_name not in ["water", "air", "none"]:
        raise HTTPException(status_code=400, detail="Mod sadece 'water', 'air' veya 'none' olabilir.")
    
    if mode_name == "water" and current_mode == "air":
        current_mode = "none"  # Su eklenmeden önce hava pasif yapılır.
    
    if mode_name == "air" and current_mode == "water":
        current_mode = "none"  # Hava eklenmeden önce su pasif yapılır.
    
    current_mode = mode_name
    return {"message": f"Mod: {current_mode} olarak ayarlandı."}

@app.post("/add_walls/")
def add_walls(points: list[tuple[int, int]]):
    for x, y in points:
        if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
            set_wall(grid, x, y)
    return {"status": "walls added", "grid": grid_to_json(grid)}

@app.post("/inject/water")
def add_water(req: WaterRequest):
    if current_mode != "water":
        raise HTTPException(status_code=403, detail="Su eklemek icin önce 'water' modu secilmeli.")
    inject_water(grid, req.x)
    return {"message": f"{req.x}. sutuna su eklendi."}

@app.post("/inject/air")
def add_air(req: AirRequest):
    if current_mode != "air":
        raise HTTPException(status_code=403, detail="Hava eklemek icin önce 'air' modu secilmeli.")
    if req.edge not in ["left", "right"]:
        raise HTTPException(status_code=400, detail="edge 'left' veya 'right' olmali.")
    inject_air(grid, req.edge, req.y)
    return {"message": f"{req.edge} kenarindan {req.y}. satira hava eklendi."}

@app.post("/step")
def simulate_step(req: StepRequest):
    result = spread_water_dynamic(grid, req.time_step)
    return {"grid": result}

@app.get("/grid")
def get_current_grid():
    return {"grid": grid_to_json(grid)}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
