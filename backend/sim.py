from models import CellType
from state import set_cell, GRID_WIDTH, GRID_HEIGHT
from utils import grid_to_json
from typing import List

class Cell:
    def __init__(self, water_amount: float = 0.0, is_wall: bool = False):
        self.water_amount = water_amount  # Hücredeki su miktarı
        self.is_wall = is_wall  # Hücrenin duvar olup olmadığı

# Su akışını yönlendiren fonksiyon: Su, sadece aşağı doğru hareket eder fakat engeller varsa yanlara doğru yayılır
def simulate_fluid_with_vertical_flow_and_walls(grid: List[List[Cell]], width: int, height: int):
    """
    Su akışını sadece yukarıdan aşağıya ve engellerle etkileşimde simüle eden fonksiyon.
    Engellerin olduğu hücrelere su geçemez, ancak yan hücrelere doğru akar.
    """
    new_grid = [[Cell(cell.water_amount, cell.is_wall) for cell in row] for row in grid]  # Yeni bir grid oluşturuyoruz

    for x in range(1, width - 1):  # X ekseninde ilerliyoruz
        for y in range(1, height - 1):  # Y ekseninde ilerliyoruz
            if grid[y][x].water_amount > 0:  # Eğer hücrede su varsa
                water_to_transfer = grid[y][x].water_amount / 4  # Su miktarını paylaştırıyoruz

                # Aşağıya su akışı: Eğer aşağıda engel yoksa, suyu aşağıya aktar
                if not grid[y + 1][x].is_wall:  # Aşağıda duvar yoksa
                    new_grid[y + 1][x].water_amount += water_to_transfer
                    new_grid[y][x].water_amount -= water_to_transfer

                # Yukarıya su akışı: Eğer yukarıda engel yoksa, suyu yukarıya aktar
                elif not grid[y - 1][x].is_wall:  # Yukarıda duvar yoksa
                    new_grid[y - 1][x].water_amount += water_to_transfer
                    new_grid[y][x].water_amount -= water_to_transfer

                # Sol hücreye su akışı: Eğer solda engel yoksa, suyu sola aktar
                elif not grid[y][x - 1].is_wall:  # Solda duvar yoksa
                    new_grid[y][x - 1].water_amount += water_to_transfer
                    new_grid[y][x].water_amount -= water_to_transfer

                # Sağ hücreye su akışı: Eğer sağda engel yoksa, suyu sağa aktar
                elif not grid[y][x + 1].is_wall:  # Sağda duvar yoksa
                    new_grid[y][x + 1].water_amount += water_to_transfer
                    new_grid[y][x].water_amount -= water_to_transfer

    return new_grid
