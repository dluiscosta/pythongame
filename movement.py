import pygame as pg

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
