""" JMetal Problems
"""
import random
from typing import Tuple, List
from jmetal.core.problem import Problem
from jmetal.core.solution import Solution

from ..ea import SolutionInterface, dominance_test
from ...util.process import Evaluable

# define EA representation for OU
IntTupple = Tuple[int]


class KOSolution(Solution[int], SolutionInterface):
    """ Class representing a KO solution """

    def __init__(self, lower_bound: int, upper_bound: int, number_of_variables: int, number_of_objectives: int,
                 number_of_constraints: int = 0):
        super(KOSolution, self).__init__(number_of_variables,
                                         number_of_objectives, number_of_constraints)
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def __eq__(self, solution) -> bool:
        if isinstance(solution, self.__class__):
            return self.variables.sort() == solution.variables.sort()
        return False

    # JMetal consideres all problems as minimization
    # Based on pareto dominance

    def __gt__(self, solution) -> bool:
        if isinstance(solution, self.__class__):
            return dominance_test(self, solution, maximize=False) == 1
        return False

    def __lt__(self, solution) -> bool:
        if isinstance(solution, self.__class__):
            return dominance_test(self, solution, maximize=False) == -1
        return False

    def __ge__(self, solution) -> bool:
        if isinstance(solution, self.__class__):
            return dominance_test(self, solution, maximize=False) != -1
        return False

    def __le__(self, solution) -> bool:
        if isinstance(solution, self.__class__):
            return dominance_test(self, solution, maximize=False) != 1
        return False

    def __copy__(self):
        new_solution = KOSolution(
            self.lower_bound,
            self.upper_bound,
            self.number_of_variables,
            self.number_of_objectives)
        new_solution.objectives = self.objectives[:]
        new_solution.variables = self.variables[:]
        new_solution.constraints = self.constraints[:]
        new_solution.attributes = self.attributes.copy()

        return new_solution

    def get_representation(self):
        """
        Returns a set representation of the candidate
        """
        return set(self.variables)

    def get_fitness(self):
        """
        Returns the candidate fitness list
        """
        return self.objectives

    def __str__(self):
        return " ".join((self.variables))


class OUSolution(Solution[IntTupple], SolutionInterface):
    """
    Class representing a Over/Under expression solution.
    """

    def __init__(self, lower_bound: List[int], upper_bound: List[int], number_of_variables: int,
                 number_of_objectives: int):
        super(OUSolution, self).__init__(number_of_variables,
                                         number_of_objectives)
        self.upper_bound = upper_bound
        self.lower_bound = lower_bound

    def __eq__(self, solution) -> bool:
        if isinstance(solution, self.__class__):
            return self.variables.sort() == solution.variables.sort()
        return False

    # JMetal consideres all problems as minimization

    def __gt__(self, solution) -> bool:
        if isinstance(solution, self.__class__):
            return dominance_test(self, solution, maximize=False) == 1
        return False

    def __lt__(self, solution) -> bool:
        if isinstance(solution, self.__class__):
            return dominance_test(self, solution, maximize=False) == -1
        return False

    def __ge__(self, solution) -> bool:
        if isinstance(solution, self.__class__):
            return dominance_test(self, solution, maximize=False) != -1
        return False

    def __le__(self, solution) -> bool:
        if isinstance(solution, self.__class__):
            return dominance_test(self, solution, maximize=False) != 1
        return False

    def __copy__(self):
        new_solution = OUSolution(
            self.lower_bound,
            self.upper_bound,
            self.number_of_variables,
            self.number_of_objectives
        )
        new_solution.objectives = self.objectives[:]
        new_solution.variables = self.variables[:]
        new_solution.constraints = self.constraints[:]
        new_solution.attributes = self.attributes.copy()

        return new_solution

    def get_fitness(self):
        """
        Returns the candidate fitness list
        """
        return self.objectives

    def __str__(self):
        return " ".join((self.variables))


class JMetalKOProblem(Problem[KOSolution], Evaluable):

    def __init__(self, problem, initial_polulation):
        """JMetal OU problem. Encapsulates a MEWpy problem
        so that it can be used in jMetal.
        """
        self.problem = problem
        self.number_of_objectives = len(self.problem.fevaluation)
        self.obj_directions = []
        self.obj_labels = []
        for f in self.problem.fevaluation:
            self.obj_labels.append(str(f))
            if f.maximize:
                self.obj_directions.append(self.MAXIMIZE)
            else:
                self.obj_directions.append(self.MINIMIZE)
        self.initial_polulation = initial_polulation
        self.__next_ini_sol = 0

    def create_solution(self) -> KOSolution:
        if self.__next_ini_sol < len(self.initial_polulation):
            solution = self.problem.encode(self.initial_polulation[self.__next_ini_sol])
            self.__next_ini_sol += 1
        else:
            solution = self.problem.generator(random, None)
        new_solution = KOSolution(
            self.problem.bounder.lower_bound,
            self.problem.bounder.upper_bound,
            len(solution),
            self.problem.number_of_objectives)
        new_solution.variables = list(solution)
        return new_solution

    def reset_initial_population_counter(self):
        """ Resets the pointer to the next initial population element.
        This strategy is used to overcome the unavailable seeding API in jMetal.
        """
        self.__next_ini_sol = 0

    def get_constraints(self, solution):
        return self.problem.decode(set(solution.variables))

    def evaluate(self, solution: KOSolution) -> KOSolution:
        candidate = set(solution.variables)
        p = self.problem.evaluate_solution(candidate)
        for i in range(len(p)):
            # JMetalPy only deals with minimization problems
            if self.obj_directions[i] == self.MAXIMIZE:
                solution.objectives[i] = -1 * p[i]
            else:
                solution.objectives[i] = p[i]
        return solution

    def evaluator(self, candidates, *args):
        res = []
        for candidate in candidates:
            res.append(self.evaluate(candidate))
        return res

    def get_name(self) -> str:
        return self.problem.get_name()


class JMetalOUProblem(Problem[OUSolution], Evaluable):

    def __init__(self, problem, initial_polulation=[]):
        """JMetal OU problem. Encapsulates a MEWpy problem
        so that it can be used in jMetal.
        """
        self.problem = problem
        self.number_of_objectives = len(self.problem.fevaluation)
        self.obj_directions = []
        self.obj_labels = []
        for f in self.problem.fevaluation:
            self.obj_labels.append(str(f))
            if f.maximize:
                self.obj_directions.append(self.MAXIMIZE)
            else:
                self.obj_directions.append(self.MINIMIZE)
        self.initial_polulation = initial_polulation
        self.__next_ini_sol = 0

    def create_solution(self) -> OUSolution:
        if self.__next_ini_sol < len(self.initial_polulation):
            solution = self.problem.encode(self.initial_polulation[self.__next_ini_sol])
            self.__next_ini_sol += 1
        else:
            solution = self.problem.generator(random, None)
        new_solution = OUSolution(
            self.problem.bounder.lower_bound,
            self.problem.bounder.upper_bound,
            len(solution),
            self.problem.number_of_objectives)
        new_solution.variables = list(solution)
        return new_solution

    def reset_initial_population_counter(self):
        self.__next_ini_sol = 0

    def get_constraints(self, solution):
        return self.problem.decode(set(solution.variables))

    def evaluate(self, solution: KOSolution) -> KOSolution:
        candidate = set(solution.variables)
        p = self.problem.evaluate_solution(candidate)
        for i in range(len(p)):
            # JMetalPy only deals with minimization problems
            if self.obj_directions[i] == self.MAXIMIZE:
                solution.objectives[i] = -1 * p[i]
            else:
                solution.objectives[i] = p[i]
        return solution

    def evaluator(self, candidates, *args):
        res = []
        for candidate in candidates:
            res.append(self.evaluate(candidate))
        return res

    def get_name(self) -> str:
        return self.problem.get_name()
