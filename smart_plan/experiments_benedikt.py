import os
import subprocess
from shutil import copyfile

from smart_plan.function_reader import FunctionReader
from smart_plan import utils
import logging

from smart_plan.utils import get_all_linear_subfunctions, get_schema_xml, get_query_xml

logging.basicConfig(filename='experiments_benedikt.log', level=logging.DEBUG)


directories = [
               "../definition/Books/",
               "../definition/Movies/",
               "../definition/Music/"
              ]

TIMEOUT = "10000"
K_MAX = 10


def find_plan_benedikt(name):
    try:
        output = subprocess.check_output(['java', '-jar',
                                          '../benedikt/pdq-benchmark-1.0.0-SNAPSHOT.one-jar.jar',
                                          'planner', '-i', name, '-W', '-v',
                                          '--timeout', TIMEOUT, "-Dreasoning_type=RESTRICTED_CHASE"]).decode("utf-8")
        found_plan = "BEST PLAN:" in output
        timeout = "TIMEOUT EXPIRED" in output
        if found_plan or not timeout:
            return found_plan, timeout
    except subprocess.CalledProcessError:
        pass
    for k in range(1, K_MAX):
        try:
            output = subprocess.check_output(['java', '-jar',
                                              '../benedikt/pdq-benchmark-1.0.0-SNAPSHOT.one-jar.jar',
                                              'planner', '-i', name, '-W', '-v', '-Dtermination_k=' + str(k),
                                              '--timeout', TIMEOUT]).decode("utf-8")
            found_plan = "BEST PLAN:" in output
            timeout = "TIMEOUT EXPIRED" in output
            if found_plan or timeout:
                return found_plan, timeout
        except subprocess.CalledProcessError:
            return False, True
    return False, True


if __name__ == '__main__':

    if not os.path.exists("../benedikt_schemas"):
        os.makedirs("../benedikt_schemas")

    for dir in directories:
        name = dir.split("/")[-2]
        print("For", dir)
        logging.info("For: %s", str(dir))

        function_reader = FunctionReader()
        functions = function_reader.get_functions_from_dir(dir)
        linear_paths = utils.get_all_linear_paths(functions)
        uids = utils.get_nicoleta_assumption_uids(linear_paths)
        print("Functions", len(functions))
        print("Linear paths", len(linear_paths))
        print("UIDS", len(uids))

        relations = sorted(utils.get_all_relations(functions))
        print("Relations", len(relations))

        schema = get_schema_xml(get_all_linear_subfunctions(functions),
                                relations,
                                uids)

        answered = 0
        n_timeout = 0

        for relation in relations:
            logging.info("Processing %s", relation)
            query_xml = get_query_xml(relation)
            dir_name = "../benedikt_schemas/" + name + "-" + relation + "/"
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
            with open(dir_name + "schema.xml", "w") as f:
                f.write(schema)
            with open(dir_name + "query.xml", "w") as f:
                f.write(query_xml)

            copyfile("../benedikt/case.properties", dir_name + "case.properties")

            found_plan, timeout = find_plan_benedikt(dir_name)

            if found_plan:
                logging.info("%s can be answered.", relation)
                answered += 1
            elif timeout:
                logging.info("%s timed out.", relation)
                n_timeout += 1
            else:
                logging.info("%s CANNOT be answered", relation)

        logging.info("%f queries were answered", answered / len(relations) * 100.0)
        logging.info("%f queries timedout", n_timeout / len(relations) * 100.0)
