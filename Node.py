from PoweGrid import Generator, Resource, PowerGrid

class Node:
    def __init__(self, id, parent, children, generators, resources, loads, powerGrid, opt):
        pass

    def isLeaf(self):
        pass

    def isRoot(self):
        pass

    def isTerminated(self):
        pass

    def isReady(self):
        pass

    def sendToPowerLine(self, line, power):
        pass

    def getValueOfLine(self, line):
        pass

    def update(self):
        pass
