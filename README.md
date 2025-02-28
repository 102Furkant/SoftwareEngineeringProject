## Fluid Simulation Project
This project is designed to simulate fluid dynamics using mathematical models and visualize the results.

## Team Members
- [**Furkan KARTALOĞLU**](https://github.com/102Furkant) - **425477**
- [**Tunahan KARALİ**](https://github.com/imnightmare53) - **425431**
- [**Mehmet Melih VAR**](https://github.com/mvarr) - **434388**
- [**Kadir YILMAZ**](https:://github.com/Kadiryilmazz) - **425481**


## Project Structure
The project consists of three main components:

1. **Backend (API)**
   - Built with FastAPI to handle user input and process fluid simulation logic.
   - Exposes RESTful endpoints for simulation requests.
   - Integrated with CI/CD pipeline for automated testing.

2. **Frontend (UI & Visualization)**
   - Displays the simulation results using interactive graphics.
   - The technology stack is still being determined (options: JavaScript, Pygame, or Web UI).

3. **Mathematical Model**
   - Computes fluid movement and behavior.
   - Uses NumPy/SciPy or custom algorithms for calculations.

## Project Status
[x] Backend API setup completed.  
[x] CI/CD pipeline implemented with GitHub Actions.  
[x] Automated testing configured using *pytest*.  
[ ] Simulation logic is under development.   
[ ] Visualization methods being planned.     

## Tech Stack
- Backend: Python, FastAPI
- Frontend: To be determined (possible options: JavaScript, Pygame, or Web UI)
- Mathematical Modeling: NumPy, SciPy, or custom algorithms
- CI/CD: GitHub Actions (Automated Testing)  

## How to Run
- **Clone the Repository**
```bash
git clone https://github.com/102Furkant/SoftwareEngineeringProject
cd SoftwareEngineeringProject
```

- **Set Up the Backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --reload
```

The backend (i suppose) will run at ```http://127.0.0.1:8000.```      
API documentation (Swagger UI) available at: http://127.0.0.1:8000/docs
```

- **Set Up the Frontend (If applicable)**
```bash
cd frontend
# Run frontend setup (depending on chosen framework)
```

## Testing
We use pytest for automated testing.    
To run the tests, activate the virtual environment and run:

```bash
pytest
```
All tests must pass before pushing changes (GitHub Actions will enforce this).

## Next Steps
- Finalizing simulation logic.
- Developing visualization and UI.
- Expanding test coverage for backend functions.
- Optimizing performance for better efficiency.
- Further updates will be provided as development progresses.

## License
MIT licence or whatever they called. just dont copy-paste our code.

**Feel free to contribute!** 
