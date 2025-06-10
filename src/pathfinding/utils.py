import math

def is_valid(row, col, ROW, COL):
    return 0 <= row < ROW and 0 <= col < COL

# Kiểm tra ô có phải điểm đích không
def is_destination(row, col, dest):
    return row == dest[0] and col == dest[1]

# Tính heuristic (h) theo khoảng cách Euclidean, đơn vị là mm
def calculate_h_value(row, col, dest, curr_height, dest_height):
    return math.hypot(100.0 * (dest_height - curr_height), math.hypot(400.0 * (row - dest[0]), 400.0 * (col - dest[1])))