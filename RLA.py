"""Module representing Relational Local Approximator."""
from GradientBoosting import GradientBoosting
from copy import deepcopy
from Logical import Prover
from Utils import Data


class RLA(object):
    """Class for distance based local value approximation."""

    def __init__(self, examples=[], facts=[], bk=[], loss="LS", RRT_depth=5):
        """Construct RLA.

        Attributes:
            examples : (string[]) Data
            facts : (string[]) Facts
            bk : (string[]) background information
            loss : (string) can be "LS", "LAD" or "Huber" (default is LS)
            RRT_depth : (int) depth of Relational Regression Trees
                        (default is 5)

        """
        if not examples:
            print ("No examples found!")
            exit()
        if not facts:
            print ("No facts found!")
            exit()
        if not bk:
            print ("No background file found!")
            exit()
        self.examples = examples
        self.facts = facts
        self.bk = bk
        self.loss = loss
        self.RRT_depth = RRT_depth

    def learn(self):
        """Learn a low variance point estimate.

        This method learns a low variance point estimate of the values
        using a deep RRT.
        """
        reg = GradientBoosting(regression=True, RRT=True,
                               treeDepth=self.RRT_depth, loss=self.loss)
        reg.setTargets(["value"])
        reg.learn(self.facts, self.examples, self.bk)
        self.model = reg

    def compute_distance(self, test_example, training_example, distances):
        """computes the distance between the test and training example"""

        treeLCAs = self.model.treeLCAs
        clauses = treeLCAs["value"][0]
        for clause in clauses:
            clause_LCA = clause.split(" ")[1]
            if '!' in clause:
                logical_clause = clause.split(" ")[0]
                if Prover.prove(self.facts,test_example,logical_clause.replace("!","").replace(";",",")) and Prover.prove(self.facts,training_example,logical_clause.replace("!","").replace(";",",")):
                    continue
                else:
                    clause_literals = logical_clause.split(";")
                    logical_clause = ",".join([literal for literal in clause_literals if "!" not in literal])
                    if Prover.prove(self.facts,test_example,logical_clause.replace("!","")) and Prover.prove(self.facts,training_example,logical_clause.replace("!","").replace(";",",")):
                        distances[test_example][training_example] = clause_LCA
            else:
                logical_clause = clause.split(" ")[0].replace(";",",")
                if Prover.prove(self.facts,test_example,logical_clause) and Prover.prove(self.facts,training_example,logical_clause):
                    distances[test_example][training_example] = clause_LCA 

    def test(self, K=1):
        """compute K nearest neighbors and average the values"""
        
        distances = {}
        for example in self.examples:
            distances[example] = {}
        training_examples = deepcopy(self.examples)
        '''
        for example in self.examples: #for now test examples considered same as train
            for training_example in training_examples:
                self.compute_distance(example.split(" ")[0],training_example.split(" ")[0],distances)
        '''
                


def main():
    """Call RelationalLocalApprox class with read examples, facts and bk."""
    examples, facts = [], []
    with open("examples.txt") as f:
        examples = f.read().splitlines()
    with open("facts.txt") as f:
        facts = f.read().splitlines()
    bk = ["tIn(+state,+truck,+city)",
          "bOn(+state,+box,+truck)",
          "destination(+state,+city)",
          "value(state)"]
    approximator = RLA(examples=examples, facts=facts, bk=bk)
    approximator.learn()
    approximator.test()


# Driver code
main()

