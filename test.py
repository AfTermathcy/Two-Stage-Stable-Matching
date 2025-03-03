import gurobipy as gp
from gurobipy import GRB
import numpy as np
import networkx as nx
import input_generate
import stable_edges
import cut_graph
import rank_graph
import input_generate
import multi_stage
import random
import pickle


A_test, B_test = input_generate.instance_uniform_random_oneone(36, 36)

prob_schools, prob_students = 0.25, 0.25

A_quota = []

st_edges_test = stable_edges.find_all_stable_edges(A_test, B_test, A_quota, 1)

chains_test = cut_graph.get_school_chains(A_test, B_test, A_quota, st_edges_test)

lbd = [0.1, 0.2, 0.3, 0.5, 0.75, 1, 2]

N = 10

value = {}

value_ALG_average, value_school_optimal_average, value_student_optimal_average, value_min_weight_average, value_offline_optimal_average = {}, {}, {}, {}, {}



for alpha in lbd:
    
    value[alpha, 'ALG'] = []
    value[alpha, 'school_optimal'] = []
    value[alpha, 'student_optimal'] = []
    value[alpha, 'min_weight'] = []
    value[alpha, 'offline'] = []
    
    M_1_test, obj_test = multi_stage.compute_matching_SAA(A_test, B_test, A_quota, prob_schools, prob_students, alpha, N)
    
    M_school_optimal = multi_stage.compute_school_optimal_M_1(A_test, B_test, A_quota, chains_test)
    
    M_student_optimal = multi_stage.compute_student_optimal_M_1(A_test, B_test, A_quota, chains_test)
    
    M_min_weight = multi_stage.compute_min_weight_M_1(A_test, B_test, A_quota, chains_test)
    
    test_round = 5
    
    
    for rd in range(test_round):
    
        A2_test, B2_test = input_generate.instance_uniform_random_leave(A_test, B_test, A_quota, prob_schools, prob_students)
        
        value[alpha, 'ALG'].append(multi_stage.compute_obj_fixed_M_1(A_test, B_test, A_quota, A2_test, B2_test, alpha, M_1_test))
        
        value[alpha, 'school_optimal'].append(multi_stage.compute_obj_fixed_M_1(A_test, B_test, A_quota, A2_test, B2_test, alpha, M_school_optimal))
        
        value[alpha, 'student_optimal'].append(multi_stage.compute_obj_fixed_M_1(A_test, B_test, A_quota, A2_test, B2_test, alpha, M_student_optimal))
        
        value[alpha, 'min_weight'].append(multi_stage.compute_obj_fixed_M_1(A_test, B_test, A_quota, A2_test, B2_test, alpha, M_min_weight))
        
        value[alpha, 'offline'].append(multi_stage.compute_obj_offline(A_test, B_test, A_quota, A2_test, B2_test, alpha))
        
    value_ALG_average[alpha] = sum(value[alpha, 'ALG']) / test_round
    
    value_school_optimal_average[alpha] = sum(value[alpha, 'school_optimal']) / test_round
    
    value_student_optimal_average[alpha] = sum(value[alpha, 'student_optimal']) / test_round
    
    value_min_weight_average[alpha] = sum(value[alpha, 'min_weight']) / test_round
    
    value_offline_optimal_average[alpha] = sum(value[alpha, 'offline']) / test_round

    print('For lambda = ', alpha, 'ALG = ', value_ALG_average[alpha], 'school_optimal = ', value_school_optimal_average[alpha], 'student_optimal = ', value_student_optimal_average[alpha], 'min_weight', value_min_weight_average[alpha], 'offline = ', value_offline_optimal_average[alpha])
    
with open('obj_values_' + str(len(A_test.keys())) + '.pkl', 'wb') as f:
    
    pickle.dump([value],f)

# to-do: compare with the optimal offline value...
# test_value_student_optimal = multi_stage.compute_obj_fixed_M_1(test_A, test_B, A_quota, test_A2, test_B2, alpha, test_M_student_optimal)

# To output data:
# with open('obj_values_3.pkl', 'rb') as f:
#   value = pickle.load(f)