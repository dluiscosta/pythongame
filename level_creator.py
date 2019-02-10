import pickle

char1_pos = (1, 3)
char2_pos = (1, 1)
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
level = [(5, 5, [char1_pos], [obj1], field1),
         (5, 5, [char2_pos], [obj2], field2)]

with open('levels/01.p', 'wb') as file:
    pickle.dump(level, file)
