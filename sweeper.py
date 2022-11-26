"""=== Module Description ===
This module contains the Sweeper class which assists in solving Minesweeper and Thrill Digger games.
"""
from typing import Optional, Iterable
from tkinter import *
import math


class BombEquation:
    """An equation representing the number of bombs in a given set of tiles.

    === Public Attributes ===
    tiles:
        The coordinates for the set of tiles.
    bombs:
        The possible numbers of bombs in these tiles.

    === Representation Invariants ===
    - n in self.bombs implies 0 <= n <= len(tiles)
    - self.bombs is sorted least to greatest
    """
    tiles: frozenset[tuple[int, int]]
    bombs: tuple[int]

    def __init__(self, tiles: Iterable[tuple[int, int]], bombs: Iterable[int]) -> None:
        """Initialize this equation.

        :param tiles: the set of tiles in question
        :param bombs: the possible number of bombs shared between these tiles sorted least to greatest
        """
        self.tiles = frozenset(tiles)
        num_tiles = len(self.tiles)
        self.bombs = tuple(bomb_num for bomb_num in bombs if 0 <= bomb_num <= num_tiles)

    def __eq__(self, other: object) -> bool:
        """Return True iff other is a BombEquation and all the attributes are the same.

        :param other: an object to check equality with
        :return: other is a BombEquation and all the attributes are the same
        """
        return isinstance(other, BombEquation) and self.tiles == other.tiles and self.bombs == other.bombs

    def __ne__(self, other: object) -> bool:
        """Return True iff not __eq__(self, other).

        :param other: an object to check equality with
        :return: not __eq__(self, other)
        """
        return not isinstance(other, BombEquation) or self.tiles != other.tiles or self.bombs != other.bombs

    def __hash__(self) -> int:
        """Return a hash value.

        :return: a hash of self
        """
        return (self.tiles, self.bombs).__hash__()

    def __le__(self, other: 'BombEquation') -> bool:
        """Return True iff self.tiles <= other.tiles and len(self.bombs) == 1.

        :param other: the other BombEquation in the comparison
        :return: self.tiles <= other.tiles and len(self.bombs) == 1
        """
        return self.tiles <= other.tiles and len(self.bombs) == 1

    def __ge__(self, other: 'BombEquation') -> bool:
        """Return True iff self.tiles >= other.tiles and len(other.bombs) == 1.

        :param other: the other BombEquation in the comparison
        :return: self.tiles >= other.tiles and len(other.bombs) == 1
        """
        return self.tiles >= other.tiles and len(other.bombs) == 1

    def __sub__(self, other: 'BombEquation') -> 'BombEquation':
        """Subtract the tiles from other from self's tiles and subtract other's bombs from self's bombs.
        Only to be used when self >= other.

        :param other: the BombEquation to subtract from this one where other <= self
        :return: a BombEquation with the tiles from other removed from self's tiles and other's bombs subtracted from
        each of self's bombs

        >>> bomb_eq = BombEquation([(0, 2), (1, 2), (2, 2)], [1]) - BombEquation([(0, 2), (1, 2)], [1])
        >>> bomb_eq == BombEquation([(2, 2)], [0])
        True
        """
        other_bomb_num = other.bombs[0]
        return BombEquation(self.tiles - other.tiles, (self_bomb_num - other_bomb_num for self_bomb_num in self.bombs))

    def is_trivial(self) -> bool:
        """Return True iff this BombEquation has a single tile and we know if it's a bomb.

        :return: this BombEquation has a single tile and we know if it's a bomb
        """
        return len(self.tiles) == len(self.bombs) == 1

    def is_splittable(self) -> bool:
        """Return True iff this equation does not involve a single tile and is either useless or can
        singlehandedly determine whether each of its tiles have a bomb.

        :return: this equation does not involve a single tile and is either useless or can
        singlehandedly determine whether each of its tiles have a bomb

        >>> BombEquation([(0, 0), (0, 1), (1, 0)], (0, )).is_splittable()
        True
        >>> BombEquation([(0, 0), (0, 1), (1, 0)], (3, )).is_splittable()
        True
        >>> BombEquation([(0, 0), (0, 1), (1, 0)], (0, 1, 2, 3)).is_splittable()
        True
        >>> BombEquation([(0, 0)], (0, )).is_splittable()
        False
        >>> BombEquation([(0, 0), (0, 1), (1, 0)], (1, )).is_splittable()
        False
        >>> BombEquation([(0, 0), (0, 1), (1, 0)], (0, 3)).is_splittable()
        False
        """
        return len(self.tiles) != 1 and ((len(self.bombs) == 1 and self.bombs[0] in (0, len(self.tiles)))
                                         or len(self.bombs) == len(self.tiles) + 1)

    def split(self) -> list['BombEquation']:
        """Return a set of BombEquations representing this one having been split into simpler componenets.
        Only to be used if self.is_splittable().

        :return: a set of BombEquations representing this one having been split into simpler componenets

        >>> components = BombEquation([(0, 0), (0, 1), (1, 0)], (0, )).split()
        >>> len(components)
        3
        >>> BombEquation([(0, 0)], (0, )) in components
        True
        >>> BombEquation([(0, 1)], (0, )) in components
        True
        >>> BombEquation([(1, 0)], (0, )) in components
        True
        >>> components = BombEquation([(0, 0), (0, 1), (1, 0)], (3, )).split()
        >>> len(components)
        3
        >>> BombEquation({(0, 0)}, (1, )) in components
        True
        >>> BombEquation({(0, 1)}, (1, )) in components
        True
        >>> BombEquation({(1, 0)}, (1, )) in components
        True
        >>> components = BombEquation({(0, 0), (0, 1), (1, 0)}, (0, 1, 2, 3)).split()
        >>> len(components)
        3
        >>> BombEquation({(0, 0)}, (0, 1)) in components
        True
        >>> BombEquation({(0, 1)}, (0, 1)) in components
        True
        >>> BombEquation({(1, 0)}, (0, 1)) in components
        True
        """
        if len(self.bombs) > 1:
            return [BombEquation((tile, ), (0, 1)) for tile in self.tiles]
        bomb = int(bool(self.bombs[0]))
        return [BombEquation((tile, ), (bomb, )) for tile in self.tiles]

    def is_impossible(self) -> bool:
        """Return True iff this equation is impossible to satisfy.

        :return: self.bombs is empty
        """
        return not self.bombs

    @staticmethod
    def integrate_new_bomb_eqs(constraints: list['BombEquation'], new_bomb_eqs: list['BombEquation']) -> bool:
        """Integrate new BombEquations into a set of constraints (BombEquations). Both will be modified.
        Return True if the integration was successful and return False if there was an impossibility.

        :param constraints:
        :param new_bomb_eqs:
        :return: if the integration was successful
        """
        # loop until there are no new constraints to integrate
        while new_bomb_eqs:
            # get a new equation to integrate
            new_bomb_eq = new_bomb_eqs.pop()
            # if it's impossible, return False
            if new_bomb_eq.is_impossible():
                return False
            # if it's splittable, split it up into its single tiles and integrate those instead
            if new_bomb_eq.is_splittable():
                new_bomb_eqs += new_bomb_eq.split()
                continue
            # otherwise, loop through all the old constraints and see if any simplifications can be made
            # check to see if the new constraint should be added to the list of constraints
            add_new_bomb_eq = True
            updated_constraints = []
            for old_bomb_eq in constraints:
                # if we have two of the same constraint, remove one of them
                if new_bomb_eq == old_bomb_eq:
                    add_new_bomb_eq = False
                    break
                # if an old constraint can be simplified by a new one, remove it from the list of old constraints,
                # simplify it, and add it to the list of new contraints
                if new_bomb_eq <= old_bomb_eq:
                    new_bomb_eqs.append(old_bomb_eq - new_bomb_eq)
                    updated_constraints.append(old_bomb_eq)
                # if the new constraint can be simplified by an old one, subtract off the old one and put the new
                # simplified one back in the set to be integrated
                elif old_bomb_eq <= new_bomb_eq:
                    new_bomb_eqs.append(new_bomb_eq - old_bomb_eq)
                    add_new_bomb_eq = False
                    break
            for old_bomb_eq in updated_constraints:
                constraints.remove(old_bomb_eq)
            if add_new_bomb_eq:
                constraints.append(new_bomb_eq)
        return True


class Solution:
    """Given a set of BombEquations there is a corresponding Solution, where for each integer number of bombs,
    the solution gives the total number of bomb placements with that number of bombs
    as well as a count for each tile occuring in any of the BombEquations of how many of these bomb placements have
    a bomb in that tile.

    === Public Attributes ===
    bombs_to_tile_bomb_frequency:
        A dictionary whose keys represent the number of bombs in a solution,
        and whose values are a tuple whose second element is the number of solutions with said number of bombs
        and whose first element is a dictionary which has tiles as keys
        and the number of solutions with said number of bombs in which this tile has a bomb the value.
    """
    bombs_to_tile_bomb_frequency: dict[int, tuple[dict[tuple[int, int], int], int]]

    def __init__(self, bombs_to_tile_bomb_frequency: dict[int, tuple[dict[tuple[int, int], int], int]]) -> None:
        """Initialize this Solution.

        :param bombs_to_tile_bomb_frequency:
        """
        self.bombs_to_tile_bomb_frequency = bombs_to_tile_bomb_frequency

    def __eq__(self, other: object) -> bool:
        """Return True iff other is a Solution and all the attributes are the same.

        :param other: an object to check equality with
        :return: other is a Solution and all the attributes are the same
        """
        return isinstance(other, Solution) and self.bombs_to_tile_bomb_frequency == other.bombs_to_tile_bomb_frequency

    def __iadd__(self, other: 'Solution') -> 'Solution':
        """Combine two sets of layout information about the same area. Assume inputs are no longer valid.

        :param other: the second set of info about the area
        :return: the combined info

        >>> sol = Solution({})
        >>> sol += Solution({})
        >>> sol == Solution({})
        True
        >>> sol = Solution({0: ({(0, 0): 0}, 1)})
        >>> sol += Solution({})
        >>> sol == Solution({0: ({(0, 0): 0}, 1)})
        True
        >>> sol = Solution({1: ({(0, 0): 0, (1, 1): 1}, 1)})
        >>> sol += Solution({1: ({(0, 0): 1, (1, 1): 0}, 1)})
        >>> sol == Solution({1: ({(0, 0): 1, (1, 1): 1}, 2)})
        True
        """
        if self.bombs_to_tile_bomb_frequency == {}:
            self.bombs_to_tile_bomb_frequency = other.bombs_to_tile_bomb_frequency
            return self
        for other_num_bombs, other_layout_totals in other.bombs_to_tile_bomb_frequency.items():
            other_bomb_instances, other_num_layouts = other_layout_totals
            bomb_instances, num_layouts = self.bombs_to_tile_bomb_frequency.get(other_num_bombs, ({}, 0))
            for tile, bomb_count in other_bomb_instances.items():
                bomb_instances[tile] = bomb_instances.get(tile, 0) + bomb_count
            self.bombs_to_tile_bomb_frequency[other_num_bombs] = (bomb_instances, num_layouts + other_num_layouts)
        return self

    def __mul__(self, other: 'Solution') -> 'Solution':
        """Combine two sets of layout information about disjoint areas.

        :param other: the second set of info about the area
        :return: the combined info

        >>> Solution({}) * Solution({}) == Solution({})
        True
        >>> Solution({0: ({(0, 0): 0}, 1)}) * Solution({}) == Solution({})
        True
        >>> sol = Solution({0: ({(0, 0): 0, (1, 1): 0}, 1),
        ...                 1: ({(0, 0): 1, (1, 1): 1}, 2), 2: ({(0, 0): 1, (1, 1): 1}, 1)})
        >>> sol * Solution({0: ({}, 1)}) == sol
        True
        >>> Solution({1: ({(0, 0): 0, (1, 1): 1}, 1)}) == (Solution({0: ({(0, 0): 0}, 1)})
        ...                                                * Solution({1: ({(1, 1): 1}, 1)}))
        True
        >>> s = (Solution({0: ({(0, 0): 0}, 1), 1: ({(0, 0): 1}, 1)})
        ...      * Solution({0: ({(1, 1): 0}, 1), 1: ({(1, 1): 1}, 1)}))
        >>> s == Solution({0: ({(0, 0): 0, (1, 1): 0}, 1),
        ...                1: ({(0, 0): 1, (1, 1): 1}, 2), 2: ({(0, 0): 1, (1, 1): 1}, 1)})
        True
        """
        result_solution: Solution = Solution({})
        for num_bombs, layout_totals in self.bombs_to_tile_bomb_frequency.items():
            for other_num_bombs, other_layout_totals in other.bombs_to_tile_bomb_frequency.items():
                bomb_instances, num_layouts = layout_totals
                other_bomb_instances, other_num_layouts = other_layout_totals
                new_bomb_instances = {}
                for tile in bomb_instances:
                    new_bomb_instances[tile] = bomb_instances[tile] * other_num_layouts
                for tile in other_bomb_instances:
                    new_bomb_instances[tile] = other_bomb_instances[tile] * num_layouts
                result_solution += Solution({num_bombs + other_num_bombs: (new_bomb_instances,
                                                                           num_layouts * other_num_layouts)})
        return result_solution

    @staticmethod
    def group_constraints(constraints: list[BombEquation]) -> list[list[BombEquation]]:
        """Group the constraints into lists of BombEquations such that each list is disjoint
        and for each BombEquation in a list, all other BombEquations that share a tile with it are in the same list.

        :return: the constraints split into lists of BombEquations such that each list is disjoint and for each
        BombEquation in a list, all other BombEquations that share a tile with it are in the same list
        """
        # a list of areas this constraint should be grouped into,
        # where an area is a tuple containing a list of the
        # bomb eqs that are grouped together and a set of tiles in the area
        grouped_constraints: list[tuple[list[BombEquation], set[tuple[int, int]]]] = []
        # group all the constraints
        for bomb_eq in constraints:
            tiles_in_common = []
            for constraints, tiles in grouped_constraints:
                # check to see if any of this bomb_eq's tiles are in this area
                for tile in bomb_eq.tiles:
                    # if so, append it to the list of areas this eq should be grouped with
                    if tile in tiles:
                        tiles_in_common.append((constraints, tiles))
                        break
            # if there are areas this eq should be grouped with, combine them all and add this eq
            if tiles_in_common:
                # combine all the areas with the first one
                first_constraints, first_tiles = tiles_in_common[0]
                for constraints, tiles in tiles_in_common[1:]:
                    # add all this area's eqs to the first area's
                    first_constraints.extend(constraints)
                    # add all this area's tiles to the first area's
                    first_tiles.update(tiles)
                # add this eq to the area
                first_constraints.append(bomb_eq)
                first_tiles.update(bomb_eq.tiles)
                # remove all the other areas from the list of areas
                for merged_area in tiles_in_common[:0:-1]:
                    grouped_constraints.remove(merged_area)

            # otherwise, create a new area for this eq
            else:
                grouped_constraints.append(([bomb_eq], set(bomb_eq.tiles)))

        return [constraint_group for constraint_group, _ in grouped_constraints]

    @staticmethod
    def find_tile_to_recurse_on(constraints: list[BombEquation]) -> tuple[int, int]:
        """
        Given a non-empty list of constraints return the most common tile.

        constraints is unchanged.

        :param constraints: the list of constraints in which we find a tile to recurse on in solve_area
        :return: the tile to recurse on in solve_area
        """
        tile_to_return: tuple[int, int] = (-1, -1)
        tile_counts: dict[tuple[int, int], int] = {(-1, -1): 0}
        for constraint in constraints:
            for tile in constraint.tiles:
                tile_count = tile_counts.get(tile, 0) + 1
                tile_counts[tile] = tile_count
                if tile_count > tile_counts[tile_to_return]:
                    tile_to_return = tile
        return tile_to_return

    @staticmethod
    def solve_area(constraints: list[BombEquation]) -> 'Solution':
        """Get a Solution corresponding to these contraints.

        constraints is not changed.

        :param constraints: a list of constraints that must be satisfied in the solution
        :return: a Solution corresponding to the contraints

        >>> Solution.solve_area([]) == Solution({0: ({}, 1)})
        True
        >>> Solution.solve_area([BombEquation([(0, 0)], [1])]) == Solution({1: ({(0, 0): 1}, 1)})
        True
        >>> Solution.solve_area([BombEquation([(0, 0)], [0])]) == Solution({0: ({(0, 0): 0}, 1)})
        True
        >>> Solution.solve_area([BombEquation([(0, 0)], [0, 1])]) == Solution({0: ({(0, 0): 0}, 1),
        ...                                                                    1: ({(0, 0): 1}, 1)})
        True
        >>> Solution.solve_area([BombEquation([(0, 0), (1, 1)], [1])]) == Solution({1: ({(0, 0): 1, (1, 1): 1}, 2)})
        True
        >>> s = Solution.solve_area([BombEquation([(0, 0), (1, 1)], [1]), BombEquation([(1, 1), (0, 1), (1, 0)], [2])])
        >>> s == Solution({2: ({(0, 0): 0, (1, 1): 2, (0, 1): 1, (1, 0): 1}, 2),
        ...                3: ({(0, 0): 1, (1, 1): 0, (0, 1): 1, (1, 0): 1}, 1)})
        True
        >>> s = Solution.solve_area([BombEquation([(0, 0), (1, 1)], [0, 1]),
        ...                          BombEquation([(1, 1), (0, 1), (1, 0)], [2])])
        >>> s == Solution({2: ({(0, 0): 0, (1, 1): 2, (0, 1): 2, (1, 0): 2}, 3),
        ...                3: ({(0, 0): 1, (1, 1): 0, (0, 1): 1, (1, 0): 1}, 1)})
        True
        >>> s = Solution.solve_area([BombEquation([(0, 1), (1, 0), (1, 1)], [1, 2]),
        ...                          BombEquation([(0, 0)], [0])])
        >>> s == Solution({1: ({(0, 0): 0, (1, 1): 1, (0, 1): 1, (1, 0): 1}, 3),
        ...                2: ({(0, 0): 0, (1, 1): 2, (0, 1): 2, (1, 0): 2}, 3)})
        True
        """
        if not constraints:
            return Solution({0: ({}, 1)})

        solution_so_far: Solution

        if len(constraints) == 1:
            only_constraint = constraints[0]
            num_tiles = len(only_constraint.tiles)
            solution_so_far = Solution({})
            for bombs in only_constraint.bombs:
                solution_so_far += Solution({bombs: ({tile: comb(num_tiles - 1, bombs - 1)
                                                      for tile in only_constraint.tiles},
                                                     comb(num_tiles, bombs))})
            return solution_so_far

        # group the constraints by overlap
        grouped_constraints = Solution.group_constraints(constraints)
        # the combined solution for all processed groups
        solution_so_far = Solution({0: ({}, 1)})
        for constraint_group in grouped_constraints:
            recurse_tile = Solution.find_tile_to_recurse_on(constraint_group)
            group_solution: Solution = Solution({})
            for bomb in (0, 1):
                # make a copy of the constraints so that any changes we make can be reversed
                constraint_group_copy = constraint_group.copy()
                new_bomb_eq = BombEquation((recurse_tile, ), (bomb, ))
                # if you can successfully integrate this tile as a bomb/not a bomb
                if BombEquation.integrate_new_bomb_eqs(constraint_group_copy, [new_bomb_eq]):
                    # remove this constraint so that the size of the area decreases by 1
                    constraint_group_copy.remove(new_bomb_eq)
                    # recurse
                    group_solution += (Solution({bomb: ({recurse_tile: bomb}, 1)})
                                       * Solution.solve_area(constraint_group_copy))
            solution_so_far *= group_solution
        # combine and return all the areas
        return solution_so_far


class Sweeper:
    """Helps solve Minesweeper games.

    === Public Attributes ===
    bomb_key:
        What each string tells us about the surrounding bombs
    version:
        The version of Minesweeper we're sweeping: Classic or Thrill Digger
    height:
        The height of the playing field in playing tiles.
    width:
        The width of the playing field in playing tiles.
    bombs:
        The total number of bombs.
    board:
        A list of lists of strings of the info on each tile.
    constraints:
        A list of constraints on the layout of the bombs imposed by uncovered tiles' information.
    unconstrained_tiles:
        A list of tiles' coordinates that have no uncovered number tiles around them.
    message:
        A message telling the user if the inputted information is invalid.
    """
    BOMB_KEY: dict[str, dict[str, list[int]]] = {
        'Classic': {'0': [0], '1': [1], '2': [2], '3': [3], '4': [4], '5': [5], '6': [6], '7': [7], '8': [8]},
        'Thrill Digger': {'Green': [0], 'Blue': [1, 2], 'Red': [3, 4], 'Silver': [5, 6], 'Gold': [7, 8]}}
    version: str
    height: int
    width: int
    bombs: int
    board: list[list[str]]
    constraints: list[BombEquation]
    unconstrained_tiles: list[tuple[int, int]]
    message: str

    def __init__(self, version='Classic') -> None:
        """Initialize this Minesweeper's boards and attributes.

        :param version: what version of Minesweeper we're sweeping
        """
        self.version = version
        if version == 'Classic':
            self.height = 9
            self.width = 9
            self.bombs = 10
        if version == 'Thrill Digger':
            self.height = 4
            self.width = 5
            self.bombs = 4
        self.board = [[''] * self.width for _ in range(self.height)]
        self.constraints = []
        self.unconstrained_tiles = [(i, j) for i in range(self.height) for j in range(self.width)]
        self.message = ''

    def integrate_new_info(self, row: int, column: int, info: str) -> None:
        """Take the information about an uncovered square and update constraints and unconstrained_tiles.

        :param row: the row of the uncovered square
        :param column: the column of the uncovered square
        :param info: what the uncovered square says
        """
        self.board[row][column] = info
        tile = (row, column)
        if info in Sweeper.BOMB_KEY[self.version]:
            if tile in self.unconstrained_tiles:
                self.unconstrained_tiles.remove(tile)
            neighbours = return_neighbours(row, column, self.height, self.width)
            for neighbour in neighbours:
                if neighbour in self.unconstrained_tiles:
                    self.unconstrained_tiles.remove(neighbour)
            if not BombEquation.integrate_new_bomb_eqs(
                    self.constraints,
                    [BombEquation((tile, ), (0, )),
                     BombEquation(neighbours, Sweeper.BOMB_KEY[self.version][info])]):
                self.message = 'Impossible layout'
        elif info in ('B', 'Rupoor'):
            if tile in self.unconstrained_tiles:
                self.unconstrained_tiles.remove(tile)
            if not BombEquation.integrate_new_bomb_eqs(self.constraints, [BombEquation((tile, ), (1, ))]):
                self.message = 'Impossible layout'

    def calculate_board(self) -> None:
        """Calculate and update the board's values."""
        bomb_instances, denominator = self.calculate_bomb_fractions(Solution.solve_area(self.constraints))
        self.process_bomb_fractions(bomb_instances, denominator)

    def calculate_bomb_fractions(self, solution: Solution) -> tuple[dict[tuple[int, int], int], int]:
        """Calculate the probability that each square has a bomb.

        :param solution: aggregate information about all possible layouts
        :return: a tuple, the first element a dictionary whose keys are tiles and values are the number of layouts in
        which the tile has a bomb, the second element the total number of layouts
        """
        # calculate the probabilities for all the unknown tiles, with (-1, -1) representing each unconstrained tile
        bomb_instances = {}
        num_unconstrained_tiles = len(self.unconstrained_tiles)
        num_layouts = 0
        for num_bombs, layout_totals in solution.bombs_to_tile_bomb_frequency.items():
            partial_bomb_instances, partial_num_layouts = layout_totals
            num_unconstrained_tile_layouts = comb(num_unconstrained_tiles, self.bombs - num_bombs)
            for tile, bomb_occurences in partial_bomb_instances.items():
                bomb_instances[tile] = bomb_instances.get(tile, 0) + bomb_occurences * num_unconstrained_tile_layouts
            bomb_instances[(-1, -1)] = bomb_instances.get((-1, -1), 0) + partial_num_layouts * comb(
                num_unconstrained_tiles - 1, self.bombs - num_bombs - 1)
            num_layouts += partial_num_layouts * num_unconstrained_tile_layouts

        unconstrained_tile_instances = bomb_instances.pop((-1, -1))
        for unconstrained_tile in self.unconstrained_tiles:
            bomb_instances[unconstrained_tile] = unconstrained_tile_instances

        return bomb_instances, num_layouts

    def process_bomb_fractions(self, bomb_instances: dict[tuple[int, int], int], total_num_layouts: int) -> None:
        """For each tile that is guaranteed to have/not have a bomb, add a trivial constraint representing this.
        Also update the board.

        :param bomb_instances: the number of layouts in which a given tile has a bomb
        :param total_num_layouts: the total number of layouts
        """
        if not total_num_layouts:
            self.message = 'Impossible layout'
            return

        consistent_tiles = []
        for tile in bomb_instances:
            row, column = tile
            if bomb_instances[tile] == 0:
                if self.board[row][column] not in Sweeper.BOMB_KEY[self.version]:
                    self.board[row][column] = 'S'
                    consistent_tiles.append(BombEquation((tile, ), (0, )))
                    if tile in self.unconstrained_tiles:
                        self.unconstrained_tiles.remove(tile)
            elif bomb_instances[tile] == total_num_layouts:
                consistent_tiles.append(BombEquation((tile, ), (1, )))
                if tile in self.unconstrained_tiles:
                    self.unconstrained_tiles.remove(tile)
                if self.board[row][column] not in ('B', 'Rupoor'):
                    self.board[row][column] = 'B/R'
            else:
                self.board[row][column] = f'{round(100 * bomb_instances[tile] / total_num_layouts)}%'
        BombEquation.integrate_new_bomb_eqs(self.constraints, consistent_tiles)

    def reset(self) -> None:
        """Reset the attributes."""
        self.board = [[''] * self.width for _ in range(self.height)]
        self.constraints = []
        self.unconstrained_tiles = [(i, j) for i in range(self.height) for j in range(self.width)]
        self.message = ''

    def set_classic(self) -> None:
        """Set the game to be the classic version of Minesweeper."""
        self.version = 'Classic'
        self.set_easy()

    def set_thrill_digger(self) -> None:
        """Set the game to be the Thrill Digger version of Minesweeper."""
        self.version = 'Thrill Digger'
        self.set_easy()

    def set_easy(self) -> None:
        """Set the difficulty to easy and reset the game."""
        if self.version == 'Classic':
            self.height = 9
            self.width = 9
            self.bombs = 10
        else:
            self.height = 4
            self.width = 5
            self.bombs = 4
        self.reset()

    def set_medium(self) -> None:
        """Set the difficulty to medium and reset the game."""
        if self.version == 'Classic':
            self.height = 16
            self.width = 16
            self.bombs = 40
        else:
            self.height = 5
            self.width = 6
            self.bombs = 8
        self.reset()

    def set_hard(self) -> None:
        """Set the difficulty to hard and reset the game."""
        if self.version == 'Classic':
            self.height = 16
            self.width = 30
            self.bombs = 99
        else:
            self.height = 5
            self.width = 8
            self.bombs = 16
        self.reset()

    def set_custom(self, height: int, width: int, bombs: int) -> None:
        """Set the custom difficulty and reset the game."""
        self.height = height
        self.width = width
        self.bombs = bombs
        self.reset()


class SweeperWindow:
    """The UI for the Sweeper class.

    === Public Attributes ===
    sweeper:
        The Sweeper that this UI interfaces with.
    root:
        The background.
    field:
        The container for the mine field.
    board:
        A list of lists of entries making up the game board.
    message:
        A message telling the user if the inputted information is invalid.
    """
    sweeper: Sweeper
    root: Tk
    field: Frame
    board: list[list[Entry]]
    message: StringVar

    def __init__(self, starting_value: Optional[list[list[str]]] = None) -> None:
        """Initialize this Sweeper's boards and attributes."""
        self.sweeper = Sweeper()

        self.root = Tk()
        self.root.title('Minesweeper Solver')

        menu_bar = Menu(self.root)
        self.root.config(menu=menu_bar)

        version_menu = Menu(menu_bar)
        menu_bar.add_cascade(label='Version', menu=version_menu)
        version_menu.add_command(label='Classic', command=self.set_classic)
        version_menu.add_command(label='Thrill Digger', command=self.set_thrill_digger)

        difficulty_menu = Menu(menu_bar)
        menu_bar.add_cascade(label='Difficulty', menu=difficulty_menu)
        difficulty_menu.add_command(label='Easy', command=self.set_easy)
        difficulty_menu.add_command(label='Medium', command=self.set_medium)
        difficulty_menu.add_command(label='Hard', command=self.set_hard)
        difficulty_menu.add_command(label='Custom', command=self.set_custom)

        new_game_button = Button(self.root, text='New Game', command=self.reset)
        new_game_button.grid(row=0)

        submit_button = Button(self.root, text='Submit', command=self.receive_input)
        submit_button.grid(row=0, column=1)

        recalculate_button = Button(self.root, text='Recalculate', command=self.recalculate)
        recalculate_button.grid(row=0, column=2)

        self.field = Frame(self.root, bg='black')
        self.field.grid(row=1, columnspan=3)

        self.board = self.create_board()

        self.message = StringVar()
        message_label = Label(self.root, textvariable=self.message)
        message_label.grid(row=2, column=2, columnspan=2)

        if starting_value is not None:
            for row in range(self.sweeper.height):
                for col in range(self.sweeper.width):
                    self.board[row][col].insert(0, starting_value[row][col])

        self.root.mainloop()

    def create_board(self) -> list[list[Entry]]:
        """Create and return the default solver board."""
        board = []
        for i in range(self.sweeper.height):
            board.append([])
            for j in range(self.sweeper.width):
                # create the user's board with entries labeled
                if self.sweeper.version == 'Classic':
                    board[i].append(Entry(self.field, width=3, justify=CENTER))
                else:
                    board[i].append(Entry(self.field, width=6, justify=CENTER))
                board[i][j].grid(row=i, column=j)
        return board

    def receive_input(self) -> None:
        """Receive the input info from the board and display the new results."""
        for row in range(self.sweeper.height):
            for column in range(self.sweeper.width):
                self.sweeper.integrate_new_info(row, column, self.board[row][column].get())
        self.sweeper.calculate_board()
        self.refresh_display()

    def recalculate(self) -> None:
        """To be used when an error has been made, so recalculate everything."""
        self.sweeper.reset()
        self.receive_input()

    def refresh_display(self) -> None:
        """Update the display."""
        for row in range(len(self.board)):
            for column in range(len(self.board[0])):
                self.board[row][column].delete(0, END)
                self.board[row][column].insert(0, self.sweeper.board[row][column])
        self.message.set(self.sweeper.message)

    def set_classic(self) -> None:
        """Set the game to be the classic version of Minesweeper."""
        self.sweeper.set_classic()
        self.reset()

    def set_thrill_digger(self) -> None:
        """Set the game to be the Thrill Digger version of Minesweeper."""
        self.sweeper.set_thrill_digger()
        self.reset()

    def set_easy(self) -> None:
        """Set the difficulty to easy and reset the game."""
        self.sweeper.set_easy()
        self.reset()

    def set_medium(self) -> None:
        """Set the difficulty to easy and reset the game."""
        self.sweeper.set_medium()
        self.reset()

    def set_hard(self) -> None:
        """Set the difficulty to easy and reset the game."""
        self.sweeper.set_hard()
        self.reset()

    def set_custom(self, height: int = 0, width: int = 0, bombs: int = 0) -> None:
        """Set a custom difficulty and reset the game."""
        if not (height and width and bombs):
            height = int(input('height: '))
            width = int(input('width: '))
            bombs = int(input('bombs: '))
        self.sweeper.set_custom(height, width, bombs)
        self.reset()

    def reset(self) -> None:
        """Reset everything."""
        # reset all the attributes
        self.sweeper.reset()

        # reset all the non-sweeper attributes
        # delete all the current playing tiles
        self.field.destroy()
        self.field = Frame(self.root, bg='black')
        self.field.grid(row=1, columnspan=4)

        self.board = self.create_board()

        self.message.set(self.sweeper.message)


def return_neighbours(row: int, column: int, height: int, width: int) -> list[tuple[int, int]]:
    """Given a tile's row and column, and the board's height and width,
    return a list of coordinates of surrounding tiles.

    :param row: row of tile in question
    :param column: column of tile in question
    :param height: height of board in tiles
    :param width: width of board in tiles
    :return: all the tile's neighbours (sorted lexicographically)

    >>> return_neighbours(0, 0, 1, 1)
    []
    >>> return_neighbours(0, 0, 9, 9)
    [(0, 1), (1, 0), (1, 1)]
    >>> return_neighbours(0, 3, 9, 9)
    [(0, 2), (0, 4), (1, 2), (1, 3), (1, 4)]
    >>> return_neighbours(0, 8, 9, 9)
    [(0, 7), (1, 7), (1, 8)]
    >>> return_neighbours(6, 0, 9, 9)
    [(5, 0), (5, 1), (6, 1), (7, 0), (7, 1)]
    >>> return_neighbours(2, 7, 9, 9)
    [(1, 6), (1, 7), (1, 8), (2, 6), (2, 8), (3, 6), (3, 7), (3, 8)]
    >>> return_neighbours(1, 8, 9, 9)
    [(0, 7), (0, 8), (1, 7), (2, 7), (2, 8)]
    >>> return_neighbours(8, 0, 9, 9)
    [(7, 0), (7, 1), (8, 1)]
    >>> return_neighbours(8, 5, 9, 9)
    [(7, 4), (7, 5), (7, 6), (8, 4), (8, 6)]
    >>> return_neighbours(8, 8, 9, 9)
    [(7, 7), (7, 8), (8, 7)]
    """
    return (([(row - 1, column - 1)] * (column > 0)
             + [(row - 1, column)]
             + [(row - 1, column + 1)] * (column < width - 1)) * (row > 0)
            + [(row, column - 1)] * (column > 0)
            + [(row, column + 1)] * (column < width - 1)
            + ([(row + 1, column - 1)] * (column > 0)
               + [(row + 1, column)]
               + [(row + 1, column + 1)] * (column < width - 1)) * (row < height - 1))


def comb(n: int, k: int):
    """
    Return n choose k.

    :param n: number of objects to choose from
    :param k: number of objects to choose
    :return: number of ways to do the choice
    """
    if k < 0 or k > n:
        return 0
    return math.comb(n, k)


if __name__ == '__main__':
    SweeperWindow()
