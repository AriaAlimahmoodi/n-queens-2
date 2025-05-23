import tkinter
from PIL._tkinter_finder import tk
import tkinter as tk
import threading
from collections import deque

from algorithms.genetic import GeneticFastGPU as GeneticFast
from algorithms.backtracking import solve_n_queens_bt



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



def run_backtracking():
    try:
        n = int(entry.get())
        solution = solve_n_queens_bt(n)
        if solution is not None:
            board = [[0] * n for _ in range(n)]
            for row, col in enumerate(solution):
                board[row][col] = 1
            display_result(board)
            result_label.config(text="Solved with Backtracking")
        else:
            result_label.config(text="No solution found (Backtracking)")
    except ValueError:
        result_label.config(text="Enter a valid number")

def run_genetic_thread():
    try:
        n = int(entry.get())
        solver = GeneticFast(n)
        solution = solver.solve()
        if solution:
            board = [[0] * n for _ in range(n)]
            for col, row in enumerate(solution):
                board[row][col] = 1
            root.after(0, lambda: display_result(board))
            root.after(0, lambda: result_label.config(text="Solved with Genetic Algorithm"))
        else:
            root.after(0, lambda: result_label.config(text="No solution found (Genetic)"))
    except ValueError:
        root.after(0, lambda: result_label.config(text="Enter a valid number"))

def run_genetic():
    thread = threading.Thread(target=run_genetic_thread)
    thread.start()

def run_mac():
    try:
        n = int(entry.get())
        solution = solve_n_queens_mac_optimized(n)
        if solution:
            board = [[0] * n for _ in range(n)]
            for col, row in solution.items():
                board[row][col] = 1
            display_result(board)
            result_label.config(text="Solved with CSP MAC")
        else:
            result_label.config(text="No solution found (MAC)")
    except ValueError:
        result_label.config(text="Enter a valid number")



canvas = None
result_frame = None

def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

def display_result(board):
    for widget in result_frame.winfo_children():
        widget.destroy()
    n = len(board)

    cell_size = 25 if n <= 20 else (15 if n <= 50 else 8)
    font_size = cell_size - 10 if cell_size > 10 else 6

    for i in range(n):
        for j in range(n):
            color = "#f0d9b5" if (i + j) % 2 == 0 else "#b58863"
            cell = tk.Label(result_frame, width=2, height=1,
                            font=("Arial", font_size, "bold"),
                            bg=color,
                            text="♛" if board[i][j] else "")
            if board[i][j]:
                cell.config(fg="red")
            cell.grid(row=i, column=j, sticky="nsew")

    for i in range(n):
        result_frame.grid_rowconfigure(i, weight=1, minsize=cell_size)
        result_frame.grid_columnconfigure(i, weight=1, minsize=cell_size)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("N-Queens Solver (Backtracking, Genetic, CSP MAC)")

    root.geometry("900x900")


    entry_label = tk.Label(root, text="Enter N (e.g. 8):")
    entry_label.pack(pady=5)

    entry = tk.Entry(root)
    entry.pack(pady=5)

    solve_bt_btn = tk.Button(root, text="Solve with Backtracking", command=run_backtracking)
    solve_bt_btn.pack(pady=5)

    solve_gen_btn = tk.Button(root, text="Solve with Genetic Algorithm", command=run_genetic)
    solve_gen_btn.pack(pady=5)

    solve_mac_btn = tk.Button(root, text="Solve with CSP (MAC)", command=run_mac)
    solve_mac_btn.pack(pady=5)

    result_label = tk.Label(root, text="", fg="blue")
    result_label.pack(pady=5)


    canvas = tk.Canvas(root)
    scrollbar_y = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollbar_x = tk.Scrollbar(root, orient="horizontal", command=canvas.xview)

    canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

    scrollbar_y.pack(side="right", fill="y")
    scrollbar_x.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True)

    result_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=result_frame, anchor='nw')

    result_frame.bind("<Configure>", on_frame_configure)

    root.mainloop()
