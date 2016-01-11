from Node import Node

class Generator:
    def __init__(self, maxValue):
        self.value = 0
        self.maxValue = maxValue

    def increase(self):
        if self.value + 1 <= self.maxValue:
            self.value += 1

    def decrease(self):
        if self.value - 1 >= 0:
            self.value -= 1

    def getValue(self):
        return self.value

class Resource:
    def __init__(self, values, distribution):
        self.values = values
        self.index = 0

    def getProbeblisticValue(self):
        return self.values[0]

    def getValue(self):
        return self.values[self.index]

class PowerGrid:
    def __init__(self, gridJSON, options, debugLevel):
        self.gridJSON = gridJSON
        self.opt = options
        self.nodes = {}
        self.powerLines = {}
        self.generators = {}
        self.loads = {}
        self.resources = {}
        self.leaves = []
        self.root = None
        self.debugLevel = debugLevel

        self.initialize()

    def initialize(self):
        for g in self.gridJSON['generators']:
            self.generators[g] = Generator(self.gridJSON['generators'][g]['maxValue'])

        for r in self.gridJSON['resources']:
            self.resources[r] = Resource(self.gridJSON['resources'][r]['values'], self.gridJSON['resources'][r]['distribution'])

        for l in self.gridJSON['loads']:
            self.loads[l] = self.gridJSON['loads'][l]

        children = set()
        nodes = set()
        for n in self.gridJSON['nodes']:
            nodes.add(n)
            if 'children' in self.nodesJSON[n]:
                if len(self.gridJSON['nodes'][n]['children']) == 0:
                    self.leaves.append(n)
                else:
                    for c in self.gridJSON['nodes'][n]['children']:
                        children.add(c)
            else:
                self.leaves.append(n)

        self.root = list(nodes - children)[0]
        if len(nodes - children) > 1:
            raise Exception('Error: More than one root found.')

        for n in self.gridJSON['nodes']:
            # looking for parent of node n
            parent = []
            for p in self.gridJSON['nodes']:
                if 'children' in self.gridJSON['nodes'][p]:
                    if n in self.gridJSON['nodes'][p]['children']:
                        parent.append(p)

            if len(parent) > 1:
                raise Exception('Error: Graph is not acyclic.')

            if len(parent) == 1:
                parent = parent[0]
            else:
                parent = None

            children = None
            if 'children' in self.gridJSON['nodes'][n]:
                children = self.gridJSON['nodes'][n]['children']

            self.nodes[n] = Node(n, parent, children, self.gridJSON['nodes'][n]['generators'],\
                self.gridJSON['nodes'][n]['resources'], self.gridJSON['nodes'][n]['loads'], self, self.opt, self.debugLevel)

        for pl in self.gridJSON['powerLines']:
            a = self.gridJSON['powerLines'][pl]['from']
            b = self.gridJSON['powerLines'][pl]['to']

            self.powerLines[(a,b)] = { 'id':pl, 'value':0, 'capacity':self.gridJSON['powerLines'][pl]['capacity'] }

    def writeResults(self):
        pass
