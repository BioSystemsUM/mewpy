from abc import ABC, abstractmethod
from ..util.constants import EAConstants


class SolutionInterface(ABC):
    """ An interface for EA solutions.
    """

    @abstractmethod
    def get_fitness(self):
        """
        returns a list of fitness values
        """
        raise NotImplementedError

    def get_representation(self):
        """
        returns a set representation of the solution
        """
        raise NotImplementedError


class Solution(SolutionInterface):

    def __init__(self, values, fitness, constraints=None, is_maximize=True):
        """
        EA Solution

        :param values: Representation of the solution.
        :param fitness:  A list of fitness values.
        :param constraints: Decoding of the representation into metabolic constraints.
        :param is_maximize: If the solution results from a maximization problem.

        """
        self.values = values
        self.fitness = fitness
        self.constraints = {} if constraints is None else dict(constraints)
        self._is_maximize = is_maximize

    def get_fitness(self):
        return self.fitness

    def get_representation(self):
        return self.values

    def get_constraints(self):
        return self.constraints

    def __str__(self):
        return f"{self.fitness};{self.values}"

    def __repr__(self):
        return f"{self.fitness};{self.values}"

    def __eq__(self, solution):
        return set(self.values) == set(solution.values)

    def __gt__(self, solution):
        if isinstance(solution, self.__class__):
            return dominance_test(self, solution, maximize=self._is_maximize) == 1
        return False

    def __lt__(self, solution):
        if isinstance(solution, self.__class__):
            return dominance_test(self, solution, maximize=self._is_maximize) == -1
        return False

    def __ge__(self, solution):
        if isinstance(solution, self.__class__):
            return dominance_test(self, solution, maximize=self._is_maximize) != -1
        return False

    def __le__(self, solution):
        if isinstance(solution, self.__class__):
            return dominance_test(self, solution, maximize=self._is_maximize) != 1
        return False

    def __copy__(self):
        import copy
        values = copy.copy(self.values)
        fitness = self.fitness.copy()
        new_solution = Solution(values, fitness)
        return new_solution

    def __hash__(self):
        return hash(str(self.values))


class AbstractEA(ABC):

    def __init__(self, problem, initial_population=[], max_generations=EAConstants.MAX_GENERATIONS,
                 mp=True, visualizer=False, **kwargs):

        self.problem = problem
        self.initial_population = initial_population
        self.max_generations = max_generations
        self.visualizer = visualizer
        self.mp = mp
        self.final_population = None

    def run(self):
        """ Runs the optimization for the defined problem.
        The number of objectives is defined to be the number of evaluation functions in fevalution.
        """

        if self.problem.fevaluation is None or len(self.problem.fevaluation) == 0:
            raise ValueError("At leat one objective should be provided.")

        # builds the target list
        self.problem.pre_process()

        if self.problem.number_of_objectives == 1:
            final_pop = self._run_so()
        else:
            final_pop = self._run_mo()

        self.final_population = self._convertPopulation(final_pop)
        return self.final_population

    @abstractmethod
    def _convertPopulation(self, population):
        raise NotImplementedError

    @abstractmethod
    def _run_so(self):
        raise NotImplementedError

    @abstractmethod
    def _run_mo(self):
        raise NotImplementedError


def dominance_test(solution1, solution2, maximize=True):
    """
    Testes Pareto dominance

    :param solution1: The first solution.
    :param solution2: The second solution.
    :param maximize: (bool) maximization (True) or minimization (False)
    :returns: 1 : if the first solution dominates the second; -1 : if the second solution dominates the first; \
         0 : if non of the solutions dominates the other.

    """

    best_is_one = 0
    best_is_two = 0

    for i in range(len(solution1.fitness)):
        value1 = solution1.fitness[i]
        value2 = solution2.fitness[i]
        if value1 != value2:
            if value1 < value2:
                best_is_one = 1
            if value1 > value2:
                best_is_two = 1

    if best_is_one > best_is_two:
        result = 1
    elif best_is_two > best_is_one:
        result = -1
    else:
        result = 0

    if not maximize:
        result = -1 * result

    return result


def non_dominated_population(solutions, maximize=True, filter_duplicate=True):
    """
    Returns the non dominated solutions from the population.
    """
    # number of solutions dominating solution ith
    dominating_ith = [0 for _ in range(len(solutions))]

    # list of solutions dominated by solution ith
    ith_dominated = [[] for _ in range(len(solutions))]

    front = []

    for p in range(len(solutions) - 1):
        for q in range(p + 1, len(solutions)):
            dominance_test_result = dominance_test(solutions[p], solutions[q], maximize=maximize)

            if dominance_test_result == -1:
                ith_dominated[p].append(q)
                dominating_ith[q] += 1
            elif dominance_test_result == 1:
                ith_dominated[q].append(p)
                dominating_ith[p] += 1

    for i in range(len(solutions)):
        if dominating_ith[i] == 0:
            front.append(solutions[i])

    if filter_duplicate:
        result = filter_duplicates(front)
    else:
        result = front
    return result


def filter_duplicates(population):
    """ Filters equal solutions from a population
    """

    def remove_equal(individual, population):
        filtered = []
        for other in population:
            if individual != other:
                filtered.append(other)
        return filtered

    fitered_list = []
    p = population
    while len(p) > 1:
        individual = p[0]
        fitered_list.append(individual)
        p = remove_equal(individual, p)
    if p:
        fitered_list.extend(p)
    return fitered_list


def cmetric(pf1, pf2, maximize=True):
    """
    Computes the c-metric quality indicator.

    :param pf1: The first pareto front.
    :param pf2: The second pareto front.
    :param maximize: (bool) maximization (True) or minimization (False).
    :returns: r1,r2,pf1_2,pf2_1
                r1: percentage of solutions on pf2 dominated by some solution on pf1;
                r2: percentage of solutions on pf1 dominated by some solution on pf2;
                pf1_2: solutions on pf2 dominated by some solution on pf1;
                pf2_1: solutions on pf1 dominated by some solution on pf2.

    """
    # solutions on pf2 dominated by some solution on pf1
    pf1_2 = set()
    # solutions on pf1 dominated by some solution on pf2
    pf2_1 = set()
    for s1 in pf1:
        for s2 in pf2:
            d = dominance_test(s1, s2, maximize=maximize)
            if d == 1:
                pf1_2.add(s2)
            elif d == -1:
                pf2_1.add(s1)
    r1 = len(pf1_2) / len(pf2)
    r2 = len(pf2_1) / len(pf1)
    return r1, r2, pf1_2, pf2_1
