import csp
from timeit import default_timer as timer
from sys import stderr
from itertools import product, permutations
from functools import reduce
from random import random, shuffle, randint, choice
from time import time
from csv import writer
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


def operation(op):

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


def adjc(line_1, line_2):
    x1, y1 = line_1
    x2, y2 = line_2
    dx, dy = x1 - x2, y1 - y2
    return (dx == 0 and abs(dy) == 1) or (dy == 0 and abs(dx) == 1)


def ken_generator(size):
    game = [[((i + j) % size) + 1 for i in range(size)] for j in range(size)]
    print(game)
    for _ in range(size):
        shuffle(game)

    for i1 in range(size):
        for j1 in range(size):
            if random() > 0.5:
                for r in range(size):
                    game[r][i1], game[r][j1] = game[r][j1], game[r][i1]

    game = {(j + 1, i + 1): game[i][j] for i in range(size) for j in range(size)}
    print(game)
    not_cg = sorted(game.keys(), key=lambda var: var[1])

    cages = []
    while not_cg:

        cages.append([])

        csize = randint(1, 4)

        square = not_cg[0]

        not_cg.remove(square)

        cages[-1].append(square)

        for _ in range(csize - 1):

            adjs = [other for other in not_cg if adjc(square, other)]

            square = choice(adjs) if adjs else None

            if not square:
                break

            not_cg.remove(square)
            
            cages[-1].append(square)
            
        csize = len(cages[-1])
        if csize == 1:
            square = cages[-1][0]
            cages[-1] = ((square, ), '.', game[square])
            continue
        elif csize == 2:
            fst, snd = cages[-1][0], cages[-1][1]
            if game[fst] / game[snd] > 0 and not game[fst] % game[snd]:
                op = "/" # choice("+-*/")
            else:
                op = "-" # choice("+-*")
        else:
            op = choice("+*")

        target = reduce(operation(op), [game[square] for square in cages[-1]])

        cages[-1] = (tuple(cages[-1]), op, int(target))

    return size, cages
    
    
def parsing_game(rows):
    if isinstance(rows, str):
        rows = rows.splitrows(True)

    try:
        content = rows[0][:-1]
        size = int(content)
    except:
        exit(11)

    cages = []
    for line in rows[1:]:
        content = line[:-1]
        if content:
            try:
                cl = eval(content)
                cages.append(cl)
            except:
                exit(12)

    return size, cages

def Valid(size, cages):
    outOfBounds = lambda xy: xy[0] < 1 or xy[0] > size or xy[1] < 1 or xy[1] > size

    mentioned = set()
    for i in range(len(cages)):
        members, op, target = cages[i]

        cages[i] = (tuple(set(members)), op, target)

        members, op, target = cages[i]

        if op not in "+-*/.":
            exit(1)

        problematic = list(filter(outOfBounds, members))
        if problematic:
            exit(2)

        problematic = mentioned.intersection(set(members))
        if problematic:
            exit(3)

        mentioned.update(set(members))

    indexes = range(1, size + 1)

    problematic = set([(x, y) for y in indexes for x in indexes]).difference(mentioned)

    if problematic:
        exit(4)


def conflicting(X, x, Y, y):
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
    for p in permutations(values):
        if reduce(operation, p) == target:
            return True

    return False


def Domain(size, cages):

    domains = {}
    for cl in cages:
        members, op, target = cl

        domains[members] = list(product(range(1, size + 1), repeat=len(members)))

        qualifies = lambda values: not conflicting(members, values, members, values) and validated(values, operation(op), target)

        domains[members] = list(filter(qualifies, domains[members]))

    return domains

def Neighbour(cages):
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

class Ken_Ken_Game(csp.CSP):

    def __init__(self, size, cages):
        Valid(size, cages)
        
        variables = [members for members, _, _ in cages]
        
        domains = Domain(size, cages)

        neighbors = Neighbour(cages)

        csp.CSP.__init__(self, variables, domains, neighbors, self.my_constarints)

        self.size = size
        self.checks = 0

    def my_constarints(self, A, a, B, b):
        self.checks += 1

        return A == B or not conflicting(A, a, B, b)


def solve_100_games(kenken, algorithm):
        kenken.checks = kenken.nassigns = 0
        dt = time()
        assignment = algorithm(kenken)
        dt = time() - dt
        return assignment, (kenken.checks, kenken.nassigns, dt)

def solve_100_board(output_file):
    bt         = lambda ken: csp.backtracking_search(ken)
    fc         = lambda ken: csp.backtracking_search(ken, inference=csp.forward_checking)
    mac        = lambda ken: csp.backtracking_search(ken, inference=csp.mac)

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