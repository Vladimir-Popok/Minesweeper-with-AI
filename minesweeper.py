import itertools
import random


class Minesweeper():

    def __init__(self, height=8, width=8, mines=8):

        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        return self.mines_found == self.mines


class Sentence():
    """
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return self.cells
        return None

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        return None

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def sentence(self, cell):
        cells = set()
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    cells.add((i, j))
        return cells

    def check(self, sentence):
        if sentence is None:
            return
        safe = sentence.known_safes()
        if safe is not None:
            safe_2 = safe.copy()
            for i in safe_2:
                self.mark_safe(i)
        mines = sentence.known_mines()
        if mines is not None:
            mines_2 = mines.copy()
            for i in mines_2:
                self.mark_mine(i)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.
        """
        self.moves_made.add(cell)
        self.safes.add(cell)
        cell_set = self.sentence(cell)

        cell_collection = cell_set.copy()
        for i in cell_collection:

            if i in self.safes:
                cell_set.discard(i)
            elif i in self.mines:
                cell_set.discard(i)
                count -= 1
        sentence = Sentence(cell_set, count)

        self.check(sentence)

        self.knowledge.append(sentence)
        for safe_cell in self.safes:
            self.mark_safe(safe_cell)
        for mine_cell in self.mines:
            self.mark_mine(mine_cell)

        copy_knowledge = self.knowledge.copy()
        for sent in copy_knowledge:
            cpy_sent = sent.cells.copy()
            if sent.count == 0:
                for c in cpy_sent:
                    self.safes.add(c)
                    sent.mark_safe(c)
            elif len(sent.cells) == sent.count:
                for c in cpy_sent:
                    self.mines.add(c)
                    sent.mark_mine(c)
            if len(sent.cells) == 0:
                self.knowledge.remove(sent)
        copy_knowledge = self.knowledge.copy()

        for set_o in copy_knowledge:
            for set_s in copy_knowledge:
                if set_o == set_s:
                    continue

                elif set_s.cells < set_o.cells:
                    new_set = set_o.cells - set_s.cells
                    new_count = set_o.count - set_s.count
                    new_sentence = Sentence(new_set, new_count)
                    if set_s in self.knowledge:
                        self.knowledge.remove(set_s)
                    self.knowledge.append(new_sentence)
                    self.check(new_sentence)

        for i in self.knowledge:
            print(i)
        print()
        print(self.mines)


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.
        """
        for move in self.safes:
            if move not in self.moves_made:
                return move
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        """
        pos_moves = []
        for i in range(self.height):
            for j in range(self.width):
                move = (i, j)
                if move not in self.mines and move not in self.moves_made:
                    pos_moves.append(move)
        if len(pos_moves) != 0:
            move = random.choice(pos_moves)
            print(move)
            return move
        return None


