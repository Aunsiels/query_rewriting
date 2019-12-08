from smart_plan.function import Function
from smart_plan import utils
from sys import argv

if len(argv) > 1:
    filename = argv[1]
else:
    filename = "result_experiments_random_new.tsv"


def get_random_relations(n):
    res = []
    for i in range(n):
        res.append(str(i))
        res.append(str(i) + "-")
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


if __name__ == '__main__':

    while True:
        for min_length, max_length, n_relation, n_function, proba_existential in experiments_setups:

            relations = get_random_relations(n_relation)
            functions = [Function.get_random_function(relations, min_length, max_length, proba_existential, str(i))
                         for i in range(n_function)]

            relations = sorted(utils.get_all_relations(functions))
            linear_paths = utils.get_all_linear_paths(functions)

            uids = utils.get_nicoleta_assumption_uids(linear_paths)

            #enfa = utils.get_enfa_from_functions(functions)
            #new_enfa = utils.get_folded_automaton(enfa)

            answered_us = 0
            answered_susie = 0
            answered_fake_susie = 0

            for relation in relations:
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
            with open(filename, "a") as f:
                f.write("\t".join(map(str, [min_length, max_length, n_relation,
                    n_function, proba_existential, 0, answered_us / len(relations), 0])) + "\n")
                f.write("\t".join(map(str, [min_length, max_length, n_relation,
                    n_function, proba_existential, 1, answered_susie / len(relations), answered_fake_susie / len(relations)])) +  "\n")
