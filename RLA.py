"""Module representing Relational Local Approximator."""
from GradientBoosting import GradientBoosting


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


# Driver code
main()
