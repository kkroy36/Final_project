class Domain(object):
    """contains which domain we are using"""

    def __init__(self,domain="logistics"):
        """constructor"""
        self.domain_name = domain
        if self.domain_name == "logistics":
            self.bk = ["tIn(+state,+truck,+city)",
                       "bOn(+state,+box,+truck)",
                       "destination(+state,+city)",
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

    def get_facts(self):
        """return the facts contained in the data object"""
        return self.facts

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
        observations = observations[1:]
        observations = self.parse_observations(observations)
        self.training_observations = observations[:int(len(observations)*train_test_split)]
        self.testing_observations = observations[int(len(observations)*train_test_split):]
        self.make_data(self.training_observations)
        self.make_data(self.testing_observations,train=False)
        self.train()

    def train()

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
                action = ["unload(s"+str(idx)+",t1)"]
                if observation_i[1] == '0':
                    action = ["move(s"+str(idx)+",t1)"]
                state_percept = ["destination(s"+str(idx)+",cd)",
                                 "bOn(s"+str(idx)+",b1,t1)",
                                 "tIn(s"+str(idx)+",t1,cd)"]
                if observation_i[3] == '0':
                    state_percept = ["destination(s"+str(idx)+",cd)",
                                     "bOn(s"+str(idx)+",b1,t1)",
                                     "tIn(s"+str(idx)+",t1,ncd)"]
                value = self.compute_value(belief_state,alpha_vector)
                example = ["value(s"+str(idx)+") "+str(value)+")"]
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
