import pygame as pg
import character as chr
import aux

class Board:
    @classmethod
    def build_tileset(cls, name, cel_size):
        dungeon_tileset = {}
        for i in range(0, 100):
            img = pg.image.load('img/' + name + '_tileset/' + name + '_' + aux.to_n_digits(i, 3) + '.png')
            img = pg.transform.scale(img, (cel_size, cel_size))
            dungeon_tileset[i] = img
            dungeon_tileset[-i] = img
        obj_img = pg.image.load('img/' + name + '_tileset/' + name + '_' + aux.to_n_digits(39, 3) + '.png')
        dungeon_tileset['objective'] = pg.transform.scale(obj_img, (cel_size, cel_size))
        cls.tileset = dungeon_tileset

    def __init__(self, cols, rows, characters_pos=[], objs_pos=[], field=None):
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
        for character_pos in characters_pos:
            char = chr.Character.get_free_characters(1)[0]
            self.place_character(char, character_pos)

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
    def draw(self, screen, start_x, start_y, cel_size):
        tileset = Board.tileset

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
            character.draw(screen,
                           start_x + character.position[0]*cel_size,
                           start_y + character.position[1]*cel_size,
                           cel_size)
