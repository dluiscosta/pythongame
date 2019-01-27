import pygame as pg
import copy, sys
import movement as mv, character as chr, board as bd

# Manages recording
record = False # don't record by default
if len(sys.argv) > 1:
    record = sys.argv[1].lower() in ['y', 'yes', 's', 'sim', 'r', 'record', '-y', '-s', '-r']
record_path = 'recording/'
if record and len(sys.argv) > 2:
    record_path = sys.argv[2].lower()
    if record_path[-1] != '/':
        record_path = record_path + '/'
record_count = 0

# Return how many digits a number has
def count_digits(n):
    return 1 + count_digits(n%10) if n>=10 else 1

# Casts an integer to a string with n digits, filling the remainder with zeros.
def to_n_digits(x, n):
    cn = count_digits(x)
    if cn > n:
        raise Exception('Too few digits for this number.')
        return None
    else:
        return '0'*(n-cn) + str(x)

# System essentials
pg.init()
done = False #to control if the program should end
clock = pg.time.Clock()
screen = pg.display.set_mode((630, 440))
FPS = 60
mov_handler = mv.Movement()
most_recent_mov_key = None
first_mov_of_keystrike = None

# Builds dungeon tileset
cel_size = 48
dungeon_tileset = {}
for i in range(0, 100):
    img = pg.image.load('img/dungeon_tileset/dungeon_' + to_n_digits(i, 3) + '.png')
    img = pg.transform.scale(img, (cel_size, cel_size))
    dungeon_tileset[i] = img
    dungeon_tileset[-i] = img
obj_img = pg.image.load('img/dungeon_tileset/dungeon_' + to_n_digits(39, 3) + '.png')
dungeon_tileset['objective'] = pg.transform.scale(obj_img, (cel_size, cel_size))

# Builds characters
chars_sprites = []
for char_n in [1, 5]:
    char_sprites = {}
    for dir in [pg.K_UP, pg.K_RIGHT, pg.K_DOWN, pg.K_LEFT]:
        dir_str = {pg.K_UP:'up', pg.K_RIGHT:'right', pg.K_DOWN:'down', pg.K_LEFT:'left'}[dir]
        path = 'img/characters/' + str(char_n) + '/'
        idle_sprite = pg.image.load(path + dir_str + '_' + to_n_digits(2, 2) + '.png')
        moving_sprites = [pg.image.load(path + dir_str + '_' + to_n_digits(i, 2) + '.png')
                          for i in [1, 3]]
        char_sprites[dir] = {'idle':idle_sprite, 'moving':moving_sprites}
    chars_sprites.append(char_sprites)
char_offset = (-(52-cel_size)/2,-(72-12-cel_size/2))

char1_pos = (1, 3)
char1 = chr.Character(chars_sprites[0], char_offset, mov_handler)
char2_pos = (1, 1)
char2 = chr.Character(chars_sprites[1], char_offset, mov_handler)
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
boards = [bd.Board(5, 5, [(char1, char1_pos)], [obj1], field1),
          bd.Board(5, 5, [(char2, char2_pos)], [obj2], field2)]

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
    boards[0].draw(screen, 50, 50, cel_size, dungeon_tileset)
    boards[1].draw(screen, 340, 50, cel_size, dungeon_tileset)

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

    # Records frame, if specified
    if record and record_count < 1000:
        pg.image.save(screen, record_path + to_n_digits(record_count, 3) + '.png')
        record_count += 1

    pg.display.flip() #flips buffers, updating screen
    clock.tick(60) #waits for the time assigned for a frame
