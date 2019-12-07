from smart_plan.function import Function
from smart_plan import utils

function0 = Function()
function0.add_atom("12", "x", "y")
function0.set_input_variable("x")

function1 = Function()
function1.add_atom("14", "x", "y")
function1.set_input_variable("x")

function2 = Function()
function2.add_atom("14-", "x", "y")
function2.add_atom("12-", "y", "z")
function2.add_atom("13", "z", "t")
function2.set_input_variable("x")

functions = [function0, function1, function2]


linear_paths = utils.get_all_linear_paths(functions)
print(linear_paths)


enfa = utils.get_enfa_from_functions(functions)
new_enfa = utils.get_folded_automaton(enfa)


deter = utils.get_dfa_from_functions(functions)

relation = "13"

res_us = utils.accept_query(new_enfa, relation)
susie_res, paths = utils.do_susie(linear_paths, relation)


query = Function()
query.add_atom(relation, "x", "y")
cfg = query.get_longest_query_grammar(["12","12-","14","14-", "13","13-"])
cfg = cfg.intersection(deter)

print(not cfg.is_empty())
print(res_us)
print(susie_res, paths)
