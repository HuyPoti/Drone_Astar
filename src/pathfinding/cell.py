from src.config import pin_max

class Cell:
    def __init__(self):
        self.parent_i = 0
        self.parent_j = 0
        self.f = float('inf')  # tổng chi phí f = g + h
        self.g = float('inf')  # chi phí từ điểm bắt đầu đến ô hiện tại
        self.h = 0  # ước lượng chi phí từ ô hiện tại đến đích
        self.battery = pin_max  # mức pin còn lại
        self.total_cost = 0
        self.height = 0