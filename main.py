from random import randint
from sys import stdout, stdin, exit
from os import system, name, O_NONBLOCK
from time import sleep
from termios import tcgetattr, ICANON, TCSANOW, ECHO, TCSAFLUSH, tcsetattr
from fcntl import fcntl, F_SETFL, F_GETFL
import os
import shlex
import struct
import platform
import subprocess


class Keys:
    ARROW_UP: str = "\x1b[A"
    ARROW_DOWN: str = "\x1b[B"
    ARROW_RIGHT: str = "\x1b[C"
    ARROW_LEFT: str = "\x1b[D"
    ESC: str = "\x1b"


def get_terminal_size():
    def ioctl_GWINSZ(fd):
        try:
            import fcntl
            import termios

            cr = struct.unpack("hh", fcntl.ioctl(fd, termios.TIOCGWINSZ, "1234"))
            return cr
        except:
            pass

    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        try:
            cr = (os.environ["LINES"], os.environ["COLUMNS"])
        except:
            return None
    return int(cr[1]), int(cr[0])


WIDTH, HEIGHT = get_terminal_size()


def getchar(keys_len=5):
    fd = stdin.fileno()

    oldterm = tcgetattr(fd)
    newattr = tcgetattr(fd)
    newattr[3] = newattr[3] & ~ICANON & ~ECHO
    tcsetattr(fd, TCSANOW, newattr)

    oldflags = fcntl(fd, F_GETFL)
    fcntl(fd, F_SETFL, oldflags | O_NONBLOCK)

    try:
        while True:
            try:
                key = stdin.read(keys_len)
                break
            except IOError:
                pass
    finally:
        tcsetattr(fd, TCSAFLUSH, oldterm)
        fcntl(fd, F_SETFL, oldflags)
    return key


def hide():
    system("stty -echo")
    stdout.write("\033[?25l")
    stdout.flush()


def show():
    system("stty echo")
    stdout.write("\033[?25h")


def clear():
    system("cls" if name == "nt" else "clear")


class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __iadd__(self, other):
        return Position((self.x + other.x), (self.y + other.y))

    def __eq__(self, other):
        return True if (self.x == other.x) and (self.y == other.y) else False


class Direction:
    UP = Position(0, -1)
    DOWN = Position(0, 1)
    LEFT = Position(-1, 0)
    RIGHT = Position(1, 0)


class Food:
    def __init__(self):
        self.spawn()

    def spawn(self):
        self.loc = Position(randint(0, WIDTH + 1), randint(0, HEIGHT + 1))

    def draw(self):
        stdout.write(f"\x1b[{self.loc.y};{self.loc.x}H{chr(9618)}")


class Snake:
    def __init__(self):
        self.head = Position(randint(0, WIDTH), randint(0, HEIGHT))
        self.direction = Direction.RIGHT
        self.length = 5
        self.body = []

    def change_direction(self, key):
        if key == Keys.ARROW_LEFT:
            self.direction = Direction.LEFT
        elif key == Keys.ARROW_RIGHT:
            self.direction = Direction.RIGHT
        elif key == Keys.ARROW_UP:
            self.direction = Direction.UP
        elif key == Keys.ARROW_DOWN:
            self.direction = Direction.DOWN

    def eat_food(self, food):
        if food.loc == self.head:
            food.spawn()
            self.length += 1
            return True
        else:
            return False

    def eat_self(self):
        for part in self.body:
            if part == self.head:
                return True
        else:
            return False

    def update(self):
        if self.head.x < 0:
            self.head = Position(WIDTH, self.head.y)
        elif self.head.x > WIDTH:
            self.head = Position(0, self.head.y)
        elif self.head.y < 0:
            self.head = Position(self.head.x, HEIGHT)
        elif self.head.y > HEIGHT:
            self.head = Position(self.head.x, 0)
        self.body.append(self.head)
        if self.length < len(self.body):
            self.body.pop(0)
        self.head += self.direction

    def draw(self):
        stdout.write(f"\x1b[{self.head.y};{self.head.x}H{chr(9608)}")
        for part in self.body:
            stdout.write(f"\x1b[{part.y};{part.x}H{chr(9617)}")


class Game:
    def __init__(self):
        self.snake = Snake()
        self.food = Food()
        self.tick_rate = 0.3

    def update(self):
        self.snake.update()
        if self.snake.eat_food(self.food):
            self.tick_rate -= 0.001
        if self.snake.eat_self():
            exit()

    def draw(self):
        self.snake.draw()
        self.food.draw()

    def mainloop(self):
        try:
            hide()
            while True:
                key = getchar()
                clear()
                self.snake.change_direction(key)
                self.update()
                self.draw()
                stdout.flush()
                if key == Keys.ESC:
                    break
                sleep(self.tick_rate)

        except Exception as e:
            print(e)

        finally:
            show()
            clear()


def main():
    game = Game()
    game.mainloop()


if __name__ == "__main__":
    main()
