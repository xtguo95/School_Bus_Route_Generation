"""
Module to get final results

Xiaotong Guo
Jan 2019
"""

from Parameters import MyGlobal
import csv
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
#import osmnx as ox
import utm


def get_results(trip_list, Beta, Gamma, alternate_mode_param):
    """
    Function to get results
    """
    nx_plot(trip_list, Beta, Gamma, alternate_mode_param)

    #osmnx_plot(trip_list)

    #get_csv(trip_list)


def nx_plot(optimal_list, Beta, Gamma, alternate_mode_param):
    """
    Function to plot results using networkx module
    """
    # Draw the route

    trip_list = []
    uber_list = []
    for i in optimal_list:
        trip = MyGlobal.trip_id_dict[i]
        if trip.uber == False:
            trip_list.append(i)
        else:
            uber_list.append(MyGlobal.request_id_dict[trip.req_list[0]])

    edges = []
    with open(MyGlobal.path + 'edges.csv', mode='r') as infile:
        reader = csv.reader(infile)
        edges = [(rows[1], rows[2]) for rows in reader]

    G_base = nx.Graph()
    for edge in edges:
        G_base.add_edge(edge[0],edge[1])

    pos_ = {}

    for node in G_base.nodes():
        longitude = MyGlobal.station_dict[int(node)][1]
        latitude = MyGlobal.station_dict[int(node)][0]
        x, y, a, b = utm.from_latlon(latitude, longitude)
        pos_[node] = (x, y)

    G = nx.Graph()
    color = ['red','blue','green','cyan','magenta','yellow','darkblue','springgreen','steelblue','salmon','gold']

    nodes = []

    for i, trip in enumerate(trip_list):
        t = MyGlobal.trip_id_dict[int(trip)]
        req_list = t.req_list
        route = MyGlobal.request_routing[tuple(req_list)]
        route_color = color[(i % 10)]
        route_weight = len(req_list)
        for j, node_a in enumerate(route):
            node_list = []
            start = MyGlobal.request_id_dict[node_a].ori
            if node_a == route[-1]:
                end = MyGlobal.request_id_dict[node_a].dest
            else:
                node_b = route[j + 1]
                end = MyGlobal.request_id_dict[node_b].ori

            # Using predecessor matrix to find exactly routing in road network
            while end != start:
                node_list.append(end)
                end = MyGlobal.predecessor[start, end]
            node_list.append(start)
            node_list.reverse()
            nodes.append(node_list)

            for i in range(len(node_list) - 1):
                if G.has_edge(node_list[i], node_list[i + 1]) == True \
                        and G[node_list[i]][node_list[i + 1]]['color'] != route_color:
                    G.add_edge(node_list[i], node_list[i + 1], color='black', weight=route_weight)
                else:
                    G.add_edge(node_list[i], node_list[i + 1], color=route_color, weight=route_weight)
    nodes_ = []
    nodes_lat = []
    nodes_long = []
    for i in nodes:
        for j in i:
            nodes_.append(j)
    pos = {}
    for node in nodes_:
        longitude= MyGlobal.station_dict[node][1]
        latitude = MyGlobal.station_dict[node][0]
        x,y,a,b = utm.from_latlon(latitude,longitude)
        pos[node] = (x,y)
        nodes_lat.append(x)
        nodes_long.append(y)

    nodes_lat.sort()
    nodes_long.sort()

    edges = G.edges()
    colors = [G[u][v]['color'] for u, v in edges]
    weights = [G[u][v]['weight'] for u, v in edges]


    legend_dict = {}
    for i in range(len(trip_list)):
        t = MyGlobal.trip_id_dict[int(trip_list[i])]
        req_list = t.req_list
        time = MyGlobal.request_routing_time[tuple(req_list)]
        number = 0
        for req in req_list:
            number = number + MyGlobal.request_id_dict[req].number
        key = 'Route' + str(i + 1) + '; Total travel time: ' + str(int(time)) + '; Number of students: ' + str(number)
        route_color = color[(i % 10)]
        legend_dict[key] = route_color
    legend_dict['Common Routes'] = 'black'

    patchList = []
    for key in legend_dict:
        data_key = mpatches.Patch(color=legend_dict[key], label=key)
        patchList.append(data_key)

    fig = plt.figure(figsize=(20, 10))
    nx.draw_networkx(G_base, pos_, node_size=0, with_labels=False, linewidths=0.1,alpha = 0.1)
    #nx.draw(G, pos, edges=edges, edge_color=colors, node_size = 0, edge_weight = weights,linewidths = 10)
    nx.draw(G, pos, edgelist=edges, edge_color=colors, node_size = 0, linewidths = 10)
    for req in MyGlobal.request_list:
        x, y, a, b = utm.from_latlon(MyGlobal.station_dict[req.ori][0],MyGlobal.station_dict[req.ori][1])
        plt.scatter(x, y, s=30 , c='b',marker = 'o')
    for r in uber_list:
        x, y, a, b = utm.from_latlon(MyGlobal.station_dict[r.ori][0], MyGlobal.station_dict[r.ori][1])
        plt.scatter(x, y, s=100, c='r', marker='X')
    dest = req.dest
    x, y, a, b = utm.from_latlon(MyGlobal.station_dict[dest][0], MyGlobal.station_dict[dest][1])
    plt.scatter(x, y, s=500, c='r', marker='*')
    plt.legend(handles=patchList,fontsize = 'medium',loc = 0)
    plt.show()
    #fig.savefig(MyGlobal.results_path + str(MyGlobal.school_id) +'_'+ str(MyGlobal.Beta) +'_' + str(MyGlobal.Gamma) + '_' +'optimal_routes.png')
    fig.savefig(str(MyGlobal.school_id) +'_'+ str(Beta) +'_' + str(Gamma) + '_' + str(alternate_mode_param) + '_' + 'optimal_routes.png')


def MIT_nx_plot(trip_list,trip_number_list,trip_number_dict,trip_time_dict,g_iteration):
    """
    Function to plot results using networkx module
    """
    # Draw the route
    edges = []
    with open(MyGlobal.path + 'edges.csv', mode='r') as infile:
        reader = csv.reader(infile)
        edges = [(rows[1], rows[2]) for rows in reader]

    G_base = nx.Graph()
    for edge in edges:
        G_base.add_edge(edge[0],edge[1])

    pos_ = {}

    for node in G_base.nodes():
        longitude = MyGlobal.station_dict[int(node)][1]
        latitude = MyGlobal.station_dict[int(node)][0]
        x, y, a, b = utm.from_latlon(latitude, longitude)
        pos_[node] = (x, y)

    G = nx.Graph()
    color = ['red','blue','green','cyan','magenta','yellow','darkblue','springgreen','steelblue','salmon','gold']

    nodes = []

    for i,trip in enumerate(trip_list):
        route = trip
        route_color = color[(i % 10)]
        route_weight = len(trip)
        for j, node_a in enumerate(route):
            node_list = []
            start = MyGlobal.request_id_dict[node_a].ori
            if node_a == route[-1]:
                end = MyGlobal.request_id_dict[node_a].dest
            else:
                node_b = route[j + 1]
                end = MyGlobal.request_id_dict[node_b].ori

            # Using predecessor matrix to find exactly routing in road network
            while end != start:
                node_list.append(end)
                end = MyGlobal.predecessor[start, end]
            node_list.append(start)
            node_list.reverse()
            nodes.append(node_list)

            for i in range(len(node_list) - 1):
                if G.has_edge(node_list[i], node_list[i + 1]) == True \
                        and G[node_list[i]][node_list[i + 1]]['color'] != route_color:
                    G.add_edge(node_list[i], node_list[i + 1], color='black', weight=route_weight)
                else:
                    G.add_edge(node_list[i], node_list[i + 1], color=route_color, weight=route_weight)
    nodes_ = []
    nodes_lat = []
    nodes_long = []
    for i in nodes:
        for j in i:
            nodes_.append(j)
    pos = {}
    for node in nodes_:
        longitude= MyGlobal.station_dict[node][1]
        latitude = MyGlobal.station_dict[node][0]
        x,y,a,b = utm.from_latlon(latitude,longitude)
        pos[node] = (x,y)
        nodes_lat.append(x)
        nodes_long.append(y)

    nodes_lat.sort()
    nodes_long.sort()

    edges = G.edges()
    colors = [G[u][v]['color'] for u, v in edges]
    weights = [G[u][v]['weight'] for u, v in edges]

    legend_dict = {}
    for i,trip in enumerate(trip_number_list):
        time = trip_time_dict[trip]
        number = trip_number_dict[trip]
        key = 'Route' + str(i + 1) + '; Total travel time: ' + str(int(time)) + '; Number of students: ' + str(number)
        route_color = color[(i % 10)]
        legend_dict[key] = route_color
    legend_dict['Common Routes'] = 'black'

    patchList = []
    for key in legend_dict:
        data_key = mpatches.Patch(color=legend_dict[key], label=key)
        patchList.append(data_key)


    fig = plt.figure(figsize=(20, 10))
    nx.draw_networkx(G_base, pos_, fig_height=10, fig_width=20, node_size=0, with_labels=False, linewidths=0.1,alpha = 0.1)
    nx.draw(G, pos, edges=edges, edge_color=colors, node_size = 0, edge_weight = weights,linewidths = 10)
    for req in MyGlobal.request_list:
        x, y, a, b = utm.from_latlon(MyGlobal.station_dict[req.ori][0],MyGlobal.station_dict[req.ori][1])
        plt.scatter(x, y, s=30 , c='b',marker = 'o')
    dest = req.dest
    x, y, a, b = utm.from_latlon(MyGlobal.station_dict[dest][0], MyGlobal.station_dict[dest][1])
    plt.scatter(x, y, s=500, c='r', marker='*')
    plt.legend(handles=patchList, fontsize='medium', loc=0)
    plt.show()
    fig.savefig( str(MyGlobal.school_id) +'_optimal_routes_MIT_'+ str(g_iteration) +'.png')


def get_csv(trip_list):
    """
    Function to get results in CSV format
    """
    # Get CSV file
    output_list = []
    output_list.append([MyGlobal.objective_value])
    for trip in trip_list:
        t = MyGlobal.trip_id_dict[int(trip)]
        req_list = t.req_list
        route = MyGlobal.request_routing[tuple(req_list)]

        number = 0
        for req in req_list:
            number = number + MyGlobal.request_id_dict[req].number
        route.append("number")
        route.append(number)
        time = MyGlobal.request_routing_time[tuple(req_list)]
        route.append("time")
        route.append(int(time))
        output_list.append(route)

    with open(MyGlobal.results_path + "results.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(output_list)


def draw_rr_graph(rr_graph,delete = False):
    """
    The function to draw the rr_graph
    :param rr_graph: rr_graph dictionary
    :return:
    """
    # Draw background
    edges = []

    with open(MyGlobal.path + 'edges.csv', mode='r') as infile:
        reader = csv.reader(infile)
        edges = [(rows[1], rows[2]) for rows in reader]

    G_base = nx.Graph()
    for edge in edges:
        G_base.add_edge(edge[0], edge[1])

    pos_ = {}

    for node in G_base.nodes():
        longitude = MyGlobal.station_dict[int(node)][1]
        latitude = MyGlobal.station_dict[int(node)][0]
        x, y, a, b = utm.from_latlon(latitude, longitude)
        pos_[node] = (x, y)


    fig = plt.figure(figsize=(20, 10))
    for node_a in rr_graph:
        req_a = MyGlobal.request_id_dict[node_a]
        lata = MyGlobal.station_dict[req_a.ori][0]
        longa = MyGlobal.station_dict[req_a.ori][1]
        ax, ay, aa, ab = utm.from_latlon(lata, longa)
        for node_b in rr_graph[node_a]:
            req_b = MyGlobal.request_id_dict[node_b]
            latb = MyGlobal.station_dict[req_b.ori][0]
            longb = MyGlobal.station_dict[req_b.ori][1]
            bx, by, ba, bb = utm.from_latlon(latb, longb)
            plt.plot([ax,bx], [ay,by], 'bo-', alpha=0.5, linewidth=0.4,markersize = 1)
    nx.draw_networkx(G_base, pos_, fig_height=10, fig_width=20, node_size=0, with_labels=False, linewidths=0.1, alpha=0.1)

    dest = req_a.dest
    x, y, a, b = utm.from_latlon(MyGlobal.station_dict[dest][0], MyGlobal.station_dict[dest][1])
    plt.scatter(x, y, s=500, c='r', marker='*')

    plt.show()
    if delete == False:
        fig.savefig(MyGlobal.results_path + str(MyGlobal.school_id)+'_' + str(MyGlobal.Beta) +'_' + str(MyGlobal.Gamma) + '_' +'rr_graph.png')
    else:
        fig.savefig(MyGlobal.results_path +  str(MyGlobal.school_id)+'_' + str(MyGlobal.Beta) +'_' + str(MyGlobal.Gamma) + '_' +'rr_graph_delete.png')


def clustering_graph(demand):
    """

    :return:
    """
    # Draw background
    edges = []
    with open(MyGlobal.path + 'edges.csv', mode='r') as infile:
        reader = csv.reader(infile)
        edges = [(rows[1], rows[2]) for rows in reader]

    G_base = nx.Graph()
    for edge in edges:
        G_base.add_edge(edge[0], edge[1])

    pos_ = {}

    for node in G_base.nodes():
        longitude = MyGlobal.station_dict[int(node)][1]
        latitude = MyGlobal.station_dict[int(node)][0]
        x, y, a, b = utm.from_latlon(latitude, longitude)
        pos_[node] = (x, y)

    fig = plt.figure(figsize=(20, 10))
    nx.draw_networkx(G_base, pos_, fig_height=10, fig_width=20, node_size=0, with_labels=False, linewidths=0.1,
                     alpha=0.1)
    dest = MyGlobal.school_id
    x, y, a, b = utm.from_latlon(MyGlobal.station_dict[dest][0], MyGlobal.station_dict[dest][1])
    plt.scatter(x, y, s=500, c='r', marker='*')
    for d1 in demand:
        d1_ori = int(d1[0])
        for d2 in demand:
            if d1 == d2:
                continue
            d2_ori = int(d2[0])
            if MyGlobal.time[d1_ori,d2_ori] + MyGlobal.time[d2_ori,dest] <= 3600 or MyGlobal.time[d2_ori,d1_ori] + MyGlobal.time[d1_ori,dest] <= 3600:
                x1, y1, a1, b1 = utm.from_latlon(MyGlobal.station_dict[d1_ori][0], MyGlobal.station_dict[d1_ori][1])
                x2, y2, a2, b2 = utm.from_latlon(MyGlobal.station_dict[d2_ori][0], MyGlobal.station_dict[d2_ori][1])
                plt.plot([x1, x2], [y1, y2], '--', alpha=0.5, linewidth=0.5, c='b')

    for d in demand:
        x1, y1, a1, b1 = utm.from_latlon(MyGlobal.station_dict[d[0]][0], MyGlobal.station_dict[d[0]][1])
        plt.scatter(x1, y1, s=10, c='b', marker='o',alpha = 0.3)
    fig.show()
    fig.savefig("node_compression.png")
