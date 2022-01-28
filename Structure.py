'''
Module to define the class used in whole model
'''

class request:
    '''
    Class for request object
    '''

    def __init__(self, id , origin, destination, number_of_people, s_list, d2d_student_list, penalty = 0, routes = None):
        self.id = id
        self.ori = origin
        self.dest = destination
        self.number = number_of_people
        self.student_list = s_list # [i,j,...] with i represents the id of students
        self.d2d_student_list = d2d_student_list # [i,j,...] with i represents the id of students
        self.penalty = penalty # TSP for d2d pickup cost
        self.routes = routes # [i,j,..] with i represents the road node number


class trip:
    '''
    Class for trip object
    '''

    def __init__(self, id, request_list, uber = False):
        self.id = id
        self.req_list = request_list
        self.uber = uber


class student:
    '''
    Class for student
    '''

    def __init__(self,id, ori, dest, walking_distance, reachable_list, assigned_stop = None):
        self.id = id
        self.ori = ori
        self.dest = dest
        self.walking_distance = walking_distance
        self.reachable_list = reachable_list
        self.assigned_stop = assigned_stop
