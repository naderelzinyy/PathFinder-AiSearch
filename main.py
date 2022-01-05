
import pygame as pg
import sys
from os import path
from menu import *
from settings import *
from sprites import *
from pathfinding import *

vec = pg.math.Vector2


class Game:
    def __init__(self):
        pg.init()
        self.window = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        pg.key.set_repeat(500, 100)
        self.load_data()
        self.playing = False
        self.running = True
        self.display = pg.Surface((WIDTH, HEIGHT))
        self.font_name = pg.font.get_default_font()
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY = False, False, False, False
        self.path_len = 0
        self.main_menu = MainMenu(self)
        self.curr_menu = self.main_menu

    def load_data(self):
        self.map_data = []
        with open(path.join(path.dirname(__file__), './Maps/map3.txt'), 'rt') as f:
            for line in f:
                self.map_data.append(line)

        # load arrow sprites
        icon_dir = path.join(path.dirname(__file__))
        self.arrows = {}
        arrow_img = pg.image.load(path.join(icon_dir, './Images/arrowRight.png')).convert_alpha()
        arrow_img = pg.transform.scale(arrow_img, (50, 50))
        for dir in [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
            self.arrows[dir] = pg.transform.rotate(arrow_img, vec(dir).angle_to(vec(1, 0)))
        self.font_name = pg.font.match_font('hack')

    def new(self):
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.Group()
        self.ias = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.walls_list = []
        mob_pos = []
        for row, tiles in enumerate(self.map_data):
            for col, tile in enumerate(tiles):
                if tile == '1':
                    Wall(self, col, row)
                    self.walls_list.append((col, row))
                if tile == 'P':
                    self.player = Player(self, col, row)
                if tile == 'M':
                    mob_pos.append((col, row))

        self.g = WeightedGrid(GRIDWIDTH, GRIDHEIGHT)
        for wall in self.walls_list:
            self.g.walls.append(vec(wall))

        for col, row in mob_pos:
            IA(self, col, row)
        print(f"walls_list : {self.walls_list}")

    def run(self):

        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()

    def quit(self):
        self.running = self.playing = False
        pg.quit()

    def update(self):

        self.all_sprites.update()

    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.window, BLACK, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.window, BLACK, (0, y), (WIDTH, y))

    def draw_search_surface(self, ia: IA):
        for pos in ia.path:
            current_pos = vec(pos)
            x = int(current_pos.x * TILESIZE)
            y = int(current_pos.y * TILESIZE)
            img = pg.Surface((TILESIZE, TILESIZE))
            img.fill(LIGHTGRAY)
            rect = img.get_rect(topleft=(x, y))
            self.window.blit(img, rect)

    def draw_path(self, start: pg.math.Vector2, goal: pg.math.Vector2, path: {(int, int): pg.math.Vector2}):
        current = start
        path_len = 0
        # try:
        while current != goal:
            v = path[(current.x, current.y)]
            if v.length_squared() == 1:
                path_len += 10
            else:
                path_len += 14
            img = self.arrows[vec2int(v)]
            x = current.x * TILESIZE + TILESIZE / 2
            y = current.y * TILESIZE + TILESIZE / 2
            rect = img.get_rect(center=(x, y))
            self.window.blit(img, rect)
            # find next in path
            current = current + path[vec2int(current)]
        # except:
        #     pass
        self.path_len = path_len

    def draw(self):
        self.window.fill(BGCOLOR)
        self.draw_grid()
        for ia in self.ias:
            self.draw_search_surface(ia)
            start = vec(ia.x // TILESIZE, ia.y // TILESIZE)
            goal = ia.goal
            self.draw_path(start, goal, ia.path)
        self.all_sprites.draw(self.window)
        draw_text("A* Search", 30, WHITE, 10,  10, self.window, self.font_name, align="topleft")
        draw_text(f"Path length:{self.path_len}", 30, WHITE, 10,  45, self.window, self.font_name, align="topleft")
        if self.path_len == 0:
            draw_text("Caught", 100, WHITE, 390, 200, self.window, self.font_name, align="topleft")
        pg.display.flip()

    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()

    def check_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running, self.playing = False, False
                self.curr_menu.run_display = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    self.START_KEY = True
                if event.key == pg.K_BACKSPACE:
                    self.BACK_KEY = True
                if event.key == pg.K_DOWN:
                    self.DOWN_KEY = True
                if event.key == pg.K_UP:
                    self.UP_KEY = True

    def reset_keys(self):
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY = False, False, False, False

    def draw_text(self, text, size, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        self.window.blit(text_surface, text_rect)


if __name__ == '__main__':
    # create the game object test
    g = Game()
    # p = pathSimulator()
    try:
        while g.running:
            g.curr_menu.display_menu()
            g.new()
            g.run()
            # p.path_fider()
    except:
        pass

