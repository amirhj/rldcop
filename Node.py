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
        self.actions = []
        for g in self.generators:
            for a in self.generators[g].getActions():
                self.actions.append({g:a})
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

    def getValueFromLineToNode(self, node):
        return self.pg.getValueOfLine((self.id, node))

    def getCapacityOfLineToNode(self, node):
        return self.pg.getCapacityOfLine((self.id, node))

    def getLoad(self):
        sum_resources = sum([ self.resources[r].getProbeblisticValue() for r in self.resources ])
        sum_loads = sum(self.loads.values())
        sum_lines = sum([ self.getValueFromLineToNode(c) for c in self.children ]) + self.getValueFromLineToNode(self.parent)
        sum_generators = sum([ self.generators[g].getValue() for g in self.generators ])

        load = sum_resources + sum_loads + sum_line + sum_generators
        return load

    def getParentLoad(self):
        return self.pg.nodes[self.parent].getLoad()

    def update(self):
        load = self.getLoad()
        parentLoad = self.getParentLoad()
        lineValue = self.getValueFromLineToNode(self.parent)
        state = (load, parentLoad, lineValue)

        action = self.policy(state)

        nextLoad = load + sum(action.values())

        self.sendPowerTo(self.parent, parentLoad + (nextLoad - load))

        nextParentLoad = self.getParentLoad()
        nextLineValue = lineValue + nextLoad - load
        nextState = (nextLoad, nextParentLoad, nextLineValue)

        nextAction = self.policy(nextState)

        reward = self.getReward(nextState)

        qstate = (state, self.encodeAction(action))
        nextQstate = (nextState, self.encodeAction(action))

        self.qvalues[qstate] = self.qvalues[qstate] * (1-self.opt['alpha']) + \
            self.opt['alpha'] * (reward + self.opt['gamma']*self.qvalues[nextQstate])

    def getReward(self, state):
        if abs(state[2]) > self.getCapacityOfLineToNode(self.parent):
            return self.opt['rewards']['lineOverflow']
        reward = 0
        if state[0] == 0:
            reward += self.opt['rewards']['properLoad']
        else:
            reward += self.opt['rewards']['badLoadWeight'] * abs(state[0])

        if state[1] == 0:
            reward += self.opt['rewards']['properParentLoad']
        else:
            reward += self.opt['rewards']['badParentLoadWeight'] * abs(state[1])

        return reward

    def policy(self, state):
        maxQ = 0
        isFirst = True
        maxActions = []
        for a in self.actions:
            a = self.encodeAction(a)
            if isFirst or self.qvalues[(state, a)] > maxQ:
                maxQ = self.qvalues[(state, a)]
                del maxActions[:]
                maxActions.append(a)
                isFirst = False
            elif self.qvalues[(state, a)] == maxQ:
                maxActions.append(a)
        return self.decodeAction(random.choice(maxActions))

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
