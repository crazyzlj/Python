# Overview of DEAP document.
import pickle
import random

import numpy
from deap import base, creator
from deap import tools

# 1. Types

# Create a class named 'FitnessMin', inherited from base.Fitness, has the weights attribute
creator.create('FitnessMin', base.Fitness, weights=(1.0,))
creator.create('Individual', list, fitness=creator.FitnessMin)

# another example of creator a class, and initialize an object.
creator.create("Foo", list, bar=dict, spam=1)
x = creator.Foo()
print x.bar, x.spam  # {} 1

# 2. Initialization
IND_SIZE = 10
toolbox = base.Toolbox()


# example of how to use Toolbox
def func(a, b, c=3):
    print a, b, c


toolbox.register('myFunc', func, 2, c=4)
toolbox.register('myFunc2', func)
toolbox.myFunc(3)  # 2 3 4, the register and call statements is equal to func(2, 3, 4)
toolbox.myFunc2(2, 3, 4)


class initParam(object):
    """Test."""

    def __init__(self, v):
        print ('initial, v: %f' % v)
        self.multiply = v
        self.fid = random.random()
    @staticmethod
    def get_random(v):
        cc = initParam(v)
        l = list()
        for i in range(10):
            l.append(random.random() * cc.multiply)
        print ('get_random, v: %s' % ','.join(str(i) for i in l))
        return l


def initRepeatWithCfg(container, generator, cf, n=2):
    return container(generator(cf) for _ in xrange(n))


def initIterateWithCfg(container, generator, cf):
    return container(generator(cf))


toolbox.register('attribute', initParam.get_random)
# toolbox.register('individual', initRepeatWithCfg, creator.Individual,
#                  toolbox.attribute, n=IND_SIZE)
toolbox.register('individual', initIterateWithCfg, creator.Individual, toolbox.attribute)
toolbox.register('population', initRepeatWithCfg, list, toolbox.individual)


# 3. Operators
def evaluate(individual, n):
    return sum(individual) / n


toolbox.register('mate', tools.cxTwoPoint)
toolbox.register('mutate', tools.mutGaussian, mu=0, sigma=1, indpb=0.1)
toolbox.register('select', tools.selTournament, tournsize=3)
toolbox.register('evaluate', evaluate)

stats = tools.Statistics(key=lambda ind: ind.fitness.values)
stats.register('avg', numpy.mean, axis=0)
stats.register('std', numpy.std, axis=0)
stats.register('min', numpy.min, axis=0)
stats.register('max', numpy.max, axis=0)

logbook = tools.Logbook()


def main():
    cc = initParam(0.8)
    pop = toolbox.population(0.8, n=50)

    CXPB, MUTPB, NGEN = 0.5, 0.2, 40

    # evaluate the entire population
    fitnesses = map(toolbox.evaluate, pop, [9]*50)
    print len(fitnesses)  # 50
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = (fit,)

    for g in range(NGEN):
        # select the next generation individuals
        offspring = toolbox.select(pop, len(pop))
        # clone the selected individuals
        offspring = map(toolbox.clone, offspring)
        # Apply crossover and mutation on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < CXPB:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values
        for mutant in offspring:
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind, [9]*len(invalid_ind))
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = (fit,)

        # The population is entirely replaced by the offspring
        pop[:] = offspring
        record = stats.compile(pop)
        # print record
        logbook.record(gen=g, **record)
    return pop, logbook


if __name__ == '__main__':
    main()
    logbook.header = 'gen', 'avg'
    print logbook
    gen = logbook.select('gen')
    fit_maxs = logbook.select('max')
    # import matplotlib.pyplot as plt
    # fig, ax1 = plt.subplots()
    # line1 = ax1.plot(gen, fit_maxs, 'b', label='Maximum fitness')
    # ax1.set_xlabel('Generation')
    # ax1.set_ylabel('Fitness', color='b')
    # for t1 in ax1.get_yticklabels():
    #     t1.set_color('b')
    # labs = [l.get_label() for l in line1]
    # ax1.legend(line1, labs, loc='center right')
    # plt.show()

    # output logbook
    f = open(r'D:\tmp\logbook.txt', 'w')
    f.write(logbook.__str__())
    f.close()
