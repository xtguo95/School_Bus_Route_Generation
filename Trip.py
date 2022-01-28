'''
Module to compute Request-Trip Graph, enumerating trip list

Xiaotong Guo
Jan 2019
'''

from Parameters import MyGlobal,detour_time
import Structure


def compute_rt_graph(rr_graph, Beta, Gamma, alternate_mode_param):
    '''
    The function to compute RT-Graph
    :param rr_graph: graph for edges of pairwise graph
    :return: return the dictionary of all possible trips; Key: number of requests in one trip, Values: a list of trips
    '''
    trip_list = {}

    # Add trips of only one request
    T_temp1 = []
    for i in MyGlobal.request_list:
        MyGlobal.request_routing_time[tuple([i.id])] = MyGlobal.time[i.ori,i.dest] + detour_time(i.number) + i.penalty
        MyGlobal.request_routing[tuple([i.id])] = [i.id]
        MyGlobal.request_number[tuple([i.id])] = i.number
        trip = Structure.trip(MyGlobal.total_trip_number, [i.id])
        MyGlobal.trip_id_dict[MyGlobal.total_trip_number] = trip
        MyGlobal.total_trip_number += 1
        T_temp1.append(trip)
    trip_list[1] = T_temp1

    # Add trips of two requests
    T_temp2 = []
    for id in rr_graph:
        for i in rr_graph[id]:
            trip = Structure.trip(MyGlobal.total_trip_number, (id,i))
            MyGlobal.trip_id_dict[MyGlobal.total_trip_number] = trip
            MyGlobal.total_trip_number += 1
            T_temp2.append(trip)
    trip_list[2] = T_temp2

    # Add trips of request size k (k > 2)
    for k in range(3,100):
        print("Consider the trip with " + str(k) + " requests")
        T_temp = []
        T_last = trip_list[k-1] # Trip list of size k-1
        for trip in T_last:
            first_id = trip.req_list[0]
            last_id = trip.req_list[-1]
            for id in rr_graph[first_id]:
                x = clique_check(rr_graph, trip.req_list, last_id, id, Gamma)
                if x == True:
                    request_list = list(trip.req_list) + [id]
                    y = check_feasibility(request_list)
                    if y == True:
                        trip_ = Structure.trip(MyGlobal.total_trip_number, request_list)
                        MyGlobal.trip_id_dict[MyGlobal.total_trip_number] = trip_
                        MyGlobal.total_trip_number += 1
                        T_temp.append(trip_)
        print(len(T_temp))
        output_log = open("output_{}_{}_{}_{}.txt".format(MyGlobal.school_id, Beta, Gamma, alternate_mode_param), "a+")
        output_log.write("Consider the trip with " + str(k) + " requests" + '\n')
        output_log.write(str(len(T_temp)) + '\n')
        output_log.close()
        if len(T_temp) == 0:
            break
        trip_list[k] = T_temp

    return trip_list


def clique_check(rr_graph,trip,last_id,id, Gamma):
    '''
    The function to check whether a list of request node form clique
    :param rr_graph: rr_graph
    :param trip: previous request list
    :param last_id: id of last request in trip
    :param id: id of new request
    :return: True of False
    '''
    if id <= last_id:
        return False
    count = 0
    for i in trip:
        if id not in rr_graph[i]:
            count = count + 1
    if count > len(trip) * Gamma:
        return False
    return True


def check_feasibility(request_list):
    '''
    The function to check feasibility for a list of request
    :param request_list: a list of requests
    :return: True or False of feasibility
    '''
    previous_trip = tuple(request_list[:-1])
    last_request_id = request_list[-1]
    previous_trip_order = MyGlobal.request_routing[previous_trip]
    previous_trip_time = MyGlobal.request_routing_time[previous_trip]
    previous_number = MyGlobal.request_number[previous_trip]
    number = previous_number + MyGlobal.request_id_dict[last_request_id].number
    if number > MyGlobal.vehicle_capacity:
        return False
    best_time = 0
    best_order = []
    for i in range(len(previous_trip) + 1):
        if i == 0:
            r1 = MyGlobal.request_id_dict[last_request_id]
            r2 = MyGlobal.request_id_dict[previous_trip_order[0]]
            temp_time = previous_trip_time + MyGlobal.time[r1.ori,r2.ori]
            temp_order = [last_request_id] + previous_trip_order
            best_time = temp_time
            best_order = temp_order
        elif i != len(previous_trip):
            r1 = MyGlobal.request_id_dict[previous_trip_order[i-1]]
            r2 = MyGlobal.request_id_dict[previous_trip_order[i]]
            r3 = MyGlobal.request_id_dict[last_request_id]
            temp_time = previous_trip_time \
                        - MyGlobal.time[r1.ori,r2.ori] \
                        + MyGlobal.time[r1.ori,r3.ori] \
                        + MyGlobal.time[r3.ori,r2.ori]
            temp_order = previous_trip_order[:i] + [last_request_id] + previous_trip_order[i:]
            if temp_time < best_time:
                best_time = temp_time
                best_order = temp_order
        else:
            r1 = MyGlobal.request_id_dict[previous_trip_order[-1]]
            r2 = MyGlobal.request_id_dict[last_request_id]
            temp_time = previous_trip_time \
                        - MyGlobal.time[r1.ori,r1.dest]\
                        + MyGlobal.time[r1.ori,r2.ori]\
                        + MyGlobal.time[r2.ori,r2.dest]
            temp_order = previous_trip_order + [last_request_id]
            if temp_time < best_time:
                best_time = temp_time
                best_order = temp_order
    if (best_time + detour_time(MyGlobal.request_id_dict[last_request_id].number)
        + MyGlobal.request_id_dict[last_request_id].penalty) < MyGlobal.max_travel_time:
        MyGlobal.request_routing_time[tuple(request_list)] =\
            best_time + detour_time(MyGlobal.request_id_dict[last_request_id].number) \
            + MyGlobal.request_id_dict[last_request_id].penalty
        MyGlobal.request_routing[tuple(request_list)] = best_order
        MyGlobal.request_number[tuple(request_list)] = number
        return True
    else:
        return False



