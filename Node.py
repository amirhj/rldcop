from PoweGrid import Generator, Resource, PowerGrid
from util import Counter

class Node:
    def __init__(self, id, parent, children, generators, resources, loads, powerGrid, opt):
        self.id = id
        self.parent = parent
        self.children = children
        self.pg = powerGrid
        self.generators = { g:self.pg.generators[g] for g in generators }
        self.loads = { r:self.pg.loads[l] for l in loads }
        self.resources = { r:self.pg.resources[r] for r in resources }
        self.opt = opt

        self.terminated = False
        self.qvalues = Counter()
        self.actions = set()
        self.log = []

    def isLeaf(self):
        if self.children == None:
            return True
        return False

    def isRoot(self):
        if self.parent == None:
            return True
        return False

    def isTerminated(self):
        return self.terminated

    def isReady(self):
        return True

    def sendPowerTo(self, node, power):
        self.pg.sendPowerThrough((self.id, node), power)

    def getValueFromNode(self, node):
        return self.pg.getValueOfLine((self.id, node))

    def update(self):
        sum_resources = sum([ self.resources[r].getProbeblisticValue() for r in self.resources ])
        sum_loads = sum(self.loads.values())
        sum_lines = sum([ self.getValueFromNode(c) for c in self.children ]) + self.getValueFromNode(self.parent)
        sum_generators = sum([ self.generators[g].getValue() for g in self.generators ])

        state = sum_resources + sum_loads + sum_line + sum_generators
        action = self.policy(state)
        nextState = state + sum(action.values())
        nextAction = self.policy(nextState)

        reward = self.getReward(state, action)

        qstate = (state, self.encodeAction(action))
        nextQstate = (nextState, self.encodeAction(action))

        self.qvalues[qstate] = self.qvalues[qstate] * (1-self.opt['alpha']) + \
            self.opt['alpha'] * (reward + self.opt['gamma']*self.qvalues[nextQstate])


    def policy(self, state):
        pass

    def encodeAction(self, action):
        a = []
        for g in action:
            a.append(g)
            a.append(action[g])
        return tuple(a)

    def decodeAction(self, action):
        a = {}
        i = 0
        while i < len(action):
            a[action[i]] = action[i+1]
            i += 2
        return a
