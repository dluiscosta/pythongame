import pygame as pg
import numpy as np
import aux

class Character:
    @classmethod
    def generate_characters(cls, cel_size, mov_handler):
        # Builds characters
        cls.chars = []
        chars_to_use = range(1, 9)
        char_offset = (-(0.1*cel_size)/2,-(0.75*cel_size))
        for char_n in chars_to_use:
            char_sprites = {}
            for dir in [pg.K_UP, pg.K_RIGHT, pg.K_DOWN, pg.K_LEFT]:
                dir_str = {pg.K_UP:'up', pg.K_RIGHT:'right', pg.K_DOWN:'down', pg.K_LEFT:'left'}[dir]
                path = 'img/characters/' + str(char_n) + '/'
                idle_sprite = pg.image.load(path + dir_str + '_' + aux.to_n_digits(2, 2) + '.png')
                idle_sprite = pg.transform.scale(idle_sprite,
                                                 (int(1.1*cel_size), int(1.5*cel_size)))
                moving_sprites = [pg.image.load(path + dir_str + '_' + aux.to_n_digits(i, 2) + '.png')
                                  for i in [1, 3]]
                moving_sprites = [pg.transform.scale(sprite,
                                                     (int(1.1*cel_size), int(1.5*cel_size)))
                                  for sprite in moving_sprites]
                char_sprites[dir] = {'idle':idle_sprite, 'moving':moving_sprites}
            cls.chars.append(Character(char_sprites, char_offset, mov_handler))

    @classmethod
    def get_free_characters(cls, n):
        free_characters = [char for char in cls.chars if char.board is None]
        if n > len(free_characters):
            raise Exception('Not enough available characters.')
        else:
            return np.random.choice(free_characters, n, replace=False)

    @classmethod
    def get_used_characters(cls):
        return [char for char in cls.chars if char.board is not None]

    def __init__(self, sprites, draw_offset = (0, 0), mov_handler = None):
        self.position = None
        self.board = None
        self.sprites = sprites
        self.draw_offset = draw_offset
        self.facing = pg.K_DOWN
        self.been_moving = 0 #frames
        self.mov_handler = mov_handler

    # Check if the position in the given direction can be occupied by the character
    def can_move_dir(self, direction):
        if self.board == None:
            raise Exception("Can't move if not on a board.")

        if direction == pg.K_UP:
            return self.board.can_occupy(self.position[0], self.position[1]-1)
        elif direction == pg.K_DOWN:
            return self.board.can_occupy(self.position[0], self.position[1]+1)
        elif direction == pg.K_LEFT:
            return self.board.can_occupy(self.position[0]-1, self.position[1])
        elif direction == pg.K_RIGHT:
            return self.board.can_occupy(self.position[0]+1, self.position[1])
        else:
            raise Exception("Invalid direction.")

    # Updates the character position, if possible
    def move_char(self, direction):
        if self.can_move_dir(direction):
            new_position = list(self.position)
            if direction == pg.K_UP: new_position[1] -= 1
            elif direction == pg.K_DOWN: new_position[1] += 1
            elif direction == pg.K_LEFT: new_position[0] -= 1
            elif direction == pg.K_RIGHT: new_position[0] += 1
            self.position = tuple(new_position)

    def at_objective(self):
        return self.position in self.board.objectives_pos


    def am_moving(self):
        return self.mov_handler.is_moving() and self.can_move_dir(self.mov_handler.get_direction())

    def draw(self, screen, start_x, start_y, cel_size):
        dx, dy = (0, 0) #delta from current movement
        img = self.sprites[self.facing]['idle']
        if self.am_moving():
            self.facing = self.mov_handler.get_direction()

            # Calculates distance already walked between two cells
            distance_covered = int(((cel_size/self.mov_handler.get_move_steps()) *
                                    self.mov_handler.get_steps_taken()))
            dx, dy = {pg.K_UP:(0,-distance_covered),
                      pg.K_DOWN:(0,+distance_covered),
                      pg.K_LEFT:(-distance_covered,0),
                      pg.K_RIGHT:(+distance_covered,0)}[self.facing]

            # Gets moving sprite
            msf = self.mov_handler.get_moving_sprite_frames()
            moving_frames = self.sprites[self.facing]['moving']
            frame_idx = int(self.been_moving/msf)%len(moving_frames)
            img = moving_frames[frame_idx]
            self.been_moving += 1
        else:
            # Restarts moving frames counter
            self.been_moving = 0

        offset_x, offset_y = self.draw_offset
        c_x = start_x + dx + offset_x
        c_y = start_y + dy + offset_y
        screen.blit(img, (c_x, c_y)) #draws the character
