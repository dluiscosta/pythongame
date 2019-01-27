import pygame as pg
import copy

# System essentials
pg.init()
done = False #to control if the program should end
clock = pg.time.Clock()
screen = pg.display.set_mode((630, 440))
FPS = 60



class Movement: #control class
    def __init__(self, move_steps=16, beginning_mov_parcel=0, moving_sprite_frames=20):
        self.move_steps = move_steps # frames required for each movement

        # Size of the beginning parcel (in frames) in which a movement can still
        # be cancelled
        self.beginning_mov_parcel = beginning_mov_parcel

        # During movement, the amount of frames that will exhibit the same image
        # before using the next on the sprite
        self.moving_sprite_frames = moving_sprite_frames

        self.moving = False #characters start idle
        self.direction = None
        self.steps_taken = 0 #in a single movement between two cells

        # First movement between 2 cells caused by a single keystrike
        self.first_mov = None

    def get_direction(self):
        return self.direction if self.is_moving() else None

    def is_moving(self):
        return self.moving

    def get_steps_taken(self):
        return self.steps_taken if self.is_moving() else None

    def get_move_steps(self):
        return self.move_steps if self.is_moving() else None

    def get_moving_sprite_frames(self):
        return self.moving_sprite_frames

    # If the movement is still at the beginning cancellable parcel (specified by
    # beginning_mov_parcel), cancel it
    def attempt_cancel(self):
        if (not self.first_mov and
            self.get_steps_taken() < self.beginning_mov_parcel):
            self.moving = False

    # Try to start a movement in a given direction
    def attempt_movement(self, dir, first=False):
        if (not self.is_moving() or
            self.attempt_cancel()): #can interrupt movements that have just started
            self.direction = dir
            self.steps_taken = 0
            self.moving = True
            self.first_mov = first

    # Passes one frame, taking a step or finishing the movement if it's complete
    def continue_movement(self, characters):
        if self.get_steps_taken() == self.move_steps: #finishes movement
            for character in characters:
                character.move_char(self.direction)
            self.moving = False
            self.first_mov = False
            return False
        else: #continue movement
            if self.is_moving():
                self.steps_taken += 1
            return True



class Character:
    def __init__(self, sprites, draw_offset = (0, 0)):
        self.position = None
        self.board = None
        self.sprites = sprites
        self.draw_offset = draw_offset
        self.facing = pg.K_DOWN
        self.been_moving = 0 #frames

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
        return mov_handler.is_moving() and self.can_move_dir(mov_handler.get_direction())

    def draw(self, start_x, start_y):
        dx, dy = (0, 0) #delta from current movement
        img = self.sprites[self.facing]['idle']
        if self.am_moving():
            self.facing = mov_handler.get_direction()

            # Calculates distance already walked between two cells
            distance_covered = int(((cel_size/mov_handler.get_move_steps()) *
                                    mov_handler.get_steps_taken()))
            dx, dy = {pg.K_UP:(0,-distance_covered),
                      pg.K_DOWN:(0,+distance_covered),
                      pg.K_LEFT:(-distance_covered,0),
                      pg.K_RIGHT:(+distance_covered,0)}[self.facing]

            # Gets moving sprite
            msf = mov_handler.get_moving_sprite_frames()
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



class Board:
    def __init__(self, cols, rows, characters_and_pos=[], objs_pos=[], field=None):
        self.size = (cols, rows)

        if field is None: #field not provided, initializes new empty field
            self.field = [[None for x in range(0, cols)] for y in range(0, rows)]
        else: #field provided, checks if it's valid
            if len(field) != rows or any([len(row) != cols for row in field]):
                raise Exception("Invalid field.")
            else:
                self.field = field

        # Places given characters
        self.characters = []
        for character_and_pos in characters_and_pos:
            self.place_character(*character_and_pos)

        # Checks validity of provided objective position
        self.objectives_pos = []
        for obj_pos in objs_pos:
            if (not isinstance(obj_pos, tuple) or len(obj_pos) != 2 or
                not self.valid_pos(*obj_pos)):
                raise Exception("Invalid objective position.")
            elif self.field_at(*obj_pos) > 0:
                raise Exception("Objective placed in obstacle or wall.")
            else:
                self.objectives_pos.append(obj_pos)

    # First place character at given position
    def place_character(self, character, position):
        if (not isinstance(position, tuple) or len(position) != 2
            or not self.valid_pos(*position)):
            raise Exception("Invalid position given for character.")
        elif not self.can_occupy(*position):
            raise Exception("Character can't occupy position.")

        character.board = self
        character.position = position
        self.characters.append(character)

    # Access field at given position
    def field_at(self, x, y):
        if self.valid_pos(x, y):
            return self.field[y][x]
        else:
            raise Exception("Trying to access invalid field position.")

    # Check if the (x,y) position is inside field
    def valid_pos(self, x, y):
        return (0 <= x < self.size[0] and 0 <= y < self.size[1])

    # Check if the (x,y) position can be occupied by the character
    def can_occupy(self, x, y):
        return (self.valid_pos(x, y) and self.field_at(x, y) < 0)

    # Returns an index following the order top-right-down-left
    def dir_to_idx(self, direction):
        return {pg.K_UP: 0, pg.K_RIGHT: 1, pg.K_DOWN: 2, pg.K_LEFT: 3}[direction]

    # Draws the board and the character, idle or moving (if possible for this board)
    def draw(self, start_x, start_y, cel_size, tileset):
        if (start_x < 0 or start_y < 0 or
            (start_x + cel_size*self.size[0]) > screen.get_size()[0] or
            (start_y + cel_size*self.size[1]) > screen.get_size()[1]):
           raise Exception("Board can't fit window screen.")

        # Draws tiles
        for t_x in range(0, self.size[0]):
            for t_y in range(0, self.size[1]):
                # Checks the tile type of the 8 neighboors, None if end of Board
                img = tileset[self.field_at(t_x, t_y)] #access the tileset
                screen.blit(img, (start_x + t_x*cel_size, start_y + t_y*cel_size)) #draws the tile

        # Draws objective
        for objective_pos in self.objectives_pos:
            ox = start_x + objective_pos[0]*cel_size
            oy = start_y + objective_pos[1]*cel_size
            screen.blit(tileset['objective'], (ox, oy)) #draws the tile

        # Draws "character"
        for character in self.characters:
            character.draw(start_x + character.position[0]*cel_size,
                           start_y + character.position[1]*cel_size)


def two_digits(n):
    if n < 10:
        return '0' + str(n)
    else:
        return str(n)

def three_digits(n):
    if n < 10:
        return '00' + str(n)
    elif n < 100:
        return '0' + str(n)
    else:
        return str(n)

# Builds dungeon tileset
cel_size = 48
dungeon_tileset = {}
for i in range(0, 100):
    img = pg.image.load('img/dungeon_tileset/dungeon_' + three_digits(i) + '.png')
    img = pg.transform.scale(img, (cel_size, cel_size))
    dungeon_tileset[i] = img
    dungeon_tileset[-i] = img
obj_img = pg.image.load('img/dungeon_tileset/dungeon_' + three_digits(39) + '.png')
dungeon_tileset['objective'] = pg.transform.scale(obj_img, (cel_size, cel_size))

# Builds character
chars_sprites = []
for char_n in [1, 5]:
    char_sprites = {}
    for dir in [pg.K_UP, pg.K_RIGHT, pg.K_DOWN, pg.K_LEFT]:
        dir_str = {pg.K_UP:'up', pg.K_RIGHT:'right', pg.K_DOWN:'down', pg.K_LEFT:'left'}[dir]
        path = 'img/characters/' + str(char_n) + '/'
        idle_sprite = pg.image.load(path + dir_str + '_' + two_digits(2) + '.png')
        moving_sprites = [pg.image.load(path + dir_str + '_' + two_digits(i) + '.png')
                          for i in [1, 3]]
        char_sprites[dir] = {'idle':idle_sprite, 'moving':moving_sprites}
    chars_sprites.append(char_sprites)
char_offset = (-(52-cel_size)/2,-(72-12-cel_size/2))


char1_pos = (1, 3)
char1 = Character(chars_sprites[0], char_offset)
char2_pos = (1, 1)
char2 = Character(chars_sprites[1], char_offset)
characters = [char1, char2]

# Builds boards
field1 = [[  0,  1,  2,  4,  5],
          [ 10,-22,-22,-22, 15],
          [ 20,-22, 50, 51, 45],
          [ 30,-22, 15, 78, 78],
          [ 40, 41, 45, 78, 78]]
obj1 = (3, 1)
field2 = [[  0,  1,  5, 78, 78],
          [ 10,-22, 15, 78, 78],
          [ 20,-22,  1,  2,  5],
          [ 30,-22,-22,-22, 35],
          [ 40, 41, 42, 44, 45]]
obj2 = (3, 3)
boards = [Board(5, 5, [(char1, char1_pos)], [obj1], field1),
          Board(5, 5, [(char2, char2_pos)], [obj2], field2)]

mov_handler = Movement()
most_recent_mov_key = None
first_mov_of_keystrike = None

# Main loop
while not done:
    for event in pg.event.get():
        if event.type == pg.QUIT: #close screen command
            done = True
        if event.type == pg.KEYDOWN and event.key in [pg.K_UP, pg.K_DOWN, pg.K_LEFT, pg.K_RIGHT]:
            most_recent_mov_key = event.key
            first_mov_of_keystrike = True

    twice = 1 #executes again if ends not moving after first iteration
    while twice == 1 or (twice == 2 and not mov_handler.is_moving()):
        twice += 1

        pressed = pg.key.get_pressed()

        # Attempts to start a movement
        # gives precedence to the most recently pressed key.
        if (most_recent_mov_key is not None and pressed[most_recent_mov_key] and
            (not mov_handler.is_moving() or
             mov_handler.get_direction() != most_recent_mov_key)):
            if any([c.can_move_dir(most_recent_mov_key) for c in characters]):
                mov_handler.attempt_movement(most_recent_mov_key, first=first_mov_of_keystrike)

        # If the key was released, cancels movement if there is still time
        if mov_handler.is_moving() and not pressed[mov_handler.get_direction()]:
            mov_handler.attempt_cancel()

        if mov_handler.is_moving():
            first_mov_of_keystrike = mov_handler.continue_movement(characters)

    # Draws screen and boards
    screen.fill((37, 19, 26))
    boards[0].draw(50, 50, cel_size, dungeon_tileset)
    boards[1].draw(340, 50, cel_size, dungeon_tileset)

    # Detects achievement of goal (all objectives)
    if all([char.at_objective() for char in characters]):
        # Draws green rectangle
        pg.draw.rect(screen, (0, 66, 37), pg.Rect(50, 340, 530, 50))
        # Writes 'THE END' centered at rectangle
        pg.font.init()
        myfont = pg.font.SysFont('Verdana', 30, bold=True)
        textsurface = myfont.render('THE END', False, (255, 255, 255))
        w, h = textsurface.get_size()
        screen.blit(textsurface, (50 + 530/2 - w/2, 340 + 50/2 - h/2))

    pg.display.flip() #flips buffers, updating screen
    clock.tick(60) #waits for the time assigned for a frame
