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
def run_simulation(shape: str, size: int, height: int = None):
    shape = shape.lower()
    
    # Validate size
    if size < 0:
        return "Size cannot be negative"
        
    if shape == "square":
        if height is not None:
            return "height section should be empty"
        area = size * size
    elif shape == "circle":
        if height is not None:
            return "height section should be empty"
        area = 3.14 * (size ** 2)
    elif shape == "triangle":
        if height is None:
            return "height is required for triangle"
        if height < 0:
            return "Height cannot be negative"
        area = (size * height) / 2
    else:
        return f"Unsupported shape: {shape}"
    return area

# GET for browser request
@app.get("/simulate", response_class=HTMLResponse)
async def get_simulate():
    return """
    <html>
    <body>
        <h1>Simulation Page</h1>
        <form action="/simulate" method="post">
        <label>Shape:
            <select id="shape" name="shape" onchange="toggleTriangleInputs()">
            <option value="square">square</option>
            <option value="circle">circle</option>
            <option value="triangle">triangle</option>
            </select>
        </label><br>
        <div id="common-inputs">
            <label>Size (base for triangle): 
            <input type="number" name="size" required>
            </label><br>
        </div>
        <div id="triangle-inputs" style="display: none;">
            <label>Height: 
            <input type="number" name="height">
            </label><br>
        </div>
        <button type="submit">Start Simulation</button>
        </form>
        <script>
        function toggleTriangleInputs() {
            var shape = document.getElementById("shape").value;
            var triangleInputs = document.getElementById("triangle-inputs");
            if (shape === "triangle") {
            triangleInputs.style.display = "block";
            // height alanini zorunlu yapmak icin:
            triangleInputs.querySelector("input[name='height']").required = true;
            } else {
            triangleInputs.style.display = "none";
            triangleInputs.querySelector("input[name='height']").required = false;
            }
        }
        </script>
    </body>
    </html>
    """

# endpoint to initializes the simulation via POST request
@app.post("/simulate")
async def simulate(shape: str = Form(...), size: int = Form(...), height: int = Form(None)):
    result = run_simulation(shape, size, height)
    return {"shape": shape, "size": size, "height": height, "result": result}