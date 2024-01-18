import pygame
import os
import sys

pygame.init()
FPS = 24
size = WIDTH, HEIGHT = 512, 512
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname).convert()
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["DUNGEONEERING", "",
                  "Убейте зомби и дойдите до люка,",
                  "чтобы перейти на следующий уровень.",
                  "Движение на стрелочки, для убийства",
                  "противника шагните на его клетку.",
                  "Стоя на люке, нажмите Space, чтобы",
                  "начать новый уровень."]

    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))

    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


LEVELS = [
    '''################
#..............#
#..............#
###########.####
#..............#
#..............#
#..............#
#..H...@.....Z.#
#..............#
#..............#
#..............#
#..............#
####.###########
#..............#
#..............#
################''',
    '''###############
#......H......#
#.....CCC.....#
#.............#
#...##...##...#
#...##...##...#
#.............#
#..@......ZZZ.#
#...##...##...#
#...##...##...#
#.............#
#.............#
#...##...##...#
#...##...##...#
#.............#
###############''',
    '''###############
#......@......#
#..Z...C...Z..#
#......C......#
#......C......#
#......C......#
#......C......#
#......C......#
#......C......#
#......C......#
#......H......#
#.............#
#.............#
#.............#
#.............#
###############''',
    '''################
#..............#
#..Z.......Z...#
#........#####C#
#........#.....#
#........#..H..#
#######..#######
#......CC......#
#....#.CC.#....#
#....#.CC.#....#
#......@......Z#
#....#.CC.#....#
#....#.CC.#....#
#......CC......#
#......Z.......#
################''',
    '''################
#..............#
#..............#
#..............#
#..............#
#.G.CCCCCCCC@..#
#..............#
#..............#
#..............#
#..............#
################'''
]


def load_level(level):
    level_map = [line for line in LEVELS[level - 1].split('\n')]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


tile_images = {
    'wall': load_image('wall.png'),
    'empty': load_image('floor.png'),
    'hatch': load_image('hatch.png'),
    'carpet': load_image('carpet.png'),
    'graal': load_image('graal.png', -1)
}
player_image = load_image('hero.png', -1)
enemy_images = {  # сюда надо добавить скелета
    'zombie': load_image('zombie.png', -1)

}
tile_width = tile_height = 32

player = None
enemies = {}
hatch_coords = (0, 0)

# группы спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
enemies_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


def generate_level(level):
    new_player, x, y, enemies = None, None, None, {}
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == 'C':
                Tile('carpet', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
            elif level[y][x] == 'Z':
                Tile('empty', x, y)
                enemies[f'zombie{x}{y}'] = Enemy('zombie', x, y)
            elif level[y][x] == 'H':
                Tile('hatch', x, y)
                hatch_coords = x, y
            elif level[y][x] == 'G':
                Tile('empty', x, y)
                Tile('graal', x, y)
                hatch_coords = x, y

    # вернем игрока, а также размер поля в клетках
    return new_player, enemies, x, y, hatch_coords


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.pos = pos_x, pos_y

    def move(self, x, y):
        self.pos = (x, y)
        self.rect = self.image.get_rect().move(tile_width * x, tile_height * y)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, enemy_type, pos_x, pos_y):
        super().__init__(enemies_group, all_sprites)
        self.image = enemy_images[enemy_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.num = f'{pos_x}{pos_y}'
        self.pos = pos_x, pos_y
        self.type = enemy_type

    def move(self, x, y):
        self.pos = (x, y)
        self.rect = self.image.get_rect().move(tile_width * x, tile_height * y)


def move(hero, step):
    x, y = hero.pos
    if step == 'up':
        if y > 0 and level_map[y - 1][x] != '#':
            hero.move(x, y - 1)
    elif step == 'down':
        if y < max_y - 1 and level_map[y + 1][x] != '#':
            hero.move(x, y + 1)
    elif step == 'left':
        if x > 0 and level_map[y][x - 1] != '#':
            hero.move(x - 1, y)
    elif step == 'right':
        if x < max_x - 1 and level_map[y][x + 1] != '#':
            hero.move(x + 1, y)
    enemy_positions = []
    for i in enemies:
        enemy_positions.append(enemies[i].pos)
    if hero.pos in enemy_positions:
        for i in enemies:
            if hero.pos == enemies[i].pos:
                enemies[i].kill()


def enemy_move(enemy, hero):
    target_x, target_y = hero.pos
    enemy_poses = []
    enemy_x, enemy_y = enemy.pos
    dx = enemy_x - target_x
    dy = enemy_y - target_y
    for e in enemies:
        enemy_poses.append((enemies[e].pos[0], enemies[e].pos[1]))
    if (abs(dx) == 0 and abs(dy) == 1) or (abs(dx) == 1 and abs(dy) == 0):  # проверка на близость к игроку
        pass
    elif abs(dx) > abs(dy):  # Шагаем горизонтально по X
        if dx < 0:
            if level_map[enemy_y][enemy_x + 1] != '#' and (enemy_x + 1, enemy_y) not in enemy_poses:
                enemy.move(enemy_x + 1, enemy_y)
        else:
            if level_map[enemy_y][enemy_x - 1] != '#' and (enemy_x - 1, enemy_y) not in enemy_poses:
                enemy.move(enemy_x - 1, enemy_y)
    else:  # Шагаем вертикально по Y
        if dy < 0:
            if level_map[enemy_y + 1][enemy_x] != '#' and (enemy_x, enemy_y + 1) not in enemy_poses:
                enemy.move(enemy_x, enemy_y + 1)
        else:
            if level_map[enemy_y - 1][enemy_x] != '#' and (enemy_x, enemy_y - 1) not in enemy_poses:
                enemy.move(enemy_x, enemy_y - 1)


def next_level(level_num):
    level_num += 1
    level_map = load_level(level_num)
    tiles_group.empty()
    enemies_group.empty()
    player_group.empty()
    enemies = {}
    player, enemies, max_x, max_y, hatch = generate_level(level_map)
    return level_num, player, enemies, max_x, max_y, hatch, level_map


def tip_screen():  # экраны переходов между уровнями
    intro_text = ["DUNGEONEERING",
                      f"Уровень {level}"]
    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))

    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)

def game_end():
    intro_text = ["DUNGEONEERING",
                  "На этом все."
                  "Спасибо за игру!"]
    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))

    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)

pygame.mixer_music.load(os.path.join('data', 'dungeon_music.mp3'))
pygame.mixer_music.set_volume(0.1)
pygame.mixer_music.play(-1)
start_screen()
level = 1
level_map = load_level(level)
player, enemies, max_x, max_y, hatch = generate_level(level_map)
next = False
tick = 1
running = True
tip_screen()
while running:
    for event in pygame.event.get():
        if next:
            level, player, enemies, max_x, max_y, hatch, level_map = next_level(level)
            tip_screen()
            next = False
        if event.type == pygame.QUIT:
            running = False
        key = pygame.key.get_pressed()
        if key[pygame.K_DOWN]:
            move(player, 'down')
            tick -= 1
        elif key[pygame.K_UP]:
            move(player, 'up')
            tick -= 1
        elif key[pygame.K_LEFT]:
            move(player, 'left')
            tick -= 1
        elif key[pygame.K_RIGHT]:
            move(player, 'right')
            tick -= 1
        elif key[pygame.K_SPACE]:
            tick = 0
            if level == 5 and player.pos == hatch:
                game_end()
                running = False
            elif player.pos == hatch:
                next = True

        if tick == 0:
            for i in enemies:
                enemy = enemies[i]
                enemy_move(enemy, player)
            tick = 1
    screen.fill((0, 0, 0))
    tiles_group.draw(screen)
    enemies_group.draw(screen)
    player_group.draw(screen)
    pygame.display.flip()

terminate()
