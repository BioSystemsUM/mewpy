""" Inspyred Operators
"""

import copy

from inspyred.ec.variators.crossovers import crossover
from inspyred.ec.variators.mutators import mutator


@mutator
def shrink_mutation(random, candidate, args):
    """Returns the mutant produced by shrink mutation on the candidate.
    If a candidate solution has length of 1, this function leaves it unchanged.

    :param random: the random number generator object. Must implement random().
    :param candidate: the candidate solution.
    :parm args: a dictionary of keyword arguments.
    :returns: A set of new candidate

    Notes:
        Optional keyword arguments in args:
        - *mutation_rate* -- the rate at which mutation is performed (default 0.1)
    """
    mutRate = args.setdefault("gs_mutation_rate", 0.1)
    minSize = args["candidate_min_size"]
    if random.random() > mutRate or len(candidate) <= minSize:
        return candidate
    index = random.randint(0, len(candidate) - 1)
    mutantL = list(candidate)
    del mutantL[index]
    mutant = set(mutantL)
    return mutant


@crossover
def uniform_crossover_KO(random, mom, dad, args):
    """Return the offspring of the uniform crossover on the candidate. Based on two candidates (parents) build 2 children:
    - elements present in both parents will be present in both children;
    - both children have at least one element;
    - elements present in only one parent have equal probability to be present in child 1 or child 2 (after each child\
    has at least one element).

    :param random: the random number generator object. Must implement random().
    :param mom: the first parent candidate
    :param dad: the second parent candidate
    :param args: a dictionary of keyword arguments.
    :param crossover_rate: The rate at which crossover is performed (default 1.0).
    :returns: Return the offspring of the candidates given as argument.

    """
    crossRate = args.setdefault("crossover_rate", 1.0)
    children = []
    if random.random() > crossRate or (len(mom) == 1 and len(dad) == 1):
        children.append(mom)
        children.append(dad)
        return children

    maxSize = args["candidate_max_size"]
    intersection = mom & dad
    otherElems = list((mom | dad).difference(intersection))
    child1 = copy.copy(intersection)
    child2 = copy.copy(intersection)

    while len(otherElems) > 0:
        elemPosition = random.randint(
            0, len(otherElems) - 1) if len(otherElems) > 1 else 0
        if len(child1) == maxSize or len(child2) == 0:
            child2.add(otherElems[elemPosition])
        elif len(child2) == maxSize or len(child1) == 0:
            child1.add(otherElems[elemPosition])
        else:
            r = random.random()
            if r <= 0.5:
                child1.add(otherElems[elemPosition])
            else:
                child2.add(otherElems[elemPosition])
        otherElems.pop(elemPosition)
    children.append(child1)
    children.append(child2)
    return children


@crossover
def uniform_crossover_OU(random, mom, dad, args):
    """Return the offspring of the uniform crossover on the candidate. Based on two candidates (parents) build 2 children:
    - elements present in both parents will be present in both children;
    - both children have at least one element;
    - elements present in only one parent have equal probability to be present in child 1 or child 2 (after each child
    has at least one element).

    :param random: the random number generator object. Must implement random().
    :param mom: the first parent candidate
    :param dad: the second parent candidate
    :param args: a dictionary of keyword arguments.
    :returns: Return the offspring of the candidates given as argument.

    Notes:
        Optional keyword arguments in args:
        - *crossover_rate* -- the rate at which crossover is performed (default 1.0)
    """
    crossRate = args.setdefault("crossover_rate", 1.0)
    children = []
    if random.random() > crossRate or (len(mom) == 1 and len(dad) == 1):
        children.append(copy.copy(mom))
        children.append(copy.copy(dad))
        return children

    maxSize = args["candidate_max_size"]
    # common idx (reactions)
    intersection = list({idx for (idx, idy) in mom} &
                        {idx for (idx, idy) in dad})
    c_mom = {idx: idy for (idx, idy) in mom if idx in intersection}
    c_dad = {idx: idy for (idx, idy) in dad if idx in intersection}
    rest = [(idx, idy) for (idx, idy) in mom if idx not in intersection] + \
           [(idx, idy) for (idx, idy) in dad if idx not in intersection]
    child1 = []
    child2 = []

    for i in range(len(intersection)):
        idx = intersection[i]
        if random.random() < 0.5:
            child1.append((idx, c_mom[idx]))
            child2.append((idx, c_dad[idx]))
        else:
            child2.append((idx, c_mom[idx]))
            child1.append((idx, c_dad[idx]))

    for i in range(len(rest)):
        if random.random() < 0.5 and len(child1) < maxSize:
            child1.append(rest[i])
        elif len(child2) < maxSize:
            child2.append(rest[i])
        else:
            child1.append(rest[i])

    if len(child1) == 0:
        i = random.randint(0, len(child2) - 1)
        p = child2[i]
        child1.append(p)
        child2.remove(p)

    if len(child2) == 0:
        i = random.randint(0, len(child1) - 1)
        p = child1[i]
        child2.append(p)
        child1.remove(p)

    children.append(set(child1))
    children.append(set(child2))
    return children


@mutator
def grow_mutation_KO(random, candidate, args):
    """Returns the mutant produced by a grow mutation on the candidate (when the representation is a set of integers).
    If a candidate solution has the maximum size candidate allowed, this function leaves it unchanged.

    :param random: the random number generator object.
    :param candidate: the candidate solution.
    :param args: a dictionary of keyword arguments.
    :returns: A set with a new candidate.

    Notes:

    Optional keyword arguments in args:
    - *mutation_rate* -- the rate at which mutation is performed (default 0.1)
    """
    bounder = args["_ec"].bounder
    mutRate = args.setdefault("gs_mutation_rate", 0.1)
    if random.random() > mutRate:
        return candidate
    maxSize = args["candidate_max_size"]
    mutant = copy.copy(candidate)
    if len(mutant) < maxSize:
        newElem = random.randint(bounder.lower_bound, bounder.upper_bound)
        while newElem in mutant:
            newElem = random.randint(bounder.lower_bound, bounder.upper_bound)
        mutant.add(newElem)
    return mutant


@mutator
def grow_mutation_OU(random, candidate, args):
    """Returns the mutant produced by a grow mutation on the candidate (when the representation is a set of integers).
    If a candidate solution has the maximum size candidate allowed, this function leaves it unchanged.

    :param random: the random number generator object.
    :param candidate: the candidate solution.
    :param args: a dictionary of keyword arguments.
    :returns: A set with a new candidate.

    Notes:

    Optional keyword arguments in args:
    - *mutation_rate* -- the rate at which mutation is performed (default 0.1)

    """
    bounder = args["_ec"].bounder
    mutRate = args.setdefault("gs_mutation_rate", 0.1)
    if random.random() > mutRate:
        return candidate
    maxSize = args["candidate_max_size"]
    mutant = copy.copy(candidate)
    if len(mutant) < maxSize:
        idx = random.randint(bounder.lower_bound[0], bounder.upper_bound[0])
        idxs = [a for (a, b) in mutant]
        while idx in idxs:
            idx = random.randint(
                bounder.lower_bound[0], bounder.upper_bound[0])
        lv = random.randint(bounder.lower_bound[1], bounder.upper_bound[1])
        mutant.add((idx, lv))
    return mutant


@mutator
def single_mutation_KO(random, candidate, args):
    """Returns the mutant produced by a single mutation on the candidate (when the representation is a set of integers).
    The candidate size is maintained.

    :param random: the random number generator object.
    :param candidate: the candidate solution.
    :param args: a dictionary of keyword arguments.
    :returns: A set with a new candidate.

    Optional keyword arguments in args:

    - *mutation_rate* -- the rate at which mutation is performed (default 0.1)
    """

    bounder = args["_ec"].bounder
    mutRate = args.setdefault("mutation_rate", 0.1)
    if random.random() > mutRate:
        return candidate
    mutant = copy.copy(candidate)
    index = random.randint(0, len(mutant) - 1) if len(mutant) > 1 else 0
    newElem = random.randint(bounder.lower_bound, bounder.upper_bound)
    while newElem in mutant:
        newElem = random.randint(bounder.lower_bound, bounder.upper_bound)
    mutantL = list(mutant)
    mutantL[index] = newElem
    mutant = set(mutantL)
    return mutant


@mutator
def single_mutation_OU(random, candidate, args):
    """Returns the mutant produced by one mutation on the candidate (when the representation is a set of (int,int)).
    The candidate size is maintained.

    :param random: the random number generator object.
    :param candidate: the candidate solution.
    :param args: a dictionary of keyword arguments.
    :returns: A set with a new candidate.

    Optional keyword arguments in args:

    - *mutation_rate* -- the rate at which mutation is performed (default 0.1)
    """

    bounder = args["_ec"].bounder
    mutRate = args.setdefault("mutation_rate", 0.1)
    if random.random() > mutRate:
        return candidate

    mutant = copy.copy(candidate)
    index = random.randint(0, len(mutant) - 1) if len(mutant) > 1 else 0
    # the first idx has a 50% chance of beeing mutated
    # the second always mutates
    ml = [i for (i, j) in mutant]
    mutantL = list(mutant)
    idx, idy = mutantL[index]
    is_mutate_idx = False
    if random.random() > 0.5:
        idx = random.randint(bounder.lower_bound[0], bounder.upper_bound[0])
        while idx in ml:
            idx = random.randint(
                bounder.lower_bound[0], bounder.upper_bound[0])
        is_mutate_idx = True
    lv = random.randint(bounder.lower_bound[1], bounder.upper_bound[1])
    while not is_mutate_idx and lv == idy:
        lv = random.randint(bounder.lower_bound[1], bounder.upper_bound[1])
    mutantL[index] = (idx, lv)
    mutant = set(mutantL)
    return mutant


@mutator
def single_mutation_OU_level(random, candidate, args):
    """Returns the mutant produced by one mutation on the candidate (when the representation is a set of (int,int)).
    The candidate size is maintained.

    :param random: the random number generator object.
    :param candidate: the candidate solution.
    :param args: a dictionary of keyword arguments.
    :returns: A set with a new candidate.


    Optional keyword arguments in args:

    - *mutation_rate* -- the rate at which mutation is performed (default 0.1)

    """

    bounder = args["_ec"].bounder
    mutRate = args.setdefault("mutation_rate", 0.1)
    if random.random() > mutRate:
        return candidate
    mutant = copy.copy(candidate)
    index = random.randint(0, len(mutant) - 1) if len(mutant) > 1 else 0
    # the first idx has a 50% chance of beeing mutated
    # the second always mutates
    mutantL = list(mutant)
    idx, idy = mutantL[index]
    lv = random.randint(bounder.lower_bound[1], bounder.upper_bound[1])
    while lv == idy:
        lv = random.randint(bounder.lower_bound[1], bounder.upper_bound[1])
    mutantL[index] = (idx, lv)
    mutant = set(mutantL)
    return mutant
