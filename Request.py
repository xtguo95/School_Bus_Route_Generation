'''
Module to compute the pairwise graph of requests and edge compression

Xiaotong Guo
Jan 2019
'''

from Parameters import MyGlobal,detour_time
import networkx as nx
#import metis
from GetResult import draw_rr_graph


def compute_rr_graph(Beta, request_list = MyGlobal.request_list):
    '''
    Compare each pairs of two requests with same destination
    :return: the list of edges in pairwise graph of requests
    '''
    rr_graph = {}
    for i in request_list:
        rr_graph[i.id] = []
        for j in request_list:
            if j.id <= i.id:
                continue
            elif i.dest != j.dest:
               continue
            elif i.number + j.number > MyGlobal.vehicle_capacity:
                continue
            else:
                x = combine_two_request(i,j)
                if x == True:
                    rr_graph[i.id].append(j.id)

    # draw_rr_graph(rr_graph, False)
    # rr_graph_1 = distance_heuristic(rr_graph)
    rr_graph_2 = adjusted_distance_heuristic(rr_graph, Beta)
    # draw_rr_graph(rr_graph_2, True)

    return rr_graph_2


def combine_two_request(request_a,request_b):
    '''
    The function to check whether two requests with same destination can share same vehicles
    :param request_a: first request
    :param request_b: second request
    :return: Ture or False for share-ability of two requests
    '''
    a_number = request_a.number
    b_number = request_b.number
    a_penalty = request_a.penalty
    b_penalty = request_b.penalty
    penalty_time = a_penalty + b_penalty
    detour = detour_time(a_number) + detour_time(b_number)
    time_ab = MyGlobal.time[request_a.ori,request_b.ori]
    time_ba = MyGlobal.time[request_b.ori,request_a.ori]
    time_ad = MyGlobal.time[request_a.ori,request_a.dest]
    time_bd = MyGlobal.time[request_b.ori,request_b.dest]
    if (time_ab + time_bd + detour + penalty_time) <= MyGlobal.max_shareable_time \
            or (time_ba + time_ad + detour + penalty_time) <= MyGlobal.max_shareable_time:
        Total_number = request_a.number + request_b.number
        MyGlobal.request_number[(request_a.id,request_b.id)] = Total_number
        if (time_ab + time_bd) >= (time_ba + time_ad):
            MyGlobal.request_routing[(request_a.id,request_b.id)] = [request_b.id , request_a.id]
            MyGlobal.request_routing_time[(request_a.id,request_b.id)] = time_ba + time_ad + detour + penalty_time
        elif (time_ab + time_bd) < (time_ba + time_ad):
            MyGlobal.request_routing[(request_a.id, request_b.id)] = [request_a.id, request_b.id]
            MyGlobal.request_routing_time[(request_a.id, request_b.id)] = time_ab + time_bd + detour + penalty_time
        return True
    else:
        return False


def distance_heuristic(rr_graph, Beta):
    '''
    Function to implement the distance heuristic to delete edges in rr_graph
    :param rr_graph: rr_graph dictionary
    :return: Revised rr_graph
    '''
    revised_rr_graph = {}

    graph = {}
    for i in rr_graph:
        graph[i] = []

    for req_a in rr_graph:
        request_a = MyGlobal.request_id_dict[req_a]
        for req_b in rr_graph[req_a]:
            request_b = MyGlobal.request_id_dict[req_b]
            travel_time = MyGlobal.time[request_a.ori,request_b.ori]
            graph[req_a].append((travel_time,request_b))
            travel_time_ = MyGlobal.time[request_b.ori,request_a.ori]
            graph[req_b].append((travel_time_, request_a))

    new_graph = {}
    for i in graph:
        graph[i].sort()
        number = 0
        delete = False
        for n,j in enumerate(graph[i]):
            number = number + j[1].number
            if number > Beta * MyGlobal.vehicle_capacity:
                new_graph[i] = graph[i][:n+1]
                delete = True
                break
        if delete == False:
            new_graph[i] = graph[i]


    for i in rr_graph:
        revised_rr_graph[i] = []
        for j in rr_graph[i]:
            request_i = MyGlobal.request_id_dict[i]
            request_j = MyGlobal.request_id_dict[j]
            for tuple in new_graph[i]:
                if tuple[1] == request_j:
                    revised_rr_graph[i].append(j)
                    break
            for tuple in new_graph[j]:
                if tuple[1] == request_i:
                    if j not in revised_rr_graph[i]:
                        revised_rr_graph[i].append(j)
                    break
    return revised_rr_graph


def adjusted_distance_heuristic(rr_graph, Beta):
    '''
    Function to implement the distance heuristic to delete edges in rr_graph
    :param rr_graph: rr_graph dictionary
    :return: Revised rr_graph
    '''
    revised_rr_graph = {}

    graph = {}
    for i in rr_graph:
        graph[i] = []

    for req_a in rr_graph:
        request_a = MyGlobal.request_id_dict[req_a]
        for req_b in rr_graph[req_a]:
            request_b = MyGlobal.request_id_dict[req_b]
            travel_time_ab = MyGlobal.time[request_a.ori,request_b.ori]
            travel_time_a = MyGlobal.time[request_a.ori,request_a.dest]
            travel_time_b = MyGlobal.time[request_b.ori, request_b.dest]
            travel_time_ab_adj = travel_time_ab * (travel_time_ab + travel_time_b) / travel_time_a
            graph[req_a].append((travel_time_ab_adj,request_b))
            travel_time_ba = MyGlobal.time[request_b.ori,request_a.ori]
            travel_time_ba_adj = travel_time_ba * (travel_time_ba + travel_time_a) / travel_time_b
            graph[req_b].append((travel_time_ba_adj, request_a))

    new_graph = {}
    for i in graph:
        graph[i].sort()
        number = 0
        delete = False
        for n,j in enumerate(graph[i]):
            number = number + j[1].number
            if number > Beta * MyGlobal.vehicle_capacity:
                new_graph[i] = graph[i][:n+1]
                delete = True
                break
        if delete == False:
            new_graph[i] = graph[i]

    for i in rr_graph:
        revised_rr_graph[i] = []
        for j in rr_graph[i]:
            request_i = MyGlobal.request_id_dict[i]
            request_j = MyGlobal.request_id_dict[j]
            for tuple in new_graph[i]:
                if tuple[1] == request_j:
                    revised_rr_graph[i].append(j)
                    break
            for tuple in new_graph[j]:
                if tuple[1] == request_i:
                    if j not in revised_rr_graph[i]:
                        revised_rr_graph[i].append(j)
                    break
    return revised_rr_graph