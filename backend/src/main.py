from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, root_validator
from typing import List, Optional
import uvicorn
from .simulation import Fluid

class SimRequest(BaseModel):
    shape: str                         # 'square','circle','triangle','ellipse','custom'
    custom_shape: Optional[List[List[int]]] = None  # only for 'custom'
    size: int                          # grid genişliği
    height: int                        # grid yüksekliği
    dt: float                          # zaman adımı
    steps: int                         # adım sayısı
    fluid_type: str = "water"        # 'water','oil','honey'
    env_type: str = "bounded"        # 'bounded','periodic'

    @root_validator(skip_on_failure=True)
    def validate_shape(cls, values):
        shape = values.get('shape')
        custom = values.get('custom_shape')
        if shape == 'custom' and custom is None:
            raise ValueError("custom_shape required when shape='custom'.")
        if shape != 'custom' and custom is not None:
            raise ValueError("custom_shape must be null unless shape='custom'.")
        if values.get('env_type') not in ('bounded','periodic'):
            raise ValueError("env_type must be 'bounded' or 'periodic'.")
        return values

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/simulate")
def simulate(req: SimRequest):
    try:
        fluid = Fluid(
            width=req.size,
            height=req.height,
            fluid_type=req.fluid_type,
            env_type=req.env_type
        )
        # başlangıç şekli
        if req.shape == 'custom':
            fluid.init_custom(req.custom_shape)
        else:
            fluid.init_shape(req.shape, req.size, req.height)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    # simülasyonu çalıştır
    for _ in range(req.steps):
        fluid.step(req.dt)
    return {"density": fluid.density.tolist()}

if __name__ == "__main__":
    uvicorn.run("backend.src.main:app", host="0.0.0.0", port=8000)