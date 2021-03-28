import os
from random import random
from shutil import copyfile

from smart_plan.experiments_benedikt import find_plan_benedikt
from smart_plan.experiments_pdq2 import find_plan_pdq
from smart_plan.function import Function
from smart_plan import utils
from sys import argv

from smart_plan.utils import get_schema_xml, get_all_linear_subfunctions, get_query_xml

if len(argv) > 1:
    filename = argv[1]
    file_unique_suffix = "_".join(argv[1].split("/")[-1].split(".")[0:-1])
else:
    filename = "result_experiments_random_new.tsv"
    file_unique_suffix = str(abs(random.randint()))

print(filename)
print(file_unique_suffix)



def get_random_relations(n):
    res = []
    for i in range(n):
        res.append("r" + str(i))
        res.append("r" + str(i) + "-")
    return res


experiments_setups = \
        [# min_length, max_length, n_relation, n_function, proba_existential
         (1, 4, 7, 5, 0.2),
         (1, 4, 7, 10, 0.2),
         (1, 4, 7, 15, 0.2),
         (1, 4, 7, 20, 0.2),
         (1, 4, 7, 15, 0.0),
         (1, 4, 7, 15, 0.2),
         (1, 4, 7, 15, 0.4),
         (1, 4, 7, 15, 0.6),
         (1, 4, 7, 15, 0.8),
         (1, 4, 7, 15, 1.0),
         (1, 4,  2, 15, 0.2),
         (1, 4, 5, 15, 0.2),
         (1, 4, 10, 15, 0.2),
         (1, 4, 15, 15, 0.2)
        ]

experiments_setups = experiments_setups[::-1]

if __name__ == '__main__':

    if not os.path.exists("../benedikt_schemas"):
        os.makedirs("../benedikt_schemas")

    while True:
        for min_length, max_length, n_relation, n_function, proba_existential in experiments_setups:

            relations = get_random_relations(n_relation)
            functions = [Function.get_random_function(relations, min_length, max_length, proba_existential, str(i))
                         for i in range(n_function)]

            relations = sorted(utils.get_all_relations(functions))
            linear_paths = utils.get_all_linear_paths(functions)

            uids = utils.get_nicoleta_assumption_uids(linear_paths)

            schema = get_schema_xml(get_all_linear_subfunctions(functions),
                                    relations,
                                    uids)

            #enfa = utils.get_enfa_from_functions(functions)
            #new_enfa = utils.get_folded_automaton(enfa)

            answered_us = 0
            answered_susie = 0
            answered_fake_susie = 0
            answered_benedikt = 0
            timeout_benedikt = 0
            answered_pdq = 0
            timeout_pdq = 0

            for relation in relations:
                query_xml = get_query_xml(relation)
                dir_name = "../benedikt_schemas/random" + file_unique_suffix + "/"
                if not os.path.exists(dir_name):
                    os.makedirs(dir_name)
                with open(dir_name + "schema.xml", "w") as f:
                    f.write(schema)
                with open(dir_name + "query.xml", "w") as f:
                    f.write(query_xml)

                copyfile("../benedikt/case.properties", dir_name + "case.properties")

                print("Benedikt")
                found_plan, timeout = find_plan_benedikt(dir_name)

                if found_plan:
                    answered_benedikt += 1
                elif timeout:
                    timeout_benedikt += 1

                print("PDQ")
                found_plan, timeout = find_plan_pdq(dir_name)

                if found_plan:
                    answered_pdq += 1
                elif timeout:
                    timeout_pdq += 1

                query = Function()
                query.add_atom(relation, "x", "y")
                deter = utils.get_dfa_from_functions(functions, relation)
                cfg = query.get_longest_query_grammar(relations, uids)
                print("Intersection")
                cfg = cfg.intersection(deter)
                res_us = False
                print("emptyness")
                if not cfg.is_empty():
                    res_us = True
                # res_us = utils.accept_query(new_enfa, relation)
                if res_us:
                    answered_us += 1
                susie_res, paths = utils.do_susie(linear_paths, relation)
                if not res_us and susie_res:
                    answered_fake_susie += 1
                elif susie_res:
                    answered_susie += 1

            print(answered_us / len(relations) * 100.0, "% queries were answered for us")
            print(answered_susie / len(relations) * 100.0, "% queries were answered for susie")
            print(answered_fake_susie / len(relations) * 100.0, "% queries were wrongly answered for susie")
            print(answered_benedikt / len(relations) * 100.0, "% queries were answered for PDQ")
            print(timeout_benedikt / len(relations) * 100.0, "% queries were timed out for PDQ")
            print(answered_pdq / len(relations) * 100.0, "% queries were answered for PDQ2")
            print(timeout_pdq / len(relations) * 100.0, "% queries were timed out for PDQ2")
            with open(filename, "a") as f:
                f.write("\t".join(map(str, [min_length, max_length, n_relation,
                    n_function, proba_existential, 0, answered_us / len(relations), 0])) + "\n")
                f.write("\t".join(map(str, [min_length, max_length, n_relation,
                    n_function, proba_existential, 1, answered_susie / len(relations), answered_fake_susie / len(relations)])) +  "\n")
                f.write("\t".join(map(str, [min_length, max_length, n_relation,
                                            n_function, proba_existential, 2, answered_benedikt / len(relations),
                                            timeout_benedikt / len(relations)])) + "\n")
                f.write("\t".join(map(str, [min_length, max_length, n_relation,
                                            n_function, proba_existential, 3, answered_pdq / len(relations),
                                            timeout_pdq / len(relations)])) + "\n")
