import pygame as pg
import copy
import movement as mv, character as chr, board as bd
import pickle
import aux

# System essentials
pg.init()
done = False #to control if the program should end
clock = pg.time.Clock()
screen = pg.display.set_mode((630, 440))
FPS = 60
mov_handler = mv.Movement()
most_recent_mov_key = None
first_mov_of_keystrike = None
cel_size = 48

# Builds boards tileset
bd.Board.build_tileset('dungeon', cel_size)

# Builds all characters
chr.Character.generate_characters(cel_size, mov_handler)

# Load data from level
with open('levels/01.p', 'rb') as file:
    level = pickle.load(file)

# Builds boards
boards = [bd.Board(*param) for param in level]

# Get all characters being used
characters = chr.Character.get_used_characters()

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
    boards[0].draw(screen, 50, 50, cel_size)
    boards[1].draw(screen, 340, 50, cel_size)

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
