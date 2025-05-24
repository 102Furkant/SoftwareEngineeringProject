2D Fluid Simulation Project
This project simulates 2D fluid dynamics using the Navier-Stokes equations and visualizes the results interactively using Pygame. The simulation supports customizable obstacles (circle, rectangle, semicircle, triangle), adjustable viscosity, and real-time visualization of velocity and pressure fields.
Team Members

Furkan KARTALOĞLU - 425477
Tunahan KARALİ - 425431
Mehmet Melih VAR - 434388
Kadir YILMAZ - 425481

Project Overview
The system consists of two main components:

Backend (FluidSimulator): Implements the fluid dynamics simulation using the Navier-Stokes equations with a semi-Lagrangian advection scheme, explicit diffusion, and pressure projection to enforce incompressibility.
Frontend (FluidUI): Provides an interactive visualization using Pygame, allowing users to add/remove obstacles, adjust viscosity, change visualization colors, and view simulation statistics.

Features

Simulation: 
2D fluid flow with inlet velocity and no-slip boundary conditions.
Supports multiple obstacle shapes: circle, rectangle, semicircle, and triangle.
Adjustable viscosity via a slider.
Computes velocity, pressure, vorticity, and divergence fields.
Tracks simulation statistics (e.g., max/avg speed, pressure, step time).


Visualization:
Real-time rendering of velocity magnitude or pressure field.
Interactive obstacle placement and removal.
Color selection for velocity visualization.
Toggleable statistics display.
Pause/resume and reset functionality.


Performance: Numerical stability ensured by adaptive time-stepping based on viscosity and grid size.

Tech Stack

Backend: Python, NumPy, SciPy
Frontend: Pygame
Mathematical Modeling: Custom implementation of Navier-Stokes equations with semi-Lagrangian advection, explicit diffusion, and Jacobi iteration for pressure projection.

Prerequisites

Python 3.8+
Required Python packages:
numpy
pygame
scipy



How to Run
Clone the Repository
```bash
git clone https://github.com/102Furkant/SoftwareEngineeringProject
cd SoftwareEngineeringProject
```

```bash
Install Dependencies
pip install numpy pygame scipy
```

Run the Simulation
```bash
python main.py
```

The simulation will open a Pygame window displaying the fluid flow. Use the controls below to interact with the simulation.


Controls

Space: Pause/resume the simulation.
R: Reset the simulation to initial state.
S: Toggle simulation statistics display.
C: Select circle obstacle mode.
X: Select rectangle obstacle mode.
H: Select semicircle obstacle mode.
T: Select triangle obstacle mode.
Left Click: Place the selected obstacle (or draw single-cell obstacles if no mode is selected).
Right Click: Remove obstacles.
Q: Quit the simulation.
Mouse Drag on Slider: Adjust viscosity (0.0 to 0.1).
Click Color Buttons: Change velocity visualization color.

Project Status

Backend simulation logic is fully implemented and stable.
Interactive Pygame-based UI is complete with obstacle placement and visualization controls.
Performance is optimized with adaptive time-stepping and efficient numerical methods.
Future improvements could include:
Additional obstacle shapes.
Enhanced visualization options (e.g., streamlines, vorticity display).
Saving/loading simulation states.



License
This project is licensed under the MIT License. Feel free to use and modify the code, but please provide attribution and avoid direct copy-pasting without contributing back.
Contributing
Contributions are welcome! Please fork the repository, create a feature branch, and submit a pull request with your changes. Ensure your code follows the existing style and includes appropriate comments.
