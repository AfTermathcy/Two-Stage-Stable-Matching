"""
Generate the input for the first stage (A_pref_first, B_pref_first, A_quota_first) and the second stage (A_pref_second, B_pref_second, A_quota_second)
"""

import random
import numpy as np
import copy


def instance_uniform_random_oneone(num_schools, num_students):
    schools_pref = {}
    students_pref = {}
    for i in range(num_schools):
        schools_pref[str(i)] = [str(element) for element in np.random.permutation(num_students)]
    for i in range(num_students):
        students_pref[str(i)] = [str(element) for element in np.random.permutation(num_schools)]
    return schools_pref, students_pref


def instance_uniform_random_leave(A_pref, B_pref, A_quota, prob_schools, prob_students):
    # prob is the leaving probability
    A_pref2 = copy.deepcopy(A_pref)  # need this because later we populate the preference lists stored in A_pref2, B_pref2
    B_pref2 = copy.deepcopy(B_pref)
    A = list(A_pref.keys())  # A = ['A0', 'A1', ..., 'A{n-1}']
    B = list(B_pref.keys())  # B = ['B0', 'B1', ..., 'B{n-1}']
    schools = np.random.choice([0, 1], size = len(A), p=[prob_schools, 1-prob_schools])
    students = np.random.choice([0, 1], size = len(B), p=[prob_students, 1-prob_students])
    schools_leave = []
    for i in range(len(A)):
        if schools[i] == 0:
            schools_leave.append(A[i])
    
    students_leave = []
    for i in range(len(B)):
        if students[i] == 0:
            students_leave.append(B[i])
    
    for school in A:
        if school in schools_leave:
            del A_pref2[school]
        else:
            for student in students_leave:
                if student in A_pref2[school]:
                    A_pref2[school].remove(student)
                
    for student in B:
        if student in students_leave:
            del B_pref2[student]
        else:
            for school in schools_leave:
                if school in B_pref2[student]:
                    B_pref2[student].remove(school)
    
    return A_pref2, B_pref2

