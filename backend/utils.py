def grid_to_json(grid):
    """
    Grid'i JSON formatına çevirir. Hücre tiplerinin adlarını (str) kullanır.
    """
    return [[cell.cell_type.name for cell in row] for row in grid]