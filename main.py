import pygame
import os
from src.gui.menu import Menu
from src.config import *
from src.gui.draw import draw_map
from src.pathfinding.pathfinder import PathFinder

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Drone Pathfinding Visualizer")
font = pygame.font.SysFont(None, 28)





# Hàm chính: đọc dữ liệu từ file và gọi thuật toán

def main():

    path = []
    done = [False]


    clock = pygame.time.Clock()
    
    step = 0
    drone_progress = 0.0
    is_waiting = False
    wait_time = 0.0

    running = True
    zoom_out = False
    fade_index = 0
    fade_progress = 0.0
    paused = False
    scroll_offset = 0 
    global in_menu, selected_map
    in_menu = True
    selected_map = None
    def on_choose_map(filename):
        global in_menu, selected_map
        selected_map = filename
        in_menu = False
        
    def on_done(p):
        print(f"Path found: {p}")
        path.extend(p)
        done[0] = True
    while running:
        delta_time = clock.tick(FPS) / 1000.0
        screen.fill((0, 0, 0))
        # Define map_width for button position calculations
        
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if not zoom_out:
                    map_width = int(WIDTH * MAP_RATIO)
                    if map_width + 5 <= mx <= map_width + 95 and HEIGHT - 100 <= my <= HEIGHT - 60:
                        paused = not paused  # Đảo trạng thái pause
                    if map_width + 105 <= mx <= map_width + 195 and HEIGHT - 100 <= my <= HEIGHT - 60:
                        in_menu = True  # Quay lại menu
                else:
                    if event.button == 4:  # Lăn chuột lên
                        scroll_offset = max(0, scroll_offset - 1)
                    elif event.button == 5:  # Lăn chuột xuống
                        max_offset = max(0, fade_index - MAX_PATH_LINES)
                        scroll_offset = min(max_offset, scroll_offset + 1)
                    map_width = int(WIDTH * 0.7)
                    if map_width + ((map_width*0.3)//2) <= mx <= map_width + (WIDTH*0.3//2) +120 and HEIGHT - 100 <= my <= HEIGHT - 60:
                        zoom_out = False
                        is_waiting = False
                        pause = False
                        in_menu = True  # Quay lại menu
            if event.type == pygame.QUIT:
                pf.running = False
                running = False
        if in_menu:
            menu = Menu(screen, on_choose_map=on_choose_map)
            menu.run()
        elif not in_menu and selected_map:
            # Đọc file map
            print(selected_map)
            input_folder = os.path.join(os.path.dirname(__file__), "input")
            input_path = os.path.join(input_folder, selected_map)
            with open(input_path, "r") as f:
                lines = [line.strip() for line in f.readlines()]

            ROW = int(lines[0])
            grid = []
            src = dest = None

            for i in range(1, ROW + 1):
                row = []
                tokens = lines[i].split()
                for j, token in enumerate(tokens):
                    if token == 'A':
                        src = (i - 1, j)
                        row.append(-1)
                    elif token == 'B':
                        dest = (i - 1, j)
                        row.append(-1)
                    else:
                        row.append(int(token))
                grid.append(row)

            if src is None or dest is None:
                print("Error: Start (A) or Destination (B) does not exist in file")
                in_menu = True
                continue

            # Reset các biến liên quan đến thuật toán
            path.clear()
            done[0] = False
            step = 0
            drone_progress = 0.0
            is_waiting = False
            wait_time = 0.0
            zoom_out = False
            fade_index = 0
            fade_progress = 0.0

            # Khởi động thuật toán tìm đường
            pf = PathFinder(grid, src, dest, on_done)
            pf.start()

            # Đặt lại selected_map để không load lại nhiều lần
            selected_map = None
        else:
            if not paused:
                if done[0] and path and step < len(path) - 1:
                    row, col, *_ = path[step]
                    # Nếu đang ở trạm sạc và chuẩn bị bắt đầu di chuyển
                    if grid[row][col] == 0 and drone_progress == 0.0:
                        if not is_waiting:
                            is_waiting = True
                            wait_time = 0.0
                        if is_waiting:
                            wait_time += delta_time
                            if wait_time >= WAIT_TIME_STATION:
                                is_waiting = False  # Hết chờ, bắt đầu di chuyển
                                drone_progress += SPEED * delta_time
                        else:
                            print("ok")
                            drone_progress += SPEED * delta_time
                            if drone_progress >= 1.0:
                                drone_progress = 0.0
                                step += 1
                    else:
                        # Các ô thường hoặc đang di chuyển giữa các ô
                        drone_progress += SPEED * delta_time
                        if drone_progress >= 1.0:
                            drone_progress = 0.0
                            step += 1
                    if done[0] and path and step >= len(path) - 1:
                        zoom_out = True
            if zoom_out:
                if fade_index < len(path):
                    fade_progress += delta_time
                    if fade_progress >= FADE_TIME_PER_CELL:
                        fade_progress = 0.0
                        fade_index += 1
            draw_map(screen, font, grid, path, step, src, dest, drone_progress, is_waiting, zoom_out, fade_index if zoom_out else 0, paused, scroll_offset=scroll_offset)
            pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()