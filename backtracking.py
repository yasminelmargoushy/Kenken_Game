identity = lambda x: x

def first(iterable, default=None):
    try:
        return iterable[0]
    except IndexError:
        return default
    except TypeError:
        return next(iterable, default)

class backtraking:

    def __init__(self, variables, domains, neighbors, constraints):
        variables = variables or list(domains.keys())

        self.variables = variables
        self.domains = domains
        self.neighbors = neighbors
        self.constraints = constraints
        self.initial = ()
        self.curr_domains = None
        self.nassigns = 0

    def assign(self, var, val, assignment):
        assignment[var] = val
        self.nassigns += 1

    def unassign(self, var, assignment):
        if var in assignment:
            del assignment[var]

    def nconflicts(self, var, val, assignment):
        def conflict(var2):
            return (var2 in assignment and
                    not self.constraints(var, val, var2, assignment[var2]))
        return sum(bool(x) for x in (conflict(v) for v in self.neighbors[var]))

    def result(self, state, action):
        (var, val) = action
        return state + ((var, val),)

    def goal_test(self, state):
        assignment = dict(state)
        return (len(assignment) == len(self.variables)
                and all(self.nconflicts(variables, assignment[variables], assignment) == 0
                        for variables in self.variables))

    def support_pruning(self):
        if self.curr_domains is None:
            self.curr_domains = {v: list(self.domains[v]) for v in self.variables}

    def suppose(self, var, value):
        self.support_pruning()
        removals = [(var, a) for a in self.curr_domains[var] if a != value]
        self.curr_domains[var] = [value]
        return removals

    def prune(self, var, value, removals):
        self.curr_domains[var].remove(value)
        if removals is not None:
            removals.append((var, value))

    def choices(self, var):
        return (self.curr_domains or self.domains)[var]

    def infer_assignment(self):
        self.support_pruning()
        return {v: self.curr_domains[v][0]
                for v in self.variables if 1 == len(self.curr_domains[v])}

    def restore(self, removals):
        for B, b in removals:
            self.curr_domains[B].append(b)


def AC3(backtraking, queue=None, removals=None):
    if queue is None:
        queue = [(Xi, Xk) for Xi in backtraking.variables for Xk in backtraking.neighbors[Xi]]
    backtraking.support_pruning()
    while queue:
        (Xi, Xj) = queue.pop()
        if revise(backtraking, Xi, Xj, removals):
            if not backtraking.curr_domains[Xi]:
                return False
            for Xk in backtraking.neighbors[Xi]:
                if Xk != Xj:
                    queue.append((Xk, Xi))
    return True


def revise(backtraking, Xi, Xj, removals):
    revised = False
    for x in backtraking.curr_domains[Xi][:]:
        # If Xi=x conflicts with Xj=y for every possible y, eliminate Xi=x
        if all(not backtraking.constraints(Xi, x, Xj, y) for y in backtraking.curr_domains[Xj]):
            backtraking.prune(Xi, x, removals)
            revised = True
    return revised

def first_unassigned_variable(assignment, backtraking):
    return first([var for var in backtraking.variables if var not in assignment])


def unordered_domain_values(var, assignment, backtraking):
    return backtraking.choices(var)


def no_inference(backtraking, var, value, assignment, removals):
    return True


def forward_checking(backtraking, var, value, assignment, removals):
    backtraking.support_pruning()
    for B in backtraking.neighbors[var]:
        if B not in assignment:
            for b in backtraking.curr_domains[B][:]:
                if not backtraking.constraints(var, value, B, b):
                    backtraking.prune(B, b, removals)
            if not backtraking.curr_domains[B]:
                return False
    return True


def mac(backtraking, var, value, assignment, removals):
    return AC3(backtraking, [(X, var) for X in backtraking.neighbors[var]], removals)


def backtracking_search(backtraking,
                        select_unassigned_variable=first_unassigned_variable,
                        order_domain_values=unordered_domain_values,
                        inference=no_inference):

    def backtrack(assignment):
        if len(assignment) == len(backtraking.variables):
            return assignment
        var = select_unassigned_variable(assignment, backtraking)
        for value in order_domain_values(var, assignment, backtraking):
            if 0 == backtraking.nconflicts(var, value, assignment):
                backtraking.assign(var, value, assignment)
                removals = backtraking.suppose(var, value)
                if inference(backtraking, var, value, assignment, removals):
                    result = backtrack(assignment)
                    if result is not None:
                        return result
                backtraking.restore(removals)
        backtraking.unassign(var, assignment)
        return None

    result = backtrack({})
    #assert result is None or backtraking.goal_test(result)
    return result