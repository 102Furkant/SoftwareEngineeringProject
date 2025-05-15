import numpy as np

class FluidSimulator:    #2D fluid simulation with solid obstacles and continuous injection.

    def __init__(
        self,
        width: int,
        height: int,
        diff: float = 0.0001,
        visc: float = 0.0001,
        env_type: str = 'bounded'
    ):
        self.width = width
        self.height = height
        self.diff = diff
        self.visc = visc
        if env_type not in ('bounded', 'periodic'):
            raise ValueError("env_type must be 'bounded' or 'periodic'")
        self.env_type = env_type

        # state fields
        self.density = np.zeros((height, width), float)
        self.Vx = np.zeros((height, width), float)
        self.Vy = np.zeros((height, width), float)
        self.Vx0 = np.zeros((height, width), float)
        self.Vy0 = np.zeros((height, width), float)

        # solid obstacle mask
        self.obstacle = np.zeros((height, width), bool)

    def set_obstacle(self, shape: str, **kwargs) -> None:       #Define a solid region where fluid cannot enter.
        mask = np.zeros_like(self.obstacle)                     #shape: 'square','circle','triangle','ellipse', or 'custom' with mask kwarg.
        if shape == 'square':
            s = kwargs.get('size', min(self.width, self.height)//4)
            x0 = (self.width - s)//2
            y0 = (self.height - s)//2
            mask[y0:y0+s, x0:x0+s] = True

        elif shape == 'circle':
            r = kwargs.get('radius', min(self.width, self.height)//4)
            cx, cy = self.width//2, self.height//2
            y, x = np.ogrid[:self.height, :self.width]
            mask[(x-cx)**2 + (y-cy)**2 <= r*r] = True

        elif shape == 'triangle':
            for j in range(self.height):
                limit = int((j / self.height) * self.width)
                mask[j, :limit] = True

        elif shape == 'ellipse':
            rx = kwargs.get('rx', self.width/4)
            ry = kwargs.get('ry', self.height/6)
            cx, cy = self.width/2, self.height/2
            y, x = np.ogrid[:self.height, :self.width]
            mask[((x-cx)/rx)**2 + ((y-cy)/ry)**2 <= 1] = True

        elif shape == 'custom':
            custom = kwargs.get('mask')
            arr = np.array(custom, bool)
            if arr.shape != mask.shape:
                raise ValueError('custom mask shape mismatch')
            mask = arr

        else:
            raise ValueError(f'Unknown shape "{shape}"')

        self.obstacle = mask
        # clear any fluid inside obstacle
        self.density[mask] = 0.0
        self.Vx[mask] = 0.0
        self.Vy[mask] = 0.0

    def inject(self, amount: float, direction: str = 'top') -> None:     #Add fluid density at boundary: 'top' or 'left'.
        if direction == 'top':
            self.density[0, ~self.obstacle[0]] += amount
        elif direction == 'left':
            self.density[~self.obstacle[:,0], 0] += amount
        else:
            raise ValueError("direction must be 'top' or 'left'")

    def step(self, dt: float) -> None:
        # velocity diffusion and projection
        self.diffuse(1, self.Vx0, self.Vx, self.visc, dt)
        self.diffuse(2, self.Vy0, self.Vy, self.visc, dt)
        self.project(self.Vx0, self.Vy0, self.Vx, self.Vy)

        # velocity advection and projection
        self.advect(1, self.Vx, self.Vx0, self.Vx0, self.Vy0, dt)
        self.advect(2, self.Vy, self.Vy0, self.Vx0, self.Vy0, dt)
        self.project(self.Vx, self.Vy, self.Vx0, self.Vy0)

        # density diffusion and advection
        self.diffuse(0, self.density, self.density, self.diff, dt)
        self.advect(0, self.density, self.density, self.Vx, self.Vy, dt)

        # enforce obstacle: clear inside
        self.density[self.obstacle] = 0.0
        self.Vx[self.obstacle] = 0.0
        self.Vy[self.obstacle] = 0.0

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
        self,
        b: int,
        d: np.ndarray,
        d0: np.ndarray,
        vel_x: np.ndarray,
        vel_y: np.ndarray,
        dt: float
    ) -> None:
        dt0 = dt * self.width
        for j in range(self.height):
            for i in range(self.width):
                x = i - dt0 * vel_x[j, i]
                y = j - dt0 * vel_y[j, i]
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
        self,
        vel_x: np.ndarray,
        vel_y: np.ndarray,
        p: np.ndarray,
        div: np.ndarray
    ) -> None:
        div[1:-1,1:-1] = -0.5 * (
            vel_x[1:-1,2:] - vel_x[1:-1,:-2]
            + vel_y[2:,1:-1] - vel_y[:-2,1:-1]
        ) / self.width
        p.fill(0.0)
        self.set_bnd(0, div)
        self.set_bnd(0, p)
        for _ in range(20):
            p[1:-1,1:-1] = (
                div[1:-1,1:-1]
                + p[1:-1,2:] + p[1:-1,:-2]
                + p[2:,1:-1] + p[:-2,1:-1]
            ) / 4.0
            self.set_bnd(0, p)
        vel_x[1:-1,1:-1] -= 0.5 * (p[1:-1,2:] - p[1:-1,:-2]) * self.width
        vel_y[1:-1,1:-1] -= 0.5 * (p[2:,1:-1] - p[:-2,1:-1]) * self.height
        self.set_bnd(1, vel_x)
        self.set_bnd(2, vel_y)

    def set_bnd(self, b: int, x: np.ndarray) -> None:
        if self.env_type == 'periodic':
            x[0, :] = x[-2, :]
            x[-1, :] = x[1, :]
            x[:, 0] = x[:, -2]
            x[:, -1] = x[:, 1]
            return

        # bounded (no-slip) boundaries
        x[0, :]  = -x[1, :]    if b == 2 else x[1, :]
        x[-1, :] = -x[-2, :]   if b == 2 else x[-2, :]
        x[:, 0]  = -x[:, 1]    if b == 1 else x[:, 1]
        x[:, -1] = -x[:, -2]   if b == 1 else x[:, -2]

        # corners
        x[0, 0]     = 0.5 * (x[1, 0] + x[0, 1])
        x[0, -1]    = 0.5 * (x[1, -1] + x[0, -2])
        x[-1, 0]    = 0.5 * (x[-2, 0] + x[-1, 1])
        x[-1, -1]   = 0.5 * (x[-2, -1] + x[-1, -2])