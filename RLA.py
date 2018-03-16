from GradientBoosting import GradientBoosting
class RLA(object):
    '''class for distance based local value approximation'''

    def __init__(self,examples=[],facts=[],bk=[],loss="LS",RRT_depth=5):
        '''constructor for class'''
        if not examples:
            print ("No examples found!")
            exit()
	if not facts:
	    print ("No facts found!")
	    exit()
        if not bk:
            print ("No background file found!")
	self.examples = examples
	self.facts = facts
	self.bk = bk
	self.loss = loss #can be LS, LAD or Huber
	self.RRT_depth = RRT_depth

    def learn(self):
        '''learns a low variance point estimate
           of the values using a deep RRT'''
        reg = GradientBoosting(regression=True,RRT=True,treeDepth=self.RRT_depth,loss=self.loss)
        reg.setTargets(["value"])
        reg.learn(self.facts,self.examples,self.bk)
        self.model = reg

def main():
    '''main method, calls RelationalLocalApprox class
       with read examples,facts,bk'''
    examples,facts = [],[]
    with open("examples.txt") as f:
        examples = f.read().splitlines()
    with open("facts.txt") as f:
        facts = f.read().splitlines()
    bk = ["tIn(+state,+truck,-city)",
	  "bOn(+state,+box,-truck)",
	  "destination(+state,+city)",
	  "value(state)"]
    approximator = RLA(examples=examples,facts=facts,bk=bk)
    approximator.learn()

main() 
