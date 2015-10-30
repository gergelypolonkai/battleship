from enum import Enum
import colorama
from colorama import Fore, Back, Style

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

    @property
    def marked_type(self):
        return self.hidden_type if self.fixed else self.player_type

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
        ret = Back.WHITE + Fore.BLACK + '+'

        for i in range(0, self.width):
            ret += '--+'

        ret += "    \n" + Style.RESET_ALL

        return ret

    def field(self, row, col):
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
            self.field(row - 2, col -1),
            self.field(row - 1, col),
            self.field(row, col - 1),
            self.field(row - 1, col - 2)
        )

    def __str__(self):
        ret = self.__border_row()

        for row in range(0, self.height):
            ret += Back.WHITE + Fore.BLACK + '|'

            for col in range(0, self.width):
                field = self.__fields[row][col]

                typ = field.hidden_type if field.fixed else field.player_type

                if typ == FieldType.empty:
                    ret += Back.WHITE + '  '
                elif typ == FieldType.water:
                    ret += Back.CYAN + Fore.BLUE + '~~'
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

                    ret += Back.CYAN

                    # Ship above and below or left and right
                    if (neighs[0] and neighs[2]) \
                       or (neighs[1] and neighs[3]):
                        ret += Fore.RED + 'XX'
                    elif neighs[0]: # Ship above, not below
                        ret += Fore.RED + 'vv'
                    elif neighs[2]: # Ship below, not above
                        ret += Fore.RED + '^^'
                    elif neighs[1]: # Ship right, not left
                        ret += Fore.RED + ' <'
                    elif neighs[3]: # Ship on left, not right
                        ret += Fore.RED + '> '
                    elif all_waters:
                        ret += Fore.RED + 'oo'
                    else:
                        ret += Fore.BROWN + '??'

                ret += Back.WHITE + Fore.BLACK + '|'

            ret += " {:<3}\n".format(self.row_ship_count(row)) + Style.RESET_ALL
            ret += self.__border_row()

        ret += Back.WHITE + Fore.BLACK

        for col in range(0, self.width):
            ret += " {:<2}".format(self.col_ship_count(col))

        ret += "     \n" + Style.RESET_ALL

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

    def mark(self, row, col, typ):
        self.__fields[row][col].player_type = typ

class Solver(object):
    def __init__(self, table):
        self.table = table

    def mark_edges(self):
        for row in range(0, self.table.height):
            for col in range(0, self.table.width):
                field = self.table.field(row, col)

                if field.marked_type == FieldType.ship:
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
