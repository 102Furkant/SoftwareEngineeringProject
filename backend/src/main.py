from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

app = FastAPI()

# basic hub endpoint vith html-json mix. when it requested from web, it returns html-based return, when it requested from api it returns JSON.
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    if "text/html" in request.headers.get("accept", ""):
        return HTMLResponse("""
        <html>
            <body>
                <h1>Status: OK</h1>
                <p><a href="/ping">try pinging the page</a></p>
            </body>
        </html>
        """)
    return JSONResponse({"status": "ok"})


# basic ping endpoint. same return type as above.
@app.get("/ping")
async def ping(request: Request):
    if "text/html" in request.headers.get("accept", ""):
        return HTMLResponse("""
        <html>
            <body>
                <h1>Status: OK</h1>
                <p><a href="/simulate">simulation page:</a></p>
            </body>
        </html>
        """)
    return JSONResponse({"status": "ok"})

# create a model to take parameters from user
class SimulationInput(BaseModel):
    shape: str 
    size: int  

# this funcion do the simulation, simple example just for now
def run_simulation(shape: str, size: int):
    if shape.lower() == "square":
        area = size * size
    elif shape.lower() == "circle":
        area = 3.14 * (size ** 2)
    else:
        area = 0
    return area

# GET for browser request
@app.get("/simulate", response_class=HTMLResponse)
async def get_simulate():
    return """
    <html>
        <body>
            <h1>Simulation Page</h1>
            <form action="/simulate" method="post">
                <label>Shape: <input type="text" name="shape"></label><br>
                <label>Size: <input type="number" name="size"></label><br>
                <button type="submit">Start Simulation</button>
            </form>
        </body>
    </html>
    """

# endpoint to initializes the simulation via POST request
@app.post("/simulate")
async def simulate(shape: str = Form(...), size: int = Form(...)):
    result = run_simulation(shape, size)
    return {"shape": shape, "size": size, "result": result}