import re
import logging
import os


def write_c_file(task, cores, descs, alg_name, fold_name, max_cores):

        # Create Dir if Doesnt Exist
        if not os.path.exists(fold_name):
            os.makedirs(fold_name)

        t = task

        file_name = alg_name + "_" +  t.name + "_" + str(cores) + ".c"

        logging.info("Writing " + file_name + " to: "  + os.getcwd() + "/" + fold_name)

        # Object List To Convert Name to Object #
        object_list = {
         "bs": "object01",
         "bsort100": "object02",
         "bsort": "object02",
         "crc": "object03",
         "expint": "object04",
         "fft": "object05",
         "insertsort": "object06",
         "jfdctint": "object07",
         "lcdnum": "object08",
         "matmult": "object09",
         "minver": "object10",
         "ns": "object11",
         "nsichneu": "object12",
         "qurt": "object13",
         "select": "object14",
         "simple": "object15",
         "sqrt": "object16",
         "statemate": "object17",
         "ud": "object18",
        }

        
        f = open("./" + fold_name + "/" + file_name, "w")

        # Write Headers
        config_str = """#include "config.h\""""
        object_head = """\n#include "objects.h\"\n\n"""

        f.write(config_str + object_head)

        # String Constants
        fj_str = "object_t *fjnodes"
        p_str = "object_t *pnodes"
        sec_str = "[NUM_SECTIONS + 1] = {\n"
        p_sec_str = "[NUM_SECTIONS][MAX_SEC_THREADS + 1] = {{\n"
        end_fstr = "};"
        end_str = "}};\n\n"

        # Initial FJ Node Str
        node_string = fj_str + "1" + sec_str 

        # Write Fj node 1
        for x in range(len(t.serial_nodes)):
            obj_name = t.serial_nodes[x].object.name
            node_string += "\t" + object_list[obj_name] + ", //" + obj_name + "\n"

        node_string += end_fstr + "\n"
        f.write(node_string)


        # Write Empty FJ Nodes, (Needs to be changed to accomodate multiple sections later)
        for x in range(2, max_cores+1): 
            node_string = "\n" + fj_str + str(x) + sec_str + end_fstr + "\n"
            f.write(node_string)


        # Write Empty Pj Nodes
        for x in range(cores+1, max_cores+1): 
            node_string = "\n" + p_str + str(x) + p_sec_str + end_str
            f.write(node_string)

 
        # Write PJ nodes
        for i in range(cores):
            
            objects_test = descs[i].split(")")
            replace = objects_test[0][0:2] + " | "
            objects_test[0] = objects_test[0].replace(replace, "")

            node_string = p_str + str(i+1) + p_sec_str 
            for x in range(len(objects_test)):
                if "<" in objects_test[x]:
                    node_string += end_str
                    f.write(node_string)
                else:
                    # Write PJNODES Object
                    object_name = objects_test[x].split("(")
                    # Remove Spaces 
                    object_name[0] = object_name[0].replace(" ", "")
                    # Check for WCET : 
                    if object_name[0][0] == ":":
                        # Remove WCET 
                         object_name[0] = re.sub("\d+", "", object_name[0])
                        # Remove : 
                         object_name[0] = object_name[0].replace(":", "")
                    # Write node_string
                    for y in range(int(object_name[1])):
                        node_string += "\t" + object_list[object_name[0]] + ", //" + object_name[0] + "\n"
                    node_string += "\n"


        f.close()