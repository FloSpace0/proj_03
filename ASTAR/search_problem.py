class SearchProblem(object):
    """
    This is a base Search Problem. Implement this to get your specific implementation depending on your domain
    """
    def __init__(self, init, goal, cost :dict):
        self.init = init
        self.goal = goal
        self.cost = cost
    
    def getSuccessors(self, state) -> set:
        raise Exception("Not implemented")
  
    def isGoal(self, state) -> bool:
        raise Exception("Not implemented")
