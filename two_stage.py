#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 19 21:11:32 2023

@author: chengyuehe
"""

import pandas as pd
import numpy as np
import itertools
import random
import copy
import re

# Reproducibility
random.seed(10)
np.random.seed(10)

# executes gale_shapley
# input is A and B's preference lists
# outputs stable matching and the last a and b that was matched (used for Gale Shapley extended)

def gale_shapley(A_pref, B_pref, A_quota):
    A_pref2 = copy.deepcopy(A_pref)  # need this because later we populate the preference lists stored in A_pref2, B_pref2
    B_pref2 = copy.deepcopy(B_pref)
    A = list(A_pref.keys())  # A = ['A0', 'A1', ..., 'A{n-1}']
    B = list(B_pref.keys())  # B = ['B0', 'B1', ..., 'B{n-1}']
    A_free = A[:]  # = A initially (Courses)
    A_matched = {}  # keys = women (B) (CAs), values = currently matched men (A)(Courses)
    A_count = {} # current matched counts
    B_matched = {}

    # initialize phase
    for i in A:
        B_matched[i] = []
        A_count[i] = 0

    while A_free:  # while there are still unmatched men (Courses)
        current_a = A_free.pop(0)
        # if no CA is required, remove this course and continue
        if A_quota[current_a] == 0:
            continue
        # get current node's preference list
        pref_a = A_pref2[current_a]
        not_matched = 1
        while not_matched:
            if len(pref_a) == 0:
                break
            partner = pref_a.pop(0)  # modified pref_a since pop(0) will remove the first element in the preference list
            match = A_matched.get(partner)  # get() returns None if partner is not yet in A_matched
            if current_a in B_pref[partner]:
                if not match: # i.e., if match == None
                    # if not yet matched
                    A_matched[partner] = current_a  # match current_a with partner
                    B_matched[current_a].append(partner)
                    A_count[current_a] += 1
                    if A_count[current_a] == A_quota[current_a]:
                        not_matched = 0

                else:  # if partner is matched to some man already
                    # if potential partner already matched, check preference list
                    pref_b = B_pref2[partner]
                    if pref_b.index(match) > pref_b.index(current_a):
                        # prefers current_a
                        A_matched[partner] = current_a
                        B_matched[current_a].append(partner)
                        B_matched[match].remove(partner)
                        A_count[current_a] += 1
                        if A_count[current_a] == A_quota[current_a]:
                            not_matched = 0
                        # no need to update last pair matched, because the original match will be matched later
                        # add original match to A_free list to be matched again
                        A_count[match] -= 1
                        if match not in A_free:
                            A_free.append(match)

    return A_matched, B_matched






def rank_student():
    
    return


def rank_school():
    
    return

