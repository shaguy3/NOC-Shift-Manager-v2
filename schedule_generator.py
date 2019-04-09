from ortools.sat.python import cp_model


class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self, shifts, all_shifts, all_emps):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._shifts = shifts
        self._all_shifts = all_shifts
        self._all_emps = all_emps

    def on_solution_callback(self):
        print('Solution:')
        for shift in self._all_shifts:
            print(f"Shift no'{shift}:")
            for emp in self._all_emps:
                if self.Value(self._shifts[shift, emp]):
                    print(f'    employee {emp} is working.')
            print()


def assign_shifts():

    # Declaring the model.
    model = cp_model.CpModel()

    # Introducing the data.
    shifts = {}
    all_shifts = range(21)
    all_emps = range(7)

    # Declaring the variables.
    for shift in all_shifts:
        for emp in all_emps:
            shifts[(shift, emp)] = model.NewBoolVar(f'shift {shift}, employee {emp}.')

    # Adding constraints.
    # Constraint no'1: two employees in each shift except for night and weekend shifts, witch require one employee.
    for shift in all_shifts:
        if shift in [2, 5, 8, 11, 14, 16, 17, 18, 19, 20]:
            model.Add(sum(shifts[(shift, emp)] for emp in all_emps) == 1)
        else:
            model.Add(sum(shifts[(shift, emp)] for emp in all_emps) == 2)

    # Constraint no'2: each employee works between four and six shifts in a given week.
    min_number_of_shifts = 4
    max_number_of_shifts = 6
    for emp in all_emps:
        number_of_shifts_worked = sum(shifts[(shift, emp)] for shift in all_shifts)
        model.Add(min_number_of_shifts <= number_of_shifts_worked)
        model.Add(number_of_shifts_worked <= max_number_of_shifts)

    # Constraint no'3: The same employee cant work two consecutive shifts.
    for shift in range(20):
        for emp in all_emps:
            model.Add(shifts[(shift, emp)] + shifts[(shift + 1, emp)] <= 1)

    # Constraint no'4: No night after morning.
    for shift in [0, 3, 6, 9, 12, 15, 18]:
        for emp in all_emps:
            model.Add(shifts[(shift, emp)] + shifts[(shift + 2, emp)] <= 1)

    # Constraint no'5: Minimize 8-8.
    for shift in range(19):
        for emp in all_emps:
            model.AddProdEquality(0, (shifts[(shift, emp)], shifts[(shift + 2, emp)]))

    # Creating the solver and solving the model. the solver prints the first solution it finds.
    solver = cp_model.CpSolver()
    solution_printer = SolutionPrinter(shifts, all_shifts, all_emps)
    status = solver.SolveWithSolutionCallback(model, solution_printer)

    # Statistics.
    print('Statistics:')
    print(f'  - Solution status: {solver.StatusName(status)}')
    print(f'  - Wall time: {solver.WallTime()}')


def main():
    assign_shifts()


if __name__ == '__main__':
    main()
