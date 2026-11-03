"""Модуль игры «Змейка».

Содержит классы игровых объектов, обработку пользовательского
ввода и основной игровой цикл, реализованные с помощью Pygame.
"""

from random import choice, randint

import pygame


# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвета:
BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32
)
pygame.display.set_caption('Змейка')
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс игрового объекта."""

    def __init__(self, body_color=None):
        """Создать объект в центре игрового поля."""
        self.position = (
            (SCREEN_WIDTH // 2 // GRID_SIZE) * GRID_SIZE,
            (SCREEN_HEIGHT // 2 // GRID_SIZE) * GRID_SIZE,
        )
        self.body_color = body_color

    def draw(self):
        """Отрисовать игровой объект."""
        raise NotImplementedError(
            'Метод draw() должен быть переопределён '
            'в дочернем классе.'
        )


class Apple(GameObject):
    """Яблоко, которое появляется в случайной свободной клетке поля."""

    def __init__(
        self, occupied_positions=(), body_color=APPLE_COLOR
    ):
        """Создать яблоко и выбрать его начальное положение."""
        super().__init__(body_color)
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions):
        """Переместить яблоко в случайную свободную клетку."""
        occupied_positions = set(occupied_positions)

        if len(occupied_positions) >= GRID_WIDTH * GRID_HEIGHT:
            raise ValueError(
                'На игровом поле нет свободных клеток для яблока.'
            )

        self.position = (
            randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
        )

        while self.position in occupied_positions:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )

    def draw(self):
        """Нарисовать яблоко на игровом поле."""
        rect = pygame.Rect(
            self.position, (GRID_SIZE, GRID_SIZE)
        )
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Змейка: хранит сегменты, двигается и меняет направление."""

    def __init__(self, body_color=SNAKE_COLOR):
        """Создать змейку длиной в один сегмент."""
        super().__init__(body_color)
        self.positions = [self.position]
        self.length = 1
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def get_head_position(self):
        """Вернуть координаты головы змейки."""
        return self.positions[0]

    def update_direction(self):
        """Применить выбранное направление движения."""
        if self.next_direction is not None:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Переместить змейку на одну клетку."""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction

        new_head = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT,
        )

        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def reset(self):
        """Вернуть змейку в начальное состояние."""
        self.length = 1
        self.positions = [
            (
                (SCREEN_WIDTH // 2 // GRID_SIZE) * GRID_SIZE,
                (SCREEN_HEIGHT // 2 // GRID_SIZE) * GRID_SIZE,
            )
        ]
        self.position = self.get_head_position()
        self.direction = choice((UP, DOWN, LEFT, RIGHT))
        self.next_direction = None
        self.last = None

    def draw(self):
        """Нарисовать сегменты змейки и очистить бывший хвост."""
        for position in self.positions:
            rect = pygame.Rect(
                position, (GRID_SIZE, GRID_SIZE)
            )
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        if self.last is not None:
            last_rect = pygame.Rect(
                self.last, (GRID_SIZE, GRID_SIZE)
            )
            pygame.draw.rect(
                screen, BOARD_BACKGROUND_COLOR, last_rect
            )


def handle_keys(game_object):
    """Обработать закрытие окна и нажатия клавиш."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit

        if event.type != pygame.KEYDOWN:
            continue

        if (
            event.key == pygame.K_UP
            and game_object.direction != DOWN
        ):
            game_object.next_direction = UP
        elif (
            event.key == pygame.K_DOWN
            and game_object.direction != UP
        ):
            game_object.next_direction = DOWN
        elif (
            event.key == pygame.K_LEFT
            and game_object.direction != RIGHT
        ):
            game_object.next_direction = LEFT
        elif (
            event.key == pygame.K_RIGHT
            and game_object.direction != LEFT
        ):
            game_object.next_direction = RIGHT


def main():
    """Запустить игровой цикл."""
    pygame.init()

    snake = Snake()
    apple = Apple(set(snake.positions))

    screen.fill(BOARD_BACKGROUND_COLOR)

    while True:
        clock.tick(SPEED)

        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(set(snake.positions))

        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(set(snake.positions))
            screen.fill(BOARD_BACKGROUND_COLOR)

        apple.draw()
        snake.draw()

        pygame.display.update()


if __name__ == '__main__':
    main()
