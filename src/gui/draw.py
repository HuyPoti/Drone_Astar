import pygame
import math
import time
from src.config import *



def draw_map(screen, font, grid, path, current_idx, src, dest, drone_progress=0.0, is_waiting=False, zoom_out=False, fade_index=0, paused=False, scroll_offset=0):
    ROW, COL = len(grid), len(grid[0])
    map_width = int(WIDTH * MAP_RATIO)
    cell_size = map_width // COL

    wall_img = pygame.image.load("assets/wall.png")
    ground_img = pygame.image.load("assets/ground.png")
    station_img = pygame.image.load("assets/station.png")
    start_img = pygame.image.load("assets/start_end.png")
    end_img = pygame.image.load("assets/start_end.png")
    drone_img = pygame.image.load("assets/drone.png")

    passed_cells = set((row, col) for row, col, *_ in path[:current_idx+1])
    offset = pygame.Vector2()
    if zoom_out:
        # Tính cell_size nhỏ nhất để vừa toàn bộ map vào màn hình
        map_width = int(WIDTH * 0.7)
        cell_size = min(map_width // COL, HEIGHT // ROW)
        offset.x = (WIDTH*MAP_RATIO - COL * cell_size) // 2
        offset.y = (HEIGHT - ROW * cell_size) // 2
    else:
        map_width = int(WIDTH * MAP_RATIO)
        cell_size = map_width // COL
        center_x = WIDTH * MAP_RATIO // 2
        center_y = HEIGHT // 2
        if path and current_idx < len(path):
            drone_pos = path[current_idx][:2]
        else:
            drone_pos = src
        offset.x = center_x - (drone_pos[1] * cell_size + cell_size // 3)
        offset.y = center_y - (drone_pos[0] * cell_size + cell_size // 3)
        max_x = 0
        max_y = 0
        min_x = WIDTH * MAP_RATIO - COL * cell_size
        min_y = HEIGHT - ROW * cell_size
        offset.x = max(min(offset.x, max_x), min_x)
        offset.y = max(min(offset.y, max_y), min_y)
    for i in range(ROW):
        for j in range(COL):
            x = j * cell_size
            y = i * cell_size
            val = grid[i][j]
            if (i, j) == src:
                img = pygame.transform.scale(start_img, (cell_size, cell_size))
            elif (i, j) == dest:
                img = pygame.transform.scale(end_img, (cell_size, cell_size))
            elif val == 0:
                img = pygame.transform.scale(station_img, (cell_size, cell_size))
            elif val == 1:
                img = pygame.transform.scale(ground_img, (cell_size, cell_size))
            else:
                img = pygame.transform.scale(wall_img, (cell_size, cell_size))
            screen.blit(img, (x+offset.x, y+offset.y))
            
            if (i, j) in passed_cells:
                if zoom_out:
                    # Tìm vị trí của ô này trong path
                    try:
                        idx = [k for k, p in enumerate(path) if p[0] == i and p[1] == j][0]
                    except IndexError:
                        idx = -1
                    if 0 <= idx < fade_index:
                        # Đã đến lượt fade sang xanh
                        green_surface = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
                        green_surface.fill((0, 255, 100, 150))  # Xanh nhạt, alpha 120
                        screen.blit(green_surface, (x+offset.x, y+offset.y))
                    else:
                        # Chưa đến lượt, vẫn đen nhạt
                        black_surface = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
                        black_surface.fill((0, 0, 0, 150))
                        screen.blit(black_surface, (x+offset.x, y+offset.y))
                else:
                    black_surface = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
                    black_surface.fill((0, 0, 0, 150))
                    screen.blit(black_surface, (x+offset.x, y+offset.y))
    # Vẽ drone (nếu chưa đến đích)
    # if not zoom_out:
        # Tính vị trí drone mượt giữa 2 ô
    angle = 0
    if path and current_idx < len(path) - 1:
        (r1, c1, *_), (r2, c2, *_) = path[current_idx], path[current_idx+1]
        drone_row = r1 + (r2 - r1) * drone_progress
        drone_col = c1 + (c2 - c1) * drone_progress
        # Tính góc hướng di chuyển (theo radian)
        dx = c2 - c1
        dy = r2 - r1
        angle = math.degrees(math.atan2(-dy, dx))  # Đảo dấu dy vì pygame y-axis ngược
    elif path:
        drone_row, drone_col = path[-1][0], path[-1][1]
    else:
        drone_row, drone_col = src
    drone_x = drone_col * cell_size
    drone_y = drone_row * cell_size
    # Hiệu ứng drone khi sạc
    drone_scaled = pygame.transform.scale(drone_img, (cell_size, cell_size))
    drone_rotated = pygame.transform.rotate(drone_scaled, angle)
    if is_waiting:
        # Hiệu ứng rung nhẹ khi sạc
        shake = math.sin(time.time() * 10) * 2  # Rung với tần số 10 Hz, biên độ 2 pixel
        drone_rect = pygame.Rect(drone_x + offset.x + shake, drone_y + offset.y + shake, cell_size, cell_size)
        drone_rotated = drone_scaled
    else:
        drone_rect = drone_rotated.get_rect(center=(drone_x + offset.x + cell_size // 2, drone_y + offset.y + cell_size // 2))
    screen.blit(drone_rotated, drone_rect)


    # Giao diện bên phải
    pygame.draw.rect(screen, (0, 0, 0), (map_width, 0, WIDTH - map_width, HEIGHT))
    if not zoom_out and current_idx < len(path) - 1:
        r, c, val, battery, cost = path[current_idx]
        # Độ cao là giá trị ô hiện tại (val)
        altitude = val if isinstance(val, (int, float)) else 0
        # Chọn màu theo độ cao
        altitude_color = (0, 200, 0) if altitude <= 100 else (220, 0, 0)
        draw_text(screen, font, f"Battery: {battery:.2f}%", map_width + 20, 40)
        draw_text(screen, font, f"Cost: {cost}", map_width + 20, 80)
        draw_text(screen, font, f"Position: ({r}, {c})", map_width + 20, 120)
        draw_text(screen, font, f"Altitude: {altitude}", map_width + 20, 160, altitude_color)
        if is_waiting:
            draw_text(screen, font, "Charging...", map_width + 20, 200)
        else:
            draw_text(screen, font, "Moving...", map_width + 20, 200)
        pause_rect = pygame.Rect(map_width + 5, HEIGHT - 100, 90, 40)
        menu_rect = pygame.Rect(map_width + 105, HEIGHT - 100, 90, 40)
        pygame.draw.rect(screen, (100, 100, 255), pause_rect)
        pygame.draw.rect(screen, (255, 180, 60), menu_rect)
        draw_text(screen, font, "Pause" if not paused else "Resume", pause_rect.x + 12, pause_rect.y + 8, (0,0,0))
        draw_text(screen, font, "Menu", menu_rect.x + 20, menu_rect.y + 8, (0,0,0))
    else:
        menu_rect = pygame.Rect(map_width + ((map_width*0.3)//2), HEIGHT - 100, 120, 40)
        pygame.draw.rect(screen, (255, 180, 60), menu_rect)
        draw_text(screen, font, "Menu", menu_rect.x + 30, menu_rect.y + 8, (0,0,0))
        draw_text(screen, font, "Path:", map_width + 20, 40)
        total_lines = fade_index
        # Chỉ vẽ các dòng trong khoảng scroll_offset
        for idx in range(scroll_offset, min(scroll_offset + MAX_PATH_LINES, total_lines)):
            if idx < len(path):
                r, c, h, *_ = path[idx]
                draw_text(screen, font, f"{idx+1}: (x: {r}, y: {c}, height: {h})", map_width + 20, 60 + (idx - scroll_offset)*25, (0,255,100))
        # Vẽ thanh trượt nếu cần
        if total_lines > MAX_PATH_LINES:
            bar_height = int(MAX_PATH_LINES / total_lines * 375)
            bar_y = 60 + int(scroll_offset / total_lines * 375)
            bar_rect = pygame.Rect(WIDTH-30, bar_y, 10, bar_height)
            pygame.draw.rect(screen, (180,180,180), (WIDTH-30, 60, 10, 375))
            pygame.draw.rect(screen, (100,100,255), bar_rect)
        
def draw_text(screen, font, text, x, y, color=(255,140,0)):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))