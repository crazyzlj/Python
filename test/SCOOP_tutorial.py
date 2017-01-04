# Script to be launched with: python -m scoop scriptName.py
from __future__ import print_function
# allows Python 2 users to have a print function compatible with Python 3
import random
import operator
from scoop import logger
from scoop import futures
from scoop import shared
from math import hypot
import time
data = [random.randint(-1000, 1000) for r in range(1000)]

def myParallelFunc(inV):
    myV = shared.getConst("myValue")
    return inV + myV
def helloworld(v):
    return "Hello SCOOP from Future #{0}".format(v)

def test(tries):
    return sum(hypot(random.random(), random.random()) < 1 for _ in range(tries))

def calcPi(nbFutures, tries):
    expr = futures.map(test, [tries] * nbFutures)
    return 4. * sum(expr) / float(nbFutures * tries)

def calcPiSerial(nbFutures, tries):
    sumexpr = sum(list(map(test, [tries] * nbFutures)))
    return 4. * sumexpr / float(nbFutures * tries)

if __name__ == '__main__':
    # # Python's standard serial function
    # dataSerial = list(map(abs, data))
    # serialSum = sum(map(abs, data))
    # print "serial: %f" % serialSum
    # # SCOOP's parallel function
    # dataParallel = list(futures.map(abs, data))
    # parallelSum = futures.mapReduce(abs, operator.add, data)
    # assert dataSerial == dataParallel
    # print  "parallel: %f" % parallelSum
    # shared.setConst(myValue = 5)
    # print (list(futures.map(myParallelFunc, range(10))))
    # logger.warn("this is a warning test!")
    # returnValues = list(futures.map(helloworld, range(6)))
    # print("\n".join(returnValues))
    t1 = time.time()
    print ("pi = {}".format(calcPi(3000, 5)))
    print (time.time() - t1)
    # t1 = time.time()
    # print("pi = {}".format(calcPiSerial(3000, 5000)))
    # print (time.time() - t1)

