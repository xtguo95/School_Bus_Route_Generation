"""
Module includes the routing algorithm based on MIT paper

Xiaotong Guo
Jan 2019
"""

from gurobipy import *
from Parameters import MyGlobal,detour_time
import random
from GetResult import MIT_nx_plot


def MITRouting(g_iteration, request_list):

    N = 400
    K = 1

    # Step 1: randomly generate feasible trip sets

    iteration = 1
    trip_routing_dict = {}
    trip_time_dict = {}
    trip_number_dict = {}
    trip_number = 0
    while iteration <= N/K:
        T = greedyrandomized(request_list)
        T_number = []
        for i in T:
            sub_T_number = []
            for j in i:
                sub_T_number.append(j.id)
            T_number.append(sub_T_number)
        for trip in T:
            number = 0
            time = 0
            for i in range(len(trip)):
                number = number + trip[i].number
                if i == len(trip) - 1:
                    continue
                time = time + MyGlobal.time[trip[i].ori, trip[i + 1].ori] + detour_time(trip[i].number) + trip[i].penalty
            time = time + MyGlobal.time[trip[-1].ori, trip[-1].dest] + detour_time(trip[-1].number) + trip[-1].penalty
            trip_routing_dict[trip_number] = trip
            trip_time_dict[trip_number] = time
            trip_number_dict[trip_number] = number
            trip_number = trip_number + 1
            #print(number, time)
        iteration = iteration + 1

    request_trip_dict = {}
    for request in request_list:
        request_trip_dict[request.id] = []
    for trip in trip_routing_dict.keys():
        route = trip_routing_dict[trip]
        for request in route:
            request_trip_dict[request.id].append(trip)

    # Step 2: Doing minimum cover problem
    m = Model("minimum_cover")
    r = m.addVars(trip_routing_dict.keys(), vtype=GRB.BINARY, name='r')

    for request in request_list:
        trip_list = request_trip_dict[request.id]
        m.addConstr((quicksum(r[i] for i in trip_list) == 1 ), "trip constraint")

    m.setObjective(MyGlobal.alpha_1 * quicksum(r[i] for i in trip_routing_dict.keys()) + quicksum(r[i] * trip_time_dict[i] * MyGlobal.speed * MyGlobal.alpha_2 for i in trip_routing_dict.keys()), GRB.MINIMIZE)
    #m.setObjective(quicksum(r[i] * trip_time_dict[i] for i in trip_routing_dict.keys()), GRB.MINIMIZE)
    m.optimize()

    optimal_pair = []
    for pair, var in r.items():
        if var.X == 1:
            optimal_pair.append(pair)
    print(optimal_pair)

    T_number = []
    for a in optimal_pair:
        route = trip_routing_dict[a]
        #print(trip_number_dict[i])
        #print(trip_time_dict[i])
        sub_T_number = []
        for i in route:
            sub_T_number.append(i.id)
        T_number.append(sub_T_number)

    print(m.objVal)
    output_log = open("output_{}_{}_{}.txt".format(MyGlobal.school_id, MyGlobal.Beta, MyGlobal.Gamma), "a+")
    output_log.write(str(optimal_pair) + '\n')
    output_log.write("Objective Value: " + str(m.objVal) + '\n')
    output_log.close()
    MIT_nx_plot(T_number,optimal_pair,trip_number_dict,trip_time_dict,g_iteration)


    # Step 3: post-processing
    


def greedyrandomized(request_list):
    T = []
    Cs = request_list.copy()
    while Cs != []:
        c = random.choice(Cs)
        Cs.remove(c)
        R = [c]
        N_student = c.number
        while Cs != []:
            T_new,c_new,i_new = BestInsertion(R,Cs)
            if T_new <= MyGlobal.max_travel_time and N_student + c_new.number <= MyGlobal.vehicle_capacity:
                R = Insert(R,c_new,i_new)
                N_student = N_student + c_new.number
                Cs.remove(c_new)
            else:
                break
        T.append(R)
    return T


def BestInsertion(R,Cs):
    M = 1000000
    T_best = M
    c_best = None
    i_best = None
    for c in Cs:
        for i in range(len(R)+1):
            T = detour_time(c.number) + c.penalty
            if i == 0:
                T = T + MyGlobal.time[c.ori,R[0].ori] + MyGlobal.time[R[-1].ori,R[-1].dest] \
                    + detour_time(R[0].number) + R[0].penalty
                if len(R) >=2 :
                    for j in range(1,len(R)):
                        T = T + MyGlobal.time[R[j-1].ori,R[j].ori] + detour_time(R[j].number) + R[j].penalty
            elif i == len(R):
                T = T + MyGlobal.time[R[-1].ori,c.ori] + MyGlobal.time[c.ori,c.dest] \
                    + detour_time(R[-1].number) + R[-1].penalty
                if len(R) >=2 :
                    for j in range(len(R) - 1):
                        T = T + MyGlobal.time[R[j].ori,R[j+1].ori] + detour_time(R[j].number) + R[j].penalty
            else:
                T = T + MyGlobal.time[R[i-1].ori,c.ori] + MyGlobal.time[c.ori,R[i].ori] \
                    + detour_time(R[i-1].number) + R[i-1].penalty
                for j in range(i - 1):
                    T = T + MyGlobal.time[R[j].ori,R[j+1].ori] + detour_time(R[j].number) + R[j].penalty
                for j in range(i, len(R) - 1):
                    T = T + MyGlobal.time[R[j].ori,R[j+1].ori] + detour_time(R[j].number) + R[j].penalty
                T = T + MyGlobal.time[R[-1].ori,R[-1].dest] + detour_time(R[-1].number) + R[-1].penalty
            if T < T_best:
                T_best = T
                c_best = c
                i_best = i
    return T_best,c_best,i_best


def Insert(R,c,i):
    if i == 0:
        R = [c] + R
    elif i == len(R):
        R = R + [c]
    else:
        R = R[:i] + [c] + R[i:]
    return R