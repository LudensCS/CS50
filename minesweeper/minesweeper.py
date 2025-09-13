import itertools
from os import access
import random

#from minesweeper.runner import WIDTH


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
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

        # Keep count of nearby mines
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
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
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
        if len(self.cells)==self.count:
            return self.cells
        else:
            return set()
        # raise NotImplementedError

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count==0:
            return self.cells
        else:
            return set()
        # raise NotImplementedError

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1
        # raise NotImplementedError

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)
        # raise NotImplementedError


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

    def neighbor(self,cell):
        """
        Return the neighbors of cell
        """
        cells=set()
        for i in range(-1,2):
            for j in range(-1,2):
                if i!=0 or j!=0:
                    if min(cell[0]+i,cell[1]+j)>=0 and cell[0]+i<self.height and cell[1]+j<self.width:
                        cells.add((cell[0]+i,cell[1]+j))
        return cells

    def conclude(self):
        """
        Conclude new unit from the current knowledge base
        Return true if new info is found
        """
        newmines = set()
        newsafes = set()
        for s in self.knowledge:
            newmines.update(s.known_mines())
            newsafes.update(s.known_safes())
        for cell in newmines:
            self.mark_mine(cell)
        for cell in newsafes:
            self.mark_safe(cell)
        if len(newsafes) > 0 or len(newmines) > 0:
            return True
        else:
            return False

    def infer(self):
        """
        Infer new sentences from the current knowledge base
        Return true if new info is found
        """
        newknowledge = []
        for s1 in self.knowledge:
            for s2 in self.knowledge:
                if s1 == s2:
                    continue
                inc = True
                for cell in s1.cells:
                    if cell not in s2.cells:
                        inc = False
                        break
                if inc:
                    s = Sentence(s2.cells-s1.cells,s2.count-s1.count)
                    if (len(s.cells) != 0) and (s not in newknowledge) and (s not in self.knowledge):
                        newknowledge.append(s)
        self.knowledge.extend(newknowledge)
        if len(newknowledge) != 0:
            return True
        else:
            return False
    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        self.moves_made.add(cell)
        self.mark_safe(cell)
        cells = self.neighbor(cell)
        cells -= self.safes
        lazydel = set()
        for c in cells:
            if c in self.mines:
                count -= 1
                lazydel.add(c)
        cells -= lazydel
        s = Sentence(cells,count)
        if (s not in self.knowledge) and len(s.cells) != 0:
            self.knowledge.append(s)
        while True:
            valid = False
            valid |= self.conclude()
            valid |= self.infer()
            if not valid:
                break
        # raise NotImplementedError

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for cell in self.safes:
            if cell not in self.moves_made:
                return cell
        return None
        # raise NotImplementedError

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        access = set()
        for x in range(self.height):
            for y in range(self.width):
                if ((x,y) not in self.moves_made) and ((x,y) not in self.mines):
                    access.add((x,y))
        if len(access) == 0:
            return None
        else:
            return random.choice(list(access))
        # raise NotImplementedError
