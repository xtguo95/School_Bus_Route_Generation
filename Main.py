'''
Module containing main simulation function

Xiaotong Guo
Jan 2019
'''

import numpy as np
import pandas as pd
import csv
import pickle
import time
from Initialization import demand_to_request, school_demand, node_compression
from Request import compute_rr_graph
from Trip import compute_rt_graph
from Assignment import optimal_assignment
from GetResult import get_results, clustering_graph
from MIT_routing import MITRouting
from Parameters import MyGlobal
import sys


def main():
    '''
    Main function process all functions in other modules
    '''

    # Beta [1, 1.3, 1.6, 1.9, 2.2, 2.5, 2.8, 3.1, 3.4, 3.7, 4] # MyGlobal.Beta
    # Gamma [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1] # MyGlobal.Gamma
    Beta = 100 # float(sys.argv[1])
    Gamma = 0 # float(sys.argv[2])
    alternate_mode_param = 10000 # float(sys.argv[3]) # MyGlobal.alpha_3
    virtual_walking_dsitance = 0.2

    print("School id: ", MyGlobal.school_id)
    print("alternate parameters: ", alternate_mode_param)
    print("Beta heuristic: ", Beta)
    print("Gamma heuristic: ", Gamma)
    output_log = open("output_{}_{}_{}_{}.txt".format(MyGlobal.school_id, Beta, Gamma, alternate_mode_param), "a")
    output_log.write("Beta heuristic: " + str(Beta) + '\n')
    output_log.write("Gamma heuristic: " + str(Gamma) + '\n')
    output_log.close()

    demand_without_stops = school_demand(MyGlobal.school_id)
    demand, student_list = node_compression(demand_without_stops, Beta, Gamma, alternate_mode_param, virtual_walking_dsitance)
    # Convert demand data into a list of request object
    demand_to_request(demand, student_list)
    print("Number of students need to pick up is: " , MyGlobal.total_student_number)
    print("Number of clusters: ", len(MyGlobal.request_list))
    output_log = open("output_{}_{}_{}_{}.txt".format(MyGlobal.school_id, Beta, Gamma, alternate_mode_param), "a+")
    output_log.write("Number of students need to pick up is: " + str(MyGlobal.total_student_number) + '\n')
    output_log.write("Number of clusters: " + str(len(MyGlobal.request_list)) + '\n')
    output_log.close()
    # clustering_graph(demand_without_stops) #Draw graph for node compression technique
    """
    temp_list = []
    for request in MyGlobal.request_list:
        dist = MyGlobal.time[request.ori,request.dest]
        temp_list.append((dist,request))
    temp_list.sort()
    MyGlobal.request_list = []
    count = 0
    for i in range(len(temp_list)):
        request = temp_list[-(i + 1)][1]
        request.id = count
        MyGlobal.request_id_dict[count] = request
        MyGlobal.request_list.append(request)
        count += 1
    """

    # MIT Routing Comparison
    # i = 1
    # while i <= 10:
    #     print("Current Iteration: ", i)
    #     output_log = open("output_{}_MIT.txt".format(MyGlobal.school_id), "a+")
    #     output_log.write("Current Iteration is: " + str(i) + '\n')
    #     output_log.close()
    #     MITRouting(i, MyGlobal.request_list)
    #     i += 1
    # exit(0)

    global_start = time.time()

    # Compute the pairwise graph (RR-Graph)
    start = time.time()
    rr_graph = compute_rr_graph(Beta)
    print("Computational time for RR-Graph: ", time.time() - start)
    output_log = open("output_{}_{}_{}_{}.txt".format(MyGlobal.school_id, Beta, Gamma, alternate_mode_param), "a+")
    output_log.write("Computational time for RR-Graph: " + str(time.time() - start) + '\n')
    output_log.close()

    # Compute the request-trip Graph (RV-Graph)
    start = time.time()
    trip_list = compute_rt_graph(rr_graph, Beta, Gamma, alternate_mode_param)
    #trip_list = Trip_new.compute_rt_graph(rr_graph)
    print("Number of trips in RV-Graph: ", MyGlobal.total_trip_number)
    print("Computational time for RV-Graph: ", time.time() - start)
    output_log = open("output_{}_{}_{}_{}.txt".format(MyGlobal.school_id, Beta, Gamma, alternate_mode_param), "a+")
    output_log.write("Number of trips in RV-Graph: " + str(MyGlobal.total_trip_number) + '\n')
    output_log.write("Computational time for RV-Graph: " + str(time.time() - start) + '\n')
    output_log.close()

    # Find best requests combination of request-trip Graph (RV-Graph) as an ILP model
    start = time.time()
    optimal_list = optimal_assignment(trip_list, Beta, Gamma, alternate_mode_param)
    print("Computational time for Optimal Assignment: ", time.time() - start)
    output_log = open("output_{}_{}_{}_{}.txt".format(MyGlobal.school_id, Beta, Gamma, alternate_mode_param), "a+")
    output_log.write("Computational time for Optimal Assignment: " + str(time.time() - start) + '\n')
    output_log.close()

    # Get the results of optimal_list
    get_results(optimal_list, Beta, Gamma, alternate_mode_param)
    print("Finish Optimization and Get Output")

    print("Overall Computational time: ", time.time() - global_start)
    output_log = open("output_{}_{}_{}_{}.txt".format(MyGlobal.school_id, Beta, Gamma, alternate_mode_param), "a+")
    output_log.write("Overall Computational time: " + str(time.time() - global_start) + '\n')
    output_log.close()
    print("--------------------------------------------------------------")

if __name__ == '__main__':
    main()