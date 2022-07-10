identity = lambda x: x

def first(iterable, default=None):
    """ Try to select frist element """
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
        """ Assign value to variable """
        assignment[var] = val
        self.nassigns += 1

    def unassign(self, var, assignment):
        """ Unassign value to variable (During Backtracking) """
        if var in assignment:
            del assignment[var]

    def nconflicts(self, var, val, assignment):
        """ Returns "0" if there is no conflicts with (var <= val) """
        def conflict(var2):
            """ Returns Conflict if the neighbouring variable (var2) is assigned and has a value equals (var) """
            return (var2 in assignment and
                    not self.constraints(var, val, var2, assignment[var2]))
        return sum(bool(x) for x in (conflict(v) for v in self.neighbors[var]))

    def goal_test(self, state):
        """ Returns True if we reached the final goal (All variables are assigned & no conflicts) """
        assignment = dict(state)
        return (len(assignment) == len(self.variables)
                and all(self.nconflicts(variables, assignment[variables], assignment) == 0
                        for variables in self.variables))

    def support_pruning(self):
        """ Put the domains in the curr_domains if curr_domains in none """
        if self.curr_domains is None:
            self.curr_domains = {v: list(self.domains[v]) for v in self.variables}

    def suppose(self, var, value):
        """ Remove All values from the domain of the selected (var) except the selected (value) """
        self.support_pruning()
        removals = [(var, a) for a in self.curr_domains[var] if a != value]
        self.curr_domains[var] = [value]
        return removals

    def prune(self, var, value, removals):
        self.curr_domains[var].remove(value)
        if removals is not None:
            removals.append((var, value))

    def choices(self, var):
        """ Returns the domain of the given variable """
        return (self.curr_domains or self.domains)[var]

    def restore(self, removals):
        """ Add removed domain values again """
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
    """ Returns the first un assigned variable """
    return first([var for var in backtraking.variables if var not in assignment])


def unordered_domain_values(var, assignment, backtraking):
    """ Return Domain of Variable """
    return backtraking.choices(var)


def no_inference(backtraking, var, value, assignment, removals):
    """ Used in backtracking only, when there is no inference [Forward Checking or Minimum Arc Consistancy] """
    return True


def forward_checking(backtraking, var, value, assignment, removals):
    backtraking.support_pruning()
    """ Perform Forward Checking """
    for B in backtraking.neighbors[var]:
        if B not in assignment:
            for b in backtraking.curr_domains[B][:]:
                # If Domain value in neigboring cell violates the constrain then remove value from Domain
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
        """ Inner Recursive Backtracking Function (For encapsulation) """
        if len(assignment) == len(backtraking.variables):
            return assignment
        # Select one of the unassigned variables
        var = select_unassigned_variable(assignment, backtraking)
        # Loop on the Domain values of the selected variable
        for value in order_domain_values(var, assignment, backtraking):
            # Check if no Conflicts
            if 0 == backtraking.nconflicts(var, value, assignment):
                # Assign (var <= value)
                backtraking.assign(var, value, assignment)
                # Change domain of selected variable to contain selected value only
                removals = backtraking.suppose(var, value)
                # Perform inference if either [Forward Checking or Minimum Arc Checking]
                if inference(backtraking, var, value, assignment, removals):
                    # Call Recursively
                    result = backtrack(assignment)
                    # if the selected value from the domain is the correct answer, then return it
                    if result is not None:
                        return result
                # otherwise try another value from the domain
                backtraking.restore(removals)
        # If all values of the domain failed backtrack
        backtraking.unassign(var, assignment)
        # return none to backtrack
        return None

    result = backtrack({})
    return result