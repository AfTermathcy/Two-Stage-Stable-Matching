# Two-Stage-Stable-Matching
We simulate the two stage stable matching problem on uniform random markets. To reproduce the results, one needs to rerun the files in order. The following numerical experiments use a reduction to a minimum s-t cut problem over the poset of edges defined in the extended abstract: "Two-stage stochastic stable matching" which appeared at the International Conference on Integer Programming and Combinatorial Optimization 2024. We note that this is equivalent to a minimum s-t cut problem over the poset of rotations defined in the full version paper "Minimum Cut Representability of Stable Matching Problems" Submitted to Operations Research.
In the following, we use $A$ to represent schools, and $B$ to represent students.

## input_generate.py
This file generates the preference profiles of the aggregate market. We assume that all students and schools are present in the first stage, and a subset of students and schools remain in the second stage.

`instance_uniform_random_oneone` generates the aggregate market. In our implementation, we choose `nun_schools = num_students = 50`.

`instance_uniform_random_leave` takes the aggregate market and the leaving probabilities as input, then output the second stage instance with `A_pref2` and `B_pref2` as a dictionary of preference lists among students and schools remaining in the second stage, respectively. 

`A_quota` can be set to be 1.

## stable_edges.py
This file searches all stable edges/pairs in a given school matching instance. In particular, for every pair ab, we check if ab is a stable pair using linear programming. 

`max_stable_matching_model` establishes the linear programming that computes the maximum weight stable matching for any given weights on edges. This function is embedded frequently in other functions. 

`determine_stable_edge` checks if a given pair `(school, student)` is stable in the school matching instance given by `(A_pref, B_pref, A_quota)`. The function returns `True` if and only if the given pair is a stable pair.

`find_all_stable_edges` searches all stable pairs in a school matching instance. It returns a list of stable pairs `st_edges`.

## cut_graph.py
For every (single stage) school matching instance, we can construct a cut graph using the stable edges. This whole process is equivalent to convert the poset of rotations to a directed graph to a cut graph introduced in our paper. The purpose of using stable edges is to construct a more clear structure when computing the rank changes between two stages. We explain as follows:

Suppose that a rotation is $\rho = ((a_1b_1, a_2b_2, a_3b_3), (a_1b_2, a_2b_3, a_3b_1))$, then $\rho$ is a node in the cut graph of rotations. In this file, we construct, instead of one node to denote $\rho$, a clique that consists of the six stable pairs $a_1b_1, a_2b_2, a_3b_3, a_1b_2, a_2b_3, a_3b_1$, each of which is a separate node. For any two nodes in this clique, we have a forward and backward arc with infinity capacity to make sure they are not separated. When constructing other arc $e$ that go outside (resp., inside) $\rho$, we use one or multiple arcs that go outside $a_1b_1, a_2b_2, a_3b_3, a_1b_2, a_2b_3, a_3b_1$, and the sum of their capacities equal to that of $e$. This does not change the minimum cut structure, since as long as the cut in this file is finite, then we can recover the rotations. 

`get_school_chains` gets all the chains from the school side. A chain on a specific school $a$ is defined as all the stable pairs that contains $a$, and we order them by the preference order given by `A_pref`.

`compare_stable_edges` computes whether `pair_1` dominates `pair_2`. More precisely, a pair $a_1b_1$ dominates another pair $a_2b_2$ if and only if the rotation $\rho_1$ that contains $a_1b_1$ dominates the rotation $\rho_2$ that contains $a_2b_2$ under the partial order of rotation.

`construct_cut_graph` computes a directed graph with nodes in `nodes` and arcs in `arcs_infty`, where the nodes are the stable pairs with source `s` and sink `t`. The arcs represents the domination under `compare_stable_edges`. 



## rank_graph.py
While `cut_graph.py` constructs the infinite arcs inside one stage, `rank_graph.py` computes the finite arcs between the copies from the disjoint union of two stage instances.

`rank_function` returns the rank of a student on a school's preference list. 

`rank_function_B` returns the rank of a school on a student's preference list. 

`match_weight_function_top5` and `match_weight_function_top5_light` give two ways of assign the weight to a pair `(school, student)`. In the defalut setting, we compute the egalitarian weight $w(ab) = (r_a(b)+r_b(a))/2$. 

`construct_rank_graph_two` constructs the cut graph that involves two stages. Inside each stage, we use `construct_cut_graph` from `cut_graph.py` to construct the infinity arcs. Between the two stage, we compute the rank change function defined in the paper, and add arcs between each pair of stable pairs that involve the same school. 

`reduce_to_mincut` takes use of the built-in minimum cut solver from NetworkX package, and compute the minimum cut of a directed graph. `cut_value` gives the optimal value, and `partition` gives a 2-d array that represents the partition of the nodes from the optimal cut. 

`recover_M1` recovers the first stage stable matching from the cut on the cut graph given by `partition`. This is achived by picking the minimum on each chain from `chains_first` that appears in `partition[0]`.


## multi_stage.py
Finally, we compute the minimum cut from the graph generated by `cut_graph.py` and `rank_graph.py`, and taking the input from a school matching instance. 

`compute_matching_SAA` is our main funciton, which simulates a random school matching instance and compute the optimal first stage stable matching using the reduction to minimum cut. The output `M_1` gives the first stage matching, and `obj` is the objective value (linear weights + rank difference)




