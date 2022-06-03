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