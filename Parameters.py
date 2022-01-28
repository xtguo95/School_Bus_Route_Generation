'''
Module to define static parameters for model and data

Xiaotong Guo
Jan 2019
'''

import pandas as pd
import csv
import pickle

class MyGlobal:

    school_id = 6248

    path = "Data/"

    results_path = "results/" + str(school_id) + "/"

    vehicle_capacity = 72

    alpha_1 = 200 # Cost for a bus per day 200

    alpha_2 = 1 # Cost for operating a bus per mile 1

    #alpha_3 = 2 # Cost for taking a Uber per mile 2

    # Beta = 1000
    #
    # Gamma = 0

    max_students_per_stop = 72

    fake_walking_distance = 0.5

    max_travel_time = 3600

    max_shareable_time = 3600

    #detour_time = 60 # Control paramater: Average detour time for picking up one cluster

    vehicle_cost = 3600

    # Read time file; data format: matrix, each entry represents the travel time between two road nodes (s)
    #time = pd.read_csv(path + 'time.csv', sep=',', header=None).values
    time = pickle.load(open(path+'time_new.p',"rb"))

    # Read predecessor file;
    # data format: matrix, each entry represents starting from row node, the predecessor of column node in shortest path
    #predecessor = pd.read_csv(path + 'predecessor.csv', sep=',', header=None).values
    predecessor = pickle.load(open(path+'predecessor.p',"rb"))

    # Read distance file; data format: matrix, each entry represents the distance between two road nodes (km)
    #distance = pd.read_csv(path + 'distance.csv', sep=',', header=None).values
    distance = pickle.load(open(path+'distance.p',"rb"))

    # Format of demand: request time, origin station, destination station, number of people for this request
    #demand = pd.read_csv(path + 'demand_cluster_graph.csv', sep=',', header=None).values
    #demand = pickle.load(open(path + 'demand.p', "rb"))
    demand = pd.read_csv(path + 'student_data.csv', sep=',', header=None).values

    # station dictionary(Road network node as station); Keys: node_id , Values: (Latitude, Longtitude)
    #station_dict = {}
    #with open(path + 'nodes.csv', mode='r') as infile:
    #    reader = csv.reader(infile)
    #    station_dict = {int(rows[0]): (float(rows[1]), float(rows[2])) for rows in reader}
    station_dict = pickle.load(open(path+'node.p',"rb"))

    # The list contains demand in request object format
    request_list = []
    # The dictionary given the request id then get request object
    request_id_dict = {}

    # Dictionary: key: requests following the order of id, values: the best routing
    request_routing = {}
    # Dictionary: key: requests following the order of id, values: travel time for best routing
    request_routing_time = {}
    # Dictionary: key: requests following the order of id, values: the number of people for all requests
    request_number = {}

    # Dictionary: key: Trip ID, Values: Trip
    trip_id_dict = {}

    # Record the total number of trips added into trip_list
    total_trip_number = 0

    # Record the total number of students for certain school
    total_student_number = 0

    # Track total number of request have already initialize
    total_request_number = 0

    # Store the objective value for MIP
    objective_value = 0

    # Dic for student, key: student id, value: student data
    student_id_dict = {}

    speed = distance[1][133] / time[1][133] # miles/second

def detour_time(number_of_students):
    """
    :return:
    """
    a = 15 # s
    b = 5 # s
    stop_time = a + b * number_of_students

    return stop_time
