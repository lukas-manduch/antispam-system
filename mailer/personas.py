import sys
import os
import json

"""
Class for representing personas
Usage: 
p = Personas(dir_name) # -> Still invalid state
if (p.next())
p.data()["first-name"]
....
if (p.next())
p.data()...

"""
class Personas:
    def __init__(self, dir_name):
        if not os.path.exists(dir_name):
            raise NameError
        self.directory = dir_name
        self.data = dict()
        self.index = -1
        self.directory_list = os.listdir(dir_name)
        print(self.directory_list)


    def __get_index(self, index):
        file_handle = open(os.path.join(self.directory,
                                        self.directory_list[index]),"r")
        decoder = json.JSONDecoder()
        data = decoder.decode(file_handle.read())
        file_handle.close()
        return data
        
    def get_data(self):
        return self.data

    def next(self):
        if not self.index < len(self.directory_list) - 1:
            return False
        self.index += 1
        self.data = self.__get_index(self.index)
        return True


    def valid(self):
        return self.index < len(self.directory_list) - 1
