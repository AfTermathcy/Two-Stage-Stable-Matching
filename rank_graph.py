"""
Construct the rank change graph for two stages
"""
import gurobipy as gp
from gurobipy import GRB
import numpy as np
import networkx as nx
import stable_edges
import cut_graph
import random

def rank_function(A_pref, B_pref, A_quota, school, student):
    r = A_pref[school].index(student) + 1
    return r

def rank_function_B(A_pref, B_pref, A_quota, school, student):
    r = B_pref[student].index(school) + 1
    return r

'''
# Define c_1 as follows
def match_weight_function_top5(A_pref, B_pref, A_quota, school, student):
    r = rank_function(A_pref, B_pref, A_quota, school, student)
    if r == 1:
        w = random.uniform(0, 0.5)
    elif 1 < r <= 5:
        w = random.uniform(0, 0.5)
    else: 
        w = random.uniform(0, 0.5)
    return w

# Define c_2 as follows
def match_weight_function_top5_light(A_pref, B_pref, A_quota, school, student):
    r = rank_function(A_pref, B_pref, A_quota, school, student)
    if r == 1:
        w = random.uniform(0, 0.5)
    elif 1 < r <= 5:
        w = random.uniform(0, 0.5)
    else: 
        w = random.uniform(0, 0.5)
    return w



def match_weight_function_top5(A_pref, B_pref, A_quota, school, student):
    r = rank_function(A_pref, B_pref, A_quota, school, student)
    if r == 1:
        w = 0
    elif 1 < r <= 5:
        w = r/5
    else: 
        w = max(len(A_pref[school]) , 5)/5
    return w

def match_weight_function_top5_light(A_pref, B_pref, A_quota, school, student):
    r = rank_function(A_pref, B_pref, A_quota, school, student)
    if r == 1:
        w = 0
    elif 1 < r <= 5:
        w = 0
    else: 
        w = max(len(A_pref[school]) , 5)/10
    return w
'''

def match_weight_function_top5(A_pref, B_pref, A_quota, school, student):
    r_A = rank_function(A_pref, B_pref, A_quota, school, student)
    r_B = rank_function_B(A_pref, B_pref, A_quota, school, student)
    if r_A <= 5 and r_B <= 5:
        w = (r_A + r_B)/2
    else:
        w = (r_A + r_B)/2
    return w

def match_weight_function_top5_light(A_pref, B_pref, A_quota, school, student):
    r_A = rank_function(A_pref, B_pref, A_quota, school, student)
    r_B = rank_function_B(A_pref, B_pref, A_quota, school, student)
    if r_A <= 5 and r_B <= 5:
        w = (r_A + r_B)/2
    else:
        w = (r_A + r_B)/2
    return w



def construct_rank_graph_two(A_pref, B_pref, A_quota, A_pref2, B_pref2, alpha):
    st_edges_1 = stable_edges.find_all_stable_edges(A_pref, B_pref, A_quota, 1)
    st_edges_2 = stable_edges.find_all_stable_edges(A_pref2, B_pref2, A_quota, 2)
    chains_1 = cut_graph.get_school_chains(A_pref, B_pref, A_quota, st_edges_1)
    chains_2 = cut_graph.get_school_chains(A_pref2, B_pref2, A_quota, st_edges_2)
    nodes_1, arcs_infty_1 = cut_graph.construct_cut_graph(A_pref, B_pref, A_quota, st_edges_1, 1)
    nodes_2, arcs_infty_2 = cut_graph.construct_cut_graph(A_pref2, B_pref2, A_quota, st_edges_2, 2)
    nodes = ['s', 't'] + nodes_1 + nodes_2
    arcs_infty = [('s', ('s', 1)), ('s', ('s', 2)), (('t', 1), 't'), (('t', 2), 't')] + arcs_infty_1 + arcs_infty_2
    
    arcs_weighted = []
    for school in chains_2.keys():
        if chains_1[school] == []:
            pass
        elif chains_2[school] == []:
            pair_2 = ('s', 2)
            for pair_1 in chains_1[school]:
                student_1 = pair_1[1]
                rank_1 = rank_function(A_pref, B_pref, A_quota, school, student_1)
                index_1 = chains_1[school].index(pair_1)
                if index_1 == 0 and (index_1+1) != len(chains_1[school]):
                    pair_next = chains_1[school][index_1+1]
                    student_next = pair_next[1]
                    rank_next = rank_function(A_pref, B_pref, A_quota, school, student_next)
                    rank_diff = rank_1
                    arcs_weighted.append((pair_2, pair_next, alpha * rank_diff))
                    
                elif index_1+1 == len(chains_1[school]):
                    pair_next = ('t', 1)
                    rank_diff = (len(A_pref[school]) + 1) - rank_1
                    arcs_weighted.append((pair_2, pair_next, alpha * rank_diff))
                    
                else:
                    pair_next = chains_1[school][index_1+1]
                    student_next = pair_next[1]
                    rank_next = rank_function(A_pref, B_pref, A_quota, school, student_next)
                    rank_diff = rank_next - rank_1
                    arcs_weighted.append((pair_2, pair_next, alpha * rank_diff))
            
        else:
            for pair_2 in chains_2[school]:
                for pair_1 in chains_1[school]:
                    student_1 = pair_1[1]
                    rank_1 = rank_function(A_pref, B_pref, A_quota, school, student_1)
                    student_2 = pair_2[1]
                    rank_2 = rank_function(A_pref, B_pref, A_quota, school, student_2)
                    if rank_2 > rank_1: # when school gets worse
                        index_1 = chains_1[school].index(pair_1)
                        if index_1+1 < len(chains_1[school]):
                            pair_next = chains_1[school][index_1+1]
                            student_next = pair_next[1]
                            rank_next = rank_function(A_pref, B_pref, A_quota, school, student_next)
                            if rank_next > rank_2:
                                rank_diff = rank_2 - rank_1
                            else:
                                rank_diff = rank_next - rank_1
                            arcs_weighted.append((pair_2, pair_next, alpha * rank_diff))
                        else: 
                            pair_next = ('t', 1)
                            rank_diff = rank_2 - rank_1
                            arcs_weighted.append((pair_2, pair_next, alpha * rank_diff))
    arcs_match = []
    for school in chains_1.keys():
        if chains_1[school] == []:
            pass
        else:
            for pair in chains_1[school]:
                student = pair[1]
                index = chains_1[school].index(pair)
                match_weight = match_weight_function_top5(A_pref, B_pref, A_quota, school, student)
                arcs_match.append((pair, ('t', 1), match_weight))
                if index+1 < len(chains_1[school]):
                    pair_next = chains_1[school][index+1]
                    arcs_match.append((('s', 1), pair_next, match_weight))
    for school in chains_2.keys():
        if chains_2[school] == []:
            pass
        else:
            for pair in chains_2[school]:
                student = pair[1]
                index = chains_2[school].index(pair)
                match_weight = match_weight_function_top5_light(A_pref, B_pref, A_quota, school, student)
                arcs_match.append((pair, ('t', 2), match_weight))
                if index+1 < len(chains_2[school]):
                    pair_next = chains_2[school][index+1]
                    arcs_match.append((('s', 2), pair_next, match_weight))

    return nodes, arcs_infty, arcs_weighted, arcs_match

def reduce_to_mincut(nodes, arcs_infty, arcs_weighted, arcs_match):
    G = nx.DiGraph()
    for arc in arcs_infty:
        G.add_edge(arc[0], arc[1])
    for arc in arcs_weighted:
        G.add_edge(arc[0], arc[1], capacity = arc[2])
    for arc in arcs_match:
        G.add_edge(arc[0], arc[1], capacity = arc[2])
    # G.add_edges_from(arcs_infty)
    # G.add_weighted_edges_from(arcs_weighted)
    cut_value, partition = nx.minimum_cut(G, 's', 't', capacity='capacity')
    
    return cut_value, partition

def compute_objective(A_pref, B_pref, A_quota, A_pref2, B_pref2, chains_first, chains_second, cut_value):
    const = 0
    for school in chains_first.keys():
        if chains_first[school] != []:
            for i in range(len(chains_first[school])-1):
                pair = chains_first[school][i]
                student = pair[1]
                const += match_weight_function_top5(A_pref, B_pref, A_quota, school, student)
    for school in chains_second.keys():
        if chains_second[school] != []:
            for i in range(len(chains_second[school])-1):
                pair = chains_second[school][i]
                student = pair[1]
                const += match_weight_function_top5_light(A_pref, B_pref, A_quota, school, student)
    
    return cut_value - const

def recover_M1(A_pref, B_pref, chains_first, partition):
    cut_s = partition[0]
    match = []
    for school in chains_first.keys():
        intersection = [pair for pair in chains_first[school] if pair in cut_s]
        sort_order = chains_first[school]
        intersection.sort(key = lambda i: sort_order.index(i))
        if intersection != []:
            pair = intersection[-1]
            match.append((pair[0], pair[1]))
    return match

