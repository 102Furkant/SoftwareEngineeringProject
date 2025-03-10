
# this function do the simulation, simple example just for now
def run_simulation(shape: str, size: int, height: int = None):
    shape = shape.lower()
    # Validate size
    if size < 0:
        return "Size cannot be negative"
    if shape == "square":
        area = size * size
    elif shape == "circle":
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