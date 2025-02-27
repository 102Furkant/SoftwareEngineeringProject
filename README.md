## Fluid Simulation Project
This project is designed to simulate fluid dynamics using mathematical models and visualize the results.

## Team Members
- [**Furkan KARTALOĞLU**](https://github.com/102Furkant) - 425477
- [**Tunahan KARALİ**](https://github.com/imnightmare53) - 425431
- [**Mehmet Melih VAR**](https://github.com/mvarr) - 434388
- [**Kadir YILMAZ**](https:://github.com/Kadiryilmazz) - 425481



The system consists of three main components:

1- Backend (API) / Handles user input and runs calculations. \
2- Frontend (UI & Visualization) / Displays the simulation results. \
3- Mathematical Model / Computes fluid movement and behavior. 

## Project Status
- Backend API setup in progress.
- Simulation logic is under development.
- Visualization methods being planned.

## Tech Stack
- Backend: Python, FastAPI
- Frontend: To be determined (possible options: JavaScript, Pygame, or Web UI)
- Mathematical Modeling: NumPy, SciPy, or custom algorithms

## How to Run
- **Clone the Repository**
```
git clone <repo-url>
cd fluid_simulation_project
```

- **Set Up the Backend**
```
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --reload
```

The backend (i suppose) will run at ```http://127.0.0.1:8000.``` \
API documentation is (probabaly will be) available at ```http://127.0.0.1:8000/docs.```

- **Set Up the Frontend (If applicable)**
```
cd frontend
# Run frontend setup (depending on chosen framework)
```

## Next Steps
- Finalizing simulation logic.
- Developing visualization and UI.
- Optimizing performance for better efficiency.
- Further updates will be provided as development progresses.

## License
MIT licence or whatever they called. just dont copy-paste our code.

**Feel free to contribute!** 
