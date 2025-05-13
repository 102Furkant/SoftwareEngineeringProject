import numpy as np
from typing import Dict, List, Optional

class FluidSimulationEngine:
    FLUID_PRESETS = {
        "water": {"diff": 0.0001, "visc": 0.0001},
        "oil": {"diff": 0.00005, "visc": 0.0005},
        "honey": {"diff": 0.00001, "visc": 0.001},
        "air": {"diff": 0.0002, "visc": 0.000015}
    }

    def __init__(self):
        self.width = 200
        self.height = 150
        self.dt = 0.1
        self.iterations = 20
        self.gravity = np.array([0.0, 0.0005])
        
        self.density = np.zeros((self.height, self.width))
        self.velocity_x = np.zeros((self.height, self.width))
        self.velocity_y = np.zeros((self.height, self.width))
        
        self.temp_density = np.zeros_like(self.density)
        self.temp_velocity_x = np.zeros_like(self.velocity_x)
        self.temp_velocity_y = np.zeros_like(self.velocity_y)
        
        self.divergence = np.zeros_like(self.density)
        self.pressure = np.zeros_like(self.density)
        
        self.fluid_type = "water"
        self.env_type = "bounded"
        self.diffusion_rate = self.FLUID_PRESETS["water"]["diff"]
        self.viscosity = self.FLUID_PRESETS["water"]["visc"]

    def reset_simulation(self, params: Dict) -> Dict:
        self.width = params.get("width", 200)
        self.height = params.get("height", 150)
        self.dt = params.get("dt", 0.1)
        self.fluid_type = params.get("fluid_type", "water")
        self.env_type = params.get("env_type", "bounded")
        
        fluid_props = self.FLUID_PRESETS.get(self.fluid_type)
        if fluid_props is None:
            raise ValueError(f"Invalid fluid_type: {self.fluid_type}")
        
        self.diffusion_rate = fluid_props["diff"]
        self.viscosity = fluid_props["visc"]
        
        self._initialize_fields()
        
        shape = params.get("shape", "circle")
        size = params.get("size", min(self.width, self.height) // 4)
        
        if shape == "custom" and "custom_shape" in params:
            custom_shape = np.array(params["custom_shape"])
            if custom_shape.shape == (self.height, self.width):
                self.density = custom_shape.copy()
        else:
            self._init_shape(shape, size)
        
        return {
            "density": self.density.tolist(),
            "velocity_x": self.velocity_x.tolist(),
            "velocity_y": self.velocity_y.tolist()
        }

    def simulate_step(self, params: Dict) -> Dict:
        steps = params.get("steps", 1)
        dt = params.get("dt", self.dt)
        
        if "custom_shape" in params:
            custom_shape = np.array(params["custom_shape"])
            if custom_shape.shape == (self.height, self.width):
                self.density = custom_shape.copy()
        
        for _ in range(steps):
            self._velocity_step(dt)
            self._density_step(dt)
        
        return {
            "density": self.density.tolist(),
            "velocity_x": self.velocity_x.tolist(),
            "velocity_y": self.velocity_y.tolist()
        }

    def _initialize_fields(self):
        self.density = np.zeros((self.height, self.width))
        self.velocity_x = np.zeros((self.height, self.width))
        self.velocity_y = np.zeros((self.height, self.width))
        self.temp_density = np.zeros_like(self.density)
        self.temp_velocity_x = np.zeros_like(self.velocity_x)
        self.temp_velocity_y = np.zeros_like(self.velocity_y)
        self.divergence = np.zeros_like(self.density)
        self.pressure = np.zeros_like(self.density)

    def _init_shape(self, shape: str, size: int):
        if shape == "circle":
            cx, cy = self.width // 2, self.height // 2
            y, x = np.ogrid[:self.height, :self.width]
            mask = (x - cx)**2 + (y - cy)**2 <= size**2
            self.density[mask] = 1.0
        elif shape == "square":
            x0, y0 = (self.width - size) // 2, (self.height - size) // 2
            self.density[y0:y0+size, x0:x0+size] = 1.0
        elif shape == "triangle":
            for y in range(self.height):
                width = int(size * (1 - y / self.height))
                x0 = (self.width - width) // 2
                self.density[y, x0:x0+width] = 1.0
        elif shape == "ellipse":
            cx, cy = self.width // 2, self.height // 2
            rx, ry = size, size // 2
            y, x = np.ogrid[:self.height, :self.width]
            mask = ((x - cx)/rx)**2 + ((y - cy)/ry)**2 <= 1
            self.density[mask] = 1.0
        else:
            raise ValueError(f"Invalid shape: {shape}")

    def _velocity_step(self, dt: float):
        self.velocity_y += self.gravity[1] * dt
        
        self._diffuse(1, self.temp_velocity_x, self.velocity_x, self.viscosity, dt)
        self._diffuse(2, self.temp_velocity_y, self.velocity_y, self.viscosity, dt)
        
        self._project(self.temp_velocity_x, self.temp_velocity_y, self.velocity_x, self.velocity_y)
        
        self._advect(1, self.velocity_x, self.temp_velocity_x, self.temp_velocity_x, self.temp_velocity_y, dt)
        self._advect(2, self.velocity_y, self.temp_velocity_y, self.temp_velocity_x, self.temp_velocity_y, dt)
        
        self._project(self.velocity_x, self.velocity_y, self.temp_velocity_x, self.temp_velocity_y)

    def _density_step(self, dt: float):
        self._diffuse(0, self.temp_density, self.density, self.diffusion_rate, dt)
        self._advect(0, self.density, self.temp_density, self.velocity_x, self.velocity_y, dt)

    def _diffuse(self, boundary: int, x: np.ndarray, x0: np.ndarray, diff: float, dt: float):
        a = dt * diff * (self.width * self.height)
        x[:] = x0
        
        for _ in range(self.iterations):
            x[1:-1, 1:-1] = (x0[1:-1, 1:-1] + a * (
                x[1:-1, 2:] + x[1:-1, :-2] + 
                x[2:, 1:-1] + x[:-2, 1:-1]
            )) / (1 + 4 * a)
            self._set_boundary(boundary, x)

    def _advect(self, boundary: int, d: np.ndarray, d0: np.ndarray, 
                vel_x: np.ndarray, vel_y: np.ndarray, dt: float):
        dt_x = dt * (self.width - 2)
        dt_y = dt * (self.height - 2)
        
        for j in range(1, self.height-1):
            for i in range(1, self.width-1):
                x = i - dt_x * vel_x[j, i]
                y = j - dt_y * vel_y[j, i]
                
                x = max(0.5, min(x, self.width - 1.5))
                y = max(0.5, min(y, self.height - 1.5))
                
                i0, j0 = int(x), int(y)
                i1, j1 = i0 + 1, j0 + 1
                s1, t1 = x - i0, y - j0
                s0, t0 = 1 - s1, 1 - t1
                
                d[j, i] = (
                    s0 * (t0 * d0[j0, i0] + t1 * d0[j1, i0]) +
                    s1 * (t0 * d0[j0, i1] + t1 * d0[j1, i1])
                )
        self._set_boundary(boundary, d)

    def _project(self, vel_x: np.ndarray, vel_y: np.ndarray, 
                p: np.ndarray, div: np.ndarray):
        h = 1.0 / self.width
        div[1:-1, 1:-1] = -0.5 * h * (
            vel_x[1:-1, 2:] - vel_x[1:-1, :-2] +
            vel_y[2:, 1:-1] - vel_y[:-2, 1:-1]
        )
        p.fill(0)
        self._set_boundary(0, div)
        self._set_boundary(0, p)
        
        for _ in range(self.iterations):
            p[1:-1, 1:-1] = (div[1:-1, 1:-1] + (
                p[1:-1, 2:] + p[1:-1, :-2] +
                p[2:, 1:-1] + p[:-2, 1:-1]
            )) / 4
            self._set_boundary(0, p)
        
        vel_x[1:-1, 1:-1] -= 0.5 * (p[1:-1, 2:] - p[1:-1, :-2]) / h
        vel_y[1:-1, 1:-1] -= 0.5 * (p[2:, 1:-1] - p[:-2, 1:-1]) / h
        
        self._set_boundary(1, vel_x)
        self._set_boundary(2, vel_y)

    def _set_boundary(self, boundary: int, field: np.ndarray):
        if self.env_type == "periodic":
            field[0, :] = field[-2, :]
            field[-1, :] = field[1, :]
            field[:, 0] = field[:, -2]
            field[:, -1] = field[:, 1]
        else:
            if boundary == 1:
                field[:, 0] = -field[:, 1]
                field[:, -1] = -field[:, -2]
                field[0, :] = field[1, :]
                field[-1, :] = field[-2, :]
            elif boundary == 2:
                field[:, 0] = field[:, 1]
                field[:, -1] = field[:, -2]
                field[0, :] = -field[1, :]
                field[-1, :] = -field[-2, :]
            else:
                field[:, 0] = field[:, 1]
                field[:, -1] = field[:, -2]
                field[0, :] = field[1, :]
                field[-1, :] = field[-2, :]
        
        field[0, 0] = 0.5 * (field[1, 0] + field[0, 1])
        field[0, -1] = 0.5 * (field[1, -1] + field[0, -2])
        field[-1, 0] = 0.5 * (field[-2, 0] + field[-1, 1])
        field[-1, -1] = 0.5 * (field[-2, -1] + field[-1, -2])