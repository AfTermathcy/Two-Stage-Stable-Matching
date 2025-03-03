"""
Construct the cut graph for one stage
"""

import gurobipy as gp
from gurobipy import GRB
import numpy as np
import stable_edges

def get_school_chains(A_pref, B_pref, A_quota, st_edges):
    A = list(A_pref.keys())  # A = ['A0', 'A1', ..., 'A{n-1}']
    B = list(B_pref.keys())  # B = ['B0', 'B1', ..., 'B{n-1}']
    chains = {school: [] for school in A}
    for school in A:
        chain = []
        for edge in st_edges:
            if edge[0] == school:
                chain.append(edge)
        
        sort_order = A_pref[school]
        chain.sort(key = lambda i: sort_order.index(i[1]))
        
        chains[school] = chain

    return chains

def compare_stable_edges(A_pref, B_pref, A_quota, st_edges, pair_1, pair_2):
    a_1 = pair_1[0]
    b_1 = pair_1[1]
    a_2 = pair_2[0]
    b_2 = pair_2[1]
    if a_1 == a_2:
        if A_pref[a_1].index(b_1) < A_pref[a_1].index(b_2):
            pair_1_dominate_pair_2 = True
        else:
            pair_1_dominate_pair_2 = False
    else:
        m, x = stable_edges.max_stable_matching_model(A_pref, B_pref, A_quota)
        obj = gp.LinExpr()
        obj += x[a_1, b_1]
        for not_better_student in A_pref[a_2]:
            if A_pref[a_2].index(b_2) <= A_pref[a_2].index(not_better_student):
                obj += x[a_2, not_better_student]
            
        m.setObjective(obj, GRB.MAXIMIZE)
        m.optimize()
        if m.getObjective().getValue() >= 1.5:
            pair_1_dominate_pair_2 = False
        else:
            pair_1_dominate_pair_2 = True

    return pair_1_dominate_pair_2
    

def construct_cut_graph(A_pref, B_pref, A_quota, st_edges, stage):
    s = ('s', stage)
    t = ('t', stage)
    nodes = [s, t] + st_edges
    arcs_infty = []
    chains = get_school_chains(A_pref, B_pref, A_quota, st_edges)
    for school_1 in chains.keys():
        for school_2 in chains.keys():
            if school_1 == school_2:
                if chains[school_1] != []:
                    arcs_infty.append((s, chains[school_1][0]))
                    for i in range(len(chains[school_1])-1):
                        arcs_infty.append((chains[school_1][i+1], chains[school_1][i]))
            else:
                for pair_1 in chains[school_1]:
                    if chains[school_2] != []:
                        if compare_stable_edges(A_pref, B_pref, A_quota, st_edges, chains[school_2][0], pair_1) == True:
                            for pair_2 in chains[school_2]:
                                if compare_stable_edges(A_pref, B_pref, A_quota, st_edges, pair_2, pair_1) == True:
                                    continue
                                else:
                                    NSD = pair_2
                                    break
                            arcs_infty.append((pair_1, NSD))
                        
    return nodes, arcs_infty
