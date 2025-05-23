def solve_n_queens_bt(n):
    board = []
    cols = [False] * n
    diag1 = [False] * (2 * n - 1)
    diag2 = [False] * (2 * n - 1)
    solution = []

    def backtrack(row):
        if row == n:
            solution.extend(board)
            return True
        for col in range(n):
            if cols[col] or diag1[row + col] or diag2[row - col + n - 1]:
                continue
            cols[col] = diag1[row + col] = diag2[row - col + n - 1] = True
            board.append(col)
            if backtrack(row + 1):
                return True
            board.pop()
            cols[col] = diag1[row + col] = diag2[row - col + n - 1] = False
        return False

    backtrack(0)
    return solution if solution else None
