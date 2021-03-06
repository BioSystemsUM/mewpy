from enum import Enum
from ..util.constants import ModelConstants

solvers = []

try:
    import gurobipy
    solvers.append('gurobi')
    # disables solver output.
    # gurobipy.setParam('OutputFlag', 0)
except ImportError:
    pass

try:
    import cplex
    solvers.append('cplex')
except ImportError:
    pass

try:
    import swiglpk
    solvers.append('glpk')
except ImportError:
    pass

default_solver = None


def get_default_solver():
    """
    Returns:
        [type]: [description]
    """
    global default_solver

    if default_solver:
        return default_solver

    solver_order = ['gurobi', 'cplex', 'glpk']

    for solver in solver_order:
        if solver in solvers:
            default_solver = solver
            break

    if not default_solver:
        raise RuntimeError("No solver available.")

    return default_solver


def set_default_solver(solvername):
    """ Sets default solver.
    Arguments:
        solvername : (str) solver name (currently available: 'gurobi', 'cplex')
    """

    global default_solver

    if solvername.lower() in solvers:
        default_solver = solvername.lower()
    else:
        raise RuntimeError(f"Solver {solvername} not available.")


solvers = []

try:
    import gurobipy
    solvers.append('gurobi')
except ImportError:
    pass


try:
    import cplex
    solvers.append('cplex')
except ImportError:
    pass

try:
    import swiglpk
    solvers.append('glpk')
except ImportError:
    pass


default_solver = None


def get_default_solver():
    """ 
    Returns:
        [type]: [description]
    """
    global default_solver

    if default_solver:
        return default_solver

    solver_order = ['gurobi','cplex', 'glpk']

    for solver in solver_order:
        if solver in solvers:
            default_solver = solver
            break

    if not default_solver:
        raise RuntimeError("No solver available.")

    return default_solver


def set_default_solver(solvername):
    """ Sets default solver.
    Arguments:
        solvername : (str) solver name (currently available: 'gurobi', 'cplex')
    """

    global default_solver

    if solvername.lower() in solvers:
        default_solver = solvername.lower()
    else:
        raise RuntimeError(f"Solver {solvername} not available.")





# Model specific simulators mapping:
# Entries take the form:  full_model_class_path -> (simulator_path, simulator_class_name)
# TODO: use qualified names

map_model_simulator = {
    'geckopy.gecko.GeckoModel': ('mewpy.simulation.cobra', 'GeckoSimulation'),
    'mewpy.model.gecko.GeckoModel': ('mewpy.simulation.reframed', 'GeckoSimulation'),
    'mewpy.model.smoment.SMomentModel': ('mewpy.simulation.reframed', 'GeckoSimulation')
}


def get_simulator(model, envcond=None, constraints=None, reference=None, reset_solver=ModelConstants.RESET_SOLVER):
    """
    Returns a simulator instance for the model.
    The simulator instance is model dependent.
    Besides able to be used on its own, this function is invoked by EA optimization problems
    and by evaluation function instances to perform phenotyoe evaluations of candidate solutions.


    :param model: the model
    :param dict envcond: A dictionary of environmental conditions.
    :param dict contrainsts: A dictionary of additional persistent constraints.
    :returns: An instance of Simulator
    """

    instance = None
    name = f"{model.__class__.__module__}.{model.__class__.__name__}"
    if name in map_model_simulator:
        module_name, class_name = map_model_simulator[name]
        module = __import__(module_name, fromlist=[None])
        class_ = getattr(module, class_name)
        instance = class_(model, envcond=envcond,
                          constraints=constraints, reference=reference, reset_solver=reset_solver)
    else:
        try:
            from cobra.core.model import Model
            if isinstance(model, Model):
                from .cobra import Simulation
                instance = Simulation(
                    model, envcond=envcond, constraints=constraints, reference=reference, reset_solver=reset_solver)
        except ImportError:
            pass
        if not instance:
            try:
                from reframed.core.cbmodel import CBModel
                if isinstance(model, CBModel):
                    from .reframed import Simulation
                    instance = Simulation(
                        model, envcond=envcond, constraints=constraints, reference=reference, reset_solver=reset_solver)
            except ImportError:
                pass
    if not instance:
        raise ValueError(f"The model <{name}> has no defined simulator.")
    return instance


def get_container(model):
    """
    Returns a container for a given model sharing a common interface.
    A container does not perform any task, it only serves as a basic interface with a phenotype simulator.

    :param model: An instance of a metabolic model.
    :returns: A container.

    """
    try:
        from reframed.core.cbmodel import CBModel
        if isinstance(model, CBModel):
            from mewpy.simulation.reframed import CBModelContainer
            return CBModelContainer(model)
    except Exception:
        pass

    try:
        from cobra.core.model import Model
        if isinstance(model, Model):
            from mewpy.simulation.cobra import CobraModelContainer
            return CobraModelContainer(model)
    except Exception:
        pass

    raise ValueError(f"Unrecognized model class: {model.__class__.name}")


class SimulationMethod(Enum):
    FBA = 'FBA'
    pFBA = 'pFBA'
    MOMA = 'MOMA'
    lMOMA = 'lMOMA'
    ROOM = 'ROOM'
    NONE = 'NONE'

    def __eq__(self, other):
        """Overrides equal to enable string name comparison.
        Allows to seamlessly use:
            SimulationMethod.FBA = SimulationMethod.FBA
            SimulationMethod.FBA = 'FBA'
        without requiring an additional level of comparison (SimulationMethod.FBA.name = 'FBA')
        """
        if isinstance(other, SimulationMethod):
            return super().__eq__(other)
        elif isinstance(other, str):
            return self.name == other
        else:
            return False

    def __hash__(self):
        return hash(self.name)


class SStatus(Enum):
    """ Enumeration of possible solution status. """
    OPTIMAL = 'Optimal'
    UNKNOWN = 'Unknown'
    SUBOPTIMAL = 'Suboptimal'
    UNBOUNDED = 'Unbounded'
    INFEASIBLE = 'Infeasible'
    INF_OR_UNB = 'Infeasible or Unbounded'

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name
