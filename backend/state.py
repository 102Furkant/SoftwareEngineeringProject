from models import Cell, CellType

# Varsayılan grid boyutları
GRID_WIDTH  = 50
GRID_HEIGHT = 50

# Kenar tanımları
LEFT_EDGE  = 'left'
RIGHT_EDGE = 'right'

def init_grid(width: int = GRID_WIDTH, height: int = GRID_HEIGHT):
    """
    width x height boyutlarında,
    her hücresi EMPTY olan bir grid (2D liste) döndürür.
    """
    return [[Cell(CellType.EMPTY) for _ in range(width)] for _ in range(height)]


def set_cell(grid, x: int, y: int, cell_type: CellType):
    """
    (x, y) koordinatındaki hücreyi verilen tipe günceller.
    Koordinat kontrolü ile sınır aşımı önlenir.
    """
    if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
        grid[y][x].cell_type = cell_type

def set_wall(grid, x: int, y: int):
    """
    Kullanıcının çizdiği duvar hücresi (OBSTACLE) ekler.
    """
    set_cell(grid, x, y, CellType.OBSTACLE)

def inject_water(grid, x: int):
    """
    Üst kenardan (y=0) su ekler.
    x: sütun indeksi
    """
    set_cell(grid, x, 0, CellType.WATER)

def inject_air(grid, edge: str, y: int):
    """
    Kenardan hava ekler.
    edge: 'left' veya 'right'
    y: satır indeksi
    """
    if edge == LEFT_EDGE:
        set_cell(grid, 0, y, CellType.AIR)
    elif edge == RIGHT_EDGE:
        set_cell(grid, len(grid[0]) - 1, y, CellType.AIR)

def print_grid(grid):
    """
    Grid'i terminalde, hücre tiplerinin ilk harfleriyle yazdırır:
    E = Empty, W = Water, A = Air, O = Obstacle
    Debug ve hızlı kontrol için.
    """
    symbol = {
        CellType.EMPTY:    'E',
        CellType.WATER:    'W',
        CellType.AIR:      'A',
        CellType.OBSTACLE: 'O'
    }
    for row in grid:
        print(' '.join(symbol[cell.cell_type] for cell in row))
