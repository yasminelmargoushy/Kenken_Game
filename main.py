import backtracking
from timeit import default_timer as timer
from itertools import product, permutations
from functools import reduce
from random import random, shuffle, randint, choice
from time import time
from csv import writer
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


def adjc(line_1, line_2):
    """ Get Adj cells """
    x1, y1 = line_1
    x2, y2 = line_2
    dx, dy = x1 - x2, y1 - y2
    return (dx == 0 and abs(dy) == 1) or (dy == 0 and abs(dx) == 1)
    

def operation(op):
    # Calculate target
    if op == '+':
        return lambda a, b: a + b
    elif op == '-':
        return lambda a, b: a - b
    elif op == '*':
        return lambda a, b: a * b
    elif op == '/':
        return lambda a, b: a / b
    else:
        return None


def ken_generator(size):
    """ Generate Kenken Board """
    game = [[((i + j) % size) + 1 for i in range(size)] for j in range(size)]

    # Shuffle values between cells
    # Shuffle Rows
    for _ in range(size):
        shuffle(game)
    # Shuffle Coloumns
    for i1 in range(size):
        for j1 in range(size):
            if random() > 0.5:
                for r in range(size):
                    game[r][i1], game[r][j1] = game[r][j1], game[r][i1]

    # Create a map between cell position and value
    game = {(j + 1, i + 1): game[i][j] for i in range(size) for j in range(size)}

    # Add All cells to as not_caged list
    not_cg = sorted(game.keys(), key=lambda var: var[1])
    # Set caged list to empty [2D list]
    cages = []
    while not_cg:
        # Add a new empty clique
        cages.append([])
        # Choose an initial random size for clique between 1 & 4
        csize = randint(1, 4)
        # Set root square to the first cell that is in the not_caged list
        square = not_cg[0]
        # Remove Selected root from not_caged list
        not_cg.remove(square)
        # Add Selected root to the last new empty clique
        cages[-1].append(square)
        # Loop on the initial random size for clique
        for _ in range(csize - 1):
            # Select all cell that are not_caged and adj to the square cell
            adjs = [other for other in not_cg if adjc(square, other)]
            # Select one of the above cells and make it the new square or if thnonee list is empty return
            square = choice(adjs) if adjs else None
            # If square equals none return [either no more cells or no more adj cells]
            if not square:
                break
            # Remove Selected Square from not_caged
            not_cg.remove(square)
            # Add Selected Square to the last current clique
            cages[-1].append(square)
        # Get the Actual final size of the clique
        csize = len(cages[-1])
        if csize == 1:
            # if 1 no operation
            square = cages[-1][0]
            cages[-1] = ((square, ), '.', game[square])
            continue
        elif csize == 2:
            # if 2 the division if remainder is zero otherwise subtraction
            fst, snd = cages[-1][0], cages[-1][1]
            if game[fst] / game[snd] > 0 and not game[fst] % game[snd]:
                op = "/" # choice("+-*/")
            else:
                op = "-" # choice("+-*")
        else:
            # else either summation or multiplication
            op = choice("+*")
        # Calculate target value based on the chosen operation
        target = reduce(operation(op), [game[square] for square in cages[-1]])
        # Create a tuple of the cliques, their operations & their target values
        cages[-1] = (tuple(cages[-1]), op, int(target))

    return size, cages


def Valid(size, cages):
    # Function that returns true if cell is within range
    outOfBounds = lambda xy: xy[0] < 1 or xy[0] > size or xy[1] < 1 or xy[1] > size

    mentioned = set()
    for i in range(len(cages)):
        members, op, target = cages[i]
        # Remove Duplicates
        cages[i] = (tuple(set(members)), op, target)

        members, op, target = cages[i]
        # Make Sure an operator is one of the following
        if op not in "+-*/.":
            exit(1)
        # Make Sure All Points are inside Bound of 0 -> Size
        problematic = list(filter(outOfBounds, members))
        if problematic:
            exit(2)
        # Make Sure Once a point is Taken it Can't be Taken Again by another Clique
        problematic = mentioned.intersection(set(members))
        if problematic:
            exit(3)

        mentioned.update(set(members))

    indexes = range(1, size + 1)
    # Make All Points are Taken and put in 1 clique
    problematic = set([(x, y) for y in indexes for x in indexes]).difference(mentioned)

    if problematic:
        exit(4)


def conflicting(X, x, Y, y):
    """ Make Sure not 2 different cells have the same values"""
    for i in range(len(X)):
        for j in range(len(Y)):
            mA = X[i]
            mB = Y[j]
            ma = x[i]
            mb = y[j]
            if (mA[0] == mB[0]) != (mA[1] == mB[1]) and ma == mb:
                return True
    return False


def validated(values, operation, target):
    """ Tests if the sent domain is valid to achieve target """
    for p in permutations(values):
        if reduce(operation, p) == target:
            return True

    return False


def Domain(size, cages):
    """Domain Function Returns the available Domains fo each clique"""
    domains = {}
    for cl in cages:
        members, op, target = cl

        domains[members] = list(product(range(1, size + 1), repeat=len(members)))

        qualifies = lambda values: not conflicting(members, values, members, values) and validated(values, operation(op), target)

        domains[members] = list(filter(qualifies, domains[members]))

    return domains


def Neighbour(cages):
    """ Returns list of the Neighbours to each clique [clique on the same row or coloumn of any cell in the clique] """
    neighbors = {}
    for members, _, _ in cages:
        neighbors[members] = []

    for A, _, _ in cages:
        for B, _, _ in cages:
            if A != B and B not in neighbors[A]:
                if conflicting(A, [-1] * len(A), B, [-1] * len(B)):
                    neighbors[A].append(B)
                    neighbors[B].append(A)

    return neighbors


class Ken_Ken_Game(backtracking.backtraking):

    def __init__(self, size, cages):
        # Make Sure generated board is valid
        Valid(size, cages)
        # Get All variables (cliques)
        variables = [members for members, _, _ in cages]
        # Get possible domain for variables that can achieve target value
        domains = Domain(size, cages)
        # Get Neighbours of each variable
        neighbors = Neighbour(cages)
        # Define call backtracking init function
        backtracking.backtraking.__init__(self, variables, domains, neighbors, self.my_constarints)

        self.size = size
        self.checks = 0

    def my_constarints(self, A, a, B, b):
        # Customize Constrains
        self.checks += 1
        return A == B or not conflicting(A, a, B, b)


def solve_100_games(kenken, algorithm):
        kenken.checks = kenken.nassigns = 0
        dt = time()
        assignment = algorithm(kenken)
        dt = time() - dt
        return assignment, (kenken.checks, kenken.nassigns, dt)


def solve_100_board(output_file):
    bt         = lambda ken: backtracking.backtracking_search(ken)
    fc         = lambda ken: backtracking.backtracking_search(ken, inference=backtracking.forward_checking)
    mac        = lambda ken: backtracking.backtracking_search(ken, inference=backtracking.mac)

    algorithms = {
        "BT": bt,
        "FC": fc,
        "MAC": mac
    }

    with open(output_file, "w+") as file:

        output_file = writer(file)

        output_file.writerow(["Algorithm", "Size", "Time"])
        for i in range (6):
            for name, algorithm in algorithms.items():
                for size in range(3, 9):
                    checks, assignments, dt = (0, 0, 0)
                    current_time1 = timer()
                    size, cages = ken_generator(size)

                    assignment, data = solve_100_games(Ken_Ken_Game(size, cages), algorithm)
                    current_time2 = timer()
                    my_time = current_time2 - current_time1
                    output_file.writerow([name, size, my_time])

#GUI
class KENKEN(QWidget):

   def __init__(self, parent = None):
      super(KENKEN, self).__init__(parent)

      self.title = "Kenken"
      self.top = 200
      self.left = 200
      self.width = 1500
      self.height = 1000
      self.paint_flag = 0
      self.sol_flag = 0

      self.btn = QPushButton("Enter the game size", self)
      self.btn.move(50,50)
      self.btn.clicked.connect(self.getint)

      self.btn2 = QPushButton("Solve Game", self)
      self.btn2.move(50,115)
      self.btn2.clicked.connect(self.s)

      self.label = QLabel('Choose the algorithm', self)
      self.label.move(50,80)

      self.dropDown = QComboBox(self)
      self.dropDown.setGeometry(QRect(250, 75, 300, 25))
      self.dropDown.setEditable(True)
      self.dropDown.lineEdit().setAlignment(Qt.AlignCenter)
      self.dropDown.addItems(["Choose the algorithm", "Backtracking", "Backtracking with forward checking", "Backtracking with arc"])

      self.dropDown.currentTextChanged.connect(self.current_text_changed)

      self.setWindowTitle("Kenken")
      self.InitWindow()


   def InitWindow(self):
       self.setGeometry(self.left, self.top, self.width, self.height)
       self.show()

   def current_text_changed(self, s):
       global alg
       alg = s

   def paintEvent(self, event):
       if self.paint_flag:
            colors = [QColor(255, 0, 0, 127), QColor(0, 0, 255, 127), QColor(0, 255, 0, 127), QColor(128, 0, 0, 127),
                    QColor(205, 92, 92, 127), QColor(255, 160, 122, 127), QColor(255, 165, 0, 127), QColor(190, 183, 107, 127),
                    QColor(128, 128, 0, 127), QColor(60, 179, 113, 127), QColor(32, 178, 170, 127), QColor(173, 216, 230, 127),
                    QColor(138, 43, 226, 127), QColor(139, 0, 139, 127), QColor(216, 191, 216, 127), QColor(221, 160, 221, 127),
                    QColor(199, 20, 133, 127), QColor(255, 20, 147, 127), QColor(245, 222, 180, 127), QColor(160, 82, 45, 127),
                    QColor(210, 133, 63, 127), QColor(119, 136, 153, 127), QColor(244, 164, 96, 127), QColor(143, 188, 143, 127),
                    QColor(255, 255, 255, 127), QColor(0, 130, 0, 127), QColor(196, 62, 68, 127), QColor(140, 100, 80, 127),
                    QColor(162, 221, 154, 127), QColor(0, 180, 110, 127), QColor(100, 100, 255, 127), QColor(150, 255, 200, 127),
                    QColor(60, 100, 154, 127), QColor(100, 60, 110, 127), QColor(60, 100, 60, 100), QColor(60, 200, 200, 60),
                    QColor(60, 255, 150, 0), QColor(200, 150, 110, 127), QColor(200, 80, 60, 200), QColor(120, 70, 200, 60)]

            painter = QPainter(self)
            w = 100
            h = 100
            c = 0
            recs = []
            for p in problem:
                for rec in p[0]:
                    rect = QRect(350 + w*rec[0],100 + h*rec[1], w, h)
                    recs.append(rect)
                    painter.setBrush(colors[c])
                    painter.drawRect(rect)
                    if rec == p[0][0]:
                        if p[-2] == ".":
                            painter.drawText(rect, Qt.AlignLeft, str(p[-1]))
                        else:
                            painter.drawText(rect, Qt.AlignLeft, str(p[-1])+str(p[-2]))
                c += 1

            if self.sol_flag:
                ind = 0
                for key, value in res.items():
                    for v in value:
                        painter.drawText(recs[ind], Qt.AlignCenter, str(v))
                        ind += 1

   def getint(self):
       """ Handle function of Game Size button """
       global x
       x,ok = QInputDialog.getInt(self,"Game Size","enter a number")
       global kenn
       kenn = do(x)
       self.paint_flag = 1
       self.sol_flag = 0
       self.update()

   def s(self):
       """ Handle function of Solve button """
       self.sol_flag = 1
       solve(kenn)
       self.update()


def do(num1):
    """ Generate and Validate Kenken Board"""
    size, cages = ken_generator(num1)
    global problem
    problem = []
    problem = cages
    ken = Ken_Ken_Game(size, cages)
    return ken


def solve(kenn):
    """ Function Called to Solve Kenken board """
    global res
    res = {}
    if (alg == "Backtracking"):
        assignment = backtracking.backtracking_search(kenn)
        res = assignment
    elif (alg == "Backtracking with forward checking"):
        assignment = backtracking.backtracking_search(kenn, inference=backtracking.forward_checking)
        res = assignment
    elif (alg == "Backtracking with arc"):
        assignment = backtracking.backtracking_search(kenn, inference=backtracking.mac)
        res = assignment


if __name__ == "__main__":

    app = QApplication(sys.argv)
    ex = KENKEN()
    ex.show()

    sys.exit(app.exec_())


"""
def printValue():
    pname = player_name.get()
    int_answer = int(pname)
    size, cages = ken_generator(int_answer)

    ken = Ken_Ken_Game(size, cages)

    assignment = csp.backtracking_search(ken,inference=csp.forward_checking)

    ken.display(assignment)



if __name__ == "__main__":
    #solve_100_game("kenken.csv")

    size, cages = ken_generator(4)

    ken = Ken_Ken_Game(size, cages)

    assignment = csp.backtracking_search(ken)
    assignemnt2 = csp.backtracking_search(ken, inference=csp.forward_checking)
    assignment3 = csp.backtracking_search(ken, inference=csp.mac)

    ken.display(assignment)
    ken.display(assignemnt2)
    ken.display(assignment3)
"""