import pygame
import random

# Инициализация Pygame
pygame.init()

# Параметры окна
WIDTH, HEIGHT = 570, 650
CELL_SIZE = 100
PADDING = 10
BORDER_RADIUS = 15
FPS = 80
TOP_PADDING = 80  # Отступ сверху для счета

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
COLORS = {
    2: (197, 75, 108),
    4: (161, 93, 152),
    8: (33, 139, 130),
    16: (247, 206, 118),
    32: (127, 199, 255),
    64: (220, 130, 143),
    128: (87, 132, 186),
    256: (230, 165, 126),
    512: (118, 205, 205),
    1024: (162,162,208),
    2048: (182, 216, 242),
    4096: (129, 199, 132),
    8192: (238, 186, 178),
    16384: (249, 150, 139),
    32768: (247, 206, 118),
    65536: (123, 146, 170),
    131072: (190, 180, 197),
    262144: (152, 212, 187),
    524288: (152, 212, 187),
    1048576: (33, 139, 130)
}

# Шрифт
font = pygame.font.SysFont("RotondacBold", 60)
score_font = pygame.font.SysFont("RotondacBold", 40)
menu_font = pygame.font.SysFont("RotondacBold", 50)

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Объединяй клетки!")
clock = pygame.time.Clock()

# Игровое поле
grid = [[0 for _ in range(5)] for _ in range(5)]

# Анимация падения клеток
falling_cells = []

# Счет
score = 0

# Состояния игры
START_MENU = 0
GAME_ACTIVE = 1
game_state = START_MENU

# Уровни сложности
EASY = "Easy"
MEDIUM = "Medium"
HARD = "Hard"
current_difficulty = MEDIUM

def render_value(value):
    """Форматирует изображение значения."""
    if value >= 16384:
        return f"{value // 1024}K"
    return str(value)

def draw_grid():
    """Отрисовка игрового поля с обновленными значениями."""
    for i in range(5):
        for j in range(5):
            # Проверяем, не находится ли текущая клетка под падающей
            is_under_falling = False
            for cell in falling_cells:
                if cell["end_i"] == i and cell["end_j"] == j:
                    is_under_falling = True
                    break

            # Если клетка не под падающей, отрисовываем её
            if not is_under_falling:
                value = grid[i][j]
                color = COLORS.get(value, GRAY)
                x = j * (CELL_SIZE + PADDING) + PADDING
                y = i * (CELL_SIZE + PADDING) + PADDING + TOP_PADDING
                pygame.draw.rect(
                    screen, color,
                    (x, y, CELL_SIZE, CELL_SIZE),
                    border_radius=BORDER_RADIUS
                )
                if value != 0:
                    text = font.render(render_value(value), True, BLACK)
                    text_rect = text.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2))
                    screen.blit(text, text_rect)

def add_random_tile(column, count):
    """Добавляет случайные плитки в указанный столбец сверху с анимацией падения."""
    global falling_cells
    for _ in range(count):
        for i in range(5):
            if grid[i][column] == 0:
                falling_cells.append({
                    "start_i": -1,
                    "start_j": column,
                    "end_i": i,
                    "end_j": column,
                    "progress": 0.0,
                    "value": random.choice([2, 4, 8, 16, 32, 64])
                })
                break

def merge_tiles(cells):
    """Объединяет несколько клеток с одинаковыми значениями."""
    global score
    if len(cells) < 2:
        return False

    value = grid[cells[0][0]][cells[0][1]]
    for i, j in cells:
        if grid[i][j] != value:
            return False

    if len(cells) == 2:
        multiplier = 2
    elif len(cells) in [3, 4]:
        multiplier = 4
    elif len(cells) >= 5:
        multiplier = 8
    else:
        multiplier = 1

    last_i, last_j = cells[-1]
    grid[last_i][last_j] = value * multiplier
    for i, j in cells[:-1]:
        grid[i][j] = 0

    # Обновляем счет
    score += value * multiplier

    return True

def is_valid_move(cells):
    """Проверяет, является ли ход допустимым (клетки могут быть соединены по диагонали)."""
    for k in range(1, len(cells)):
        prev_i, prev_j = cells[k - 1]
        curr_i, curr_j = cells[k]
        if abs(prev_i - curr_i) > 1 or abs(prev_j - curr_j) > 1:
            return False
    return True

def shift_cells_down():
    """Сдвигает все клетки вниз, чтобы заполнить пустоты, и запускает анимацию."""
    global falling_cells
    falling_cells = []
    for j in range(5):
        i = 4
        while i >= 0:
            if grid[i][j] == 0:
                for k in range(i - 1, -1, -1):
                    if grid[k][j] != 0:
                        falling_cells.append({
                            "start_i": k,
                            "start_j": j,
                            "end_i": i,
                            "end_j": j,
                            "progress": 0.0,
                            "value": grid[k][j]
                        })
                        grid[k][j] = 0
                        break
                else:
                    break
            i -= 1

def draw_line(cells):
    """Отрисовывает линию, соединяющую выбранные клетки."""
    if len(cells) > 1:
        points = []
        for i, j in cells:
            x = j * (CELL_SIZE + PADDING) + PADDING + CELL_SIZE // 2
            y = i * (CELL_SIZE + PADDING) + PADDING + CELL_SIZE // 2 + TOP_PADDING
            points.append((x, y))
        pygame.draw.lines(screen, BLACK, False, points, 3)

def handle_drag(cells):
    """Обрабатывает перетаскивание мыши и объединение клеток."""
    if len(cells) >= 2 and is_valid_move(cells):
        if merge_tiles(cells):
            shift_cells_down()
            # Добавляем новые клетки во все столбцы, где есть пустые места
            for j in range(5):
                # Проверяем, есть ли пустые места в столбце
                if any(grid[i][j] == 0 for i in range(5)):
                    add_random_tile(j, 1)  # Добавляем по одной новой клетке в каждый столбец с пустыми местами

def update_falling_cells():
    """Обновляет анимацию падения клеток."""
    global falling_cells
    for cell in falling_cells:
        cell["progress"] += 0.05
        if cell["progress"] >= 1.0:
            cell["progress"] = 1.0
            grid[cell["end_i"]][cell["end_j"]] = cell["value"]
    falling_cells = [cell for cell in falling_cells if cell["progress"] < 1.0]

def draw_falling_cells():
    """Отрисовывает падающие клетки."""
    for cell in falling_cells:
        start_i, start_j = cell["start_i"], cell["start_j"]
        end_i, end_j = cell["end_i"], cell["end_j"]
        progress = cell["progress"]
        current_i = start_i + (end_i - start_i) * progress
        current_j = start_j + (end_j - start_j) * progress
        value = cell["value"]
        color = COLORS.get(value, WHITE)
        x = current_j * (CELL_SIZE + PADDING) + PADDING
        y = current_i * (CELL_SIZE + PADDING) + PADDING + TOP_PADDING
        pygame.draw.rect(
            screen, color,
            (x, y, CELL_SIZE, CELL_SIZE),
            border_radius=BORDER_RADIUS
        )
        if value != 0:
            text = font.render(str(value), True, BLACK)
            text_rect = text.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2))
            screen.blit(text, text_rect)

def draw_score():
    """Отрисовывает счет над игровым полем."""
    score_text = score_font.render(f"Счет: {score}", True, BLACK)
    # Центрируем счет по горизонтали и располагаем выше игрового поля
    score_text_rect = score_text.get_rect(center=(WIDTH // 2, 30))
    screen.blit(score_text, score_text_rect)

def draw_start_menu():
    """Отрисовывает стартовое меню с выбором уровня сложности."""
    screen.fill(WHITE)
    title_text = menu_font.render("Выберите уровень сложности", True, BLACK)
    title_rect = title_text.get_rect(center=(WIDTH // 2, 100))
    screen.blit(title_text, title_rect)

    # Цвета для уровней сложности
    easy_color = (144, 238, 144)  # Светло-зеленый
    medium_color = (255, 223, 186)  # Светло-оранжевый
    hard_color = (255, 182, 193)  # Светло-розовый

    # Рисуем прямоугольники для уровней сложности
    easy_rect = pygame.Rect(WIDTH // 2 - 100, 220, 200, 80)
    medium_rect = pygame.Rect(WIDTH // 2 - 100, 320, 200, 80)
    hard_rect = pygame.Rect(WIDTH // 2 - 100, 420, 200, 80)

    pygame.draw.rect(screen, easy_color, easy_rect, border_radius=20)
    pygame.draw.rect(screen, medium_color, medium_rect, border_radius=20)
    pygame.draw.rect(screen, hard_color, hard_rect, border_radius=20)

    # Отрисовываем текст поверх прямоугольников
    easy_text = menu_font.render("Easy", True, BLACK)
    easy_text_rect = easy_text.get_rect(center=easy_rect.center)
    screen.blit(easy_text, easy_text_rect)

    medium_text = menu_font.render("Medium", True, BLACK)
    medium_text_rect = medium_text.get_rect(center=medium_rect.center)
    screen.blit(medium_text, medium_text_rect)

    hard_text = menu_font.render("Hard", True, BLACK)
    hard_text_rect = hard_text.get_rect(center=hard_rect.center)
    screen.blit(hard_text, hard_text_rect)

def handle_menu_click(pos):
    """Обрабатывает клик в стартовом меню для выбора уровня сложности."""
    global game_state, current_difficulty
    # Проверяем, куда кликнул пользователь
    if 220 <= pos[1] <= 300:  # Easy
        current_difficulty = EASY
        game_state = GAME_ACTIVE
    elif 320 <= pos[1] <= 400:  # Medium
        current_difficulty = MEDIUM
        game_state = GAME_ACTIVE
    elif 420 <= pos[1] <= 500:  # Hard
        current_difficulty = HARD
        game_state = GAME_ACTIVE

def initialize_grid():
    """Инициализирует игровое поле в зависимости от выбранного уровня сложности."""
    global grid
    grid = [[0 for _ in range(5)] for _ in range(5)]
    for i in range(5):
        for j in range(5):
            if current_difficulty == EASY:
                grid[i][j] = random.choice([2, 4, 8])
            elif current_difficulty == MEDIUM:
                grid[i][j] = random.choice([2, 4, 8, 16, 32, 64])
            elif current_difficulty == HARD:
                grid[i][j] = random.choice([8, 16, 32, 64, 128, 256])

def check_and_fill_grid():
    """Проверяет, есть ли на поле пустые клетки, и заполняет их случайными значениями."""
    empty_cells = []
    for i in range(5):
        for j in range(5):
            if grid[i][j] == 0:
                empty_cells.append((i, j))

    if empty_cells:
        for i, j in empty_cells:
            grid[i][j] = random.choice([2, 4, 8, 16, 32, 64])


# Основной цикл игры
running = True
dragging = False
selected_cells = []

while running:
    if game_state == START_MENU:
        draw_start_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    handle_menu_click(event.pos)
                    initialize_grid()
    elif game_state == GAME_ACTIVE:
        screen.fill(WHITE)
        draw_grid()  # Отрисовываем сетку
        draw_falling_cells()  # Отрисовываем падающие клетки
        if dragging:
            draw_line(selected_cells)  # Отрисовываем линию, если происходит перетаскивание
        update_falling_cells()  # Обновляем анимацию падения
        draw_score()  # Отрисовываем счет

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    dragging = True
                    i = (event.pos[1] - TOP_PADDING) // (CELL_SIZE + PADDING)
                    j = event.pos[0] // (CELL_SIZE + PADDING)
                    if 0 <= i < 5 and 0 <= j < 5:
                        selected_cells.append((i, j))
                elif event.button == 3:
                    if len(selected_cells) > 0:
                        selected_cells.pop()
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and dragging:
                    handle_drag(selected_cells)
                    dragging = False
                    selected_cells = []
                    check_and_fill_grid()  # Проверяем и заполняем пустые клетки после хода

            elif event.type == pygame.MOUSEMOTION:
                if dragging:
                    mouse_x, mouse_y = event.pos
                    for i in range(5):
                        for j in range(5):
                            cell_center_x = j * (CELL_SIZE + PADDING) + PADDING + CELL_SIZE // 2
                            cell_center_y = i * (CELL_SIZE + PADDING) + PADDING + CELL_SIZE // 2 + TOP_PADDING
                            if abs(mouse_x - cell_center_x) <= 30 and abs(mouse_y - cell_center_y) <= 30:
                                # Проверяем, что значение клетки совпадает с первой выбранной клеткой
                                if len(selected_cells) > 0:
                                    first_cell_value = grid[selected_cells[0][0]][selected_cells[0][1]]
                                    current_cell_value = grid[i][j]
                                    if current_cell_value != first_cell_value:
                                        continue  # Пропускаем клетку с другим значением

                                if len(selected_cells) > 1 and (i, j) == selected_cells[-2]:
                                    selected_cells.pop()
                                elif (i, j) not in selected_cells:
                                    selected_cells.append((i, j))
                                break

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()