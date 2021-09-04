import sys
import copy

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        local_domain = copy.deepcopy(self.domains)
        for var, vocab in local_domain.items():
            for word in vocab:
                if len(word) != var.length:
                    self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        vocab_x = copy.deepcopy(self.domains[x])
        overlap_x, overlap_y = self.crossword.overlaps[x, y]

        for word_x in vocab_x:
            # Default is to remove the word unless an overlap is present
            remove_word = True
            for word_y in self.domains[y]:
                # Keep word if an overlap, else remove if exhaust all possibilities
                if word_x[overlap_x] == word_y[overlap_y]:
                    remove_word = False
            if remove_word:
                self.domains[x].remove(word_x)

        # Check to see if the domain is the same as initial, return True if modified
        return len(self.domains[x]) != len(vocab_x)

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            arcs = []
            for v1 in self.domains.keys():
                for v2 in self.domains.keys():
                    if v1 != v2 and self.crossword.overlaps[v1, v2] is not None:
                        arcs.append((v1, v2))

        while len(arcs):
            x, y = arcs.pop()
            # Check if a revision can be made
            if self.revise(x, y):
                # If no more domains exist then exit since no solution possible
                if len(self.domains[x]) == 0:
                    return False
                else:
                    # Loop across all neighbors and add them for potential revisions
                    for z in self.crossword.neighbors(x):
                        if z == y:
                            continue
                        else:
                            arcs.append((z, x))
        return True


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if len(assignment) == 0:
            return False

        for val in self.crossword.variables:
            if assignment.get(val) is None:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # Check unique values
        if len(assignment) != len(set(assignment.values())):
            return False

        # Check words are correct length
        for var, word in assignment.items():
            if len(word) != var.length:
                return False

        # Check overlaps match
        for var_x, word_x in assignment.items():
            for var_y, word_y in assignment.items():
                if var_x == var_y:
                    continue
                else:
                    if self.crossword.overlaps[var_x, var_y] is not None:
                        overlap_x, overlap_y = self.crossword.overlaps[var_x, var_y]
                        if word_x[overlap_x] != word_y[overlap_y]:
                            return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        neighbors_local = copy.deepcopy(self.crossword.neighbors(var))

        for neighbor in self.crossword.neighbors(var):
            if assignment.get(neighbor) is not None:
                neighbors_local.remove(neighbor)

        domain_rank = len(self.domains[var]) * [0]

        for neighbor in neighbors_local:
            overlap_x, overlap_y = self.crossword.overlaps[var, neighbor]
            for i, word_x in enumerate(self.domains[var]):
                for word_y in self.domains[neighbor]:
                    if word_x[overlap_x] != word_y[overlap_y]:
                        domain_rank[i] += 1

        ranked_domain = [x for _, x in sorted(zip(domain_rank, self.domains[var]), key=lambda pair: pair[0])]
        return ranked_domain

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned = []
        domain_count = []

        # Keep track of each unassigned variable and corresponding domain count
        for var in self.crossword.variables:
            if assignment.get(var) is None:
                unassigned.append(var)
                domain_count.append(len(self.domains.get(var)))

        # If only one unassigned variable return it
        if len(unassigned) == 1:
            return unassigned[0]

        # Sort variables according to domain
        dom_sorted, var_sorted = zip(*sorted(zip(domain_count, unassigned), key=lambda pair: pair[0]))

        # If no tie return first variable
        if dom_sorted[0] != dom_sorted[1]:
            return var_sorted[0]
        else:
            # If a tie return variable with highest degree (number of neighbours)
            if len(self.crossword.neighbors(var_sorted[0])) > len(self.crossword.neighbors(var_sorted[1])):
                return var_sorted[0]
            else:
                return var_sorted[1]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)

        for value in self.order_domain_values(var, assignment):
            # Create a temporary version to test with
            new_assignment = assignment.copy()
            new_assignment[var] = value
            if self.consistent(new_assignment):
                assignment[var] = value
                result = self.backtrack(assignment)
                if result is not None:
                    return result
            # Remove assignment if not consistent
            assignment.pop(var, None)
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
