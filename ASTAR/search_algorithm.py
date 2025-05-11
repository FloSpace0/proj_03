import search_problem as SearchProblem

# È la definizione generale di un algoritmo di ricerca. 
# È una classe che tiene traccia di quanti nodi sono stati espansi, ha un metodo solve, che dovremo implementare
class Node:
    def __init__(self, state, parent = None, action = None, g = 0) -> None:
        self.state = state # State is a pair (x,y)
        self.parent = parent
        self.action = action
        self.g = g
        
class SearchAlgorithm:
    def __init__(self, view = False) -> None:
        self.expanded = 0
        self.expanded_states = set()
        self.view = view

    def solve(self, problem: SearchProblem) -> list:
        raise NotImplementedError()

    
    def update_expanded(self, state):
        if (self.view):
            self.expanded_states.add(state)
        self.expanded += 1

    def reset_expanded(self):
        if (self.view):
            self.expanded_states = set()
        self.expanded = 0
        
    # questa funzione va sempre in sù dal figlio e trova così la soluzione dicendoci tutti i genitori del figlio
    def extract_solution(self, node) -> list:
        sol = list()
        while (node.parent is not None):
            sol.insert(0,node.action) #node è definita nello stesso file, è una classe nodo, che fa da contenitore di informazioni
            node = node.parent
        return sol


# ogni volta che vogliamo mettere nuove cose nella frontiera ci mettiamo il nodo e non lo stato


    def count_parents(self, node):
        count = 0
        while (node.parent is not None):
            count += 1
            node = node.parent
        return count