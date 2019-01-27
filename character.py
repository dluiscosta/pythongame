import pygame as pg

class Character:
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
