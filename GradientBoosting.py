"""Module represents Gradient Boosting."""
from __future__ import print_function
from Utils import Utils
from Tree import node
from Boosting import Boosting


class GradientBoosting(object):
    """Class for Gradient Boosting."""

    def __init__(self, RRT=False, regression=False, trees=10, treeDepth=2,
                 loss="LS", sampling_rate=1.0):
        """Initialize the class.

        Attributes:
            RRT : (bool)
            regression : (bool)
            trees : (int) Number of trees
            treeDepth : (int) Depth of the Trees
            loss : loss function to be used, can be "LS", "LAD", or "Huber"
                (default is "LS")
            sampling_rate : (float)

        """
        self.targets = None
        self.regression = regression
        self.sampling_rate = sampling_rate
        self.numberOfTrees = trees
        self.treeDepth = treeDepth
        self.trees = {}
        self.treeLCAs = {}
        if RRT:
            Utils.setRRT()
            self.numberOfTrees = 1
        self.data = None
        self.loss = loss
        self.testPos, self.testNeg, self.testExamples = {}, {}, {}

    def setTargets(self, targets):
        """Set the target."""
        self.targets = targets

    def learn(self, facts, examples, bk):
        """Learn the clause."""
        for target in self.targets:
            data = Utils.setTrainingData(target=target, facts=facts,
                                         examples=examples, bk=bk,
                                         regression=self.regression,
                                         sampling_rate=self.sampling_rate)
            trees = []
            treeLCAs = []
            for i in range(self.numberOfTrees):
                print ('='*20, "learning tree", str(i), '='*20)
                node.setMaxDepth(self.treeDepth)
                node.learnTree(data)
                trees.append(node.learnedDecisionTree)
                treeLCAs.append(node.LCAS)
                Boosting.updateGradients(data, trees, loss=self.loss)
        self.trees[target] = trees
        self.treeLCAs[target] = treeLCAs
        for tree in trees:
            print ('='*30, "tree", str(trees.index(tree)), '='*30)
            for clause in tree:
                print (clause)
        for treeLCA in treeLCAs:
            print ('='*30, "tree", str(treeLCAs.index(treeLCA)), '='*30)
            for clause in treeLCA:
                print (clause)

    def infer(self, facts, examples):
        """Infer."""
        self.testExamples = {}
        for target in self.targets:
            data = Utils.setTestData(target=target, facts=facts,
                                     examples=examples,
                                     regression=self.regression)
            Boosting.performInference(data, self.trees[target])
            self.testExamples[target] = data.examples
            print (data.examples)
