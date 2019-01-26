import pygame as pg
import copy

# System essentials
pg.init()
done = False #to control if the program should end
clock = pg.time.Clock()
screen = pg.display.set_mode((630, 440))
FPS = 60

# Movement auxiliars
moving = False #characters start idle
most_recent_mov_key = None
first_mov = False
move_steps = 16 #frames required for each movement
beginning_mov_parcel = 3 #size (1/x %) of the beginning parcel in which a movement it can still be cancelled
moving_sprite_frames = 20 #during movement, the amount of frames that will exhibit the same image before using the next on the sprite


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
            if moving[0] == pg.K_UP: new_position[1] -= 1
            elif moving[0] == pg.K_DOWN: new_position[1] += 1
            elif moving[0] == pg.K_LEFT: new_position[0] -= 1
            elif moving[0] == pg.K_RIGHT: new_position[0] += 1
            self.position = tuple(new_position)

    def at_objective(self):
        return self.position in self.board.objectives_pos

    def draw(self, start_x, start_y):
        dx, dy = (0, 0) #delta from current movement
        img = self.sprites[self.facing]['idle']
        if moving:
            self.facing = moving[0]
            distance_covered = int((cel_size/move_steps) * moving[1][0])
            if moving[0] == pg.K_UP and self.can_move_dir(pg.K_UP):
                dy = - distance_covered
            elif moving[0] == pg.K_DOWN and self.can_move_dir(pg.K_DOWN):
                dy = + distance_covered
            elif moving[0] == pg.K_LEFT and self.can_move_dir(pg.K_LEFT):
                dx = - distance_covered
            elif moving[0] == pg.K_RIGHT and self.can_move_dir(pg.K_RIGHT):
                dx = + distance_covered

            # Gets moving sprite
            moving_frame = int(self.been_moving/moving_sprite_frames)%len(self.sprites[moving[0]]['moving'])
            img = self.sprites[moving[0]]['moving'][moving_frame]
            self.been_moving += 1
        else:
            # Restarts moving frames counter
            self.been_moving = 0

        offset_x, offset_y = self.draw_offset
        c_x = start_x + dx + offset_x
        c_y = start_y + dy + offset_y
        screen.blit(img, (c_x, c_y)) #draws the tile
        # r = int(cel_size/2)
        # pg.draw.circle(screen, (255, 0, 0), (cx+r, cy+r), r)


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
    def draw(self, start_x, start_y, cel_size, moving, tileset):
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
for char_n in [1, 2]:
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



# Main loop
while not done:
    for event in pg.event.get():
        if event.type == pg.QUIT: #close screen command
            done = True
        if event.type == pg.KEYDOWN and event.key in [pg.K_UP, pg.K_DOWN, pg.K_LEFT, pg.K_RIGHT]:
            most_recent_mov_key = event.key
            first_mov = True

    twice = 1 #executes again if ends not moving after first iteration
    while twice == 1 or (twice == 2 and not moving):
        twice += 1

        # Starts a movement
        # gives precedence to the most recently pressed key.
        if (not moving or
            (moving and moving[0] != most_recent_mov_key and
             moving[1][0] < move_steps/beginning_mov_parcel)):
             #can interrupt movements that have just started
            pressed = pg.key.get_pressed()

            #moving = (direction, steps taken)
            if pressed[pg.K_UP] and most_recent_mov_key == pg.K_UP:
                if any([character.can_move_dir(pg.K_UP) for character in characters]):
                    moving = (pg.K_UP, [0])
            elif pressed[pg.K_DOWN] and most_recent_mov_key == pg.K_DOWN:
                if any([character.can_move_dir(pg.K_DOWN) for character in characters]):
                    moving = (pg.K_DOWN, [0])
            elif pressed[pg.K_LEFT] and most_recent_mov_key == pg.K_LEFT:
                if any([character.can_move_dir(pg.K_LEFT) for character in characters]):
                    moving = (pg.K_LEFT, [0])
            elif pressed[pg.K_RIGHT] and most_recent_mov_key == pg.K_RIGHT:
                if any([character.can_move_dir(pg.K_RIGHT) for character in characters]):
                    moving = (pg.K_RIGHT, [0])

        # Continues or finishes a movement
        if moving:
            if moving[1][0] == move_steps: #finishes
                # Updates the characters positions
                for character in characters:
                    character.move_char(moving[0])
                first_mov = False
                moving = False
            else: #continues
                if not first_mov and moving[1][0] < move_steps/beginning_mov_parcel:
                    #if it's in the beginning, checks if key still pressed
                    pressed = pg.key.get_pressed()
                    if not pressed[moving[0]]:
                        moving = False # cancels movement
                if moving:
                    moving[1][0] += 1 #takes one more step in defined direction

    # Draws screen and boards
    screen.fill((37, 19, 26))
    boards[0].draw(50, 50, cel_size, moving, dungeon_tileset)
    boards[1].draw(340, 50, cel_size, moving, dungeon_tileset)

    if all([char.at_objective() for char in characters]):
        pg.draw.rect(screen, (0, 255, 0), pg.Rect(50, 340, 530, 50))

    pg.display.flip() #flips buffers, updating screen
    clock.tick(60) #waits for the time assigned for a frame
