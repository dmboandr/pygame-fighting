import pygame
import sys  # стандартный модуль (библиотека) для управления процессами приложения
import random
import os  # модуль позволяет производить действия над директориями (папками)

pygame.init()  # активация модуля pygame
screen = pygame.display.set_mode(size=(1000, 600))
pygame.display.set_caption("Game")
clock = pygame.time.Clock()  # объект для управления фпс
FPS = 60  # 30, 60, 120

# картинки заднего фона
bg_img_mountain = pygame.image.load("img/background/mountain.png").convert_alpha()
bg_img_pine1 = pygame.image.load("img/background/pine1.png").convert_alpha()
bg_img_pine2 = pygame.image.load("img/background/pine2.png").convert_alpha()
bg_img_sky = pygame.image.load("img/background/sky_cloud.png").convert_alpha()
bg_imgs = [bg_img_sky, bg_img_mountain, bg_img_pine2, bg_img_pine1]
bg_img_lower_line = bg_img_sky.get_height() - bg_img_mountain.get_height()

tile_img_0 = pygame.image.load("img/tile/0.png").convert_alpha()

bullet_img = pygame.image.load("img/icons/bullet.png").convert_alpha()

# ЗВУКИ ИГРЫ
music_sound = pygame.mixer.Sound("audio/music2.mp3")
music_sound.set_volume(0.1)  # 1 - 100%, 0.05 = 5%
music_sound.play(loops=-1)  # повторяй бесконечно

jump_sound = pygame.mixer.Sound("audio/jump.wav")
jump_sound.set_volume(0.8)  # 1 - 100%, 0.05 = 5%

shot_sound = pygame.mixer.Sound("audio/shot.wav")
shot_sound.set_volume(0.5)  # 1 - 100%, 0.05 = 5%

# переменные для игры
endgame_timer = 120
game_active = True

# Pattern - паттерн - набор шаблонов и правил как оформить часть кода
# Singleton - это такой паттерн, который подразумевает что мы будем создавать класс,
# но объект у этого класса будет всего 1


class Character(pygame.sprite.Sprite):
    def __init__(self, x, y, size=1.0, speed=5, char_type=""):
        pygame.sprite.Sprite.__init__(self)  # мы наследуем от pygame.sprite.Sprite
        # анимации
        self.animation_list = []
        self.flip = False   # переворачивать картинку
        self.animation_index = 0
        self.animation_cooldown = 0
        self.action = 0
        self.char_type = char_type
        # для сражения
        self.health = 100
        self.alive = True
        self.death_anim = False
        self.is_attacking = False
        self.attack_cooldown = 0  # как часто мы можем нажимать на атаку
        self.attack_delay = 60

        self.attack_speed = 60  # сколько длится состояние атаки в фреймах
        self.attack_time = self.attack_speed  # сколько мы находимся в состоянии атаки


        # стрельба
        self.is_shooting = False
        self.direction = 1
        self.shoot_cooldown = 0
        self.shoot_delay = 20

        # для ИИ
        self.ai_moving_timer = 0

        if self.char_type == "player":
            animations = ["Idle", "Run", "Jump", "Death", "Attack"]
        elif self.char_type == "enemy":
            animations = ["Idle", "Run", "Jump", "Death", "Attack"]

        for animation_type in animations:
            if animation_type == "Attack":
                size *= 0.9
            img_names = os.listdir(f"img/{self.char_type}/{animation_type}")
            images = []  #
            for i in range(len(img_names)):  # 0, 1, 2, 3, 4
                image = pygame.image.load(f"img/{self.char_type}/{animation_type}/{i}.png").convert_alpha()
                image = self.crop_transparent(image)
                image = pygame.transform.rotozoom(image, 0, size)
                images.append(image)
                print(image, self.char_type)
            self.animation_list.append(images)

        # для движения
        self.speed = speed
        self.moving_left = False
        self.moving_right = False
        # для прыжка
        self.jump = False
        self.in_air = False
        self.gravity = 0.75  # с какой силой нас тянет  вниз
        self.jump_velocity = 0  # высота прыжка

        self.surface = self.animation_list[self.action][self.animation_index]
        self.rect = self.surface.get_rect(bottomleft=(x, y))

    def move(self):
        dx = 0
        dy = 0

        if self.jump_velocity > 10:
            self.jump_velocity = 10

        # получилось сделать прыжок
        if self.jump and self.in_air == False:
            self.jump_velocity = -18
            self.in_air = True
            self.jump = False
            jump_sound.play()

        self.jump_velocity += self.gravity  # -10 -9.25 ... 0 ... 10
        dy += self.jump_velocity

        # проверка на коллизию с землей
        if self.rect.bottom + dy >= 422:  # 422
            dy = 422 - self.rect.bottom
            self.in_air = False

        # движение игрока
        if self.moving_left and self.action != 4:
            dx -= self.speed
            self.flip = True
            self.direction = -1
            self.update_action(new_action=1)
        elif self.moving_right and self.action != 4:
            dx += self.speed
            self.flip = False
            self.direction = 1
            self.update_action(new_action=1)

        # проверка на выход игрока за края экрана
        if ((self.rect.right >= screen.get_width() and self.moving_right) or
                (self.rect.left <= 0 and self.moving_left)):
            dx = 0  # опять сбрасываем наше изменение по x на 0

        #  применение изменений в координатах игрока
        self.rect.x += dx
        self.rect.y += dy

    def ai(self, target):
        # движение бота
        if abs(self.rect.x - target.rect.x) < 40:
            self.attack(target)
        elif self.ai_moving_timer <= 0:
            if self.rect.x < target.rect.x:
                self.moving_right = True
                self.moving_left = False
            elif self.rect.x > target.rect.x:
                self.moving_left = True
                self.moving_right = False
            self.ai_moving_timer = random.randint(30, 120)
        self.ai_moving_timer -= 1
        # 1   0


    def crop_transparent(self, image):
        """Обрезает прозрачные края у изображения"""
        mask = pygame.mask.from_surface(image)
        bounding_rect = mask.get_bounding_rects()  # []

        cropped_image = pygame.Surface((bounding_rect[0].width, bounding_rect[0].height), pygame.SRCALPHA)
        cropped_image.blit(image, (0, 0), bounding_rect[0])

        return cropped_image

    def shoot(self):
        if self.shoot_cooldown == 0:
            bullet = Bullet((self.rect.x + ((self.rect.width//2 + 30) * self.direction), self.rect.y + (self.rect.height//2)), self.direction)
            bullet_group.add(bullet)
            self.shoot_cooldown = self.shoot_delay
            shot_sound.play()

    def attack(self, target):
        if self.attack_cooldown == 0:  # если счётчик равен 0
            self.is_attacking = True  # я перехожу в состояние атаки
            self.attack_cooldown = self.attack_delay  # сразу же меняю счётчик
            self.surf = pygame.surface.Surface(size=(self.rect.width, self.rect.height))
            # (self.rect.x + ((self.rect.width//2 + 30) * self.direction)
            self.attack_hitbox = self.surf.get_rect(topleft=(self.rect.x + (self.rect.width * self.direction), self.rect.y))
            self.surf.fill((255, 0, 0))

            if self.attack_hitbox.colliderect(target.rect):
                target.health -= 50


    def update_animation(self):
        self.animation_cooldown += 1

        if self.animation_cooldown == 10:
            self.animation_index += 1  # 3.5 = 3
            self.animation_cooldown = 0
            # бег - 10 картинок
            if self.animation_index >= len(self.animation_list[self.action]) and self.action != 3:
                self.animation_index = 0

            if self.animation_index >= len(self.animation_list[self.action]) and self.action == 3:
                self.animation_index -= 1

        self.surface = self.animation_list[self.action][self.animation_index]
        self.rect = self.surface.get_rect(topleft=(self.rect.x, self.rect.top))

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.animation_cooldown = 0
            self.animation_index = 0

    def update(self):
        if self.alive:

            #screen.blit(self.surf, self.attack_hitbox)

            if self.health <= 0:
                self.alive = False
                self.health = 0

            # прыжок
            if self.in_air == True:
                self.update_action(new_action=2)
            # атака ближняя
            elif self.is_attacking:
                self.update_action(new_action=4)
            # движение влево-вправо
            elif self.moving_left or self.moving_right:
                self.update_action(new_action=1)
            # idle
            else:
                self.update_action(new_action=0)

            # стрельба
            if self.is_shooting:
                self.shoot()

            if self.shoot_cooldown > 0:
                self.shoot_cooldown -= 1

            # удар в ближнем бою
            if self.is_attacking:
                self.attack(enemy)

            if self.attack_cooldown > 0:
                self.attack_cooldown -= 1

            if self.is_attacking and self.attack_time > 0:
                self.attack_time -= 1

            if self.attack_time == 0:
                self.is_attacking = False
                self.attack_time = self.attack_speed

        else:
            if self.death_anim == False:
                self.update_action(3)
                self.death_anim = True

        self.update_animation()
        #self.test_rect()
        self.move()

    def test_rect(self):
        self.square_surf = pygame.surface.Surface(size=(self.surface.get_width() + 3, self.surface.get_height() + 3))
        self.square_surf.fill((255, 0, 0))
        self.square_rect = self.square_surf.get_rect(bottomleft=(self.rect.x, self.rect.y + self.surface.get_height()))
        screen.blit(self.square_surf, self.square_rect)
        print(player.rect.x, player.rect.y)

    def draw(self):
        screen.blit(pygame.transform.flip(self.surface, self.flip, False), self.rect)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, direction):
        pygame.sprite.Sprite.__init__(self)  # мы наследуем от pygame.sprite.Sprite
        self.speed = 15
        self.direction = direction

        self.image = bullet_img
        self.rect = self.image.get_rect(center=pos)

    def update(self):
        self.rect.x += self.speed * self.direction

        for character in character_group:
            if self.rect.colliderect(character.rect) and character.alive:
                self.kill()  # update вызывает пуля, т.к. это класс Bullet
                character.health -= 50
                print(character.health)


class HealthBar(pygame.sprite.Sprite):
    def __init__(self, x, y, health, max_health, color=(230, 5, 10)):
        pygame.sprite.Sprite.__init__(self)  # мы наследуем от pygame.sprite.Sprite

        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health
        self.color = color
        self.ratio = self.health / self.max_health  # 100/100 = 1

    def draw(self, health, pos, style=1, color=None):
        width = int(self.ratio * (40-2))
        height = 15-2

        if style != 1:
            width = screen.get_width() // 2
            height = 40

        self.x, self.y = pos

        self.ratio = health / self.max_health

        black_surface = pygame.surface.Surface(size=(width, height))  # surface - поверхность
        black_surface.fill((0, 0, 0))
        if health > 0:
            red_surface = pygame.surface.Surface(size=(int(width * self.ratio), height))  # surface - поверхность
            red_surface.fill(self.color)
            screen.blit(black_surface, (self.x, self.y))
            screen.blit(red_surface, (self.x, self.y))
        else:
            screen.blit(black_surface, (self.x, self.y))





# ФУНКЦИИ
def draw_bg():
    """ Функция рисования заднего фона """
    screen.blit(bg_img_sky, (0, 0))
    screen.blit(bg_img_pine2, (0, bg_img_lower_line))
    screen.blit(bg_img_pine1, (0, bg_img_lower_line))
    screen.blit(bg_img_mountain, (0, bg_img_lower_line))
    for i in range(0, 35):
        screen.blit(tile_img_0, (i * tile_img_0.get_width(), bg_img_sky.get_height()))

def restart():
    global player, enemy
    player.kill()
    enemy.kill()
    player = Character(x=100, y=422, size=1.5, char_type="player")
    enemy = Character(x=500, y=422, size=2, char_type="enemy")
    player_hp.health = 100
    enemy_hp.health = 100
    character_group.add(player)
    character_group.add(enemy)


player = Character(x=100, y=422, size=1.5, char_type="player")
enemy = Character(x=500, y=422, size=2, char_type="enemy")
player_hp = HealthBar(x=player.rect.x,
                      y=player.rect.y,
                      health=100,
                      max_health=100,
                      color=(10, 250, 15))

enemy_hp = HealthBar(x=screen.get_width() // 2,
                      y=30,
                      health=100,
                      max_health=100)

# группы объектов
character_group = pygame.sprite.Group()
character_group.add(player)
character_group.add(enemy)

bullet_group = pygame.sprite.Group()



# ОСНОВНОЙ ЦИКЛ ИГРЫ
run = True
while run:
    # проход по событиям
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()  # закроет текущий процесс (выйдет из программы)
        if event.type == pygame.KEYDOWN:  # когда нажата
            # подсобытие
            if game_active:
                if event.key == pygame.K_a:
                    player.moving_left = True

                if event.key == pygame.K_d:
                    player.moving_right = True

                if event.key == pygame.K_SPACE:
                    player.jump = True

                if event.key == pygame.K_e:
                    player.is_shooting = True

                if event.key == pygame.K_f:
                    player.attack(enemy)
            else:
                if event.key == pygame.K_SPACE:
                    restart()
                    game_active = True
                    endgame_timer = 120

        if event.type == pygame.KEYUP:  # когда отжата
            # подсобытие
            if event.key == pygame.K_a:
                player.moving_left = False

            if event.key == pygame.K_d:
                player.moving_right = False

            if event.key == pygame.K_e:
                player.is_shooting = False


    # задний фон
    draw_bg()

    if game_active:
        if not (player.alive == True and enemy.alive == True):
            endgame_timer -= 1
            if endgame_timer == 0:
                game_active = False

        # отображать врага
        if enemy.alive:
            enemy.ai(player)
        else:
            #enemy.update_action(4)
            enemy.moving_left = False
            enemy.moving_right = False
        enemy.update()
        enemy.draw()
        enemy_hp.draw(enemy.health, pos=(500, 0), style=2)

        # рисовать игрока
        player.update()
        player.draw()
        player_hp.draw(player.health, pos=(0, 0), style=2)

        # отображение групп объектов
        bullet_group.update()
        bullet_group.draw(screen)
    else:
        player.draw()
        enemy.draw()

    pygame.display.update()
    clock.tick(FPS)  # я гарантирую, что цикл не будет выполнять больше FPS раз
