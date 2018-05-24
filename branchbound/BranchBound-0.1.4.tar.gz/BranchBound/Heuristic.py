from solve import solve_main

def compute_initial_heuristic(tree_seq, init_alg, edge_weight_func, cpu_affinity=1, 
                                develop_tree=False, init_branching_factor=1,
                                dynamic_heuristic=False, recursive_decisions=False):
    # develop_tree represents the assemble variable
    solve(''.join(tree_seq), assemble=develop_tree)
    
    return 0
    
def compute_recursive_heuristic(init_heuristic_object):
    return 0

def update_dynamic_bound(heuristic_object, bound):
    return 0
