from enum import Enum

class FieldType(Enum):
    empty = 1
    water = 2
    ship = 3

class Field(object):
    def __init__(self, fieldtype, fixed=False):
        if not isinstance(fieldtype, FieldType):
            raise AttributeError("fieldtype must be a FieldType instance")

        self.fixed = fixed
        self.hidden_type = fieldtype
        self.player_type = fieldtype if fixed else FieldType.empty

    def is_ship(self, from_fixed=False):
        return ((self.fixed or from_fixed) \
                and self.hidden_type == FieldType.ship) \
            or self.player_type == FieldType.ship

    def is_water(self, from_fixed=False):
        return ((self.fixed or from_fixed) \
                and self.hidden_type == FieldType.water) \
            or self.player_type == FieldType.water

    def __repr__(self):
        return '<{} field>'.format(self.hidden_type.name)

class Table(object):
    def __init__(self, width, height):
        self.__fields = []
        self.width = width
        self.height = height

        for x in range(1, width + 1):
            self.__fields.append([])

            for y in range(1, height + 1):
                self.__fields[x - 1].append(Field(FieldType.water))

    def __border_row(self):
        ret = '+'

        for i in range(0, self.width):
            ret += '--+'

        ret += "\n"

        return ret

    def __field(self, row, col):
        if row < 0 \
           or row >= self.height \
           or col < 0 \
           or col >= self.width:
            return None

        return self.__fields[row][col]

    def col_ship_count(self, col):
        return len([r[col] for r in self.__fields \
                    if r[col].hidden_type == FieldType.ship])

    def row_ship_count(self, row):
        return len([r for r in self.__fields[row] \
                    if r.hidden_type == FieldType.ship])

    def __neighbours(self, row, col):
        return (
            self.__field(row - 2, col -1),
            self.__field(row - 1, col),
            self.__field(row, col - 1),
            self.__field(row - 1, col - 2)
        )

    def __str__(self):
        ret = self.__border_row()

        for row in range(0, self.height):
            ret += '|'

            for col in range(0, self.width):
                field = self.__fields[row][col]

                typ = field.hidden_type if field.fixed else field.player_type

                if typ == FieldType.empty:
                    ret += '  '
                elif typ == FieldType.water:
                    ret += '~~'
                elif typ == FieldType.ship:
                    # Check neighbours

                    # upper, right, lower, left
                    neighbours = self.__neighbours(row + 1, col + 1)

                    all_waters = True

                    for n in neighbours:
                        all_waters = all_waters and \
                                     (n is None \
                                      or n.is_water(from_fixed=field.fixed))

                    neighs = [False if n is None \
                              else n.is_ship(from_fixed=field.fixed) \
                              for n in neighbours]

                    # Ship above and below or left and right
                    if (neighs[0] and neighs[2]) \
                       or (neighs[1] and neighs[3]):
                        ret += 'XX'
                    elif neighs[0]: # Ship above, not below
                        ret += 'vv'
                    elif neighs[2]: # Ship below, not above
                        ret += '^^'
                    elif neighs[1]: # Ship right, not left
                        ret += ' <'
                    elif neighs[3]: # Ship on left, not right
                        ret += '> '
                    elif all_waters:
                        ret += 'oo'
                    else:
                        ret += '??'

                ret += '|'

            ret += " {}\n".format(self.row_ship_count(row))
            ret += self.__border_row()

        for col in range(0, self.width):
            ret += " {:<2}".format(self.col_ship_count(col))

        ret += "\n"

        return ret

    def add_ship(self, start_row, start_col, length, vertical):
        row, col = start_row - 1, start_col - 1

        for i in range(0, length):
            self.__fields[row][col].hidden_type = FieldType.ship

            if vertical:
                row += 1
            else:
                col += 1

    def clean(self):
        for row in self.__fields:
            for field in row:
                field.hidden_type = FieldType.water
                field.player_type = FieldType.empty
                field.fixed = False

    def reveal(self, row, col):
        self.__fields[row - 1][col - 1].fixed = True

    def reveal_all(self):
        for row in self.__fields:
            for field in row:
                field.fixed = True

    @property
    def solved(self):
        # Check if all fileds have been marked
        for row in self.__fields:
            for field in row:
                if field.player_type == FieldType.empty:
                    return False

        # TODO: Check if marked ships are placed sanely
        # TODO: Check if side-numbers equal the number of marked ship-parts

        return True

t = Table(6, 6)
t.add_ship(1, 3, 1, False)
t.add_ship(2, 5, 2, False)
t.add_ship(3, 1, 3, False)
t.add_ship(5, 1, 1, False)
t.add_ship(5, 3, 2, True)
t.add_ship(6, 5, 1, False)
t.reveal(1, 2)
t.reveal(3, 3)
t.reveal(5, 1)
t.reveal(5, 2)

print(str(t))
