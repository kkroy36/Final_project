"""Module represents Regression Trees."""
from __future__ import print_function

from Utils import Utils
from Logic import Logic, Prover
from copy import deepcopy


class node(object):
    """Class for Nodes in Trees."""
    expandQueue = []  # Breadth first search node expansion strategy
    depth = 0  # initial depth is 0 because no node present
    maxDepth = 1  # max depth set to 1 because we want to at least learn a tree of depth 1
    learnedDecisionTree = []  # this will hold all the clauses learned
    data = None   # stores all the facts, positive and negative examples
    # learnedDotFile = []  # this will store the dot file for the tree learned
    LCAS = []  # this will store the rrt with negations with LCA score
    label = 1

    def __init__(self, test=None, examples=None, information=None, level=None,
                 parent=None, pos=None, label=1):
        """Construct node.

        Attributes:
            test :     test condition, should be a horn clause
            examples : all examples that are available for testing at this node
            information : notion (some score) contained at this node
            level :    level of the node in the tree, 0 for root node
            parent :   pointer to the parent node
            position : position relative to the parent in the tree,
                       can be "left" or "right"

        """
        self.label = label
        self.test = test  # set test condition, which will be a horn clause
        if level > 0:  # check if not root,
            self.parent = parent  # set parent as the nodes parent
        else:     # else if root,
            self.parent = "root"  # set parent to "root" to signify root
        self.pos = pos  # position of the node, i.e. "left" or "right"
        self.examples = examples  # all examples that are available for testing at this node
        self.information = information  # information contained at this node
        self.level = level  # level of the node, 0 for root
        self.left = None  # left subtree
        self.right = None  # right subtree
        node.expandQueue.insert(0, self)  # add to the queue of nodes to expand

    @staticmethod
    def setMaxDepth(depth):
        """Set max depth."""
        node.maxDepth = depth

    @staticmethod
    def initTree(trainingData):
        """Create the root node."""
        node.data = trainingData
        node.expandQueue = []  # reset node queue for every tree to be learned
        node.learnedDecisionTree = []  # reset clauses for every tree to be learned
        # node.learnedDotFile = []  # reset dot file for every tree to be learned
        if not trainingData.regression:
            """@batflyer
            In Python 2, .keys() returns a list, whereas in Python 3 it returns a dictionary view.
            ===> Forcing a list.
            """
            examples = list(trainingData.pos.keys()) + list(trainingData.neg.keys())  # collect all examples
            node(None,examples,Utils.variance(examples),0,"root",node.label)  # create root node
        elif trainingData.regression:
            examples = list(trainingData.examples.keys())  # collect regression examples
            node(None,examples,Utils.variance(examples),0,"root",node.label)

    @staticmethod
    def learnTree(data):
        """Learn decision tree."""
        node.initTree(data)  # create the root
        while len(node.expandQueue) > 0:
            curr = node.expandQueue.pop()
            curr.expandOnBestTest(data)
        node.learnedDecisionTree.sort(key=len)
        node.learnedDecisionTree = node.learnedDecisionTree[::-1]
        node.LCAS.sort(key=len)
        node.LCAS = node.LCAS[::-1]

    def getTrueExamples(self, clause, test, data):
        """Return List of examples that satisfy clause with conjoined test literal."""
        tExamples = []  # intialize list of true examples
        clauseCopy = deepcopy(clause)
        if clauseCopy[-1] == "-":  # construct clause for prover
            clauseCopy += test
        elif clauseCopy[-1] == ';':
            clauseCopy = clauseCopy.replace(';', ',')+test
        # to keep track of output, following for loop can be parallelized
        print ("testing clause: ", clauseCopy)
        for example in self.examples:
            # prove if example satisfies clause
            if Prover.prove(data, example, clauseCopy):
                tExamples.append(example)
        return tExamples

    def expandOnBestTest(self, data=None):
        """Expand the node based on the best test."""
        target = data.getTarget()  # get the target
        # initialize clause learned at this node with empty body
        clause = target+":-"
        clause_with_negations = target+":-"
        curr = self  # while loop to obtain clause learned at this node
        ancestorTests = []
        while curr.parent != "root":
            if curr.pos == "left":
                clause += curr.parent.test+";"
                clause_with_negations += curr.parent.test+";"
                ancestorTests.append(curr.parent.test)
            elif curr.pos == "right":
                clause += ""  # "!"+curr.parent.test+","
                clause_with_negations += "!"+curr.parent.test+";"
                ancestorTests.append(curr.parent.test)
            curr = curr.parent
        if self.level != node.maxDepth and round(self.information, 8) != 0:
            if clause_with_negations[-1] != '-':
                node.LCAS.append(clause_with_negations[:-1] + " " +
                                 str(self.level))
            else:
                node.LCAS.append(clause_with_negations + " " +
                                 str(self.level))
        else:
            if clause_with_negations[-1] != '-':
                node.LCAS.append(clause_with_negations[:-1] + " " +
                                 str(self.level))
            else:
                node.LCAS.append(clause_with_negations+" l" + str(self.level))
        if self.level == node.maxDepth or round(self.information, 8) == 0:
            if clause[-1] != '-':
                node.learnedDecisionTree.append(clause[:-1] + " " +
                                                str(Utils.getleafValue(
                                                              self.examples)))
            else:
                node.learnedDecisionTree.append(clause + " " +
                                                str(Utils.getleafValue(
                                                              self.examples)))
            return
        if clause[-2] == '-':
            clause = clause[:-1]
        print('-'*80)
        print("pos: ", self.pos)
        print("node depth: ", self.level)
        print("parent: ", self.parent)
        print("number of examples at node: ", len(self.examples))
        if self.parent != "root":
            print("test at parent: ", self.parent.test)
        print("clause for generate test at current node: ", clause)
        # print "examples at current node: ",self.examples
        minScore = float('inf')  # initialize minimum weighted variance to be 0
        bestTest = ""  # initalize best test to empty string
        # list for best test examples that satisfy clause
        bestTExamples = []
        # list for best test examples that don't satisfy clause
        bestFExamples = []
        # get all the literals that the data (facts) contains
        literals = data.getLiterals()
        tests = []
        for literal in literals:  # for every literal generate test conditions
            literalName = literal
            literalTypeSpecification = literals[literal]
            # generate all possible literal, variable and constant combinations
            tests += Logic.generateTests(literalName, literalTypeSpecification,
                                         clause)
        if self.parent != "root":
                tests = [test for test in tests if not test in ancestorTests]
        tests = sorted(list(set(tests)))
        if not tests:
            if clause[-1] != '-':
                node.learnedDecisionTree.append(clause[:-1] + " " +
                                                str(Utils.getleafValue(
                                                              self.examples)))
                node.LCAS.append(clause_with_negations[:-1] + " " +
                                 str(self.level))
            else:
                node.learnedDecisionTree.append(clause + " " +
                                                str(Utils.getleafValue(
                                                              self.examples)))
                node.LCAS.append(clause_with_negations + " " + str(self.level))
            return
        for test in tests:  # see which test scores the best
            # get examples satisfied
            tExamples = self.getTrueExamples(clause, test, data)
            fExamples = [example for example in self.examples if example not in tExamples]  # get examples unsatsified (closed world assumption made)
            score = ((len(tExamples)/float(len(self.examples))) *
                     Utils.variance(tExamples) + (len(fExamples) /
                                                  float(len(self.examples))) *
                     Utils.variance(fExamples))  # calculate weighted variance
            # score = len([example for example in tExamples if example in data.pos.keys()]) - len([example for example in tExamples if example in data.neg.keys()])
            if score < minScore:  # if score lower than current lowest
                minScore = score  # assign new minimum
                bestTest = test  # assign new best test
                bestTExamples = tExamples  # collect satisfied examples
                bestFExamples = fExamples  # collect unsatisfied examples
        Utils.addVariableTypes(bestTest)  # add variable types of new variables
        # assign best test after going through all literal specs
        self.test = bestTest
        print("best test found at current node: ", self.test)
        # if self.parent != "root":
        # node.learnedDotFile.append(self.parent.test+str("->")+self.test)
        # if examples still need explaining create left node and add to queue
        if len(bestTExamples) > 0:
            self.left = node(None, bestTExamples,
                             Utils.variance(bestTExamples),
                             self.level+1, self, "left", node.label+1)
            node.label += 1
            if self.level+1 > node.depth:
                node.depth = self.level+1
        # if examples still need explaining, create right node and add to queue
        if len(bestFExamples) > 0:
            self.right = node(None, bestFExamples,
                              Utils.variance(bestFExamples),
                              self.level+1, self, "right", node.label+1)
            node.label += 1
            if self.level+1 > node.depth:
                node.depth = self.level+1
        # if no examples append clause as is
        if self.test == "" or round(self.information, 8) == 0:
            if clause[-1] != '-':
                node.learnedDecisionTree.append(clause[:-1])
                node.LCAS.append(clause_with_negations[:-1] + " " +
                                 str(self.level))
            else:
                node.learnedDecisionTree.append(clause)
                node.LCAS.append(clause_with_negations[:-1] + " " +
                                 str(self.level))
            return
