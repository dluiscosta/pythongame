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
    def __init__(self, cols, rows, field = None, char = (0, 0)):
        self.size = (cols, rows)

        if field is None: #field not provided, initializes new empty field
            field = [[None for x in range(0, cols)] for y in range(0, rows)]
        else: #field provided, checks if it's valid
            if len(field) != rows or any([len(row) != cols for row in field]):
                raise Exception("Invalid field.")
        self.field = field

        self.char = char

    # Check if the (x,y) position can be occupied by the character
    def can_move(self, x, y):
        return (0 <= x < self.size[0] and 0 <= y < self.size[1] and
                self.field[y][x] <= 2)

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
    def draw(self, start_x, start_y, cel_size, moving):
        if (start_x < 0 or start_y < 0 or
            (start_x + cel_size*self.size[0]) > screen.get_size()[0] or
            (start_y + cel_size*self.size[1]) > screen.get_size()[1]):
           raise Exception("Board can't fit window screen.")

        # Draws grid background, only on transponable cells
        #pg.draw.rect(screen, (30, 0, 0),
        #    pg.Rect(start_x, start_y, self.size[0]*cel_size, self.size[1]*cel_size))
        for g_x in range(0, self.size[0]):
            for g_y in range(0, self.size[1]):
                if self.field[g_y][g_x] <= 2:
                    color = (60, 0, 0)
                    if (g_x+g_y)%2 == 0:
                        color = (100, 0, 0)
                    pg.draw.rect(screen, color,
                        pg.Rect(start_x + g_x*cel_size, start_y + g_y*cel_size,
                                cel_size, cel_size))

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

field1 = [[0, 0, 2],
          [0, 3, 3],
          [1, 3, 3]]

field2 = [[2, 3, 3],
          [0, 3, 3],
          [0, 0, 1]]

boards = [Board(3, 3, field1, (0,2)), Board(3, 3, field2, (2,2))]

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
    boards[0].draw(50, 50, 20, moving)
    boards[1].draw(550, 50, 20, moving)

    pg.display.flip() #flips buffers, updating screen
    clock.tick(60) #waits for the time assigned for a frame
