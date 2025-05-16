import pygame
import sys
import abc
import random
import os
from pygame.constants import KEYDOWN


class State(abc.ABC):
    @abc.abstractmethod
    def handle_events(self, canvas):
        pass

    @abc.abstractmethod
    def update(self):
        pass

    @abc.abstractmethod
    def draw(self, screen):
        pass


class SplashScreen(State):
    def __init__(self):
        self.text = "Zastavka"
        self.surface = font.render(self.text, True, (255, 255, 255))
        self.hint = "Нажмите для продолжения"
        self.hint_surface = font.render(self.hint, True, (255, 255, 255))
        self.hint_visible = True
        self.hint_time = pygame.time.get_ticks()

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                return Menuscreen()
        return self

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.hint_time > 800:
            self.hint_visible = not self.hint_visible
            self.hint_time = current_time

    def draw(self, screen):
        screen.fill(BACKGROUND)
        rect = self.surface.get_rect()
        rect.centerx = screen.get_rect().centerx
        rect.centery = screen.get_rect().centery - 100
        screen.blit(self.surface, rect)

        if self.hint_visible:
            hint_rect = self.hint_surface.get_rect()
            hint_rect.centerx = screen.get_rect().centerx
            hint_rect.centery = screen.get_rect().centery + 100
            screen.blit(self.hint_surface, hint_rect)


class Menuscreen(State):
    def __init__(self):
        self.items = ['Играть', 'Выбрать имя игрока', 'Выйти']
        self.surfaces = [font.render(item, True, (255, 255, 255)) for item in self.items]
        self.selected = 0

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == KEYDOWN:
                if event.key == pygame.K_UP:
                    self.prev()
                if event.key == pygame.K_DOWN:
                    self.next()
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    return self.process_item()
        return self

    def update(self):
        pass

    def draw(self, screen):
        screen.fill((0, 0, 0))
        for i, item in enumerate(self.items):
            color = (255, 0, 0) if i == self.selected else (255, 255, 255)
            surface = font.render(item, True, color)
            rect = surface.get_rect()
            rect.centerx = screen.get_rect().centerx
            rect.top = screen.get_rect().top + 100 * (i + 1)
            screen.blit(surface, rect)

    def next(self):
        if self.selected < len(self.items) - 1:
            self.selected += 1

    def prev(self):
        if self.selected > 0:
            self.selected -= 1

    def process_item(self):
        if self.selected == 0:
            return PuzzleGame()
        if self.selected == 1:
            return Namescreen()
        if self.selected == 2:
            pygame.quit()
            exit()


class Namescreen(State):
    def __init__(self):
        self.text = "Player Name"
        self.surface = font.render(self.text, True, (255, 255, 255))
        self.name = ""
        self.name_surface = None

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    if len(self.name) > 0:
                        self.name = self.name[:-1]
                elif event.key == pygame.K_RETURN:
                    global player_name
                    player_name = self.name
                    return Menuscreen()
                else:
                    if event.unicode.isalnum() and len(self.name) < 10:
                        self.name += event.unicode
                        self.name_surface = font.render(self.name, True, (255, 255, 255))
        return self

    def update(self):
        pass

    def draw(self, screen):
        screen.fill(BACKGROUND)
        rect = self.surface.get_rect()
        rect.centerx = screen.get_rect().centerx
        rect.top = screen.get_rect().top + 100
        screen.blit(self.surface, rect)
        if self.name_surface is not None:
            name_rect = self.name_surface.get_rect()
            name_rect.centerx = screen.get_rect().centerx
            name_rect.top = screen.get_rect().top + 200
            screen.blit(self.name_surface, name_rect)


class PuzzleGame(State):
    def __init__(self):
        self.ROWS = 3
        self.COLS = 3
        self.MARGIN = 2
        self.swaps = 0
        self.selected = None

        # Загрузка изображения
        pictures = os.listdir('pictures')
        picture = random.choice(pictures)
        self.image = pygame.image.load('pictures/' + picture)

        # Подготовка тайлов
        image_width, image_height = self.image.get_size()
        self.TILE_WIDTH = image_width // self.COLS
        self.TILE_HEIGHT = image_height // self.ROWS

        self.tiles = []
        for i in range(self.ROWS):
            for j in range(self.COLS):
                rect = pygame.Rect(j * self.TILE_WIDTH,
                                   i * self.TILE_HEIGHT,
                                   self.TILE_WIDTH,
                                   self.TILE_HEIGHT)
                tile = self.image.subsurface(rect)
                self.tiles.append(tile)

        self.origin_tiles = self.tiles.copy()
        random.shuffle(self.tiles)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return Menuscreen()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()

                for i in range(len(self.tiles)):
                    row = i // self.ROWS
                    col = i % self.COLS
                    x = col * (self.TILE_WIDTH + self.MARGIN) + self.MARGIN
                    y = row * (self.TILE_HEIGHT + self.MARGIN) + self.MARGIN

                    if x <= mouse_x <= x + self.TILE_WIDTH and y <= mouse_y <= y + self.TILE_HEIGHT:
                        if self.selected is not None and self.selected != i:
                            self.tiles[i], self.tiles[self.selected] = self.tiles[self.selected], self.tiles[i]
                            self.selected = None
                            self.swaps += 1
                        elif self.selected == i:
                            self.selected = None
                        else:
                            self.selected = i
        return self

    def update(self):
        pass

    def draw(self, screen):
        screen.fill(BACKGROUND)

        # Отрисовка тайлов
        for i in range(len(self.tiles)):
            tile = self.tiles[i]
            row = i // self.ROWS
            col = i % self.COLS
            x = col * (self.TILE_WIDTH + self.MARGIN) + self.MARGIN
            y = row * (self.TILE_HEIGHT + self.MARGIN) + self.MARGIN
            if i == self.selected:
                pygame.draw.rect(screen, (0, 255, 0), (x - self.MARGIN, y - self.MARGIN,
                                                       self.TILE_WIDTH + self.MARGIN * 2,
                                                       self.TILE_HEIGHT + self.MARGIN * 2))
            screen.blit(tile, (x, y))

        # Отрисовка счетчика перестановок
        font = pygame.font.SysFont('Arial', 32)
        text = font.render(f'Количество перестановок: {self.swaps}', True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.center = (screen.get_rect().width // 2, screen.get_rect().height // 2 + 300)
        pygame.draw.rect(screen, (0, 0, 0), text_rect.inflate(4, 4))
        screen.blit(text, text_rect)

        # Проверка завершения игры
        if self.tiles == self.origin_tiles:
            font = pygame.font.SysFont('Arial', 64)
            text = font.render('Ура, картинка собрана!', True, (255, 255, 255))
            text_rect = text.get_rect()
            text_rect.center = (screen.get_rect().width // 2, screen.get_rect().height // 2)
            pygame.draw.rect(screen, (0, 0, 0), text_rect.inflate(4, 4))
            screen.blit(text, text_rect)


# Инициализация pygame
pygame.init()
pygame.font.init()

size = (1280, 720)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("My Game")
BACKGROUND = (0, 0, 0)
screen.fill(BACKGROUND)
FPS = 60
clock = pygame.time.Clock()

player_name = "Anonim Tusk"
font = pygame.font.SysFont(None, 64)

# Создаем папку pictures, если её нет
if not os.path.exists('pictures'):
    os.makedirs('pictures')
    print("Создана папка 'pictures'. Добавьте туда изображения для игры.")

# Запуск игры
state = SplashScreen()
while True:
    events = pygame.event.get()
    state = state.handle_events(events)
    state.update()
    state.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()