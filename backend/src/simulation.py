import numpy as np
from typing import List

class Fluid:
    _presets = {
        "water": {"diff": 0.0001, "visc": 0.0001},
        "oil":   {"diff": 0.00005, "visc": 0.0005},
        "honey": {"diff": 0.00001, "visc": 0.001},
    }

    def __init__(
        self,
        width: int,
        height: int,
        fluid_type: str = "water",
        env_type: str = "bounded"
    ):
        if fluid_type not in self._presets:
            raise ValueError(f"Unknown fluid_type: {fluid_type}. Valid: {list(self._presets.keys())}")
        if env_type not in ("bounded","periodic"):
            raise ValueError("env_type must be 'bounded' or 'periodic'.")
        self.width = width
        self.height = height
        self.env_type = env_type
        params = self._presets[fluid_type]
        self.diff = params["diff"]
        self.visc = params["visc"]
        self.density = np.zeros((height, width), dtype=float)
        self.Vx = np.zeros((height, width), dtype=float)
        self.Vy = np.zeros((height, width), dtype=float)
        self.Vx0 = np.zeros((height, width), dtype=float)
        self.Vy0 = np.zeros((height, width), dtype=float)

    def init_shape(self, shape: str, size: int, height: int) -> None:
        if shape == "square":
            x0 = self.width // 4
            y0 = self.height // 4
            s = min(size, self.width, self.height) // 2
            self.density[y0:y0+s, x0:x0+s] = 1.0
        elif shape == "circle":
            cx, cy, r = self.width//2, self.height//2, min(self.width, self.height)//4
            y, x = np.ogrid[:self.height, :self.width]
            mask = (x-cx)**2 + (y-cy)**2 <= r*r
            self.density[mask] = 1.0
        elif shape == "triangle":
            for j in range(self.height):
                limit = int((j/self.height) * self.width)
                self.density[j, :limit] = 1.0
        elif shape == "ellipse":
            cx, cy = self.width/2, self.height/2
            rx, ry = self.width/4, self.height/6
            y, x = np.ogrid[:self.height, :self.width]
            mask = ((x-cx)/rx)**2 + ((y-cy)/ry)**2 <= 1
            self.density[mask] = 1.0
        else:
            raise ValueError(f"Unknown shape: {shape}. Valid: ['square','circle','triangle','ellipse']")

    def init_custom(self, mask: List[List[int]]) -> None:
        arr = np.array(mask, dtype=bool)
        if arr.shape != self.density.shape:
            raise ValueError(f"custom_shape size {arr.shape} does not match grid {(self.height,self.width)}")
        self.density[arr] = 1.0

    def step(self, dt: float) -> None:
        self.diffuse(1, self.Vx0, self.Vx, self.visc, dt)
        self.diffuse(2, self.Vy0, self.Vy, self.visc, dt)
        self.project(self.Vx0, self.Vy0, self.Vx, self.Vy)
        self.advect(1, self.Vx, self.Vx0, self.Vx0, self.Vy0, dt)
        self.advect(2, self.Vy, self.Vy0, self.Vx0, self.Vy0, dt)
        self.project(self.Vx, self.Vy, self.Vx0, self.Vy0)
        self.diffuse(0, self.density, self.density, self.diff, dt)
        self.advect(0, self.density, self.density, self.Vx, self.Vy, dt)

    def diffuse(self, b: int, x: np.ndarray, x0: np.ndarray, diff: float, dt: float) -> None:
        a = dt * diff * self.width * self.height
        for _ in range(20):
            x[1:-1,1:-1] = (
                x0[1:-1,1:-1]
                + a * (
                    x[1:-1,2:] + x[1:-1,:-2]
                    + x[2:,1:-1] + x[:-2,1:-1]
                )
            ) / (1 + 4 * a)
            self.set_bnd(b, x)

    def advect(
        self, b: int, d: np.ndarray, d0: np.ndarray,
        VelX: np.ndarray, VelY: np.ndarray, dt: float
    ) -> None:
        dt0 = dt * self.width
        for j in range(self.height):
            for i in range(self.width):
                x = i - dt0 * VelX[j, i]
                y = j - dt0 * VelY[j, i]
                x = min(max(x, 0.5), self.width - 1.5)
                y = min(max(y, 0.5), self.height - 1.5)
                i0, i1 = int(x), int(x) + 1
                j0, j1 = int(y), int(y) + 1
                s1, s0 = x - i0, 1 - (x - i0)
                t1, t0 = y - j0, 1 - (y - j0)
                d[j, i] = (
                    s0 * (t0 * d0[j0, i0] + t1 * d0[j1, i0])
                    + s1 * (t0 * d0[j0, i1] + t1 * d0[j1, i1])
                )
        self.set_bnd(b, d)

    def project(
        self, VelX: np.ndarray, VelY: np.ndarray,
        p: np.ndarray, div: np.ndarray
    ) -> None:
        div[1:-1,1:-1] = -0.5 * (
            VelX[1:-1,2:] - VelX[1:-1,:-2]
            + VelY[2:,1:-1] - VelY[:-2,1:-1]
        ) / self.width
        p.fill(0)
        self.set_bnd(0, div)
        self.set_bnd(0, p)
        for _ in range(20):
            p[1:-1,1:-1] = (
                div[1:-1,1:-1]
                + p[1:-1,2:] + p[1:-1,:-2]
                + p[2:,1:-1] + p[:-2,1:-1]
            ) / 4
            self.set_bnd(0, p)
        VelX[1:-1,1:-1] -= 0.5 * (p[1:-1,2:] - p[1:-1,:-2]) * self.width
        VelY[1:-1,1:-1] -= 0.5 * (p[2:,1:-1] - p[:-2,1:-1]) * self.height
        self.set_bnd(1, VelX)
        self.set_bnd(2, VelY)

    def set_bnd(self, b: int, x: np.ndarray) -> None:
        if self.env_type == "periodic":
            # wrap-around boundaries
            x[0, :] = x[-2, :]
            x[-1, :] = x[1, :]
            x[:, 0] = x[:, -2]
            x[:, -1] = x[:, 1]
            return
        # bounded (no-slip) boundaries
        x[0, :] = -x[1, :] if b == 2 else x[1, :]
        x[-1, :] = -x[-2, :] if b == 2 else x[-2, :]
        x[:, 0] = -x[:, 1] if b == 1 else x[:, 1]
        x[:, -1] = -x[:, -2] if b == 1 else x[:, -2]
        # corners
        x[0, 0] = 0.5 * (x[1, 0] + x[0, 1])
        x[0, -1] = 0.5 * (x[1, -1] + x[0, -2])
        x[-1, 0] = 0.5 * (x[-2, 0] + x[-1, 1])
        x[-1, -1] = 0.5 * (x[-2, -1] + x[-1, -2])