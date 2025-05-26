# 2D Fluid Simulation Project

This project simulates 2D fluid dynamics using the Navier-Stokes equations and visualizes the results interactively using Pygame. The simulation supports customizable obstacles (circle, rectangle,
semicircle, triangle), adjustable viscosity, and real-time visualization of velocity and pressure fields.

## Team Members

- Furkan KARTALOĞLU - 425477
- Tunahan KARALİ - 425431
- Mehmet Melih VAR - 434388
- Kadir YILMAZ - 425481

## Project Overview

The system consists of two main components:

### Backend (FluidSimulator)
- Implements fluid dynamics simulation using Navier-Stokes equations
- Features semi-Lagrangian advection scheme
- Includes explicit diffusion and pressure projection for incompressibility

### Frontend (FluidUI)
- Interactive visualization using Pygame
- Obstacle management (add/remove)
- Viscosity adjustment
- Customizable visualization colors
- Real-time simulation statistics

## Features

### Simulation
- 2D fluid flow with inlet velocity and no-slip boundary conditions
- Multiple obstacle shapes:
  - Circle
  - Rectangle
  - Semicircle
  - Triangle
- Adjustable viscosity via slider
- Comprehensive field computation:
  - Velocity
  - Pressure
  - Vorticity
  - Divergence
- Real-time simulation statistics tracking

### Visualization
- Real-time rendering of velocity magnitude/pressure field
- Interactive obstacle placement and removal
- Customizable velocity visualization colors
- Toggleable statistics display
- Pause/resume and reset functionality

### Performance
- Numerical stability through adaptive time-stepping
- Optimized based on viscosity and grid size

## Tech Stack

- **Backend**: Python, NumPy, SciPy
- **Frontend**: Pygame
- **Mathematical Modeling**: Custom Navier-Stokes implementation
  - Semi-Lagrangian advection
  - Explicit diffusion
  - Jacobi iteration for pressure projection

## Prerequisites

- Python 3.8+
- Required Python packages:
  - numpy
  - pygame
  - scipy

## Installation and Running

1. Clone the Repository:
```
git clone https://github.com/102Furkant/SoftwareEngineeringProject
cd SoftwareEngineeringProject
```

2. Install Dependencies:
```
pip install numpy pygame scipy
```

3. Run the Simulation:
```
python main.py
```

The simulation will open a Pygame window displaying the fluid flow. Use the controls below to interact with the simulation.

## Controls
- **Space**: Pause/resume simulation
- **R**: Reset simulation
- **S**: Toggle statistics display
- **C**: Circle obstacle mode
- **X**: Rectangle obstacle mode
- **H**: Semicircle obstacle mode
- **T**: Triangle obstacle mode
- **Left Click**: Place selected obstacle
- **Right Click**: Remove obstacles
- **Q**: Quit simulation
- **Mouse Drag on Slider**: Adjust viscosity (0.0 to 0.1)
- **Color Buttons**: Change velocity visualization color

### Current Status
- Backend simulation logic fully implemented and stable
- Interactive Pygame-based UI complete
- Performance optimization implemented

### Future Improvements
- Additional obstacle shapes
- Enhanced visualization options (streamlines, vorticity display)
- Save/load simulation states