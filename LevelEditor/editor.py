"""
Этот файл предназначен для создания уровней
для игры Shooter написанной на pygame

.csv - comma separated value
"""

import pygame
import csv  # модуль для csv-файлов

pygame.init()  # активировать pygame

FPS = 60
clock = pygame.time.Clock()

# настройки экрана редактора уровней
SCREEN_WIDTH = 800  # ширина
SCREEN_HEIGHT = 640  # высота
LOWER_MARGIN = 100  # нижний отступ
SIDE_MARGIN = 300  # отступ сбоку

# объект экрана
screen = pygame.display.set_mode((SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN))
pygame.display.set_caption("Level Editor for Shooter")

# классы

class Button():
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, ((int(width * scale)), (int(height * scale))))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False


    def draw(self, surface):
        action = False

        pos = pygame.mouse.get_pos()

        # проверить кликнули ли мы на кнопку
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        surface.blit(self.image, (self.rect.x, self.rect.y))
        return action

# переменные для тайлов
ROWS = 16  # строки
MAX_COLS = 150  # колонки
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
level = 0
current_tile = 0

# переменные для скроллинга
scroll_left = False
scroll_right = False
scroll = 0
scroll_speed = 1

# изображения
mountain = pygame.image.load("img/background/mountain.png").convert_alpha()
sky = pygame.image.load("img/background/sky_cloud.png").convert_alpha()
pine1 = pygame.image.load("img/background/pine1.png").convert_alpha()
pine2 = pygame.image.load("img/background/pine2.png").convert_alpha()
img_list = []  # пустой массив для тайлов
for x in range(TILE_TYPES):  # 0, 1, 2, ..., 20
    img = pygame.image.load(f"img/tile/{x}.png").convert_alpha()
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)  # добавить в массив img_list картинку img

save_img = pygame.image.load("img/save_btn.png").convert_alpha()
load_img = pygame.image.load("img/load_btn.png").convert_alpha()


# переменные для кнопок
button_list = []
button_col = 0  # column (столбец, колонка)
button_row = 0  # row (строка)
for i in range(len(img_list)):  # 0, 1, 2, 3, 4, 5, ... 20
    tile_button = Button(30 + SCREEN_WIDTH + (75 * button_col), 75 * button_row + 50, img_list[i], 1)
    button_list.append(tile_button)
    button_col += 1
    if button_col == 3:
        button_col = 0
        button_row += 1

# шрифт
font = pygame.font.SysFont("Futura", 30)

# переменные для цвета RGB
RED = (255, 0, 0)
BLACK = (10, 10, 10)
GREEN = (10, 244, 75)
WHITE = (250, 245, 244)

# игровой мир
world_data = []
for row in range(ROWS):
    r = [-1] * MAX_COLS
    world_data.append(r)


for tile in range(0, MAX_COLS):
    world_data[ROWS - 1][tile] = 0
    world_data[ROWS - 2][tile] = 1

print(world_data)
# Функции для игры


def draw_bg():
    """ Функция отрисовывающая задний фон """
    width = sky.get_width()
    for x in range(4):  # 0*1400, 1*1400, 2*1400, 3*1400
        screen.blit(sky, ((x * width) - scroll * 0.5, 0))
        screen.blit(mountain, ((x * width) - scroll * 0.6, SCREEN_HEIGHT - mountain.get_height() - 200))
        screen.blit(pine2, ((x * width) - scroll * 0.7, SCREEN_HEIGHT - pine2.get_height()))
        screen.blit(pine1, ((x * width) - scroll * 0.8, SCREEN_HEIGHT - pine1.get_height()))


def draw_grid():
    # вертикальные линии для сетки (столбцы)
    # column - столбец, row - строка
    for c in range(MAX_COLS+1):  # 0, 1, 2, 3, 4, 5, ... 200
        pygame.draw.line(screen, WHITE,  ((c * TILE_SIZE) - scroll, 0), ((c * TILE_SIZE) - scroll, SCREEN_HEIGHT))
    # горизонтальные линии для сетки (строки)
    for r in range(MAX_COLS+1):  # 0, 1, 2, 3, 4, 5, ... 200
        pygame.draw.line(screen, WHITE,  (0, (r * TILE_SIZE)), (SCREEN_WIDTH, (r * TILE_SIZE)))


def draw_world():
    for y, row in enumerate(world_data):  # [[-1, -1, -1, -1], [0, 1, 1, 2], [0, 0, 0, 0]]
        for x, tile in enumerate(row):
            if tile >= 0:
                screen.blit(img_list[tile], (x * TILE_SIZE - scroll, y * TILE_SIZE))


# основной цикл
run = True
while run:
    for event in pygame.event.get():
        # закрытие приложения
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                scroll_left = True
            if event.key == pygame.K_d:
                scroll_right = True
            if event.key == pygame.K_LSHIFT:
                scroll_speed = 5

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                scroll_left = False
            if event.key == pygame.K_d:
                scroll_right = False
            if event.key == pygame.K_LSHIFT:
                scroll_speed = 1

    # механика скролла (сдвига по экрану)
    if scroll_left == True and scroll > 0:
        scroll -= 5 * scroll_speed
    if scroll_right == True:
        scroll += 5 * scroll_speed

    # логика отрисовки на сетки по клику мыши
    pos = pygame.mouse.get_pos()  # pos[0] -> x; pos[1] -> y
    x = (pos[0] + scroll) // TILE_SIZE
    y = pos[1] // TILE_SIZE

    if pos[0] < SCREEN_WIDTH and pos[1] < SCREEN_HEIGHT:  # кликаю именно на сетку
        if pygame.mouse.get_pressed()[0] == 1:  # лкм
            if world_data[y][x] != current_tile:
                world_data[y][x] = current_tile  # [[3, 1, 5], [], []]
        if pygame.mouse.get_pressed()[1] == 1:  # колёсико
            for y, row in enumerate(world_data):  # [[3, 1, 5], [], []]
                for x in row:
                    world_data[y][x] = -1
        if pygame.mouse.get_pressed()[2] == 1:  # пкм
            world_data[y][x] = -1

    # отрисовка сетки, заднего  фона и т.д.
    screen.fill((10, 244, 75))  # func(10, "abc", 5)
    draw_bg()
    draw_world()  # это действие делается 60 раз в секунду
    draw_grid()
    pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH, 0, SIDE_MARGIN, SCREEN_HEIGHT))

    # отображение кнопок
    button_count = 0
    for button_count, i in enumerate(button_list):  # [button, button, button]
        if i.draw(screen):
            current_tile = button_count
            print("click", (i.rect.x, i.rect.y), current_tile)

    pygame.draw.rect(screen, RED, button_list[current_tile], 3)
    #                     800 // 4 = 200
    save_button = Button(SCREEN_WIDTH // 4, SCREEN_HEIGHT + LOWER_MARGIN - 80, save_img, 1)
    load_button = Button(SCREEN_WIDTH // 2, SCREEN_HEIGHT + LOWER_MARGIN - 80, load_img, 1)

    if save_button.draw(screen):
        with open(f"level_{level}.csv", "w", newline="") as file:
            writer = csv.writer(file, delimiter=",")
            for row in world_data:
                writer.writerow(row)

    if load_button.draw(screen):
        scroll = 0
        with open(f"level_0.csv") as file:
            reader = csv.reader(file, delimiter=",")
            for x, row in enumerate(reader):
                for y, tile in enumerate(row):
                    world_data[x][y] = int(tile)

    pygame.display.update()
    clock.tick(FPS)
