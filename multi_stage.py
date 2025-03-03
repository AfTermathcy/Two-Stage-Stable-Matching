"""
SAA
"""
import gurobipy as gp
from gurobipy import GRB
import numpy as np
import networkx as nx
import stable_edges
import cut_graph
import rank_graph
import input_generate
import random


def compute_matching_SAA(A_pref, B_pref, A_quota, prob_schools, prob_students, alpha, N):
    
    st_edges_1 = stable_edges.find_all_stable_edges(A_pref, B_pref, A_quota, 1)
    chains_1 = cut_graph.get_school_chains(A_pref, B_pref, A_quota, st_edges_1)
    nodes_1, arcs_infty_1 = cut_graph.construct_cut_graph(A_pref, B_pref, A_quota, st_edges_1, 1)
    nodes = ['s', 't'] + nodes_1
    arcs_infty = [('s', ('s', 1)), (('t', 1), 't')] + arcs_infty_1
    arcs_weighted = []
    arcs_match = []
    const = 0
    
    '''Add the arccs that stand for the quality of M_1''' 
    for school in chains_1.keys():
        if chains_1[school] == []:
            pass
        else:
            for pair in chains_1[school]:
                student = pair[1]
                index = chains_1[school].index(pair)
                match_weight = rank_graph.match_weight_function_top5(A_pref, B_pref, A_quota, school, student)
                arcs_match.append((pair, ('t', 1), match_weight))
                if index+1 < len(chains_1[school]):
                    pair_next = chains_1[school][index+1]
                    arcs_match.append((('s', 1), pair_next, match_weight))
                    const += match_weight
    
    for i in range(N):
        stage = i + 2
        A_pref2, B_pref2 = input_generate.instance_uniform_random_leave(A_pref, B_pref, A_quota, prob_schools, prob_students)
        st_edges_2 = stable_edges.find_all_stable_edges(A_pref2, B_pref2, A_quota, stage)
        chains_2 = cut_graph.get_school_chains(A_pref2, B_pref2, A_quota, st_edges_2)
        nodes_2, arcs_infty_2 = cut_graph.construct_cut_graph(A_pref2, B_pref2, A_quota, st_edges_2, stage)
        nodes += nodes_2
        arcs_infty = arcs_infty + arcs_infty_2 + [('s', ('s', stage)), (('t', stage), 't')]
        
        '''Add the arccs that stand for the rank change'''
        for school in chains_2.keys():
            if chains_1[school] == []:
                pass
            elif chains_2[school] == []:
                pair_2 = ('s', stage)
                for pair_1 in chains_1[school]:
                    student_1 = pair_1[1]
                    rank_1 = rank_graph.rank_function(A_pref, B_pref, A_quota, school, student_1)
                    index_1 = chains_1[school].index(pair_1)
                    if index_1 == 0 and (index_1+1) != len(chains_1[school]):
                        pair_next = chains_1[school][index_1+1]
                        student_next = pair_next[1]
                        rank_next = rank_graph.rank_function(A_pref, B_pref, A_quota, school, student_next)
                        rank_diff = rank_1
                        arcs_weighted.append((pair_2, pair_next, alpha * rank_diff))
                        
                    elif index_1+1 == len(chains_1[school]):
                        pair_next = ('t', 1)
                        rank_diff = (len(A_pref[school]) + 1) - rank_1
                        arcs_weighted.append((pair_2, pair_next, alpha * rank_diff))
                        
                    else:
                        pair_next = chains_1[school][index_1+1]
                        student_next = pair_next[1]
                        rank_next = rank_graph.rank_function(A_pref, B_pref, A_quota, school, student_next)
                        rank_diff = rank_next - rank_1
                        arcs_weighted.append((pair_2, pair_next, alpha * rank_diff))
                
            else:
                for pair_2 in chains_2[school]:
                    for pair_1 in chains_1[school]:
                        student_1 = pair_1[1]
                        rank_1 = rank_graph.rank_function(A_pref, B_pref, A_quota, school, student_1)
                        student_2 = pair_2[1]
                        rank_2 = rank_graph.rank_function(A_pref, B_pref, A_quota, school, student_2)
                        if rank_2 > rank_1: # when school gets worse
                            index_1 = chains_1[school].index(pair_1)
                            if index_1+1 < len(chains_1[school]):
                                pair_next = chains_1[school][index_1+1]
                                student_next = pair_next[1]
                                rank_next = rank_graph.rank_function(A_pref, B_pref, A_quota, school, student_next)
                                if rank_next > rank_2:
                                    rank_diff = rank_2 - rank_1
                                else:
                                    rank_diff = rank_next - rank_1
                                arcs_weighted.append((pair_2, pair_next, alpha * rank_diff))
                            else: 
                                pair_next = ('t', 1)
                                rank_diff = rank_2 - rank_1
                                arcs_weighted.append((pair_2, pair_next, alpha * rank_diff))
                                
        '''Add the arccs that stand for the quality of M_2'''                      
        for school in chains_2.keys():
            if chains_2[school] == []:
                pass
            else:
                for pair in chains_2[school]:
                    student = pair[1]
                    index = chains_2[school].index(pair)
                    match_weight = rank_graph.match_weight_function_top5_light(A_pref, B_pref, A_quota, school, student)
                    arcs_match.append((pair, ('t', stage), match_weight))
                    if index+1 < len(chains_2[school]):
                        pair_next = chains_2[school][index+1]
                        arcs_match.append((('s', stage), pair_next, match_weight))
                        const += match_weight
                        
    cut_value, partition = rank_graph.reduce_to_mincut(nodes, arcs_infty, arcs_weighted, arcs_match)
        
    
    M_1 = rank_graph.recover_M1(A_pref, B_pref, chains_1, partition)
    obj = cut_value - const
    return M_1, obj

def compute_school_optimal_M_1(A_pref, B_pref, A_quota, chains_first):
    M_1 = []
    for school in chains_first.keys():
        if chains_first[school] != []:
            pair = chains_first[school][0]
            student = pair[1]
            M_1.append((school, student))
    return M_1

def compute_student_optimal_M_1(A_pref, B_pref, A_quota, chains_first):
    M_1 = []
    for school in chains_first.keys():
        if chains_first[school] != []:
            pair = chains_first[school][-1]
            student = pair[1]
            M_1.append((school, student))
    return M_1

def compute_min_weight_M_1(A_pref, B_pref, A_quota, chains_first):
    M_1 = []
    m, x = stable_edges.max_stable_matching_model(A_pref, B_pref, A_quota)
    obj = gp.LinExpr()
    for school in A_pref.keys():
        for student in A_pref[school]:
            weight = rank_graph.match_weight_function_top5_light(A_pref, B_pref, A_quota, school, student)
            obj += weight * x[school, student]
            
    m.setObjective(obj, GRB.MINIMIZE)
    m.optimize()
    # value = m.getObjective().getValue()
    for school in A_pref.keys():
        for student in A_pref[school]:
            if x[school, student].X >= 0.5:
                M_1.append((school, student))
    return M_1
    
    


def compute_obj_fixed_M_1(A_pref, B_pref, A_quota, A_pref2, B_pref2, alpha, M_1):
    
    m, x = stable_edges.max_stable_matching_model(A_pref2, B_pref2, A_quota)
    obj = gp.LinExpr()
    for school in A_pref2.keys():
        student_1 = None
        for pair in M_1:
            if pair[0] == school:
                student_1 = pair[1]
        if student_1 == None:
            rank_1 = len(A_pref[school]) + 1
        else:
            rank_1 = rank_graph.rank_function(A_pref, B_pref, A_quota, school, student_1)
        
        for student in A_pref2[school]:
            weight = rank_graph.match_weight_function_top5_light(A_pref, B_pref, A_quota, school, student)
            rank_2 = rank_graph.rank_function(A_pref, B_pref, A_quota, school, student)
            if rank_2 > rank_1:
                rank_diff = rank_2 - rank_1
            else:
                rank_diff = 0
            obj += (alpha * rank_diff + weight) * x[school, student]
        
    m.setObjective(obj, GRB.MINIMIZE)
    m.optimize()
    value = m.getObjective().getValue()
    
    for school in A_pref.keys():
        student_1 = None
        for pair in M_1:
            if pair[0] == school:
                student_1 = pair[1]
        if student_1 != None:
            value += rank_graph.match_weight_function_top5(A_pref, B_pref, A_quota, school, student_1)
    
    return value


def compute_obj_fixed_M_12(A_pref, B_pref, A_quota, A_pref2, B_pref2, alpha, M_1, M_2):
    c_1 = 0
    c_2 = 0
    d = 0
    for school in A_pref.keys():
        student_1 = None
        for pair in M_1:
            if pair[0] == school:
                student_1 = pair[1]
        if student_1 == None:
            rank_1 = len(A_pref[school]) + 1
        else:
            rank_1 = rank_graph.rank_function(A_pref, B_pref, A_quota, school, student_1)
            c_1 += rank_graph.match_weight_function_top5(A_pref, B_pref, A_quota, school, student_1)
            

        student_2 = None
        for pair in M_2:
            if pair[0] == school:
                student_2 = pair[1]
        if student_2 == None:
            rank_2 = len(A_pref[school]) + 1
        else:
            rank_2 = rank_graph.rank_function(A_pref, B_pref, A_quota, school, student_2)
            c_2 += rank_graph.match_weight_function_top5_light(A_pref, B_pref, A_quota, school, student_2)
            
        if school in A_pref2.keys():
            if rank_2 > rank_1:
                rank_diff = rank_2 - rank_1
            else:
                rank_diff = 0
            d += alpha * rank_diff
            
    return c_1 + c_2 + d

def compute_obj_offline(A_pref, B_pref, A_quota, A_pref2, B_pref2, alpha):
    nodes, arcs_infty, arcs_weighted, arcs_match = rank_graph.construct_rank_graph_two(A_pref, B_pref, A_quota, A_pref2, B_pref2, alpha)
    cut_value, partition = rank_graph.reduce_to_mincut(nodes, arcs_infty, arcs_weighted, arcs_match)
    st_edges_1 = stable_edges.find_all_stable_edges(A_pref, B_pref, A_quota, 1)
    st_edges_2 = stable_edges.find_all_stable_edges(A_pref2, B_pref2, A_quota, 2)
    chains_first = cut_graph.get_school_chains(A_pref, B_pref, A_quota, st_edges_1)
    chains_second = cut_graph.get_school_chains(A_pref2, B_pref2, A_quota, st_edges_2)
    value = rank_graph.compute_objective(A_pref, B_pref, A_quota, A_pref2, B_pref2, chains_first, chains_second, cut_value)
    return value