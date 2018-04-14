"""Module representing Relational Local Approximator."""
from GradientBoosting import GradientBoosting
#from Logical import Prover
import Utils
class Domain(object):
    """contains which domain we are using"""

    def __init__(self,domain="logistics"):
        """constructor"""
        self.domain_name = domain
        if self.domain_name == "logistics":
            self.bk = ["tIn(+state,+truck,+city,[h0;h1;h2;h3;h4])",
                       "destination(+state,+city)",
                       "move(+state,+truck,[h0;h1;h2;h3;h4])",
                       "unload(+state,+truck,[h0;h1;h2;h3;h4])",
                       "value(state)"]
class Data(object):
    """holds the data object"""

    def __init__(self,domain="logistics",horizon=None):
        """constructor, creates data about a domain"""
        self.horizon = horizon
        self.facts = []
        self.examples = []
        self.domain = domain
        domain_object = Domain(domain=self.domain)
        self.bk = domain_object.bk

    def get_bk(self):
        """returns background file"""
        return self.bk

    def get_facts(self):
        """return the facts contained in the data object"""
        return self.facts

    def get_examples(self):
        """returns all examples in the data object"""
        return self.examples

    def get_horizon(self):
        """returns horizon"""
        return self.horizon

    def add_facts(self,facts):
        """adds facts to the data object"""
        self.facts += facts

    def add_examples(self,examples):
        """adds examples to the data object"""
        self.examples += examples

    def __repr__(self):
        """string representation"""
        return (str(self.facts)+"\n"+str(self.examples)+"\n"+str(self.bk)+"\n"+str(self.horizon))


class RLPOMDP(object):
    """pomdp"""

    def __init__(self,observations,train_test_split=0.8):
        """constructor"""
        observations = observations[1:200]
        observations = self.parse_observations(observations)
        self.training_observations = observations[:int(len(observations)*train_test_split)]
        self.testing_observations = observations[int(len(observations)*train_test_split):]
        self.make_data(self.training_observations)
        self.make_data(self.testing_observations,train=False)
        self.model = None
        self.train()
        print("-------Test----------")
        self.test()

    def train(self):
        """train the model"""
        reg_learners = [GradientBoosting(regression=True,RRT=True,treeDepth=5) for i in range(len(self.training_data_objects))]
        for idx,reg_learner in enumerate(reg_learners):
            reg_learner.setTargets(["value"])
            reg_learner.learn(self.training_data_objects[2].get_facts(),self.training_data_objects[2].get_examples(),self.training_data_objects[2].get_bk())
            self.model = reg_learner
            break

    def test(self):
        """prelim testing"""
        test_data_object = self.testing_data_objects[2]
        facts = test_data_object.get_facts()
        examples = test_data_object.get_examples()
        self.model.infer(facts,examples)
        print("======original=====")
        print(examples)
        

    def compute_value(self,belief_state,alpha_vector):
        """computes value of belief_state and action combination"""
        n_states = len(belief_state)
        return sum([belief_state[i]*alpha_vector[i] for i in range(n_states)])

    def create_data_set(self,current_data_object,facts,current_example):
        """creates the data set for the different horizons for learning"""
        current_data_object.add_facts(facts)
        current_data_object.add_examples(current_example)
        
        

    def make_data(self,observations,train=True):
        """makes training or testing data set"""
        max_observation_length = max([len(observation) for observation in observations])
        if train:
            self.training_data_objects = [Data(domain="logistics",horizon=i) for i in range(max_observation_length)]
            data_objects = self.training_data_objects
        else:
            self.testing_data_objects = [Data(domain="logistics",horizon=i) for i in range(max_observation_length)]
            data_objects = self.testing_data_objects
        for idx,observation in enumerate(observations):
            #print (observation)
            observation_length = len(observation)
            facts = []
            for i in range(observation_length):
                observation_i = observation[i].split(',')
                belief_state = [float(item.strip()) for item in observation_i[0][1:-1].split(' ')]
                alpha_vector = [float(item.strip()) for item in observation_i[2][1:-1].split(' ') if item.strip() != ""]
                action = ["unload(s"+str(idx)+",t1,h"+str(i)+")"]
                if observation_i[1] == '0':
                    action = ["move(s"+str(idx)+",t1,h"+str(i)+")"]
                state_percept = ["destination(s"+str(idx)+",cd)",#,h"+str(i)+")",
                                 "bOn(s"+str(idx)+",b1,t1,h"+str(i)+")",
                                 "tIn(s"+str(idx)+",t1,cd,h"+str(i)+")"]
                if observation_i[3] == '0':
                    state_percept = ["destination(s"+str(idx)+",cd)",#,h"+str(i)+")",
                                     "bOn(s"+str(idx)+",b1,t1,h"+str(i)+")",
                                     "tIn(s"+str(idx)+",t1,ncd,h"+str(i)+")"]
                value = self.compute_value(belief_state,alpha_vector)
                example = ["value(s"+str(idx)+") "+str(value)]
                facts += state_percept + action
                self.create_data_set(data_objects[i],facts, example)
            

    def parse_observations(self,observations):
        """makes trajectories from the observations"""
        trajectories = []
        trajectory = []
        for observation in observations:
            trajectory.append(observation)
            if "None" in observation:
                trajectories.append(trajectory)
                trajectory = []
        return trajectories
                        

    def print_training_observations(self):
        """prints the training observations"""
        for observation in self.training_observations:
            print (observation)

    def print_testing_observations(self):
        """prints the testing observations"""
        for observation in self.testing_observations:
            print (observation)

def main():
    with open("observations.txt") as f:
        observations = f.read().splitlines()
        pomdp_object = RLPOMDP(observations)

if __name__ == '__main__':
    main()
