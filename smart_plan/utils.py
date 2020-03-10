from pyformlang.finite_automaton import NondeterministicTransitionFunction, State, Symbol, NondeterministicFiniteAutomaton
from pyformlang import finite_automaton
from pyformlang.fst import FST

from smart_plan.uid import UID


def get_inverse_relation(relation):
    if relation == "STAR":
        return relation
    if relation[-1] == "-":
        return relation[:-1]
    else:
        return relation + "-"


def turn_functions_into_regex(functions):
    linear_paths = get_all_linear_paths(functions)
    linear_paths_regex = "|".join(["(" + ".".join(path) + ")" for path in linear_paths])
    return "(" + linear_paths_regex + ")*"


def get_all_linear_paths(functions):
    linear_paths = []
    for function in functions:
        for path in function.get_linear_paths():
            if path not in linear_paths:
                linear_paths.append(path)
    #print("We extracted:", len(linear_paths), "linear paths")
    return linear_paths


def get_all_relations(functions):
    relations = set()
    for function in functions:
        relations = relations.union(function.get_relations_and_inverses())
    return relations


def get_transition_function_and_states_and_symbols(functions, query):
    states = set()
    symbols = set()
    start_state = State("Start")
    states.add(start_state)
    final_states_intermediate = set()
    final_states = set()
    counter = 0
    transition_function = NondeterministicTransitionFunction()
    linear_paths = get_all_linear_paths(functions)
    linear_paths = sorted(linear_paths, key=len) # Need to sort by length here
    all_starting = set()
    for linear_path in linear_paths:
        current_state = start_state
        last_is_final = False
        last_atom = ""
        for i, atom in enumerate(linear_path):
            symbol = Symbol(atom)
            symbols.add(symbol)
            last_is_final = current_state in final_states_intermediate or current_state == start_state
            last_atom = atom
            next_states = transition_function(current_state, symbol)
            if next_states:
                current_state = list(next_states)[0]
            else:
                next_state = State(str(counter))
                counter += 1
                transition_function.add_transition(current_state, symbol, next_state)
                current_state = next_state
            if i == 0:
                all_starting.add((current_state, symbol))
        final_states_intermediate.add(current_state)
        if last_is_final and (last_atom == query or last_atom == get_inverse_relation(query)):
            final_states.add(current_state)
    for final_state in final_states_intermediate:
        for state, symbol in all_starting:
            transition_function.add_transition(final_state, symbol, state)


    return transition_function, states, symbols, final_states


def get_transition_function_and_states_and_symbols_non_reduced(functions):
    states = set()
    symbols = set()
    start_state = State("Start")
    states.add(start_state)
    final_states = set()
    counter = 0
    transition_function = NondeterministicTransitionFunction()
    linear_paths = get_all_linear_paths(functions)
    linear_paths = sorted(linear_paths, key=len)
    for linear_path in linear_paths:
        current_state = start_state
        for i, atom in enumerate(linear_path):
            symbol = Symbol(atom)
            symbols.add(symbol)
            next_state = State(str(counter))
            states.add(next_state)
            counter += 1
            transition_function.add_transition(current_state, symbol, next_state)
            current_state = next_state
        final_states.add(current_state)
    for final_state in final_states:
        transition_function.add_transition(final_state,
                                           finite_automaton.Epsilon(),
                                           start_state)
    return transition_function, states, symbols, final_states


def get_enfa_from_functions(functions):
    transition_function, states, symbols, final_states = get_transition_function_and_states_and_symbols_non_reduced(functions)
    enfa = NondeterministicFiniteAutomaton(states, symbols, transition_function, {State("Start")}, final_states)
    return enfa


def get_folded_automaton(enfa):
    in_edges = dict()
    out_edges = dict()
    processed = set()
    to_process = []
    final_states = enfa.get_final_states()
    start_states = enfa.get_start_states()
    alphabet = enfa.get_symbols()
    states = enfa.get_states()
    star = Symbol("STAR")
    for state in states:
        in_edges[state] = dict()
        out_edges[state] = dict()
        for a in alphabet:
            in_edges[state][a] = []
            out_edges[state][a] = []
    # Construction
    for from_state in states:
        for symbol in alphabet:
            for next_state in enfa(from_state, symbol):
                if from_state not in in_edges[next_state][symbol]:
                    in_edges[next_state][symbol].append(from_state)
                if next_state not in out_edges[from_state][symbol]:
                    out_edges[from_state][symbol].append(next_state)
    # Initialization
    # From final state
    for final_state in final_states:
        if not in_edges[final_state][star]:
            continue
        first = in_edges[final_state][star][0]
        for relation in in_edges[first]:
            if relation == star:
                continue
            inverse_relation = Symbol(get_inverse_relation(relation.value))
            for previous_state in in_edges[first][relation]:
                for start_state in start_states:
                    for next_state in out_edges[start_state].get(inverse_relation, []):
                        # previous_state -- relation --> first -- STAR -->
                        # final_state -- epsilon --> start_state -- inverse -->
                        # next_state
                        to_process.append((previous_state, next_state))
                        processed.add((previous_state, next_state))
    # From other states
    for state in states:
        for relation in out_edges[state]:
            if relation == star:
                continue
            inverse = Symbol(get_inverse_relation(relation.value))
            for middle_state in out_edges[state][relation]:
                for middle_state2 in out_edges[middle_state][star]:
                    if inverse not in out_edges[middle_state2]:
                        continue
                    for next_state in out_edges[middle_state2][inverse]:
                        to_process.append((state, next_state))
                        processed.add((state, next_state))
    while to_process:
        first, second = to_process.pop()
        # first -- epsilon --> second
        if first == second:
            continue
        # Special cases!
        if first in start_states:
            for final_state in final_states:
                if (final_state, second) not in processed:
                    processed.add((final_state, second))
                    to_process.append((final_state, second))
        if second in final_states:
            for start_state in start_states:
                if (first, start_state) not in processed:
                    processed.add((first, start_state))
                    to_process.append((first, start_state))
        # Reduction only if between two stars
        if len(out_edges[second][star]) == 0 or \
                len(in_edges[first][star]) == 0:
            continue
        # Only one possibility normally
        first = in_edges[first][star][0]
        second = out_edges[second][star][0]
        # Apply L -> a- L a
        for a in out_edges[second]:
            if a == star:
                continue
            for state in out_edges[second][a]:
                # second -- a ---> state
                opposite = Symbol(get_inverse_relation(a.value))
                if opposite in alphabet:
                    for begin in in_edges[first][opposite]:
                        # begin -- a- ---> first
                        if (begin, state) not in processed:
                            to_process.append((begin, state))
                            processed.add((begin, state))
        # Apply L -> L * L
        for next_state in out_edges[second][star]:
            for state in states:
                if (next_state, state) in processed:
                    if (first, state) not in processed:
                        processed.add((first, state))
                        to_process.append((first, state))
        for previous_state in in_edges[first][star]:
            for state in states:
                if (state, previous_state) in processed:
                    if (state, second) not in processed:
                        processed.add((state, second))
                        to_process.append((state, second))
    new_enfa = enfa.copy()
    epsilon = finite_automaton.Epsilon()
    for first, second in processed:
        new_enfa.add_transition(first, epsilon, second)
        # For conveniant reasons, we also transform L -> * L, when not final...
        if second not in final_states:
            for previous_star in in_edges[first][star]:
                new_enfa.add_transition(previous_star, epsilon, second)
    return new_enfa


def accept_query(enfa, query):
    inverse = get_inverse_relation(query)
    return enfa.accepts([query]) or \
        enfa.accepts([query, inverse]) or \
        enfa.accepts(["STAR", query, inverse])


def get_dfa_from_functions(functions, query):
    transition_function, states, symbols, final_states = get_transition_function_and_states_and_symbols(functions, query)
    nfa = NondeterministicFiniteAutomaton(states, symbols, transition_function, {State("Start")}, final_states)
    dfa = nfa.to_deterministic()
    #print("We have:", dfa.get_number_states(), "states")
    #print("Minimize")
    dfa = dfa.minimize()
    return dfa


def get_transducer_parser(functions):
    fst = FST()
    start_state = "Start"
    fst.add_start_state(start_state)
    counter = 0
    for function in functions:
        for linear_path in function.get_linear_paths():
            current_state = start_state
            for i, atom in enumerate(linear_path):
                out = []
                if i == len(linear_path) - 1:
                    out.append(function.name)
                next_state = str(counter)
                counter += 1
                fst.add_transition(current_state, atom, next_state, out)
                current_state = next_state
            fst.add_transition(current_state, "epsilon", start_state, [])
            fst.add_final_state(current_state)
    return fst


def get_translation(fst, word):
    word = [x.value for x in word]
    for translation in fst.translate(word):
        return translation


def do_susie(linear_paths, query):
    to_process = []
    for linear_path in linear_paths:
        if linear_path[-1] == query and (len(linear_path) == 1 or linear_path[:-1] in linear_paths):
            if len(linear_path) == 1:
                return True, [linear_path]
            to_process.append((list(map(get_inverse_relation, linear_path[-2::-1])), [linear_path]))
    while to_process:
        current, paths = to_process.pop()
        for linear_path in linear_paths:
            if len(linear_path) > len(current):
                continue
            if linear_path == current:
                return True, [linear_path] + paths
            if linear_path == current[-len(linear_path):]:
                to_process.append((current[:-len(linear_path)], [linear_path] + paths))
    return False, []


def get_nicoleta_assumption_uids(linear_functions):
    uids = set()
    for linear_function in linear_functions:
        for i in range(0, len(linear_function) - 1):
            uids.add(UID(get_inverse_relation(linear_function[i]),
                         linear_function[i+1]))
    return deduce_all_uids(list(uids))


def get_full_nicoleta_assumption_uids(linear_functions):
    uids = set()
    for linear_function in linear_functions:
        for i in range(0, len(linear_function) - 1):
            uids.add(UID(get_inverse_relation(linear_function[i]),
                         linear_function[i+1]))
            uids.add(UID(linear_function[i + 1],
                         get_inverse_relation(linear_function[i])))
    return deduce_all_uids(list(uids))


def deduce_all_uids(original_uids):
    uids, reversed_uids = get_uids_and_reversed_as_dict(original_uids)
    to_process = get_initial_process_queue(original_uids, reversed_uids)
    while to_process:
        body, head = to_process.pop()
        if head in uids[body]:
            continue
        uids[body].add(head)
        for other_body in reversed_uids[body]:
            to_process.append((other_body, head))
    resulting_uids = generate_uids_from_dict(uids)
    return resulting_uids


def generate_uids_from_dict(uids):
    resulting_uids = []
    for body in uids:
        for head in uids[body]:
            resulting_uids.append(UID(body, head))
    return resulting_uids


def get_initial_process_queue(original_uids, reversed_uids):
    to_process = []
    for uid in original_uids:
        for other_body in reversed_uids[uid.get_body()]:
            to_process.append((other_body, uid.get_head()))
    return to_process


def get_uids_and_reversed_as_dict(original_uids):
    uids = dict()
    reversed_uids = dict()
    for uid in original_uids:
        if uid.get_body() not in uids:
            uids[uid.get_body()] = set()
            reversed_uids[uid.get_body()] = set()
        if uid.get_head() not in uids:
            uids[uid.get_head()] = set()
            reversed_uids[uid.get_head()] = set()
        uids[uid.get_body()].add(uid.get_head())
        reversed_uids[uid.get_head()].add(uid.get_body())
    return uids, reversed_uids


def get_schema_xml(functions, relations, uids):
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<schema>\n<relations>\n'
    for relation in relations:
        if relation[-1] == "-":
            continue
        xml += '<relation name="' + relation + '">\n'
        xml += '<attribute name="' + relation + '.1" type="java.lang.String"/>\n'
        xml += '<attribute name="' + relation + '.2" type="java.lang.String"/>\n'
        xml += '</relation>\n'
    for function in functions:
        xml += function.get_xml_relation()
    xml += "</relations>\n\n<dependencies>\n"
    for uid in uids:
        xml += uid.get_xml_dependency()
    for function in functions:
        xml += function.get_xml_dependencies()
    xml += '</dependencies>\n</schema>\n'
    return xml


def get_query_xml(relation):
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<query type="conjunctive">\n<body>\n'
    if relation[-1] == "-":
        relation = get_inverse_relation(relation)
        xml += '<atom name="' + relation + '">\n'
        xml += '<variable name="b" />\n'
        xml += '<constant value="a" />\n'
    else:
        xml += '<atom name="' + relation + '">\n'
        xml += '<constant value="a" />\n'
        xml += '<variable name="b" />\n'
    xml += """</atom>
    </body>
    <head name="Q">
        <variable name="b" />
    </head>
    </query>
    """
    return xml


def get_all_linear_subfunctions(functions):
    result = []
    for function in functions:
        result += function.get_linear_subfunctions()
    return result
