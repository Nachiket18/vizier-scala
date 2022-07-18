'''
Created on 11-May-2021
@author: Nachiket Deo
'''


import ast
from collections import deque,defaultdict
from builtins import isinstance


##
## class Visitast - responsible for parsing the source code and generating the AST (Abstract Syntax Tree).
## This is phase one of the process where we store information about variables in dictionaries for bookkeeping.
##
## INFO - 1. The key information that is stored is when variable gets assigned a value and when the variable is referred.
##        2. Separate dictionaries are kept for functions,loops and control flow statements
##



class Visitast(ast.NodeVisitor):
        
    
    def __init__(self):
        
        self.main_dict_store = defaultdict(list)
        self.main_dict_load = defaultdict(list)
        self.scope_dict_stack = deque()
        self.control_flow_stack = deque()  
        self.all_stack = deque()
        self.output_loop_dicts = defaultdict(list) 
        self.output_control_flow_dicts = defaultdict(list)
        self.output_func_dicts = defaultdict(list)
        self.output_class_dicts = defaultdict(list)
        self.import_block = False
        self.function_scope_dict_stack = deque()
        
    def generic_visit(self,node):
        #print(node.__class__.__name__)            
        if isinstance(node,ast.Name):     
            
            if not (self.scope_dict_stack or self.control_flow_stack or self.function_scope_dict_stack):
                
                ##
                ## The variables captured in main program flow
                ##
                
                #x = 2

                #y = x + 3

                if (isinstance(node.ctx,ast.Store)):
                    self.main_dict_store[node.lineno].append(node.id)
                
                elif(isinstance(node.ctx,ast.Load)):
                    self.main_dict_load[node.lineno].append(node.id)    
            
            elif self.scope_dict_stack and (self.scope_dict_stack[0] == self.all_stack[0]) :
                
                ##
                ## Variables in a loop are captured
                ##
                
                line_no_control = self.scope_dict_stack[0]
                
                output_control = self.output_loop_dicts[line_no_control]
                
                store_dict_scope = output_control[0]
                load_dict_scope = output_control[1]
                
                if (isinstance(node.ctx,ast.Store)):
                    store_dict_scope[node.lineno] = (node.id)
                
                elif(isinstance(node.ctx,ast.Load)):
                    load_dict_scope[node.lineno].append(node.id) 
                
                self.output_loop_dicts[line_no_control] = (store_dict_scope,load_dict_scope)
            
            elif self.control_flow_stack and (self.control_flow_stack[0] == self.all_stack[0]):
                
                ##
                ## Variables in control flow are captured
                ##

                line_no_control = self.control_flow_stack[0]
                
                output_control = self.output_control_flow_dicts[line_no_control]
                
                store_dict_control = output_control[0]
                load_dict_control = output_control[1]
                
                if (isinstance(node.ctx,ast.Store)):
                    store_dict_control[node.lineno] = (node.id)
                
                elif(isinstance(node.ctx,ast.Load)):
                    load_dict_control[node.lineno].append(node.id) 
                
                self.output_control_flow_dicts[line_no_control] = (store_dict_control,load_dict_control)
                  
            elif self.function_scope_dict_stack and (self.function_scope_dict_stack[0] == self.all_stack[0]):
                
                ##
                ## Variables present in function definition are captured
                ##
                
                
                line_no_func = self.function_scope_dict_stack[0]
                
                out_loop_func = self.output_func_dicts[line_no_func]
                
                store_dict  = out_loop_func[0]
                load_dict = out_loop_func[1] 
                
                if (isinstance(node.ctx,ast.Store)):
                    store_dict[node.lineno].append(node.id)
                
                elif(isinstance(node.ctx,ast.Load)):
                    load_dict[node.lineno].append(node.id)  
                
                self.output_func_dicts[line_no_func] = (store_dict,load_dict)   
            
            
            else:
                
                line_no = self.scope_dict_stack[0] 
                out_loop = self.output_loop_dicts[line_no]  
                
                store_dict = out_loop[0]
                load_dict = out_loop[1]
               
                self.output_loop_dicts[line_no] = (store_dict,load_dict)
                
                   
        elif isinstance(node,(ast.arg)) and self.function_scope_dict_stack:
            
    
            func_lineno = self.function_scope_dict_stack[0]
            
            out_func_dict =  self.output_func_dicts[func_lineno]
            
            store_dict = out_func_dict[0]
            load_dict = out_func_dict[1]
            
            store_dict[node.lineno].append(node.arg)
                
            self.output_func_dicts[func_lineno] = (store_dict,load_dict)
      
            
        elif isinstance(node,(ast.FunctionDef)):
            
            ##
            ## When function definition is appearing in AST then we keep track of it by appending the function name to stack
            ##
            
            dict_loop_store  = defaultdict(list)
            dict_loop_load = defaultdict(list)
            
            self.function_scope_dict_stack.append(node.name)
            self.output_func_dicts[node.name] = (dict_loop_store,dict_loop_load)

            self.all_stack.append(node.name)

        elif isinstance(node,(ast.For,ast.While)):
            
            ##
            ## When loop definition is appearing in AST then we keep track of it by 
            ## appending the lineno to scope stack
            ##

            dict_loop_store  = defaultdict(list)
            dict_loop_load = defaultdict(list)
            self.scope_dict_stack.append(node.lineno)
            self.output_loop_dicts[node.lineno] = (dict_loop_store,dict_loop_load)
            self.all_stack.append(node.lineno)

        elif isinstance(node,ast.If):
            
            ##
            ## When If definition is appearing in AST then we keep track of it by 
            ## appending the lineno to control flow stack
            ##
            
            dict_loop_store  = defaultdict(list)
            dict_loop_load = defaultdict(list)
            self.control_flow_stack.append(node.lineno)
            self.output_control_flow_dicts[node.lineno] = (dict_loop_store,dict_loop_load) 
            self.all_stack.append(node.lineno)

        elif isinstance(node,(ast.Import,ast.ImportFrom)):
            self.import_block = True
    
        elif self.import_block == True:
            if node.asname != None:
                self.main_dict_store[0].append(node.asname)
            else:
                self.main_dict_store[0].append(node.name)
                
        
        ##
        ## Recursive call to visit the children of a particular node in AST
        ##
        ast.NodeVisitor.generic_visit(self,node)
        
        ##
        ## IF - ELSEIF usage:
        ##
        ## When a particular node ( of type loop, control flow or function definition) is visited completely (all the children)
        ## Pop out the top of stack so the program control shifts to the outer scope     
        ##
        
        if isinstance(node,(ast.For,ast.While)):
            self.scope_dict_stack.pop()
            self.all_stack.pop()

        elif isinstance(node,(ast.If)):
            self.control_flow_stack.pop()
            self.all_stack.pop()

        elif isinstance(node,(ast.Import,ast.ImportFrom)):
            self.import_block = False
        
        elif isinstance(node,(ast.FunctionDef)):
            self.function_scope_dict_stack.pop()
            self.all_stack.pop()
    
    def display_store_dict(self):
        return self.main_dict_store
    
    def display_load_dict(self):
        return self.main_dict_load
    
    def display_loop_dictionaries(self):
        return self.output_loop_dicts
    
    def display_control_flow_dictionaries(self):
        return self.output_control_flow_dicts
    
    def display_func_dictionaries(self):
        return self.output_func_dicts

        
class Vertex:
    def __init__(self,key):
        self.id = key
        self.connectedTo = {}
        self.backconnectedTo = {}

    def addNeighbor(self,nbr,dep_object = ''):
        self.connectedTo[nbr] = dep_object

    def addBackNeighbor(self,nbr,dep_object = ''):
        self.backconnectedTo[nbr] = dep_object

    def __str__(self):
        return str(self.id) + ' connectedTo: ' + str([x.id for x in self.connectedTo])

    def getConnections(self):
        return self.connectedTo.keys()

    def getBackConnections(self):
        return self.backconnectedTo.keys()

    def getId(self):
        return self.id

    def getWeight(self,nbr):
        return self.connectedTo[nbr]

class Vertex_process:
    def __init__(self,key):
        self.id = key
        self.connectedTo = {}
        self.backconnectedTo = {}

    def addNeighbor(self,nbr,dep_object = ''):

        if nbr in self.connectedTo.keys():
            if dep_object not in self.connectedTo[nbr]: 
                self.connectedTo[nbr].append(dep_object)
        else:
            self.connectedTo[nbr] = [dep_object]

    def addBackNeighbor(self,nbr,dep_object = ''):
        if nbr in self.backconnectedTo.keys():
            if dep_object not in self.backconnectedTo[nbr]:
                self.backconnectedTo[nbr].append(dep_object)
        else:
            self.backconnectedTo[nbr] = [dep_object]

    def __str__(self):
        return str(self.id) + ' connectedTo: ' + str([x.id for x in self.connectedTo])

    def getConnections(self):
        return self.connectedTo.keys()

    def getBackConnections(self):
        return self.backconnectedTo.keys()

    def getId(self):
        return self.id

    def getWeight(self,nbr):
        return self.connectedTo[nbr]


class Graph:
    def __init__(self):
        self.vertList = {}
        self.numVertices = 0

    def addVertex(self,key):
        self.numVertices = self.numVertices + 1
        newVertex = Vertex(key)
        self.vertList[key] = newVertex
        return newVertex

    def getVertex(self,n):
        if n in self.vertList:
            return self.vertList[n]
        else:
            return None

    def __contains__(self,n):
        return n in self.vertList

    def addEdge(self,f,t,dep_object=''):
        if f not in self.vertList:
            nv = self.addVertex(f)
        if t not in self.vertList:
            nv = self.addVertex(t)
        self.vertList[f].addNeighbor(self.vertList[t], dep_object)
        self.vertList[t].addBackNeighbor(self.vertList[f],dep_object)


    def getVertices(self):
        return self.vertList.keys()

    def __iter__(self):
        return iter(self.vertList.values())    


class Graphprocess:
    def __init__(self):
        self.vertList = {}
        self.numVertices = 0

    def addVertex(self,key):
        self.numVertices = self.numVertices + 1
        newVertex = Vertex_process(key)
        self.vertList[key] = newVertex
        return newVertex

    def getVertex(self,n):
        if n in self.vertList:
            return self.vertList[n]
        else:
            return None

    def __contains__(self,n):
        return n in self.vertList

    def addEdge(self,f,t,dep_object=''):
        if f not in self.vertList:
            nv = self.addVertex(f)
        if t not in self.vertList:
            nv = self.addVertex(t)
        self.vertList[f].addNeighbor(self.vertList[t], dep_object)
        self.vertList[t].addBackNeighbor(self.vertList[f],dep_object)


    def getVertices(self):
        return self.vertList.keys()

    def __iter__(self):
        return iter(self.vertList.values()) 

##
## FOR TESTING ONLY
##
##

def main():
    
    # with open('/home/nachiket/vizier-scala/parallel_test/test_3_read_performance.ipynb', "r") as source:
    #     tree = ast.parse(source.read())
    
    tree = ast.parse("x = 1; y=1; y=y+2; x = y+5")
    
    print(ast.dump(tree))
    
    vis = Visitast()
    vis.visit(tree)
    # print(vis.display_store_dict())
    # print(vis.display_load_dict())
    # print(vis.display_loop_dictionaries())
    # print("Func",vis.display_func_dictionaries())
    # for node in ast.walk(tree):
    #     print(node.__class__.__name__)
    #     print(node._fields)
    #     print(node._attributes)
    #     print(node.__class__._fields)
    #     print(node.__class__._attributes)
    #     print(node.__class__.)

#     g = Graph()
    
#     for key,value in vis.display_store_dict().items():
#         g.addVertex(key)
    
#     for key,value in vis.display_loop_dictionaries().items():
#         dict_left = value[0]
#         dict_right = value[1]
#         for key,value in dict_left.items():
#             g.addVertex(key)
            
#         for key,value in dict_right.items():
#             if g.getVertex(key) == None:
#                 g.addVertex(key)
                
#     dependency_list = defaultdict(list)
    
#     inverted_left_dict = defaultdict(list)
     
#     for k, v in vis.display_store_dict().items():
#             for elem in v:
#                 inverted_left_dict[elem].append(k)
        
# #     for key,value in vis.line_dict_right.items():
# #         for key_1,value_1 in vis.line_dict_left.items():
# #             if value == value_1 and key_1 < key:
# #                 dependency_list[key_1] = (key,value)
    
#     print("D2",inverted_left_dict)
     
#     for key,value in vis.display_store_dict().items():
#             for j in value:
#                 key_left = inverted_left_dict[j]
#                 key_left.sort(reverse = True)
#                 if isinstance(key_left,list):
#                     for k in key_left:
#                         if k < key:
#                             dependency_list[k].append((key,j))
#                             break
#     #print(dependency_list) 
#     for key_line,dict_loop in vis.display_loop_dictionaries().items():
             
#             dict_left = dict_loop[0]
#             dict_right = dict_loop[1]
            
#             d3 = defaultdict(list) 
#             for k, v in dict_left.items():
#                 for elem in v:
#                     d3[elem].append(k)
        
            
#             print("d3",d3)
#             for key,value in dict_right.items():
#                     print("Value",value)
#                     for j in value:
#                         print("j",j)
#                         key_left = d3.get(j, None)
#                         if key_left is not None:
#                             for key_left_dict in key_left:
#                                 if key_left_dict < key: 
#                                     dependency_list[key_left_dict].append((key,j))
                        
#                         elif key_left is None:
#                             key_left_main = inverted_left_dict.get(j,None)
#                             print("Key",key_left_main,key_left)
#                             if key_left_main: 
#                                 for k in key_left_main:
#                                     if k < key:
#                                         dependency_list[k].append((key,j))
                                    
                    
    
    
    
#     for key,value in dependency_list.items():
#         for data in value:
#             elem_1,elem_2 = data
#             g.addEdge(key,elem_1,elem_2) 
    
    
#     #print(dependency_list)
     
#     for v in g:
#         if not v.getConnections():
#             print(v.getId())
#         else:
#             for nbr in v.getConnections():
#                 print(v.getId(),"->",nbr.getId(),"on",v.getWeight(nbr))
            
        

if __name__ == '__main__':
    main() 