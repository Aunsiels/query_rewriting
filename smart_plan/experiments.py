from smart_plan.function import Function
from smart_plan.function_reader import FunctionReader
from smart_plan import utils
import logging

logging.basicConfig(filename='experiments.log', level=logging.DEBUG)


directories = [
               "../definition/Books/",
               "../definition/Movies/",
               "../definition/Music/"
              ]


if __name__ == '__main__':

    for dir in directories:
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

        # enfa = utils.get_enfa_from_functions(functions)
        # enfa = utils.get_folded_automaton(enfa)

        fst = utils.get_transducer_parser(functions)

        answered = 0
        sizes = []

        for relation in relations:
            logging.info("Processing %s", relation)
            query = Function()
            query.add_atom(relation, "x", "y")
            deter = utils.get_dfa_from_functions(functions, relation)
            cfg = query.get_longest_query_grammar(relations, uids)
            cfg = cfg.intersection(deter)
            if not cfg.is_empty():
                logging.info("%s can be answered.", relation)
                answered += 1
                for word in cfg.get_words():
                    logging.info(str(word))
                    logging.info(str(utils.get_translation(fst, word)))
                    sizes.append(len(word))
                    break
            else:
                logging.info("%s CANNOT be answered", relation)


        logging.info("%f queries were answered", answered / len(relations) * 100.0)
        logging.info("The mean size of the plan is %f", sum(sizes) / len(sizes))
