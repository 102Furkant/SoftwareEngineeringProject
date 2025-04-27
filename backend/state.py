from models import Cell, CellType

# Varsayılan grid boyutları
GRID_WIDTH  = 50
GRID_HEIGHT = 50

# Kenar tanımları
LEFT_EDGE  = 'left'
RIGHT_EDGE = 'right'

current_mode = "none"  # Başlangıçta hiçbir mod aktif değil.

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
    Eğer grid tamamen boşsa, suyu her hücreye yayar.
    Eğer sadece bir hücreye su ekleniyorsa, o hücreye su ekler.
    """
    if all(cell.cell_type == CellType.EMPTY for row in grid for cell in row):
        # Grid tamamen boşsa, her hücreye su ekle
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                set_cell(grid, x, y, CellType.WATER)
    else:
        set_cell(grid, x, 0, CellType.WATER)  # Diğer durumda, yukarıdan su ekler.

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
    Grid'i yazdıran fonksiyon.
    """
    for row in grid:
        print(' '.join([cell.cell_type.name[0] for cell in row]))

