from enum import Enum

class CellType(Enum):
    EMPTY    = 0   # Boş hücre
    WATER    = 1   # Su
    AIR      = 2   # Hava
    OBSTACLE = 3   # Duvar/Engel

class Cell:
    """
    Her hücre, bir CellType taşır. Varsayılan olarak EMPTY.
    """
    def __init__(self, cell_type: CellType = CellType.EMPTY):
        self.cell_type = cell_type

    def __repr__(self):
        return f"Cell({self.cell_type.name})"