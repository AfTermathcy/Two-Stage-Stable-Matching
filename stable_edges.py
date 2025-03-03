"""
Output all the stable edges
"""

import gurobipy as gp
from gurobipy import GRB
import numpy as np

def max_stable_matching_model(A_pref, B_pref, A_quota):
    
    A = list(A_pref.keys())  # A = ['A0', 'A1', ..., 'A{n-1}']
    B = list(B_pref.keys())  # B = ['B0', 'B1', ..., 'B{n-1}']
    
    pairs = []
    
    for school in A:
        for student in B:
            pairs.append((school, student))
    
    m = gp.Model("max_stable_matching")
    m.params.LogToConsole=0
    x = m.addVars(pairs, name='x', lb = 0, ub = 1, vtype = GRB.CONTINUOUS)
    m.addConstrs((x.sum('*', student) <= 1 for student in B), 'student capacity')
    m.addConstrs((x.sum(school, '*') <= 1 for school in A), 'school capacity')
    
    for school in A:
        for student in B:
            lhs = gp.LinExpr()
            lhs += x[school, student]
            for better_student in A_pref[school]:
                if better_student != student:
                    lhs += x[school, better_student]
                else:
                    break
            for better_school in B_pref[student]:
                if better_school != school:
                    lhs += x[better_school, student]
                else:
                    break
            m.addConstr(lhs >= 1, 'stability'+str(school)+' '+str(student))
            
            
    return m, x

def determine_stable_edge(A_pref, B_pref, A_quota, school, student):
    m, x = max_stable_matching_model(A_pref, B_pref, A_quota)
    m.setObjective(x[school, student], GRB.MAXIMIZE)
    m.optimize()
    if m.getObjective().getValue() >= 0.5:
        stable = True
    else:
        stable = False
    return stable

def find_all_stable_edges(A_pref, B_pref, A_quota, stage):
    A = list(A_pref.keys())  # A = ['A0', 'A1', ..., 'A{n-1}']
    B = list(B_pref.keys())  # B = ['B0', 'B1', ..., 'B{n-1}']
    
    st_edges = []
    for school in A:
        for student in B:
            if determine_stable_edge(A_pref, B_pref, A_quota, school, student) == True:
                st_edges.append((school, student, stage))
    return st_edges

