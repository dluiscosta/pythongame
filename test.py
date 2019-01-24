import pygame

# Parameters
grid_size = (20, 15)
cel_size = 25
move_steps = 10 #frames required for each movement

# System essentials
pygame.init()
done = False #to control if the program should end
clock = pygame.time.Clock()
screen = pygame.display.set_mode(
            (grid_size[0]*cel_size, grid_size[1]*cel_size))

# Setup character
x, y = (10, 10) #initial position on the grid system
moving = False #character starts idle

# Main loop
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: #close screen command
            done = True

    d_x, d_y = (x*cel_size, y*cel_size) #display position, can be between cells during movement

    # Starts a movement
    if not moving:
        pressed = pygame.key.get_pressed()
        #moving = (direction, steps taken)
        if pressed[pygame.K_UP]: moving = ("up", [0])
        elif pressed[pygame.K_DOWN]: moving = ("down", [0])
        elif pressed[pygame.K_LEFT]: moving = ("left", [0])
        elif pressed[pygame.K_RIGHT]: moving = ("right", [0])

    # Continues or finishes a movement
    if moving:
        if moving[1][0] == move_steps: #finishes
            # Updates the grid position
            if moving[0] == "up": y -= 1
            elif moving[0] == "down": y += 1
            elif moving[0] == "left": x -= 1
            elif moving[0] == "right": x += 1
            d_x, d_y = (x*cel_size, y*cel_size) #recalc display position
            moving = False
        else: #continues
            moving[1][0] += 1 #takes one more step in defined direction
            # Calculates display position
            distance_covered = int((cel_size/move_steps) * moving[1][0])
            if moving[0] == "up": d_y = y*cel_size - distance_covered
            elif moving[0] == "down": d_y = y*cel_size + distance_covered
            elif moving[0] == "left": d_x = x*cel_size - distance_covered
            elif moving[0] == "right": d_x = x*cel_size + distance_covered

    # Draws grid background
    screen.fill((0, 0, 0))
    for g_x in range(0, grid_size[0]):
        for g_y in range(0, grid_size[1]):
            if (g_x+g_y)%2 == 0:
                pygame.draw.rect(screen, (40, 0, 0),
                    pygame.Rect(g_x*cel_size, g_y*cel_size, cel_size, cel_size))

    # Draws "character"
    pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(d_x, d_y, cel_size, cel_size))

    pygame.display.flip() #flips buffers, updating screen
    clock.tick(60) #waits for the time assigned for a frame
