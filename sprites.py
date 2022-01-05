import pygame as pg
from settings import *
from pathfinding import *

vec = pg.math.Vector2

def collide_rect(one, two):  # one -> player ; two -> wall
    return one.rect.colliderect(two.rect)

def collide_with_walls(sprite, sprite_group, direction):
    if direction == 'x':
        hits = pg.sprite.spritecollide(sprite, sprite_group, False, collide_rect)
        if hits:
            if hits[0].rect.centerx > sprite.rect.centerx:
                # if moves to the right
                sprite.pos.x = hits[0].rect.left - sprite.rect.width / 2
            if hits[0].rect.centerx < sprite.rect.centerx:
                # if moves left-handed
                sprite.pos.x = hits[0].rect.right + sprite.rect.width / 2
            sprite.vel.x = 0
            sprite.rect.centerx = sprite.pos.x
    if direction == 'y':
        hits = pg.sprite.spritecollide(sprite, sprite_group, False, collide_rect)
        if hits:
            if hits[0].rect.centery > sprite.rect.centery:
                sprite.pos.y = hits[0].rect.top - sprite.rect.height / 2
            if hits[0].rect.centery < sprite.rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.rect.height / 2
            sprite.vel.y = 0
            sprite.rect.centery = sprite.pos.y


class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(CYAN)
        self.rect = self.image.get_rect()
        self.vx, self.vy = 0, 0
        self.x = x * TILESIZE
        self.y = y * TILESIZE

    def get_keys(self):
        self.vx, self.vy = 0, 0
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.vx = -PLAYER_SPEED
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.vx = PLAYER_SPEED
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.vy = -PLAYER_SPEED
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.vy = PLAYER_SPEED
        if self.vx != 0 and self.vy != 0:
            self.vx *= 0.7071
            self.vy *= 0.7071

    def collide_with_walls(self, dir):
        if dir == 'x':
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vx > 0:
                    self.x = hits[0].rect.left - self.rect.width
                if self.vx < 0:
                    self.x = hits[0].rect.right
                self.vx = 0
                self.rect.x = self.x
        if dir == 'y':
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vy > 0:
                    self.y = hits[0].rect.top - self.rect.height
                if self.vy < 0:
                    self.y = hits[0].rect.bottom
                self.vy = 0
                self.rect.y = self.y

    def update(self):
        self.get_keys()
        self.x += self.vx * self.game.dt
        self.y += self.vy * self.game.dt
        self.rect.x = self.x
        self.collide_with_walls('x')
        self.rect.y = self.y
        self.collide_with_walls('y')


class IA(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.ias
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.pos = vec(self.x, self.y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        scale = 0.9
        self.image = pg.Surface((int(TILESIZE * scale), int(TILESIZE * scale)))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(self.x, self.y))

        self.last_update = pg.time.get_ticks()
        self.g = game.g
        self.goal = vec(game.player.x // TILESIZE, game.player.y // TILESIZE)
        start = vec(self.get_tile())
        self.path, self.c = a_star_search(self.g, self.goal, start)

    def get_tile(self) -> (int, int):
        """ Returns the tile on which the sprite is located. """
        return self.x // TILESIZE, self.y // TILESIZE

    def move1(self):
        """
        The new position of the sprite becomes the next tile in the path.
        Use and update self.x and self.y
         """
        direction = self.path[self.get_tile()]
        if direction:  # if direction != None
            self.x += (direction.x * TILESIZE)
            self.y += (direction.y * TILESIZE)
        self.rect.x = self.x
        self.rect.y = self.y

    def move2(self):
        """
        The sprite moves to the center of the next tile in the path.
        Use and update self.pos and self.vel
        Is more efficient if the size of the sprite rect is less than TILESIZE.
        """
        self.vel = vec(0, 0)
        direction = self.path[self.get_tile()]
        if direction:  # if direction != None
            speed = 230
            next_tile = vec(self.get_tile()) + direction
            # target : center of the next tile
            target = vec(int(next_tile.x * TILESIZE + TILESIZE / 2), int(next_tile.y * TILESIZE + TILESIZE / 2))
            rot = (target - self.pos).angle_to(vec(1, 0))
            self.vel += vec(speed, 0).rotate(-rot)
            self.pos += self.vel * self.game.dt

        self.rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        self.x, self.y = self.pos.x, self.pos.y

    def update(self):
        now = pg.time.get_ticks()
        if (now - self.last_update) > 400:
            self.last_update = now
            self.goal = vec(self.game.player.x // TILESIZE, self.game.player.y // TILESIZE)
            start = vec(self.get_tile())
            self.path, self.c = a_star_search(self.g, self.goal, start)
            # self.move1()
        self.move2()


class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(DARKPURPLE)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

