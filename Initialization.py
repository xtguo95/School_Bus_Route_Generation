'''
Module to choose the demand w.r.t. certain school and node compression

Xiaotong Guo
Jan 2019
'''

import Structure
from Parameters import MyGlobal
import math
from gurobipy import *
import TSP


def school_demand(school_id):
    """
    Function to filter demand for certain schools
    """
    demand = []
    for student in MyGlobal.demand:
        if student[1] == school_id:
            demand.append(list(student))
    return demand


def node_compression(demand, Beta, Gamma, alternate_mode_param, virtual_walking_dsitance):
    """
    Function for node compression techniques
    :param demand:
    :return:
    """
    bus_stops = list(MyGlobal.station_dict.keys())
    distance = MyGlobal.distance

    d2d = 0
    student_list = []
    for id, s in enumerate(demand):
        reachable_stop = []
        ori = int(s[0])
        dest = int(s[1])
        walking_distance = s[2]
        if walking_distance == 0:
            maximum_walking_distance = virtual_walking_dsitance * 1.60934
            # maximum_walking_distance = MyGlobal.fake_walking_distance * 1.60934
            d2d += 1
        else:
            maximum_walking_distance = walking_distance * 1.60934
        for stop in bus_stops:
            stop_node = stop
            d = distance[ori][stop_node]
            if d <= maximum_walking_distance:
                reachable_stop.append(stop_node)
        student = Structure.student(id,ori,dest,walking_distance,reachable_stop)
        student_list.append(student)

    print("The number of door-to-door students is: " + str(d2d))
    output_log = open("output_{}_{}_{}_{}.txt".format(MyGlobal.school_id, Beta, Gamma, alternate_mode_param), "a+")
    output_log.write("The number of door-to-door students is: " + str(d2d) + '\n')
    output_log.close()

    # Store in the MyGlobal object
    for student in student_list:
        MyGlobal.student_id_dict[student.id] = student

    # m = Model("IP")
    # m.setParam("OutputFlag", 0)
    #
    # mu = {}
    # for stop in bus_stops:
    #     for student in student_list:
    #         mu[(stop, student.id)] = m.addVar(vtype=GRB.BINARY, name='mu')
    #
    # nu = {}
    # for stop in bus_stops:
    #     nu[stop] = m.addVar(vtype=GRB.BINARY, name='nu')
    #
    # for student in student_list:
    #     stop_list = student.reachable_list
    #     m.addConstr(quicksum(mu[(id, student.id)] for id in stop_list) == 1, str(student.id))
    #
    # for student in student_list:
    #     stop_list = student.reachable_list
    #     for stop in bus_stops:
    #         if stop not in stop_list:
    #             m.addConstr(mu[(stop, student.id)] == 0)
    #
    # for stop in bus_stops:
    #     m.addConstr(quicksum(mu[(stop, student.id)] for student in student_list) <= MyGlobal.max_students_per_stop)
    #
    # for stop in bus_stops:
    #     for student in student_list:
    #         m.addConstr(nu[stop] >= mu[(stop, student.id)])
    #
    # m.setObjective(quicksum(nu[stop] for stop in bus_stops), GRB.MINIMIZE)
    # m.optimize()
    #
    # optimal_stops = []
    # for id, var in nu.items():
    #     if var.X == 1:
    #         optimal_stops.append(id)
    #
    # dic_stops = {}
    # for stop in optimal_stops:
    #     dic_stops[stop] = 0
    #
    # for (stop, student_id), var in mu.items():
    #     if var.X == 1:
    #         dic_stops[stop] += 1
    #         student = MyGlobal.student_id_dict[student_id]
    #         student.assigned_stop = stop

    m = Model("IP")
    m.setParam("OutputFlag", 0)
    x = {}
    for stop in bus_stops:
        x[int(stop)] = m.addVar(vtype=GRB.BINARY, name='x')

    for student in student_list:
        stop_list = student.reachable_list
        m.addConstr(quicksum(x[id] for id in stop_list) >= 1, str(student.id))

    m.setObjective(quicksum(x[i] for i in range(0,len(bus_stops))), GRB.MINIMIZE)
    m.optimize()

    optimal_stops = []
    for id, var in x.items():
        if var.X == 1:
            optimal_stops.append(id)

    dic_covered_stops = {}
    for student in student_list:
        dic_covered_stops[student.id] = []
        for stop in optimal_stops:
            if stop in student.reachable_list:
                dic_covered_stops[student.id].append(stop)

    dic_stops = {}
    for stop in optimal_stops:
        dic_stops[stop] = 0

    for student in student_list:
        if len(dic_covered_stops[student.id]) == 1:
            dic_stops[dic_covered_stops[student.id][0]] += 1
            student.assigned_stop = dic_covered_stops[student.id][0]

    for student in student_list:
        if len(dic_covered_stops[student.id]) > 1:
            listt = dic_covered_stops[student.id]
            comparing_list = []
            for i in listt:
                if dic_stops[i] >= MyGlobal.vehicle_capacity:
                    continue
                comparing_list.append((dic_stops[i], i))
            comparing_list.sort()
            dic_stops[comparing_list[-1][1]] += 1
            student.assigned_stop = comparing_list[-1][1]

    if sum(dic_stops.values()) != len(student_list):
        print("Error in node compression")

    return_demand = []
    for stop in optimal_stops:
        demand_ = [stop,MyGlobal.school_id,dic_stops[stop]]
        return_demand.append((demand_))

    return return_demand, student_list


def demand_to_request(demand, student_list):
    '''
    Convert the demand to request object and store in the list in MyGloble object
    '''

    for i, value in enumerate(demand):
        s_list = []
        d2d_student_list = []
        stop_id = value[0]

        for student in student_list:
            if student.assigned_stop == stop_id:
                s_list.append(student.id)
                if student.walking_distance == 0:
                    d2d_student_list.append(student.id)

        if d2d_student_list == []:
            request = Structure.request(MyGlobal.total_request_number, int(stop_id), int(value[1]), int(value[2]),
                                        s_list, d2d_student_list)
            MyGlobal.request_list.append(request)
            MyGlobal.request_id_dict[MyGlobal.total_request_number] = request
            MyGlobal.total_student_number = MyGlobal.total_student_number + value[2]
            MyGlobal.total_request_number = MyGlobal.total_request_number + 1
        else:
            if len(d2d_student_list) == 1:
                # if len(s_list) == len(d2d_student_list):
                #     student_ori = MyGlobal.student_id_dict[d2d_student_list[0]].ori
                #     routes = [stop_id,student_ori,stop_id]
                #     penalty = MyGlobal.time[stop_id,student_ori] + MyGlobal.time[student_ori,stop_id]
                #     request = Structure.request(MyGlobal.total_request_number, int(stop_id), int(value[1]),
                #                                 int(value[2]), s_list, d2d_student_list, penalty, routes)
                #     MyGlobal.request_list.append(request)
                #     MyGlobal.request_id_dict[MyGlobal.total_request_number] = request
                #     MyGlobal.total_student_number = MyGlobal.total_student_number + value[2]
                #     MyGlobal.total_request_number = MyGlobal.total_request_number + 1
                #     continue
                student_ori = MyGlobal.student_id_dict[d2d_student_list[0]].ori
                routes = [stop_id,student_ori,stop_id]
                penalty = MyGlobal.time[stop_id,student_ori] + MyGlobal.time[student_ori,stop_id]
            else:
                points = []
                for student in d2d_student_list:
                    student_ori = MyGlobal.student_id_dict[student].ori
                    points.append(student_ori)
                if stop_id not in points:
                    points = [stop_id] + points
                if len(points) == 2:
                    penalty = MyGlobal.time[points[0],points[1]] + MyGlobal.time[points[1],points[0]]
                    if points[0] == stop_id:
                        routes = points + [stop_id]
                    else:
                        routes = [stop_id] + points
                else:
                    penalty, routes = TSP.small_tsp(points)

            request = Structure.request(MyGlobal.total_request_number, int(stop_id), int(value[1]), int(value[2]),
                                        s_list, d2d_student_list, penalty, routes)
            MyGlobal.request_list.append(request)
            MyGlobal.request_id_dict[MyGlobal.total_request_number] = request
            MyGlobal.total_student_number = MyGlobal.total_student_number + value[2]
            MyGlobal.total_request_number = MyGlobal.total_request_number + 1


