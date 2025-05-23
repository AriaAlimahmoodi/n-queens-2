from collections import deque

def solve_n_queens_mac_optimized(n):
    domains = {i: set(range(n)) for i in range(n)}
    constraints = [(i, j) for i in range(n) for j in range(n) if i != j]
    queue = deque(constraints)

    while queue:
        xi, xj = queue.popleft()
        if revise(domains, xi, xj):
            if not domains[xi]:
                return None
            for xk in range(n):
                if xk != xi and xk != xj:
                    queue.append((xk, xi))

    assignment = {}
    return backtrack_mac(assignment, domains, n)

def revise(domains, xi, xj):
    revised = False
    to_remove = set()
    for vi in domains[xi]:
        if not any(is_consistent(xi, vi, xj, vj) for vj in domains[xj]):
            to_remove.add(vi)
            revised = True
    domains[xi] -= to_remove
    return revised

def is_consistent(xi, vi, xj, vj):
    if vi == vj:
        return False
    if abs(xi - xj) == abs(vi - vj):
        return False
    return True

def backtrack_mac(assignment, domains, n):
    if len(assignment) == n:
        return assignment
    var = select_unassigned_var(assignment, domains)
    for value in sorted(domains[var]):
        if all(is_consistent(var, value, other, assignment[other]) for other in assignment):
            assignment[var] = value
            result = backtrack_mac(assignment, domains, n)
            if result:
                return result
            del assignment[var]
    return None

def select_unassigned_var(assignment, domains):
    unassigned = [v for v in domains if v not in assignment]
    return min(unassigned, key=lambda var: len(domains[var]))
