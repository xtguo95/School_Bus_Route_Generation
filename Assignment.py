'''
Module to solve the ILP problem given all possible requests (trip-request assignment)

Xiaotong Guo
Jan 2019
'''

from gurobipy import *
from Parameters import MyGlobal
import time
import Structure

def optimal_assignment(trip_dict, Beta, Gamma, alternate_mode_param):
    '''
    Function to get optimal assignment of all possible trip list
    :param trip_list: The dictionary of all possible trips; Key: number of requests in one trip, Values: a list of trips
    :return: The optimal tirps list including id of trip
    '''

    start = time.time()
    optimal_list = []

    trip_list = []
    for k in trip_dict:
        trip_list = trip_list + trip_dict[k]
    #temp_trip_list = trip_dict

    trip_without_uber = []
    for trip in trip_list:
        t = trip.id
        trip_without_uber.append(t)

    # Adding uber trips
    trip_with_uber = []
    for r in MyGlobal.request_list:
        trip = Structure.trip(MyGlobal.total_trip_number,[r.id],True)
        MyGlobal.trip_id_dict[MyGlobal.total_trip_number] = trip
        MyGlobal.total_trip_number += 1
        trip_list.append(trip)
        trip_with_uber.append(trip.id)

    # Requests list
    request = []
    for r in MyGlobal.request_list:
        req = r.id
        request.append(req)

    req_trip_dict = {}
    for r in request:
        req_trip_dict[r] = []
        for trip in trip_list:
            list = trip.req_list
            if r in list:
                req_trip_dict[r].append(trip)

    # Trip cost
    trip_cost = {}
    for trip in trip_list:
        if trip.uber == False:
            req_list = trip.req_list
            t = trip.id
            travel_time = MyGlobal.request_routing_time[tuple(req_list)]
            trip_cost[t] = travel_time
        elif trip.uber == True:
            request_id = trip.req_list[0]
            r = MyGlobal.request_id_dict[request_id]
            travel_time = MyGlobal.time[r.ori,r.dest]
            t = trip.id
            trip_cost[t] = travel_time * r.number
            #print(trip_cost[t])
        else:
            print("Error in uber choices setting")

    # Model
    m = Model("assignment")
    m.setParam('TimeLimit', 21600) #m.setParam('TimeLimit', 21600)
    m.setParam('MIPFocus', 1)
    m.setParam('Heuristics', 1)

    y = {}
    for trip in trip_list:
        t = trip.id
        y[t] = m.addVar(vtype=GRB.BINARY, name= 'y')
        #y[t] = m.addVar(vtype=GRB.CONTINUOUS,lb=0,ub=1,name='y')
    for r in request:
        req_trip_list = req_trip_dict[r]
        m.addConstr(quicksum(y[t.id] for t in req_trip_list) == 1, "request constraints")

    # for t in trip_with_uber:
    #     m.addConstr(y[t] == 0)

    m.setObjective(quicksum((trip_cost[t] * MyGlobal.speed * MyGlobal.alpha_2 + MyGlobal.alpha_1) * y[t] for t in trip_without_uber) +
                   quicksum((trip_cost[t] * MyGlobal.speed * alternate_mode_param) * y[t] for t in trip_with_uber), GRB.MINIMIZE)

    m.optimize()
    print("Got optimal solution for ILP", time.time() - start)

    for i, var in y.items():
        if abs(var.X - 1) <= 1e-2:
            optimal_list.append(i)

    MyGlobal.objective_value = m.objVal

    print(optimal_list)
    #print(len(optimal_list))
    print("Objective Value: ", m.objVal)

    number = 0
    for i in optimal_list:
        req_list = MyGlobal.trip_id_dict[i].req_list
        if MyGlobal.trip_id_dict[i].uber == True:
            for j in req_list:
                number += MyGlobal.request_id_dict[j].number

    print("The number of students taking Uber is: " + str(number))

    output_log = open("output_{}_{}_{}_{}.txt".format(MyGlobal.school_id, Beta, Gamma, alternate_mode_param), "a+")
    output_log.write("Got optimal solution for ILP" + str(time.time() - start) + '\n')
    output_log.write(str(optimal_list) + '\n')
    output_log.write("Objective Value: " + str(m.objVal) + '\n')
    output_log.write("The number of students taking Uber is: " + str(number) + '\n')
    output_log.close()

    return optimal_list
