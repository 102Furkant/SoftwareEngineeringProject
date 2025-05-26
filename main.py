from backend.simulation import FluidSimulator
from frontend.python.ui import FluidUI

def main():
    simulator = FluidSimulator(nx=80, ny=60, dx=1.0, dt=0.1, viscosity=0.02, u_in=1.0)
    ui = FluidUI(simulator, width=1200, height=800)
    ui.run()

if __name__ == "__main__":
    main()
