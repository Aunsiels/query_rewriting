import networkx as nx
from pyformlang.cfg import Production, Variable, Terminal, CFG, Epsilon
from .utils import get_inverse_relation
import random

RELATION = 0
LAST_ELEMENT = -1
FIRST_ELEMENT = 0
OUTPUT_VARIABLE = 2
INPUT_VARIABLE = 1


class Function(object):

    def __init__(self, name="NONAME"):
        self._relations = set()
        self.existential_variables = set()
        self.atoms = nx.MultiDiGraph()
        self.start_node = None
        self.name = name

    def get_number_variables(self):
        return len(self.atoms.nodes)

    def add_atom(self, relation, variable0, variable1):
        if self.start_node is None:
            self.start_node = variable0
        atom = (relation, variable0, variable1)
        self._add_variables(atom)
        self._relations.add(relation)
        self._relations.add(get_inverse_relation(relation))
        self._insert_atom(atom)

    def _add_variables(self, atom):
        self.atoms.add_node(atom[INPUT_VARIABLE])
        self.atoms.add_node(atom[OUTPUT_VARIABLE])

    def _insert_atom(self, atom):
        self.atoms.add_edge(atom[INPUT_VARIABLE], atom[OUTPUT_VARIABLE], relation=atom[RELATION])
        self.atoms.add_edge(atom[OUTPUT_VARIABLE],
                            atom[INPUT_VARIABLE],
                            relation=get_inverse_relation(atom[RELATION]))

    def get_number_atoms(self):
        return int(len(self.atoms.edges) / 2)

    def get_linear_paths(self):
        linear_paths = []
        for target_node in self.atoms.nodes:
            if target_node != self.start_node and target_node not in self.existential_variables:
                linear_paths += self.get_all_paths_to(target_node)
        return linear_paths

    def get_all_paths_to(self, target_node):
        linear_paths = []
        for unlabeled_path in nx.all_simple_paths(self.atoms, self.start_node, target_node):
            self.add_previously_unseen_plans(linear_paths, unlabeled_path)
        return linear_paths

    def add_previously_unseen_plans(self, linear_paths, unlabeled_path):
        for path in self.get_all_relation_paths_from_unlabeled_path(unlabeled_path):
            if path not in linear_paths:
                linear_paths.append(path)

    def get_all_relation_paths_from_unlabeled_path(self, unlabeled_path):
        previous_node = self.start_node
        labeled_paths = [[]]
        for next_node in unlabeled_path[1:]:
            labeled_paths = self.explore_all_relations_between_two_nodes(next_node, previous_node, labeled_paths)
            previous_node = next_node
        return labeled_paths

    def explore_all_relations_between_two_nodes(self, next_node, previous_node, previous_plans):
        next_plans = []
        for _, relation_d in self.atoms.get_edge_data(previous_node, next_node).items():
            temp = add_relation_to_paths(relation_d["relation"], previous_plans)
            next_plans += temp
        return next_plans

    def get_number_existential_variables(self):
        return len(self.existential_variables)

    def set_existential_variable(self, variable):
        self.existential_variables.add(variable)

    def set_input_variable(self, input_variable):
        self.start_node = input_variable

    def get_longest_query(self):
        linear_paths = self.get_linear_paths()
        if not linear_paths:
            return []
        longest_path = max(linear_paths, key=len)
        pos = 0
        while pos < len(longest_path):
            shorter_path = longest_path[:pos] + longest_path[pos + 1:]
            exists_shorter_with_output_at_pos = longest_path[pos] == "STAR" and shorter_path in linear_paths
            if exists_shorter_with_output_at_pos:
                longest_path = shorter_path
            pos += 1
        return longest_path

    def get_longest_query_grammar(self, relations, uids):
        var_s = Variable("S")
        b_relation_variables = dict()
        l_relation_variables = dict()
        for relation in relations:
            b_relation_variables[relation] = Variable("B" + relation)
            l_relation_variables[relation] = Variable("L" + relation)

        productions = set()

        # For now only single query
        longest_query = self.get_longest_query()
        q = Terminal(longest_query[0])
        q_minus = Terminal(get_inverse_relation(longest_query[0]))

        # S -> q
        productions.add(Production(var_s, [q]))

        # S -> Bq . q
        productions.add(Production(var_s, [b_relation_variables[q.get_value()], q]))
        # S -> q Bq- q-
        productions.add(Production(var_s, [q, b_relation_variables[q_minus.get_value()], q_minus]))
        # S -> Bq q Bq- q-
        productions.add(Production(var_s, [b_relation_variables[q.get_value()], q,
                                           b_relation_variables[q_minus.get_value()],
                                           q_minus]))

        # Br1 -> Br1 Lr2
        for uid in uids:
            productions.add(Production(b_relation_variables[uid.get_body()], [b_relation_variables[uid.get_body()],
                                                                              l_relation_variables[uid.get_head()]]))
        # Br1 -> Lr2
        for uid in uids:
            productions.add(Production(b_relation_variables[uid.get_body()], [l_relation_variables[uid.get_head()]]))

        # Lr -> r Br- r-
        for relation in relations:
            productions.add(Production(l_relation_variables[relation],
                                       [Terminal(relation), b_relation_variables[get_inverse_relation(relation)],
                                        Terminal(get_inverse_relation(relation))]))
        # Lr -> r r-
        for relation in relations:
            productions.add(Production(l_relation_variables[relation],
                                       [Terminal(relation),
                                        Terminal(get_inverse_relation(relation))]))

        return CFG(start_symbol=var_s, productions=productions)

    def get_relations_and_inverses(self):
        return self._relations

    @classmethod
    def get_random_function(cls, relations, min_length, max_length, proba_existential, name="NONAME"):
        length = random.randint(min_length, max_length)
        current_variable = 0
        function = Function(name)
        function.set_input_variable(current_variable)
        for i in range(length):
            new_variable = current_variable + 1
            relation = random.choice(relations)
            function.add_atom(relation, current_variable, new_variable)
            if i != length - 1 and (random.random() < proba_existential or i < min_length):
                function.set_existential_variable(new_variable)
            current_variable = new_variable
        return function

    def __str__(self):
        res = []
        for edge in self.atoms.edges.data():
            res.append("".join([edge[2]["relation"],
                                "(",
                                edge[0],
                                ",",
                                edge[1],
                                ")"]))
        nodes = list(self.atoms.nodes)
        if self.start_node in nodes:
            nodes.remove(self.start_node)
        new_nodes = []
        for node in nodes:
            if node in self.existential_variables:
                new_nodes.append("Existential:" + str(node))
            else:
                new_nodes.append("Output:" + str(node))
        start_node = self.start_node or ""
        return self.name + "(" + ", ".join(["Input:" + start_node] + new_nodes) \
            + ")" + " = " + " and ".join(res)


def put_out_indicators_in_query(longest_query):
    new_longest_query = []
    n_unseen_star = 1
    for atom in longest_query:
        if atom == "STAR":
            n_unseen_star = 0
        else:
            n_unseen_star += 1
            if n_unseen_star > 2:
                new_longest_query.append("OUT")
        new_longest_query.append(atom)
    return new_longest_query


def add_relation_to_paths(relation, previous_paths):
    next_paths = []
    for path in previous_paths:
        new_path = path[:]
        new_path.append(relation)
        next_paths.append(new_path)
    return next_paths

