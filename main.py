from backend.simulation import FluidSimulator
from frontend.python.ui import FluidUI

def main():
    simulator = FluidSimulator(nx=65, ny=65, dx=1.0, dt=0.1, viscosity=0.02, u_in=1.0)
    ui = FluidUI(simulator, width=800, height=800)
    ui.run()

if __name__ == "__main__":
    main()
