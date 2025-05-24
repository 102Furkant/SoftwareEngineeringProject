import numpy as np
import time

def laplacian(field: np.ndarray, dx: float) -> np.ndarray:
    """Discrete Laplacian with zero-Neumann at boundaries"""
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
        self.time = 0.0
        self.step_count = 0
        
        # Initialize fields
        shape = (ny, nx)
        self.u = np.zeros(shape)
        self.v = np.zeros(shape)
        self.p = np.zeros(shape)
        self.obstacle = np.zeros(shape, dtype=bool)
        
        # Set inlet velocity
        self.u[:, 0] = u_in
        
        # Performance tracking
        self.last_step_time = 0.0
        self.avg_step_time = 0.0
        
    def set_obstacle(self, mask: np.ndarray) -> None:
        """Set obstacle mask and reset velocities in obstacle regions"""
        self.obstacle = mask.copy()
        self.u[mask] = 0
        self.v[mask] = 0
        self.p[mask] = 0
        
    def create_circle_obstacle(self, cx: int, cy: int, radius: int) -> np.ndarray:
        """Create circular obstacle"""
        mask = np.zeros((self.ny, self.nx), dtype=bool)
        y, x = np.ogrid[:self.ny, :self.nx]
        dist = np.sqrt((x - cx)**2 + (y - cy)**2)
        mask[dist <= radius] = True
        return mask
        
    def create_rectangle_obstacle(self, x1: int, y1: int, x2: int, y2: int) -> np.ndarray:
        """Create rectangular obstacle"""
        mask = np.zeros((self.ny, self.nx), dtype=bool)
        mask[y1:y2+1, x1:x2+1] = True
        return mask
        
    def create_semicircle_obstacle(self, cx: int, cy: int, radius: int) -> np.ndarray:
        """Create semicircle obstacle (upper half)"""
        mask = np.zeros((self.ny, self.nx), dtype=bool)
        y, x = np.ogrid[:self.ny, :self.nx]
        dist = np.sqrt((x - cx)**2 + (y - cy)**2)
        # Üst yarım daire için y <= cy koşulu
        mask[(dist <= radius) & (y <= cy)] = True
        return mask
        
    def create_triangle_obstacle(self, cx: int, cy: int, size: int) -> np.ndarray:
        """Create triangular obstacle (base at bottom)"""
        mask = np.zeros((self.ny, self.nx), dtype=bool)
        y, x = np.ogrid[:self.ny, :self.nx]
        # Üçgenin tabanı cy + size/2, tepe noktası (cx, cy - size/2)
        height = size
        base = size
        # Üçgenin sınırları içinde kalan pikselleri hesapla
        for i in range(self.ny):
            for j in range(self.nx):
                if i >= cy - height // 2 and i <= cy + height // 2:  # Üçgenin yüksekliği içinde
                    base_width = base * (1 - (i - (cy - height // 2)) / height)  # Taban genişliği lineer olarak azalır
                    if abs(j - cx) <= base_width / 2:
                        mask[i, j] = True
        return mask
        
    def advect(self, field: np.ndarray, u0: np.ndarray, v0: np.ndarray) -> np.ndarray:
        """Semi-Lagrangian advection"""
        ny, nx = field.shape
        dt_dx = self.dt / self.dx
        
        i, j = np.meshgrid(np.arange(ny), np.arange(nx), indexing='ij')
        
        # Backward trace
        x_back = j - u0 * dt_dx
        y_back = i - v0 * dt_dx
        
        # Clamp to domain
        x_back = np.clip(x_back, 0, nx-1)
        y_back = np.clip(y_back, 0, ny-1)
        
        # Bilinear interpolation
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
        """Apply diffusion using explicit method"""
        return field + self.nu * self.dt * laplacian(field, self.dx)
        
    def project(self) -> None:
        """Pressure projection to enforce incompressibility"""
        dx = self.dx
        
        # Compute divergence
        div = np.zeros_like(self.u)
        div[1:-1,1:-1] = (
            (self.u[1:-1,2:] - self.u[1:-1,:-2]) + 
            (self.v[2:,1:-1] - self.v[:-2,1:-1])
        ) / (2*dx)
        
        # Solve Poisson equation using Jacobi iteration
        p_new = self.p.copy()
        for iteration in range(100):  # Max iterations
            p_old = p_new.copy()
            p_new[1:-1,1:-1] = (
                p_new[1:-1,2:] + p_new[1:-1,:-2] + 
                p_new[2:,1:-1] + p_new[:-2,1:-1] - 
                div[1:-1,1:-1] * dx*dx
            ) * 0.25
            
            # Apply boundary conditions
            p_new[self.obstacle] = 0
            
            # Check convergence
            if iteration > 0 and np.max(np.abs(p_new - p_old)) < 1e-6:
                break
                
        self.p = p_new
        
        # Update velocity field
        self.u[1:-1,1:-1] -= (self.p[1:-1,2:] - self.p[1:-1,:-2]) / (2*dx)
        self.v[1:-1,1:-1] -= (self.p[2:,1:-1] - self.p[:-2,1:-1]) / (2*dx)
        
        # Enforce boundary conditions
        self.u[:, 0] = self.u_in  # Inflow
        self.u[:, -1] = self.u[:, -2]  # Outflow (Neumann)
        self.v[:, 0] = 0  # No vertical velocity at inflow
        self.v[:, -1] = 0  # No vertical velocity at outflow
        
        # No-slip at top and bottom walls
        self.u[0, :] = 0
        self.u[-1, :] = 0
        self.v[0, :] = 0
        self.v[-1, :] = 0
        
        # Zero velocity in obstacles
        self.u[self.obstacle] = 0
        self.v[self.obstacle] = 0
        
    def step(self) -> None:
        """Perform one simulation step"""
        start_time = time.time()
        
        # Ensure numerical stability
        max_dt = self.dx**2 / (4 * self.nu)
        if self.dt > max_dt:
            self.dt = max_dt * 0.9
            
        # Store current velocity field
        u0, v0 = self.u.copy(), self.v.copy()
        
        # Advection step
        self.u = self.advect(self.u, u0, v0)
        self.v = self.advect(self.v, u0, v0)
        
        # Diffusion step
        self.u = self.diffuse(self.u)
        self.v = self.diffuse(self.v)
        
        # Projection step
        self.project()
        
        # Update time and step count
        self.time += self.dt
        self.step_count += 1
        
        # Performance tracking
        step_time = time.time() - start_time
        if self.step_count == 1:
            self.avg_step_time = step_time
        else:
            self.avg_step_time = 0.9 * self.avg_step_time + 0.1 * step_time
        self.last_step_time = step_time
        
    def get_velocity(self) -> tuple[np.ndarray, np.ndarray]:
        """Get velocity components"""
        return self.u, self.v
        
    def get_pressure(self) -> np.ndarray:
        """Get pressure field"""
        return self.p
        
    def get_obstacle(self) -> np.ndarray:
        """Get obstacle mask"""
        return self.obstacle
        
    def get_velocity_magnitude(self) -> np.ndarray:
        """Get velocity magnitude"""
        return np.sqrt(self.u**2 + self.v**2)
        
    def get_vorticity(self) -> np.ndarray:
        """Compute vorticity field"""
        vorticity = np.zeros_like(self.u)
        vorticity[1:-1, 1:-1] = (
            (self.v[1:-1, 2:] - self.v[1:-1, :-2]) - 
            (self.u[2:, 1:-1] - self.u[:-2, 1:-1])
        ) / (2 * self.dx)
        return vorticity
        
    def get_divergence(self) -> np.ndarray:
        """Compute velocity divergence"""
        div = np.zeros_like(self.u)
        div[1:-1, 1:-1] = (
            (self.u[1:-1, 2:] - self.u[1:-1, :-2]) + 
            (self.v[2:, 1:-1] - self.v[:-2, 1:-1])
        ) / (2 * self.dx)
        return div
        
    def get_statistics(self) -> dict:
        """Get simulation statistics"""
        u, v = self.get_velocity()
        speed = self.get_velocity_magnitude()
        
        stats = {
            'time': self.time,
            'step_count': self.step_count,
            'dt': self.dt,
            'max_speed': np.max(speed),
            'avg_speed': np.mean(speed[~self.obstacle]),
            'max_pressure': np.max(self.p),
            'min_pressure': np.min(self.p),
            'mass_flow_in': np.sum(self.u[:, 0]) * self.dx,
            'mass_flow_out': np.sum(self.u[:, -1]) * self.dx,
            'avg_step_time': self.avg_step_time,
            'last_step_time': self.last_step_time
        }
        
        return stats
        
    def reset(self) -> None:
        """Reset simulation to initial state"""
        self.u.fill(0)
        self.v.fill(0)
        self.p.fill(0)
        self.u[:, 0] = self.u_in
        self.time = 0.0
        self.step_count = 0
        
        # Reset velocities in obstacles
        self.u[self.obstacle] = 0
        self.v[self.obstacle] = 0
        self.p[self.obstacle] = 0