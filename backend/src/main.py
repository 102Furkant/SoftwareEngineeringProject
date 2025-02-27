from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# basic helloworld endpoint
@app.get("/")
def read_root():
    return {"message": "Hello World"}

# create a model to take parameters from user
class SimulationInput(BaseModel):
    shape: str 
    size: int  

# endpoint to initializes the simulation via POST request
@app.post("/simulate")
def simulate(input: SimulationInput):
    # lets keep it simple for now and return simply the input
    return {"received_shape": input.shape, "received_size": input.size}