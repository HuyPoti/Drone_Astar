import math
import threading
import heapq
from src.pathfinding.cell import Cell
from src.pathfinding.utils import is_destination, is_valid, calculate_h_value
from src.config import pin_max

class PathFinder(threading.Thread):
    def __init__(self, grid, src, dest, callback):
        super().__init__()
        self.grid = grid
        self.src = src
        self.dest = dest
        self.callback = callback
        self.ROW = len(grid)
        self.COL = len(grid[0])
        self.running = True
    def run(self):
        path = self.a_star_search()
        self.callback(path)
    # Truy vết đường đi từ đích về đầu, tính tổng chi phí di chuyển
    def trace_path(self, cell_details, dest):
        grid = self.grid
        path = []
        row, col = dest
        final_total_cost = 0

        # Lặp lại cho đến khi về đến điểm bắt đầu
        while not (cell_details[row][col].parent_i == row and cell_details[row][col].parent_j == col):
            path.append((row, col, cell_details[row][col].height, cell_details[row][col].battery))
            temp_row = cell_details[row][col].parent_i
            temp_col = cell_details[row][col].parent_j
            row, col = temp_row, temp_col

        # Thêm điểm bắt đầu
        path.append((row, col, cell_details[row][col].height, cell_details[row][col].battery))
        path.reverse()
        path_with_cost = []
        for idx in range(len(path)):
            if idx == 0:
                path_with_cost.append((*path[idx], 0.0))
            else:
                r1, c1, *_ = path[idx]
                final_total_cost += cell_details[r1][c1].total_cost
                path_with_cost.append((*path[idx], round(final_total_cost, 2)))
        with open("output.txt", "w") as f:
            f.write("The Path is:\n")
            for i in path_with_cost:
                f.write(f" -> {i}\n")
            f.write(f"\nTotal cost of the Path is: {final_total_cost:.2f}\n")
        return path_with_cost
    # Thuật toán A* tìm đường có xét đến pin và địa hình
    def a_star_search(self):
        grid = self.grid
        src, dest = self.src, self.dest
        ROW, COL = self.ROW, self.COL
        if not is_valid(src[0], src[1], ROW, COL) or not is_valid(dest[0], dest[1], ROW, COL):
            print("Source or destination is invalid")
            return

        closed_list = [[False for _ in range(COL)] for _ in range(ROW)]
        cell_details = [[Cell() for _ in range(COL)] for _ in range(ROW)]

        i, j = src
        cell_details[i][j].f = 0.0
        cell_details[i][j].g = 0.0
        cell_details[i][j].h = 0.0
        cell_details[i][j].battery = pin_max
        cell_details[i][j].parent_i = i
        cell_details[i][j].parent_j = j
        open_list = []
        heapq.heappush(open_list, (0.0, i, j, pin_max))
        found_dest = False

        directions = [(0, 1), (1, 0), (1, 1), (-1, 0),
                    (0, -1), (1, -1), (-1, 1), (-1, -1)]

        # Tìm tất cả điểm 0 (điểm sạc)
        list_of_zero_cells = [(r, c) for r in range(ROW) for c in range(COL) if grid[r][c] == 0]

        while open_list and self.running:
            f_val, i, j, battery = heapq.heappop(open_list)

            if closed_list[i][j]:
                continue
            closed_list[i][j] = True

            for dir in directions:
                new_i, new_j = i + dir[0], j + dir[1]

                if not is_valid(new_i, new_j, ROW, COL):
                    continue
                if closed_list[new_i][new_j]:
                    continue

                # Tính chi phí di chuyển: chéo hoặc thẳng
                move_cost = 400.0 * math.sqrt(2) if dir[0] != 0 and dir[1] != 0 else 400.0

                # Lấy độ cao (chi phí) ô hiện tại và ô mới
                curr_cell_cost = 0.0 if grid[i][j] == -1 else grid[i][j]
                new_cell_cost = 0.0 if grid[new_i][new_j] == -1 else grid[new_i][new_j]

                # Tính chi phí pin và điều chỉnh nếu lên/xuống dốc
                if curr_cell_cost == new_cell_cost:
                    battery_cost = 0.02 * move_cost
                    new_battery = battery - battery_cost
                elif curr_cell_cost > new_cell_cost:
                    movedown_cost = (curr_cell_cost - new_cell_cost) * 100.0
                    battery_cost = 0.02 * (move_cost + movedown_cost * 0.1)
                    move_cost += movedown_cost
                    new_battery = battery - battery_cost
                else:
                    moveup_cost = (new_cell_cost - curr_cell_cost) * 100.0
                    battery_cost = 0.02 * (move_cost + moveup_cost * 1.25)
                    move_cost += moveup_cost
                new_battery = battery - battery_cost
                if new_battery <= 0.0:
                    continue  # Bỏ qua nếu pin không đủ

                if new_cell_cost == 0.0 and not is_destination(new_i, new_j, dest):
                    new_battery = pin_max


                if is_destination(new_i, new_j, dest):
                    cell_details[new_i][new_j].parent_i = i
                    cell_details[new_i][new_j].parent_j = j
                    cell_details[new_i][new_j].total_cost = round(move_cost, 2)
                    found_dest = True
                    return self.trace_path(cell_details, dest)

                g_new = cell_details[i][j].g + move_cost

                # Tính h mới: nếu gần ô sạc hơn thì ưu tiên
                h_to_closest_zero = min(calculate_h_value(new_i, new_j, zero_cell, new_cell_cost, 0) for zero_cell in list_of_zero_cells)
                h_to_dest = calculate_h_value(new_i, new_j, dest, new_cell_cost, 0)
                #h_new = min(h_to_closest_zero, h_to_dest)

                # Nếu không đủ pin tới đích thì đi tìm trạm
                if new_battery < 0.02 * h_to_dest:
                    h_new = h_to_closest_zero
                else:
                    h_new = h_to_dest
                
                # Nếu có trạm gần đó thì tới đó luôn, tránh trường hợp gần đến đích lại phải đi tìm trạm
                if h_to_closest_zero < h_to_dest:
                    h_new = h_to_closest_zero
                else:
                    h_new = h_to_dest
                # Ưu tiên các ô có chi phí thấp hơn bằng cách giảm f theo priority_bias
                #priority_bias = 10.0 / (1 + new_cell_cost)
            
                f_new = g_new + h_new # - - priority_bias
                # Nếu ô mới tốt hơn (f nhỏ hơn), cập nhật thông tin
                if cell_details[new_i][new_j].f > f_new:
                    heapq.heappush(open_list, (f_new, new_i, new_j, new_battery))
                    cell_details[new_i][new_j].f = f_new
                    cell_details[new_i][new_j].g = g_new
                    cell_details[new_i][new_j].h = h_new
                    cell_details[new_i][new_j].battery = round(new_battery, 2)
                    cell_details[new_i][new_j].parent_i = i
                    cell_details[new_i][new_j].parent_j = j
                    cell_details[new_i][new_j].total_cost = round(move_cost, 2)
                    cell_details[new_i][new_j].height = grid[new_i][new_j]*100

        if not found_dest:
            # Tìm trạm sạc gần nhất đã duyệt được
            best_station = None
            min_h = float('inf')
            for i in range(ROW):
                for j in range(COL):
                    if closed_list[i][j] and grid[i][j] == 0:
                        h = calculate_h_value(i, j, dest, 0, 0)
                        if h < min_h:
                            min_h = h
                            best_station = (i, j)
            if best_station:
                print("Không đủ pin đến đích, dừng ở trạm sạc gần nhất:", best_station)
                return self.trace_path(cell_details, best_station)
            else:
                with open("output.txt", "w") as f:
                    f.write("Cannot find the destination cell\n")
            return []