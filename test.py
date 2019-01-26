import pygame as pg

# System essentials
pg.init()
done = False #to control if the program should end
clock = pg.time.Clock()
screen = pg.display.set_mode((1000, 500))

# Movement auxiliars
moving = False #characters start idle
most_recent_mov_key = None
first_mov = False
move_steps = 20 #frames required for each movement
beginning_mov_parcel = 3 #size (1/x %) of the beginning parcel in which a movement it can still be cancelled

class Board:
    def __init__(self, cols, rows, char, obj, field = None):
        self.size = (cols, rows)

        if field is None: #field not provided, initializes new empty field
            self.field = [[None for x in range(0, cols)] for y in range(0, rows)]
        else: #field provided, checks if it's valid
            if len(field) != rows or any([len(row) != cols for row in field]):
                raise Exception("Invalid field.")
            else:
                self.field = field

        # Checks validity of provided character position
        if (not isinstance(char, tuple) or len(char) != 2 or
            not self.valid_pos(*char)):
            raise Exception("Invalid character position.")
        elif self.field_at(*char) > 0:
            raise Exception("Character placed in obstacle or wall.")
        else:
            self.char = char

        # Checks validity of provided objective position
        if (not isinstance(obj, tuple) or len(obj) != 2 or
            not self.valid_pos(*obj)):
            raise Exception("Invalid objective position.")
        elif self.field_at(*obj) > 0:
            raise Exception("Objective placed in obstacle or wall.")
        else:
            self.obj = obj

    # Access field at given position
    def field_at(self, x, y):
        return self.field[y][x]

    # Check if the (x,y) position is inside field
    def valid_pos(self, x, y):
        return (0 <= x < self.size[0] and 0 <= y < self.size[1])

    # Check if the (x,y) position can be occupied by the character
    def can_move(self, x, y):
        return (self.valid_pos(x, y) and self.field_at(x, y) < 0)

    # Check if the position in the given direction can be occupied by the character
    def can_move_dir(self, direction):
        if direction == pg.K_UP:
            return self.can_move(self.char[0], self.char[1]-1)
        elif direction == pg.K_DOWN:
            return self.can_move(self.char[0], self.char[1]+1)
        elif direction == pg.K_LEFT:
            return self.can_move(self.char[0]-1, self.char[1])
        elif direction == pg.K_RIGHT:
            return self.can_move(self.char[0]+1, self.char[1])
        else:
            raise Exception("Invalid direction.")

    # Updates the character position, if possible
    def move_char(self, direction):
        new_pos = list(self.char)
        if moving[0] == pg.K_UP: new_pos[1] -= 1
        elif moving[0] == pg.K_DOWN: new_pos[1] += 1
        elif moving[0] == pg.K_LEFT: new_pos[0] -= 1
        elif moving[0] == pg.K_RIGHT: new_pos[0] += 1
        if self.can_move(*new_pos):
            self.char = new_pos

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
        ox = start_x + self.obj[0]*cel_size
        oy = start_y + self.obj[1]*cel_size
        pg.draw.rect(screen, (0, 255, 0), pg.Rect(ox, oy, cel_size, cel_size))


        # Draws "character"
        dx, dy = (0, 0) #delta from current movement
        if moving:
            distance_covered = int((cel_size/move_steps) * moving[1][0])
            if moving[0] == pg.K_UP and self.can_move(self.char[0], self.char[1]-1):
                dy = - distance_covered
            elif moving[0] == pg.K_DOWN and self.can_move(self.char[0], self.char[1]+1):
                dy = + distance_covered
            elif moving[0] == pg.K_LEFT and self.can_move(self.char[0]-1, self.char[1]):
                dx = - distance_covered
            elif moving[0] == pg.K_RIGHT and self.can_move(self.char[0]+1, self.char[1]):
                dx = + distance_covered
        cx = start_x + self.char[0]*cel_size + dx
        cy = start_y + self.char[1]*cel_size + dy
        r = int(cel_size/2)
        pg.draw.circle(screen, (255, 0, 0), (cx+r, cy+r), r)
        #pg.draw.rect(screen, (255, 0, 0), pg.Rect(cx, cy, cel_size, cel_size))


field1 = [[  0,  1,  2,  4,  5],
          [ 10,-22,-22,-22, 15],
          [ 20,-22, 50, 51, 45],
          [ 30,-22, 15, 78, 78],
          [ 40, 41, 45, 78, 78]]
char1 = (1, 3)
obj1 = (3, 1)

field2 = [[-1,  1,  1],
          [-1,  1,  1],
          [-1, -1, -1]]
char2 = (2, 2)
obj2 = (0, 0)

boards = [Board(5, 5, char1, obj1, field1), Board(3, 3, char2, obj2, field2)]

dungeon_tileset = {}
def three_digits(n):
    if n < 10:
        return '00' + str(n)
    elif n < 100:
        return '0' + str(n)
    else:
        return str(n)

for i in range(0, 100):
    img = pg.image.load('img/dungeon_tileset/dungeon_' + three_digits(i) + '.png')
    dungeon_tileset[i] = img
    dungeon_tileset[-i] = img

# Main loop
while not done:
    for event in pg.event.get():
        if event.type == pg.QUIT: #close screen command
            done = True
        if event.type == pg.KEYDOWN and event.key in [pg.K_UP, pg.K_DOWN, pg.K_LEFT, pg.K_RIGHT]:
            most_recent_mov_key = event.key
            first_mov = True

    # Starts a movement
    # gives precedence to the most recently pressed key.
    if (not moving or
        (moving and moving[0] != most_recent_mov_key and moving[1][0] < move_steps/beginning_mov_parcel)): #can interrupt movements that have just started
        pressed = pg.key.get_pressed()

        #moving = (direction, steps taken)
        if pressed[pg.K_UP] and most_recent_mov_key == pg.K_UP:
            if any([board.can_move_dir(pg.K_UP) for board in boards]):
                moving = (pg.K_UP, [0])
        elif pressed[pg.K_DOWN] and most_recent_mov_key == pg.K_DOWN:
            if any([board.can_move_dir(pg.K_DOWN) for board in boards]):
                moving = (pg.K_DOWN, [0])
        elif pressed[pg.K_LEFT] and most_recent_mov_key == pg.K_LEFT:
            if any([board.can_move_dir(pg.K_LEFT) for board in boards]):
                moving = (pg.K_LEFT, [0])
        elif pressed[pg.K_RIGHT] and most_recent_mov_key == pg.K_RIGHT:
            if any([board.can_move_dir(pg.K_RIGHT) for board in boards]):
                moving = (pg.K_RIGHT, [0])

    # Continues or finishes a movement
    if moving:
        if moving[1][0] == move_steps: #finishes
            # Updates the characters positions
            for board in boards:
                board.move_char(moving[0])
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
    screen.fill((0, 0, 0))
    boards[0].draw(50, 50, 16, moving, dungeon_tileset)
    boards[1].draw(550, 50, 16, moving, dungeon_tileset)

    pg.display.flip() #flips buffers, updating screen
    clock.tick(60) #waits for the time assigned for a frame
