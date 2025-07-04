import itertools
import random


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
        if self.count == len(self.cells):
            return self.cells
        else:
            return set()


    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """

        if self.count == 0:
            return self.cells
        else:
            return set()
        

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.count -= 1
            self.cells.remove(cell)


    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
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
        if cell in self.moves_made:
            return
        
        self.moves_made.add(cell)
        self.mark_safe(cell)

        surrounding_cells = set()

        for i in range(-1,2):
            for j in range(-1,2):
                if i == 0 and j == 0:
                    continue
                neighbor = (cell[0] + i, cell[1] + j)
                if 0 <= neighbor[0] < self.height and 0 <= neighbor[1] < self.width:
                    if neighbor in self.mines:
                        count -= 1
                        continue
                    elif neighbor in self.safes:
                        continue
                    elif neighbor not in self.moves_made:
                        surrounding_cells.add(neighbor)
        
        new_sentence = Sentence(surrounding_cells, count)
        
        if len(new_sentence.known_safes()) > 0:
            for s in new_sentence.known_safes():
                if s not in self.safes:
                    self.mark_safe(s)

        if len(new_sentence.known_mines()) > 0:
            for m in new_sentence.known_mines():
                if m not in self.mines:
                    self.mark_mine(m) 

        self.knowledge.append(new_sentence)

        KB = self.knowledge.copy()
        for sentence in KB:
            
            if len(sentence.known_safes()) > 0:
                safe_set = sentence.known_safes().copy()
                for s in safe_set:
                    if s not in self.safes:
                        self.mark_safe(s)

            if len(sentence.known_mines()) > 0:
                mine_set = sentence.known_mines().copy()
                for m in mine_set:
                    if m not in self.mines:
                        self.mark_mine(m) 

            for sentence_list in KB:
                if sentence == new_sentence:
                    continue
                
                diff = set()
                if sentence.cells.issubset(sentence_list.cells):
                    diff = sentence_list.cells.difference(sentence.cells)
                    if len(diff) > 0:
                        new_info = Sentence(diff, sentence_list.count - sentence.count)        
                elif sentence.cells.issuperset(sentence_list.cells):
                    diff = sentence.cells.difference(sentence_list.cells)
                    if len(diff) > 0:
                        new_info = Sentence(diff, sentence.count - sentence_list.count)
                
                if len(diff) > 0:
                    if new_info not in self.knowledge:
                        if len(new_info.known_safes()) > 0:
                            for s in new_info.known_safes():
                                self.mark_safe(s)

                        if len(new_info.known_mines()) > 0:
                            for mine in new_info.known_mines():
                                self.mark_mine(mine) 
                        
                        self.knowledge.append(new_info)


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

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        available_cells = set()
        for i in range(self.height):
            for j in range(self.width):
                cell = (i, j)

                # check if cell has already been done
                if cell in self.moves_made:
                    continue
                
                if cell in self.safes:
                    continue

                # check if cell is a mine
                if cell in self.mines:
                    continue

                available_cells.add(cell)
        
        if available_cells:
            return random.choice(list(available_cells))

        return None
        


