import pygame as pg

# Parameters
grid_size = (20, 15)
cel_size = 40
move_steps = 20 #frames required for each movement

# System essentials
pg.init()
done = False #to control if the program should end
clock = pg.time.Clock()
screen = pg.display.set_mode(
            (grid_size[0]*cel_size, grid_size[1]*cel_size))

# Setup character
x, y = (10, 10) #initial position on the grid system
moving = False #character starts idle

most_recent_mov_key = None
def can_move(x, y):
    return 0 <= x < grid_size[0] and 0 <= y < grid_size[1]

# Main loop
while not done:
    for event in pg.event.get():
        if event.type == pg.QUIT: #close screen command
            done = True
        if event.type == pg.KEYDOWN and event.key in [pg.K_UP, pg.K_DOWN, pg.K_LEFT, pg.K_RIGHT]:
            most_recent_mov_key = event.key;


    d_x, d_y = (x*cel_size, y*cel_size) #display position, can be between cells during movement

    # Starts a movement
    # gives precedence to the most recently pressed key.
    if (not moving or
        (moving and moving[0] != most_recent_mov_key and moving[1][0] < move_steps/4)): #can interrupt movements that have just started
        pressed = pg.key.get_pressed()

        #moving = (direction, steps taken)
        if pressed[pg.K_UP] and most_recent_mov_key == pg.K_UP and can_move(x, y-1):
            moving = (pg.K_UP, [0])
        elif pressed[pg.K_DOWN] and most_recent_mov_key == pg.K_DOWN and can_move(x, y+1):
            moving = (pg.K_DOWN, [0])
        elif pressed[pg.K_LEFT] and most_recent_mov_key == pg.K_LEFT and can_move(x-1, y):
            moving = (pg.K_LEFT, [0])
        elif pressed[pg.K_RIGHT] and most_recent_mov_key == pg.K_RIGHT and can_move(x+1, y):
            moving = (pg.K_RIGHT, [0])

    # Continues or finishes a movement
    if moving:
        if moving[1][0] == move_steps: #finishes
            # Updates the grid position
            if moving[0] == pg.K_UP: y -= 1
            elif moving[0] == pg.K_DOWN: y += 1
            elif moving[0] == pg.K_LEFT: x -= 1
            elif moving[0] == pg.K_RIGHT: x += 1
            d_x, d_y = (x*cel_size, y*cel_size) #recalc display position
            moving = False
        else: #continues
            moving[1][0] += 1 #takes one more step in defined direction
            # Calculates display position
            distance_covered = int((cel_size/move_steps) * moving[1][0])
            if moving[0] == pg.K_UP: d_y = y*cel_size - distance_covered
            elif moving[0] == pg.K_DOWN: d_y = y*cel_size + distance_covered
            elif moving[0] == pg.K_LEFT: d_x = x*cel_size - distance_covered
            elif moving[0] == pg.K_RIGHT: d_x = x*cel_size + distance_covered

    # Draws grid background
    screen.fill((0, 0, 0))
    for g_x in range(0, grid_size[0]):
        for g_y in range(0, grid_size[1]):
            if (g_x+g_y)%2 == 0:
                pg.draw.rect(screen, (40, 0, 0),
                    pg.Rect(g_x*cel_size, g_y*cel_size, cel_size, cel_size))

    # Draws "character"
    pg.draw.rect(screen, (255, 0, 0), pg.Rect(d_x, d_y, cel_size, cel_size))

    pg.display.flip() #flips buffers, updating screen
    clock.tick(60) #waits for the time assigned for a frame
