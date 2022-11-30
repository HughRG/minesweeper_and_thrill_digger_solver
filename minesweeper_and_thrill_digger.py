"""=== Module Description ===
This module contains the Minesweeper and MinesweeperWindow class which together creates a Minesweeper game,
and the Thrill Digger class which is a variation of Minesweeper found in The Legend of Zelda: Skyward Sword.
"""
from sweeper import Sweeper, return_neighbours
from tkinter import *
from random import random, choice
from abc import ABC, abstractmethod


class Minesweeper(ABC):
    """A Minesweeper game.

    === Public Attributes ===
    REVEALED_TILES:
        A set of possible revealed tiles.
    height:
        The height of the playing field in tiles.
    width:
        The width of the playing field in tiles.
    bombs:
        The total number of bombs.
    board:
        A list of lists of strings making up the game board.
    shadow_board:
        A list of lists of ints representing the answer board. A -1 represents a bomb, and otherwise it is the number of
        surrounding bombs.
    squares_left:
        The number of non-bomb squares yet to be uncovered.
    bombs_left:
        The number of bombs minus the number of marked tiles.
    sweeper:
        A Sweeper used to determine if a game is solvable and to provide information to the user if requested.
    message:
        A message to the user.
    game_over:
        A bool that states if the game is over.
    """
    REVEALED_TILES: frozenset[str]
    height: int
    width: int
    bombs: int
    board: list[list[str]]
    shadow_board: list[list[int]]
    squares_left: int
    bombs_left: int
    sweeper: Sweeper
    message: str
    game_over: bool

    @abstractmethod
    def __init__(self) -> None:
        """Initialize this Minesweeper's boards and attributes."""

    @staticmethod
    def init_bomb_counts(shadow_board: list[list[int]]) -> list[list[int]]:
        """Finish initializing the shadow_board so that non-bomb squares count the surrounding bombs.

        :param shadow_board: self's shadow_board
        :return shadow_board: self's shadow_board with the counts initialized
        """
        height = len(shadow_board)
        width = len(shadow_board[0])
        for row in range(height):
            for column in range(width):
                if shadow_board[row][column] >= 0:
                    for r, c in return_neighbours(row, column, height, width):
                        if shadow_board[r][c] < 0:
                            shadow_board[row][column] += 1
        return shadow_board

    def is_solvable(self, shadow_board: list[list[int]], first_row: int, first_column: int) -> bool:
        """Return True if the shadow_board is solvable with the given first_click.

        :param shadow_board: the shadow_board
        :param first_row: the row of the first revealed tile
        :param first_column: the column of the first revealed tile
        :return: if the game is solvable
        """
        height = self.height
        width = self.width
        sweeper = self.sweeper
        squares_left = height * width - self.bombs
        safe_tiles: list[tuple[int, int]] = [(first_row, first_column)]
        while safe_tiles:
            for row, column in safe_tiles:
                info: int = shadow_board[row][column]
                if info == -1:  # This should not occur
                    print(first_row)
                    print(first_column)
                    print(shadow_board)
                sweeper.integrate_new_info(row, column, str(info))
                squares_left -= 1
            sweeper.calculate_board()
            safe_tiles = [(row, column) for row in range(height) for column in range(width) if
                          sweeper.board[row][column] == 'S']
        sweeper.reset()
        return squares_left == 0

    @abstractmethod
    def regular_click(self, row: int, column: int) -> None:
        """What happens if someone clicks this square.

        :param row: the row of the clicked square
        :param column: the column of the clicked square
        """

    def clear_neighbours(self, row: int, column: int) -> None:
        """Reveal all non-flagged neighbouring squares.

        :param row: the row of the centre square
        :param column: the column of the centre square
        """
        for r, c in return_neighbours(row, column, self.height, self.width):
            if self.board[r][c] not in self.REVEALED_TILES.union({'F'}):
                self.regular_click(r, c)

    def flag_click(self, row: int, column: int) -> None:
        """What happens if someone clicks this square with flag mode.

        :param row: the row of the clicked square
        :param column: the column of the clicked square
        """
        if self.game_over:
            return

        label = self.board[row][column]
        # if the tile was flagged, question mark it
        if label == 'F':
            self.board[row][column] = '?'
            self.bombs_left += 1

        # if the tile was question marked, make it blank
        elif label == '?':
            self.board[row][column] = ''

        # if the tile is unrevealed, flag it
        elif label not in self.REVEALED_TILES:
            self.board[row][column] = 'F'
            self.bombs_left -= 1

    @abstractmethod
    def hint(self) -> None:
        """Give the player a hint."""

    @abstractmethod
    def set_easy(self) -> None:
        """Set the difficulty to easy and reset the game."""

    @abstractmethod
    def set_medium(self) -> None:
        """Set the difficulty to medium and reset the game."""

    @abstractmethod
    def set_hard(self) -> None:
        """Set the difficulty to hard and reset the game."""

    def game_lost(self):
        """Inform the player that they lost the game."""
        self.message = 'You lost...'
        self.game_over = True

    def game_won(self):
        """Inform the player that they won the game."""
        self.message = 'You won!'
        self.game_over = True

    @abstractmethod
    def reset(self) -> None:
        """Reset the playing field."""


class ClassicMinesweeper(Minesweeper):
    """A Minesweeper game that is guaranteed to be solvable without guessing."""
    REVEALED_TILES: frozenset[str] = {'0', '1', '2', '3', '4', '5', '6', '7', '8'}

    def __init__(self) -> None:
        """Initialize this Minesweeper's boards and attributes."""
        self.height = 9
        self.width = 9
        self.bombs = 10
        self.board = [[''] * self.height for _ in range(self.width)]
        self.shadow_board = []
        self.squares_left = self.height * self.width - self.bombs
        self.bombs_left = self.bombs
        self.sweeper = Sweeper()
        self.message = ''
        self.game_over = False

    def create_shadow_board(self, clicked_row: int, clicked_column: int) -> list[list[int]]:
        """Create and return a game shadow board such that the clicked square has a value of 0.

        :param clicked_row: the row of the clicked square
        :param clicked_column: the column of the clicked square
        """
        bombs_to_place = self.bombs
        height = self.height
        width = self.width
        squares_to_be_covered = height * width - len(return_neighbours(clicked_row, clicked_column, height, width))

        shadow_board = [[0] * width for _ in range(height)]
        for row in range(height):
            for column in range(width):
                if abs(clicked_row - row) > 1 or abs(clicked_column - column) > 1:
                    if random() < bombs_to_place / squares_to_be_covered:
                        shadow_board[row][column] = -1
                        bombs_to_place -= 1
                    squares_to_be_covered -= 1

        return self.init_bomb_counts(shadow_board)

    def regular_click(self, row: int, column: int) -> None:
        """What happens if someone clicks this square.

        :param row: the row of the clicked square
        :param column: the column of the clicked square
        """
        if self.game_over:
            return

        board = self.board
        clicked_square = board[row][column]
        # if this is a revealed number with the appropriate number of flags around it, clear the non-flagged
        # neighbouring tiles
        if clicked_square in ClassicMinesweeper.REVEALED_TILES:
            flagged_neighbours = 0
            for r, c in return_neighbours(row, column, self.height, self.width):
                if board[r][c] == 'F':
                    flagged_neighbours += 1
            if flagged_neighbours == int(clicked_square):
                self.clear_neighbours(row, column)

        # if the square is not revealed, flagged, or question marked
        elif clicked_square not in ('F', '?'):
            # if it's a new game, setup the underlying board and then continue with the click
            if self.squares_left == self.height * self.width - self.bombs:
                do = True
                shadow_board = []
                while do:
                    shadow_board = self.create_shadow_board(row, column)
                    do = not self.is_solvable(shadow_board, row, column)
                self.shadow_board = shadow_board
            # if it's a bomb, print out 'B' and have them lose the game
            if self.shadow_board[row][column] == -1:
                board[row][column] = 'B'
                self.sweeper.integrate_new_info(row, column, 'B')
                self.game_lost()
            # otherwise print out the number
            else:
                board[row][column] = str(self.shadow_board[row][column])
                # integrate that info into the sweeper
                self.sweeper.integrate_new_info(row, column, str(board[row][column]))
                self.squares_left -= 1
                # if all the non-bomb squares have been revealed, we have a winner
                if self.squares_left == 0:
                    self.game_won()
                # if a zero was clicked, reveal everything around it
                if self.shadow_board[row][column] == 0:
                    self.clear_neighbours(row, column)

    def hint(self) -> None:
        """Give the player a hint that they could've figured out if one exists."""
        if self.game_over:
            return

        self.sweeper.calculate_board()
        hint_squares = [(row, column) for row in range(self.height) for column in range(self.width) if
                        self.sweeper.board[row][column] == 'S' or (
                                self.sweeper.board[row][column] == 'B' and self.board[row][column] != 'F')]
        if hint_squares:  # This should always be a non-empty list during a game
            row, column = choice(hint_squares)
            self.board[row][column] = 'H'

    def set_easy(self) -> None:
        """Set the difficulty to easy and reset the game."""
        self.height = 9
        self.width = 9
        self.bombs = 10
        self.reset()

    def set_medium(self) -> None:
        """Set the difficulty to medium and reset the game."""
        self.height = 16
        self.width = 16
        self.bombs = 40
        self.reset()

    def set_hard(self) -> None:
        """Set the difficulty to hard and reset the game."""
        self.height = 16
        self.width = 30
        self.bombs = 99
        self.reset()

    def set_custom(self, height: int, width: int, bombs: int) -> None:
        """Set the custom difficulty and reset the game."""
        self.height = height
        self.width = width
        self.bombs = bombs
        self.reset()

    def reset(self) -> None:
        """Reset the game."""
        self.board = [[''] * self.width for _ in range(self.height)]
        self.shadow_board = []
        self.squares_left = self.height * self.width - self.bombs
        self.bombs_left = self.bombs
        self.message = ''
        self.game_over = False

        self.sweeper.height = self.height
        self.sweeper.width = self.width
        self.sweeper.bombs = self.bombs
        self.sweeper.reset()


class ThrillDigger(Minesweeper):
    """A Thrill Digger game.

    === Public Attributes ===
    RUPEE_TO_BOMBS:
        Maps rupee colours to the number of surrounding bombs.
    BOMBS_TO_RUPEE:
        Maps the number of surrounding bombs to rupee colour.
    rupoors:
        The number of non-lethal bombs.
    rupoors_left:
        The number of non-lethal bombs yet to be uncovered.
    """
    RUPEE_TO_BOMBS: dict[str, tuple[int]] = {'Green': (0,), 'Blue': (1, 2), 'Red': (3, 4),
                                             'Silver': (5, 6), 'Gold': (7, 8)}
    BOMBS_TO_RUPEE: dict[int, str] = {0: 'Green', 1: 'Blue', 2: 'Blue', 3: 'Red', 4: 'Red',
                                      5: 'Silver', 6: 'Silver', 7: 'Gold', 8: 'Gold'}
    REVEALED_TILES = {'Green', 'Blue', 'Red', 'Silver', 'Gold', 'Rupoor'}
    rupoors: int
    rupoors_left: int

    def __init__(self) -> None:
        """Initialize this Minesweeper's boards and attributes."""
        self.height = 4
        self.width = 5
        self.bombs = 4
        self.rupoors = 0
        self.board = [[''] * self.width for _ in range(self.height)]
        self.shadow_board = []
        self.squares_left = self.height * self.width - self.bombs
        self.bombs_left = self.bombs
        self.rupoors_left = self.rupoors
        self.sweeper = Sweeper(version='Thrill Digger')
        self.message = ''
        self.game_over = False

    def create_shadow_board(self) -> list[list[int]]:
        """Create and return a game shadow board."""
        bombs_to_place = self.bombs
        squares_to_be_covered = self.height * self.width

        shadow_board = [[0] * self.width for _ in range(self.height)]
        for row in range(self.height):
            for column in range(self.width):
                if random() < bombs_to_place / squares_to_be_covered:
                    shadow_board[row][column] = -1
                    bombs_to_place -= 1
                squares_to_be_covered -= 1

        return self.init_bomb_counts(shadow_board)

    def regular_click(self, row: int, column: int) -> None:
        """What happens if someone clicks this square.

        :param row: the row of the clicked square
        :param column: the column of the clicked square
        """
        if self.game_over:
            return

        clicked_square = self.board[row][column]
        # if this is a revealed number with the appropriate number of bomb marks around it, clear the other
        # neighbouring tiles
        if clicked_square in ('Green', 'Blue', 'Red', 'Silver', 'Gold'):
            flagged_neighbours = 0
            for r, c in return_neighbours(row, column, self.height, self.width):
                if self.board[r][c] in ('F', 'Rupoor'):
                    flagged_neighbours += 1
            if flagged_neighbours == ThrillDigger.RUPEE_TO_BOMBS[clicked_square][-1]:
                self.clear_neighbours(row, column)

        # if the square is not revealed, flagged, or question marked
        elif clicked_square not in ('Rupoor', 'F', '?'):
            # if it's a new game, setup the underlying board and then continue with the click
            if self.squares_left == self.height * self.width - self.bombs:
                self.shadow_board = self.create_shadow_board()
            # if it's a bomb
            if self.shadow_board[row][column] == -1:
                # if it's non-lethal, print out 'Rupoor'
                if random() < self.rupoors_left / (self.bombs - self.rupoors + self.rupoors_left):
                    self.board[row][column] = 'Rupoor'
                    self.bombs_left -= 1
                    self.sweeper.integrate_new_info(row, column, 'Rupoor')
                # otherwise, print out 'B' and have them lose the game
                else:
                    self.board[row][column] = 'B'
                    self.sweeper.integrate_new_info(row, column, 'B')
                    self.game_lost()
            # otherwise print out the rupee colour
            else:
                uncovered_square = ThrillDigger.BOMBS_TO_RUPEE[self.shadow_board[row][column]]
                self.board[row][column] = uncovered_square
                # integrate that info into the sweeper
                self.sweeper.integrate_new_info(row, column, uncovered_square)
                self.squares_left -= 1
                # if all the non-bomb squares have been revealed, we have a winner
                if self.squares_left == 0:
                    self.game_won()
                # if a zero was clicked, reveal everything around it
                if self.shadow_board[row][column] == 0:
                    self.clear_neighbours(row, column)

    def hint(self) -> None:
        """Print the Sweeper analysis to the board."""
        if self.game_over:
            return

        self.sweeper.calculate_board()
        for row in range(self.height):
            for column in range(self.width):
                if self.board[row][column] not in ThrillDigger.REVEALED_TILES:
                    self.board[row][column] = self.sweeper.board[row][column]

    def set_easy(self) -> None:
        """Set the difficulty to easy and reset the game."""
        self.height = 4
        self.width = 5
        self.bombs = 4
        self.rupoors = 0
        self.reset()

    def set_medium(self) -> None:
        """Set the difficulty to medium and reset the game."""
        self.height = 5
        self.width = 6
        self.bombs = 8
        self.rupoors = 4
        self.reset()

    def set_hard(self) -> None:
        """Set the difficulty to hard and reset the game."""
        self.height = 5
        self.width = 8
        self.bombs = 16
        self.rupoors = 8
        self.reset()

    def set_custom(self, height: int, width: int, bombs: int, rupoors: int = 0) -> None:
        """Set the custom difficulty and reset the game."""
        self.height = height
        self.width = width
        self.bombs = bombs
        self.rupoors = rupoors
        self.reset()

    def reset(self) -> None:
        """Reset the game."""
        self.board = [[''] * self.width for _ in range(self.height)]
        self.shadow_board = []
        self.squares_left = self.height * self.width - self.bombs
        self.bombs_left = self.bombs
        self.rupoors_left = self.rupoors
        self.message = ''
        self.game_over = False

        self.sweeper.height = self.height
        self.sweeper.width = self.width
        self.sweeper.bombs = self.bombs
        self.sweeper.reset()


class MinesweeperWindow:
    """The UI for the Minesweeper class.

    === Public Attributes ===
    classic_colour_key:
        What colour should go with which text for the classic Minesweeper game.
    thrill_digger_colour_key:
        What colour should go with which text for the Thrill Digger game.
    game:
        The Minesweeper game displayed by this window.
    root:
        The background.
    bombs_left_label:
        A label whose text is the number of bombs minus the number of bomb marks.
    flag_mode:
        A boolean representing if the player is in flag mode.
    flag_label:
        A label that prints if the player is in flag mode.
    field:
        The container for the mine field.
    board:
        A list of lists of buttons making up the game board.
    message:
        A message telling the user if they won or lost.
    """
    CLASSIC_COLOUR_KEY: dict[str, str] = {'0': 'white', '1': 'blue', '2': 'green', '3': 'red', '4': 'navy',
                                          '5': 'firebrick4', '6': 'SeaGreen3', '7': 'black', '8': 'purple',
                                          'F': 'purple', '?': 'blue', 'B': 'red'}
    THRILL_DIGGER_COLOUR_KEY: dict[str, str] = {'Green': 'green', 'Blue': 'blue', 'Red': 'red', 'Silver': 'silver',
                                                'Gold': 'gold', 'Rupoor': 'black', 'F': 'purple', '?': 'blue',
                                                'B': 'red', 'B/R': 'red'}
    game: Minesweeper
    root: Tk
    bombs_left_label: Label
    flag_mode: bool
    flag_label: Label
    field: Frame
    board: list[list[Button]]
    message: StringVar

    def __init__(self) -> None:
        """Initialize this Minesweeper's boards and attributes.
        """
        self.game = ClassicMinesweeper()

        self.root = Tk()
        self.root.title('Minesweeper')

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

        self.bombs_left_label = Label(self.root, text=('Bombs left: ' + str(self.game.bombs_left).zfill(3)))
        self.bombs_left_label.grid(row=0)

        new_game_button = Button(self.root, text='New Game', command=self.reset)
        new_game_button.grid(row=0, column=1)

        self.flag_mode = False
        self.flag_label = Label(self.root, text='Flag Mode is off')
        self.flag_label.grid(row=0, column=2)

        self.field = Frame(self.root, bg='black')
        self.field.grid(row=1, column=0, columnspan=4)

        self.board = [[self.create_button(i, j) for j in range(self.game.width)] for i in range(self.game.height)]

        hint_button = Button(self.root, text='Hint', command=self.hint)
        hint_button.grid(row=2, column=0)

        self.message = StringVar()
        message_label = Label(self.root, textvariable=self.message)
        message_label.grid(row=2, column=1, columnspan=3)

        self.set_hard()

        self.root.bind("<Key>", self.process_keystroke)

        self.root.mainloop()

    def create_button(self, row: int, column: int) -> Button:
        """Create the game board button for the specified square.

        :param row: the row of the button
        :param column: the column of the button
        :return: the game board button for the specified square
        """

        def button_command():
            """Let the board know this button has been clicked."""
            self.click_button(row, column)

        button = Button(self.field, text='', width=1 if isinstance(self.game, ClassicMinesweeper) else 2,
                        highlightbackground='black', command=button_command)
        button.grid(row=row, column=column)
        return button

    def refresh_display(self) -> None:
        """Refresh the UI to match the Minesweeper game."""
        self.bombs_left_label['text'] = 'Bombs left: ' + str(self.game.bombs_left).zfill(3)

        for row in range(self.game.height):
            for column in range(self.game.width):
                button = self.board[row][column]
                button_text = self.game.board[row][column]
                button['text'] = button_text
                if isinstance(self.game, ThrillDigger):
                    button['highlightbackground'] = MinesweeperWindow.THRILL_DIGGER_COLOUR_KEY.get(button_text, 'black')
                else:
                    button['highlightbackground'] = MinesweeperWindow.CLASSIC_COLOUR_KEY.get(button_text, 'black')

        self.message.set(self.game.message)

        if self.game.game_over:
            self.disable_tiles()

    def click_button(self, row: int, column: int) -> None:
        """What happens if someone clicks this square.

        :param row: the row clicked
        :param column: the column clicked
        """
        if self.flag_mode:
            self.game.flag_click(row, column)
        else:
            self.game.regular_click(row, column)
        self.refresh_display()

    def process_keystroke(self, event) -> None:
        """Process a keystroke."""
        if event.char == 'f':
            self.flag_mode = True
            self.flag_label['text'] = 'Flag Mode is on'
        elif event.char == 'e':
            self.flag_mode = False
            self.flag_label['text'] = 'Flag Mode is off'

    def hint(self) -> None:
        """Give the player a hint that they could've figured out."""
        self.game.hint()
        self.refresh_display()

    def set_classic(self) -> None:
        """Set the game to be the classic version of Minesweeper."""
        self.game = ClassicMinesweeper()
        self.reset()

    def set_thrill_digger(self) -> None:
        """Set the game to be the Thrill Digger version of Minesweeper."""
        self.game = ThrillDigger()
        self.reset()

    def set_easy(self) -> None:
        """Set the difficulty to easy and reset the game."""
        self.game.set_easy()
        self.reset()

    def set_medium(self) -> None:
        """Set the difficulty to medium and reset the game."""
        self.game.set_medium()
        self.reset()

    def set_hard(self) -> None:
        """Set the difficulty to hard and reset the game."""
        self.game.set_hard()
        self.reset()

    def set_custom(self, height: int, width: int, bombs: int, rupoors: int = 0) -> None:
        """Set the custom difficulty and reset the game."""
        if isinstance(self.game, ThrillDigger):
            self.game.set_custom(height, width, bombs, rupoors)
        else:
            assert isinstance(self.game, ClassicMinesweeper)
            self.game.set_custom(height, width, bombs)
        self.reset()

    def disable_tiles(self) -> None:
        """Disable the playing tiles' buttons."""
        for row in self.board:
            for tile in row:
                tile['command'] = lambda: None

    def reset(self) -> None:
        """Reset the playing field."""
        self.game.reset()

        self.flag_mode = False
        self.flag_label['text'] = 'Flag Mode is off'

        # delete all the current playing tiles
        self.field.destroy()
        self.field = Frame(self.root, bg='black')
        self.field.grid(row=1, columnspan=4)

        self.board = [[self.create_button(i, j) for j in range(self.game.width)] for i in range(self.game.height)]

        self.refresh_display()


if __name__ == '__main__':
    MinesweeperWindow()
