import numpy as np

def laplacian(field: np.ndarray, dx: float) -> np.ndarray:
    # discrete Laplacian with zero-Neumann at boundaries
    lap = np.zeros_like(field)
    lap[1:-1,1:-1] = (
        field[:-2,1:-1] + field[2:,1:-1] +
        field[1:-1,:-2] + field[1:-1,2:] -
        4 * field[1:-1,1:-1]
    ) / (dx**2)
    return lap

class FluidSimulator:
    def __init__(self, nx: int, ny: int, dx: float=1.0, dt: float=0.1,
                 viscosity: float=0.02, u_in: float=1.0):
        self.nx, self.ny = nx, ny
        self.dx, self.dt = dx, dt
        self.nu = viscosity
        self.u_in = u_in
        shape = (ny, nx)
        self.u = np.zeros(shape)
        self.v = np.zeros(shape)
        self.p = np.zeros(shape)
        self.obstacle = np.zeros(shape, dtype=bool)

    def set_obstacle(self, mask: np.ndarray) -> None:
        self.obstacle = mask.copy()
        self.u[mask] = 0
        self.v[mask] = 0
        self.p[mask] = 0

    def advect(self, field: np.ndarray, u0: np.ndarray, v0: np.ndarray) -> np.ndarray:
        ny, nx = field.shape
        dt_dx = self.dt / self.dx
        i, j = np.meshgrid(np.arange(ny), np.arange(nx), indexing='ij')
        x_back = j - u0 * dt_dx
        y_back = i - v0 * dt_dx
        x_back = np.clip(x_back, 0, nx-1)
        y_back = np.clip(y_back, 0, ny-1)
        x0 = np.floor(x_back).astype(int)
        y0 = np.floor(y_back).astype(int)
        x1 = np.clip(x0 + 1, 0, nx-1)
        y1 = np.clip(y0 + 1, 0, ny-1)
        sx = x_back - x0
        sy = y_back - y0
        f00 = field[y0, x0]
        f10 = field[y0, x1]
        f01 = field[y1, x0]
        f11 = field[y1, x1]
        advected = (1-sx)*(1-sy)*f00 + sx*(1-sy)*f10 + (1-sx)*sy*f01 + sx*sy*f11
        advected[self.obstacle] = 0
        return advected

    def diffuse(self, field: np.ndarray) -> np.ndarray:
        return field + self.nu * self.dt * laplacian(field, self.dx)

    def project(self) -> None:
        dx = self.dx
        p = self.p
        # Compute divergence with proper boundary handling
        div = np.zeros_like(self.u)
        div[1:-1,1:-1] = (
            (self.u[1:-1,2:] - self.u[1:-1,:-2]) +
            (self.v[2:,1:-1] - self.v[:-2,1:-1])
        ) / (2*dx)
        
        # Solve Poisson equation for pressure
        p_new = p.copy()
        for _ in range(100):
            p_new[1:-1,1:-1] = (
                p_new[1:-1,2:] + p_new[1:-1,:-2] +
                p_new[2:,1:-1] + p_new[:-2,1:-1] -
                div[1:-1,1:-1] * dx*dx
            ) * 0.25
            p_new[self.obstacle] = 0
            p = p_new
        
        self.p = p
        
        # Update velocity field
        self.u[1:-1,1:-1] -= (p[1:-1,2:] - p[1:-1,:-2]) / (2*dx)
        self.v[1:-1,1:-1] -= (p[2:,1:-1] - p[:-2,1:-1]) / (2*dx)
        
        # Enforce boundary conditions
        self.u[:,0] = self.u_in  # Inflow
        self.u[:,-1] = 0  # Outflow
        self.v[:,0] = 0  # No vertical velocity at inflow
        self.v[:,-1] = 0  # No vertical velocity at outflow
        self.u[self.obstacle] = 0
        self.v[self.obstacle] = 0

    def step(self) -> None:
        # Ensure stability
        max_dt = self.dx**2 / (4 * self.nu)
        if self.dt > max_dt:
            self.dt = max_dt
        
        # Store current velocity field
        u0, v0 = self.u.copy(), self.v.copy()
        
        # Advect
        self.u = self.advect(self.u, u0, v0)
        self.v = self.advect(self.v, u0, v0)
        
        # Diffuse
        self.u = self.diffuse(self.u)
        self.v = self.diffuse(self.v)
        
        # Project
        self.project()

    def get_velocity(self) -> tuple[np.ndarray, np.ndarray]:
        return self.u, self.v

    def get_pressure(self) -> np.ndarray:
        return self.p

    def get_obstacle(self) -> np.ndarray:
        return self.obstacle