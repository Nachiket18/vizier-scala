from ast_parse import Visitast
from collections import deque,defaultdict
import ast


class ProcessCellProvenance:

    def __init__(self):
        self.input_provenance = []
        self.output_provenance = []
    
    def display_output_provenance(self):
        return self.input_provenance

    def display_input_provenance(self):
        return self.output_provenance
    
    def processProvenance(self,src):

        vis = Visitast() 
        tree = ast.parse(src)
        vis.visit(tree)

        if len(vis.display_store_dict()) != 0:
            store_dict = vis.display_store_dict()
            for key,value in store_dict.items():
                for variables in value:
                    if variables not in self.output_provenance:
                        self.output_provenance.append(variables)

        inverted_store_dict = defaultdict(list)
        for k, v in vis.display_store_dict().items():
                        for elem in v:
                            inverted_store_dict[elem].append(k)


        if len(vis.display_load_dict()) != 0:
            load_dict = vis.display_load_dict()
            for key,value in load_dict.items():
                for variables in value:
                    key_store_dict = []
                    if variables in inverted_store_dict: 
                        key_store_dict = inverted_store_dict[variables]
                        
                        isOrphan = False
        
                        for elem in key_store_dict:
                            if key <= elem:
                            ##
                            ## The element was accessed before it was assigned. 
                            ## Suggesting that the variable was assigned value in previous cells
                            ##
                                isOrphan = True
                                break
                    if (variables not in self.output_provenance) or (isOrphan == False):
                        if (variables not in self.input_provenance):
                            self.input_provenance.append(variables)

        if len(vis.display_func_dictionaries()) != 0:
            for key_line,dict_loop in vis.display_func_dictionaries().items():
                    
                        dict_store_func = dict_loop[0]
                        dict_load_func = dict_loop[1] 
                        for key,value in dict_store_func.items():
                            for variables in value:
                                if variables not in self.output_provenance:
                                    self.output_provenance.append(variables)
                        
                        for key,value in dict_load_func.items():
                            for variables in value:
                                if variables not in self.input_provenance:
                                    self.input_provenance.append(variables)

        if len(vis.display_loop_dictionaries()) != 0:
            for key_line,dict_loop in vis.display_loop_dictionaries().items():
                    
                dict_store = dict_loop[0]
                dict_load = dict_loop[1] 

                for key,value in dict_store.items():
                    for variables in value:
                        if variables not in self.output_provenance:
                            self.output_provenance.append(variables)
                
                for key,value in dict_load.items():
                    for variables in value:
                        if variables not in self.input_provenance:
                            self.input_provenance.append(variables)

        if  len(vis.display_control_flow_dictionaries()) != 0:
            for key_line,dict_loop in vis.display_control_flow_dictionaries().items():
                    
                dict_store_control = dict_loop[0]
                dict_load_control = dict_loop[1] 

                for key,value in dict_store_control.items():
                    for variables in value:
                        if variables not in self.output_provenance:
                            self.output_provenance.append(variables)
                
                for key,value in dict_load_control.items():
                    for variables in value:
                        if variables not in self.input_provenance:
                            self.input_provenance.append(variables)
def main():
    
    holder = ProcessCellProvenance()
    holder.processProvenance("x = 1; y=1; y=y+2; x = z+5")
    print(holder.display_input_provenance())
    print(holder.display_output_provenance())

if __name__ == '__main__':
    main()