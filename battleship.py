from enum import Enum
import colorama
from colorama import Fore, Back, Style

class FieldType(Enum):
    empty = 1
    water = 2
    ship = 3

class ShipOrientation(Enum):
    unknown = 0
    none = 1
    north = 2
    south = 3
    east = 4
    west = 5
    both = 6

class Field(object):
    def __init__(self):
        self.__fixed = False
        self.__type = FieldType.empty
        self.__marked_type = FieldType.empty
        self.__orientation = ShipOrientation.none

    @property
    def marked_type(self):
        return self.__type if self.__fixed else self.__marked_type

    def set_fixed(self, typ=None, orientation=ShipOrientation.unknown):
        self.__fixed = True

        if typ is not None:
            self.__type = typ
            self.__marked_type = typ
        self.__orientation = orientation

    def __str__(self):
        typ = self.__type if self.__fixed else self.__marked_type

        if typ == FieldType.empty:
            return '  '
        elif typ == FieldType.water:
            return '~~'
        elif typ == FieldType.ship:
            if self.__orientation == ShipOrientation.unknown:
                return '??'
            elif self.__orientation == ShipOrientation.none:
                return '<>'
            elif self.__orientation == ShipOrientation.north:
                return '^^'
            elif self.__orientation == ShipOrientation.south:
                return 'vv'
            elif self.__orientation == ShipOrientation.west:
                return ' <'
            elif self.__orientation == ShipOrientation.east:
                return '> '
            elif self.__orientation == ShipOrientation.both:
                return 'XX'

    def set_type(self, typ, orientation=ShipOrientation.unknown):
        self.__type = typ
        self.__orientation = orientation

class Table(object):
    def __init__(self, width, height):
        self.__fields = []
        self.__width = width
        self.__height = height
        self.__col_counts = []
        self.__row_counts = []
        self.__ships = []

        for count in range(0, height):
            self.__fields.append([])
            self.__row_counts.append(0)

        for count in range(0, width):
            self.__col_counts.append(0)

            for row in range(0, height):
                self.__fields[row].append(Field())

        self.clean()

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    def __check_height(self, row):
        if row not in range(0, self.__height):
            raise IndexError("Invalid row number")

    def __check_width(self, col):
        if col not in range(0, self.__width):
            raise IndexError("Invalid column number")

    def row(self, row):
        self.__check_height(row)

        # TODO: This doesn’t feel right
        return self.__fields[row]

    def col(self, col):
        self.__check_width(col)

        # TODO: This doesn’t feel right
        return [f[col] for f in f.__fields]

    def clean(self):
        for row in self.__fields:
            for field in row:
                field.hidden_type = FieldType.water
                field.player_type = FieldType.empty
                field.fixed = False

    def __check_collision(self, parts):
        pass

    def add_ship(self, start_row, start_col, length, vertical):
        row, col = start_row - 1, start_col - 1
        parts = []

        for i in range(0, length):
            parts.append((row, col))

            if vertical:
                row += 1
            else:
                col += 1

        count = 0

        for row, col in parts:
            count += 1
            orientation = ShipOrientation.unknown

            if length == 1:
                orientation=ShipOrientation.none
            else:
                if count == 1:
                    orientation = ShipOrientation.north if vertical \
                                  else ShipOrientation.west
                elif count == length:
                    orientation = ShipOrientation.south if vertical \
                                  else ShipOrientation.east
                else:
                    orientation = ShipOrientation.both

            self.__fields[row][col].set_type(FieldType.ship,
                                             orientation=orientation)

    def reveal(self, row, col):
        self.__fields[row - 1][col - 1].set_fixed()

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

    def mark(self, row, col, typ):
        field = self.__field(row, col)

        if field is not None:
            field.player_type = typ

    def is_ship(self, row, col):
        return self.__fields[row][col].player_type == FieldType.ship

    def __str__(self):
        def divider():
            ret = '+'

            for i in range(0, self.__width):
                ret += '--+'

            ret += "\n"

            return ret

        ret = divider()

        for row in self.__fields:
            ret += '|'

            for field in row:
                ret += '{}|'.format(field)

            ret += "\n"
            ret += divider()

        return ret

class Solver(object):
    def __init__(self, table):
        self.table = table

    def mark_edges(self):
        for row in range(0, self.table.height):
            for col in range(0, self.table.width):
                if self.table.is_ship(row, col):
                    print("MARK!")
                    self.table.mark(row - 1, col - 1, FieldType.water)
                    self.table.mark(row - 1, col + 1, FieldType.water)
                    self.table.mark(row + 1, col - 1, FieldType.water)
                    self.table.mark(row + 1, col + 1, FieldType.water)

    def show(self):
        print(str(self.table))

colorama.init()

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

s = Solver(t)
s.show()
s.mark_edges()
s.show()
