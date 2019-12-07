from smart_plan.function import Function
from smart_plan.function_reader import FunctionReader
from smart_plan import utils
import logging

logging.basicConfig(filename='experiments_susie.log', level=logging.DEBUG)

directories = ["../definition/Books/",
               "../definition/Movies/",
               "../definition/Music/"]


if __name__ == '__main__':

    for dir in directories:
        logging.info("For: %s", dir)

        function_reader = FunctionReader()
        functions = function_reader.get_functions_from_dir(dir)

        relations = sorted(utils.get_all_relations(functions))
        linear_paths = utils.get_all_linear_paths(functions)

        answered = 0
        sizes = []

        for query in relations:
            logging.info("Processing %s", query)
            susie_res, paths = utils.do_susie(linear_paths, query)
            if susie_res:
                logging.info("%s can be answered.", query)
                logging.info(str(susie_res))
                logging.info(str(paths))
                answered += 1
            else:
                logging.info("%s CANNOT be answered", query)

        logging.info("%f queries were answered", answered / len(relations) * 100.0)
