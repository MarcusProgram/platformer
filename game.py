####################################################################################
# Данный код представляет собой каркас для игры в жанре платформер                 #
# В нем определены: классы главного героя, врагов, собираемых предметов и платформ #
# управление с помощью клавиатуры, проверка коллизий объектов                      #
# Проект можно запустить для демонстрации функционала                              #
####################################################################################


################################################################
# При запуске:                                                  #
# синие элементы - платформы,                                  #
# красный элемент - враг,                                      #
# зеленый элемент - игрок,                                     #
# желтый элемент - собираемый предмет                          #
#                                                              #
# Управление: стрелки клавиатуры для движения, пробел для прыжка#
################################################################

# подключние бибилиотек
import pygame
import random
import time
import os
import sys
import json
import base64


######### СОЗДАНИЕ, ЗАПИСЫВАНИЕ И ТД короче суть этих пару десятков строк в том что я создаю папку coinsDB если ее нет, так же coin.json
# записываю в них параметры, и шифрую их в base64, так же обновление в файле и load из файла
directory = 'db'
coins_file_path = os.path.join(directory, 'stat.json')

if not os.path.exists(directory):
    os.makedirs(directory)

if not os.path.exists(coins_file_path):
    with open(coins_file_path, 'w') as file:
        json.dump({'coins': base64.b64encode(str(0).encode('utf-8')).decode(), 'skin': 'c3RhdGljLnBuZw=='}, file)  # Добавляем поле "skin"

def update_coins_file(coins_data):
    coins_data_encoded = {k: base64.b64encode(v.encode('utf-8')).decode() if isinstance(v, str) else v for k, v in coins_data.items()}
    with open(coins_file_path, 'w') as file:
        json.dump(coins_data_encoded, file)

def decode_coins_data(coins_data_encoded):
    return {k: base64.b64decode(v.encode()).decode() if isinstance(v, str) else v for k, v in coins_data_encoded.items()}

def load_coins_data():
    coins_data = {'coins': 0, 'skin': 'c3RhdGljLnBuZw=='}

    try:
        with open(coins_file_path, 'r') as file:
            data = file.read()
            if data:
                coins_data_encoded = json.loads(data)
                coins_data = decode_coins_data(coins_data_encoded)
                coins = int(coins_data.get('coins', 0))
                return coins, coins_data
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"Ошибка отрытия файла!!!")

    return 0, coins_data

coins, coins_data = load_coins_data()
with open("db/stat.json", "r") as file:
    json_data = json.load(file)
    encoded_skin = json_data["skin"]
decoded_skin = base64.b64decode(encoded_skin).decode('utf-8')


###все закончилось шифрование

## что бы звуки были без задержки
pygame.mixer.pre_init(44100,-16,1,512)
# инициализация Pygame
pygame.init()

# константы-параметры окна
WIDTH = 800
HEIGHT = 600
# константы-цвета
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GOLD = (255, 215, 0)
BLACK = (0, 0, 0)
ONE_BLUE = (66,170,255)

player_damaged = False
damage_time = 0
shout_time = 0
is_touching_enemy = False  # Переменная для отслеживания касания игрока врага
last_damage_time = 0  # Переменная для отслеживания времени последнего полученного урона игроком
health_recovery_delay = 5  # Задержка в секундах перед началом восстановления здоровья
health_recovery_rate = 0.5  # Количество восстанавливаемого здоровья за тик
MAIN_MENU = 0 # Определение возможных состояний игры
PLAYING = 1 # Определение возможных состояний игры
LEVEL_1 = 2 # Определение возможных состояний игры
SKINS = 3 # Определение возможных состояний игры
game_state = MAIN_MENU  # Начинаем с главного меню
running = True  # Переменная для управления циклом игры
have_key = False


##### вся музыка

music = pygame.mixer

coin_music = music.Sound("music/coin.mp3")
jump_music = music.Sound("music/action_jump.mp3")
steps_music = music.Sound("music/action_footsteps_plastic.mp3")
game_over_music = music.Sound("music/gameover_1.mp3")
key_up_music = music.Sound("music/key_up.mp3")
you_win = music.Sound("music/you_win.mp3")
button_click = music.Sound("music/minecraft_click.mp3")
buy_music = music.Sound("music/cash.mp3")
fon = music.Sound("music/bird.mp3")
fon.play(-1)

####

bg = pygame.image.load("backgrounds/bg.jpg")
main_bg = pygame.image.load("backgrounds/main_bg.png")



sprite_key = pygame.image.load("backgrounds/key.png")
sprite_key = pygame.transform.scale(sprite_key, (50,50 ))
sprite_rect = sprite_key.get_rect()
sprite_rect.center = (640, HEIGHT-330)

door = pygame.image.load("backgrounds/door.png")
door = pygame.transform.scale(door, (50,100 ))
door_rect = door.get_rect()
door_rect.center = (290, HEIGHT - 480)

class Button:
    def __init__(self, x, y, width, height, image_path):
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.clicked = True
        else:
            self.clicked = False

exit_button = Button(WIDTH/2-60, HEIGHT/2+60, 119, 45, "buttons/exit.png")
skins_button = Button(WIDTH/2-60, HEIGHT/2, 119, 45, "buttons/skins.png")
play_button = Button(WIDTH/2-60, HEIGHT/2-60, 119, 45, "buttons/play.png")

left_button = Button(WIDTH/2-70, HEIGHT/2, 32, 32, "buttons/left.png")
right_button = Button(WIDTH/2+30, HEIGHT/2, 32, 32, "buttons/right.png")

buy_button = Button(WIDTH/2-66, HEIGHT/2+60, 123, 42, "buttons/buy.png")

back_button = Button(10, 100, 32, 32, "buttons/left.png")
class CollisionRect:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 0, 0), (self.x, self.y, self.width, self.height), 1) # проверял коллизию rect1.draw()

    def check_collision(self, sprite_rect):
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        return rect.colliderect(sprite_rect)


sprite_collision_rect = CollisionRect(sprite_rect.left, sprite_rect.top, sprite_rect.width, sprite_rect.height)
rect1 = CollisionRect(630, HEIGHT-340, 20, 30)

door_collision_rect = CollisionRect(door_rect.left, door_rect.top, door_rect.width, door_rect.height)
rect2 = CollisionRect(290, HEIGHT - 480, 50,100)
# класс для игрока

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, skin_path):
        super().__init__()

        self.skin_path = skin_path
        self.load_image()

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.x_velocity = 0
        self.y_velocity = 0
        self.on_ground = False

    def load_image(self):
        self.image = pygame.image.load(self.skin_path).convert()
        self.image = pygame.transform.scale(self.image, (32, 32))

    def update(self):
        self.rect.x += self.x_velocity
        self.rect.y += self.y_velocity

# класс для патрулирующих врагов
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # создание изображения для спрайта
        self.image = pygame.Surface((32, 32))
        self.image.fill(RED)

        # начальная позиция по Х, нужна для патрулирования
        self.x_start = x
        # выбор направления начального движения
        self.direction = random.choice([-1, 1])

        # создание хитбокса для спрайта
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # компоненты скорости по оси Х и Y
        self.x_velocity = 1
        self.y_velocity = 0

    def update(self):
        # если расстояние от начальной точки превысило 50
        # то меняем направление
        if abs(self.x_start - self.rect.x) > 50:
            self.direction *= -1

        # движение спрайта по оси Х
        self.rect.x += self.x_velocity * self.direction


# класс для поднимаемых предметов
class Collectible(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # создание изображения для спрайта
        self.image = pygame.Surface((16, 16))
        self.image.fill(GOLD)

        # создание хитбокса для спрайта
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


# класс для платформы
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        # создание изображения для спрайта
        self.image = pygame.Surface((width, height))
        self.image.fill(BLUE)

        # создание хитбокса для спрайта
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

def check_collision(sprite_rect, other_rect):
    return sprite_rect.colliderect(other_rect)
## функция вывода на экран game over если умер либо выпал за карту
def game_over():
    music.Channel(0).play(game_over_music)
    font = pygame.font.Font(None, 100)
    screen.fill(WHITE)
    text = font.render("Game Over :(", True, RED)
    text_rect = text.get_rect(center=(screen.get_width() / 2, screen.get_height() / 2))
    screen.blit(text, text_rect)
    pygame.display.update()
    time.sleep(1.9)
    pygame.quit()
    sys.exit()

#был баг что послеп завершения игры персонаж оставался на том же меcте, а коины не деспавнились, вот тут я этот баг убрал
def reset_game():
    global collectibles_list
    player.rect.x = 10
    player.rect.y = HEIGHT
    player.x_velocity = 0
    player.y_velocity = 0
    player.on_ground = False
    collectibles_list = [
        Collectible(195, 470),
        Collectible(642, HEIGHT - 90),
        Collectible(672, HEIGHT - 90),
        Collectible(702, HEIGHT - 90),
        Collectible(62, HEIGHT - 370),
        Collectible(92, HEIGHT - 370),
        Collectible(122, HEIGHT - 370)
    ]
    collectibles.empty()
    for coin in collectibles_list:
        collectibles.add(coin)

# функция для проверки коллизий c платформой
def check_collision_platforms(object, platform_list):
    # перебираем все платформы из списка (не группы спрайтов)
    for platform in platform_list:
        if object.rect.colliderect(platform.rect):
            if object.y_velocity > 0:  # Если спрайт падает
                # меняем переменную-флаг
                object.on_ground = True
                # ставим его поверх платформы и сбрасываем скорость по оси Y
                object.rect.bottom = platform.rect.top
                object.y_velocity = 0
            elif object.y_velocity < 0:  # Если спрайт движется вверх
                # ставим спрайт снизу платформы
                object.rect.top = platform.rect.bottom
                object.y_velocity = 0
            elif object.x_velocity > 0:  # Если спрайт движется вправо
                # ставим спрайт слева от платформы
                object.rect.right = platform.rect.left
            elif object.x_velocity < 0:  # Если спрайт движется влево
                # ставим спрайт справа от платформы
                object.rect.left = platform.rect.right

def check_collision_enemies(player, enemies_list):
    global running
    global health
    global player_damaged
    global damage_time
    global shout_time
    global is_touching_enemy
    global last_damage_time

    is_touching_enemy = False

    # логика восстановления здоровья
    if time.time() - last_damage_time >= health_recovery_delay:
        if health < 100:  # елси здоровье не превышает максимальное значение
            health += health_recovery_rate  #то хилить

    # проверка на столкновение с врагами
    for enemy in enemies_list:
        if player.rect.colliderect(enemy.rect) and not player_damaged:
            player_damaged = True
            damage_time = time.time()
            is_touching_enemy = True  #если касается врага то TRUE
            last_damage_time = time.time()  # обновляем время последнего полученного урона игроком

    # проверка на то, получил ли игрок урок, и сбросит player_damaged спустя 1 секунду
    if player_damaged and time.time() - damage_time >= 1:
        player_damaged = False

    # каждую 0.1 секунду если игрок соприкосается с врагом то убирать по 20 хп
    if is_touching_enemy and (time.time() - shout_time) >= 0.1:
        health -= 40
        shout_time = time.time()

    # если меньше 0 здоровье то гейм овер
    if health <= 0:
        game_over()


def check_collision_collectibles(object):
    # делаем видимыми объекты для подбора в игре и очки
    global collectibles_list
    global coins
    # если object касается collictible
    for collectible in collectibles_list:
        if object.rect.colliderect(collectible.rect):
            # убираем этот объект из всех групп
            collectible.kill()
            # убираем этот объект из списка (чтобы не было проверки коллизии)
            collectibles_list.remove(collectible)
            # прибавляем одно очко
            coins += 1
            #звук, а так же обновление в файле
            music.Channel(1).play(coin_music)
            coins_data['coins'] = str(coins)
            update_coins_file(coins_data)


# создаем экран, счетчик частоты кадров и очков
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
health = 100.0


player = Player(10, HEIGHT+10,f'skins/{decoded_skin}')

platforms_list = [Platform(0, HEIGHT - 25, 100, 50),
                  Platform(180, 500, 50, 30),
                  Platform(300, HEIGHT - 25, 100, 30),
                  Platform(640, HEIGHT - 70, 80, 30),
                  Platform(500, HEIGHT - 190, 80, 30),
                  Platform(600, HEIGHT - 300, 80, 30),
                  Platform(400, HEIGHT - 390, 80, 30),
                  Platform(250, HEIGHT - 450, 80, 30),
                  Platform(60, HEIGHT - 350, 80, 30),]

enemies_list = [Enemy(330, HEIGHT-60),
                Enemy(650, HEIGHT - 105),
                Enemy(90, HEIGHT - 385),]

collectibles_list = [Collectible(195, 470),
                     Collectible(642, HEIGHT - 90),
                     Collectible(672, HEIGHT - 90),
                     Collectible(702, HEIGHT - 90),
                     Collectible(62, HEIGHT - 370),
                     Collectible(92, HEIGHT - 370),
                     Collectible(122, HEIGHT - 370)]

# счёт игры
wintext = pygame.font.Font(None, 30)
font = pygame.font.Font(None, 36)  # создание объекта, выбор размера шрифта
score_text = font.render(f"Coins: {coins}", True, (0, 0, 0))
score_rect = score_text.get_rect()  # создание хитбокса текста
score_rect.topleft = (10, 10)  # расположение хитбокса\текста на экране

# создаем текст "Health: "  в черном цвете
text_health = "Health: "
health_text_health = font.render(text_health, True, BLACK)
health_rect_health = health_text_health.get_rect(topleft=(HEIGHT, 10))


# создаем групп спрайтов
player_and_platforms = pygame.sprite.Group()
enemies = pygame.sprite.Group()
collectibles = pygame.sprite.Group()

# в трех циклах добавляем объекты в соответствующие группы
for i in enemies_list:
    enemies.add(i)

for i in platforms_list:
    player_and_platforms.add(i)

for i in collectibles_list:
    collectibles.add(i)

# отдельно добавляем игрока
player_and_platforms.add(player)

i = 0
prev_left_button_state = False
prev_right_button_state = False

left_key_pressed = False
right_key_pressed = False
if __name__ == "__main__":
    while running:

        #главная менюшка
        if game_state == MAIN_MENU:
            screen.blit(main_bg, (0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                exit_button.handle_event(event)
                skins_button.handle_event(event)
                play_button.handle_event(event)

            exit_button.draw(screen)
            skins_button.draw(screen)
            play_button.draw(screen)

            if play_button.clicked:
                music.Channel(1).play(button_click)
                game_state = LEVEL_1
            elif exit_button.clicked:
                music.Channel(1).play(button_click)
                time.sleep(0.5)
                pygame.quit()
                sys.exit()
            elif skins_button.clicked:
                music.Channel(1).play(button_click)
                game_state = SKINS
            pygame.display.flip()
        elif game_state == LEVEL_1:

            ### банально текст на весь экран LEVEL 1, 2 секунды
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            current_path = os.path.dirname(__file__)
            font_path = os.path.join(current_path, 'fonts')

            font2 = pygame.font.Font(os.path.join(font_path, 'Gamtex.ttf'), 100)
            text = "level 1"
            text_surface = font2.render(text, True, (255, 255, 255))
            screen.fill(BLACK)
            text_rect = text_surface.get_rect(center=(WIDTH / 2, HEIGHT / 2))
            screen.blit(text_surface, text_rect)

            pygame.display.flip()
            time.sleep(2)
            game_state = PLAYING
            pygame.display.flip()
            ###
        elif game_state == SKINS:
            screen.blit(main_bg, (0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                left_button.handle_event(event)
                right_button.handle_event(event)
                buy_button.handle_event(event)
                back_button.handle_event(event)
            back_button.draw(screen)
            left_button.draw(screen)
            right_button.draw(screen)
            buy_button.draw(screen)
            coast_skin = ['10','50','100','1000','1000000']
            #OTk5OTk5OTk5OTk5OTk5OTk5 = 999999999999999999
            skins_arr = ['blue.png','red.png','gold.png','best.png','king.png']
            if back_button.clicked:
                game_state = MAIN_MENU

            #сделал чекеры, так как если бы не они то при одном нажатии сразу перекидывало бы в конец массива
            if left_button.clicked != prev_left_button_state:
                if left_button.clicked: # просто матать скины вперед назад
                    if i > 0:
                        i -= 1
                        music.Channel(1).play(button_click)
            elif right_button.clicked != prev_right_button_state:
                if right_button.clicked:
                    if i < len(skins_arr) - 1:
                        i += 1
                        music.Channel(1).play(button_click)
            elif buy_button.clicked: # покупка скинов и запись их в бд, так же в base 64
                if coins >= int(coast_skin[i]):
                    music.Channel(1).play(buy_music)
                    coins -= int(coast_skin[i])
                    coins_data['coins'] = coins
                    coins_data['skin'] = skins_arr[i]
                    update_coins_file(coins_data)
                    player = Player(10, HEIGHT, f'skins/{decoded_skin}')
                else:
                    call_text = wintext.render("NO MONEY - NO FUNNY", True, GOLD)
                    call_text_rect = call_text.get_rect(center=(395, 100))
                    screen.blit(call_text, call_text_rect)
            # Обновите предыдущее состояние кнопок
            prev_left_button_state = left_button.clicked
            prev_right_button_state = right_button.clicked
            #показ скинов из папки
            image = pygame.image.load(f'skins/{skins_arr[i]}')
            image = pygame.transform.scale(image, (50, 50))
            screen.blit(image, (HEIGHT/2+70, WIDTH/2-110))
            #стоимость скинов
            call_text = wintext.render(coast_skin[i], True, GOLD)
            call_text_rect = call_text.get_rect(center=(395, 250))
            screen.blit(call_text, call_text_rect)

            pygame.display.flip()

        elif game_state == PLAYING:

            screen.blit(bg, (0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    ## движение + музыка, и куча проверок что бы музыка не наслаивалась на себя же, а то звуки как из ада (мной проверенно в наушниках)
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        player.x_velocity = -3
                        left_key_pressed = True
                        if not music.Channel(2).get_busy():
                            music.Channel(2).play(steps_music)
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        player.x_velocity = 3
                        right_key_pressed = True
                        if not music.Channel(3).get_busy():
                            music.Channel(3).play(steps_music)

                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        left_key_pressed = False
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        right_key_pressed = False
            # проверяем нажатие на клавиши для перемещения
            keys = pygame.key.get_pressed()
            player.x_velocity = 0
            ## то же самое что выше было
            if left_key_pressed and (keys[pygame.K_LEFT] or keys[pygame.K_a]):
                player.x_velocity = -3
                if not music.Channel(2).get_busy():
                    music.Channel(2).play(steps_music)

            if right_key_pressed and (keys[pygame.K_RIGHT] or keys[pygame.K_d]):
                player.x_velocity = 3
                if not music.Channel(3).get_busy():
                    music.Channel(3).play(steps_music)

            # условие прыжка остается неизменным
            if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and player.on_ground == True:
                player.y_velocity = -9
                player.on_ground = False
                if not music.Channel(4).get_busy():
                    music.Channel(4).play(jump_music)
            # гравитация для игрока
            player.y_velocity += 0.3
            # перемещение игрока из одного конца в другой, если игрок вышел
            player.rect.x = (player.rect.x + player.x_velocity) % WIDTH
            if player.rect.y-20 > HEIGHT:
                game_over()
            # обновляем значения атрибутов игрока и врагов
            player.update()
            enemies.update()

            # отрисовываем фон, платформы, врагов и собираемые предметы
            #screen.fill(WHITE)
            player_and_platforms.draw(screen)
            enemies.draw(screen)
            collectibles.draw(screen)
            screen.blit(door, door_rect)
            if have_key == False:
                screen.blit(sprite_key, sprite_rect)
                if rect2.check_collision(player):
                    call_text = wintext.render("Вы не подобрали ключ!", True, RED)
                    call_text_rect = call_text.get_rect(center=(400, 50))
                if rect2.check_collision(player):  # вывод текста при коллизии
                    screen.blit(call_text, call_text_rect,)
                if rect1.check_collision(player):
                    sprite_rect.x = -1000
                    sprite_rect.y = -1000
                    have_key = True
                    music.Channel(5).play(key_up_music)
            if have_key == True:
                if rect2.check_collision(player):
                    call_text = wintext.render("Нажмите E что бы пройти дальше", True, RED)
                    call_text_rect = call_text.get_rect(center=(400, 50))
                if rect2.check_collision(player):  # вывод текста при коллизии
                    screen.blit(call_text, call_text_rect,)
                if (keys[pygame.K_e]):
                    music.Channel(6).play(you_win)
                    time.sleep(2)
                    game_state=MAIN_MENU
                    reset_game()
                # проверяем все возможные коллизии
            check_collision_platforms(player, platforms_list)
            check_collision_enemies(player, enemies_list)
            check_collision_collectibles(player)

            # обновление счёта на экране
            score_text = font.render(f"Coins: {coins}", True, (0, 0, 0))
            screen.blit(score_text, score_rect)

            # создаем текст с количеством здоровья в зеленом цвете
            text_score = str(health)
            health_text_score = font.render(text_score, True, (0, 255, 0))  # Зеленый цвет
            health_rect_score = health_text_score.get_rect(topleft=(health_rect_health.right, 10))
            # отображаем текст "Здоровье:" и количество здоровья на экране
            screen.blit(health_text_health, health_rect_health)
            screen.blit(health_text_score, health_rect_score)
            #платформа без коллизии для троллигна)))
            pygame.draw.rect(screen, ONE_BLUE, (480, HEIGHT - 50, 80, 30))
            pygame.display.update()
            clock.tick(60)

    pygame.quit()