import os
from xml.etree import ElementTree as ElementTree

from smart_plan.function import Function


def get_attribute_from_triple(child, attr):
    return child.attrib[attr].replace("?", "").replace(":", "")


class FunctionReader(object):

    def __init__(self):
        self.filename = ""
        self.counter = 0

    def get_function_from_file(self, filename):
        self.filename = filename
        name = filename.split("/")[-1].split(".")[0]
        function = self.create_new_function(name)
        self.add_atoms_from_xml_to_function(function)
        return self.return_function_if_single_input(function)

    def add_atoms_from_xml_to_function(self, function):
        root = self.get_root_xml()
        for definition in root.iter("definition"):
            self.add_all_triples_definition_to_function(definition, function)

    def create_new_function(self, name="NONAME"):
        function = Function(name=name)
        self.counter = 0
        return function

    def add_all_triples_definition_to_function(self, definition, function):
        for triple in definition:
            self.add_triple_to_function(triple, function)

    def return_function_if_single_input(self, function):
        is_single_output = self.counter == 1
        if not is_single_output:
            return Function()
        return function

    def add_triple_to_function(self, triple, function):
        input_variable = get_attribute_from_triple(triple, "subject")
        relation = str(get_attribute_from_triple(triple, "predicate"))
        output_variable = get_attribute_from_triple(triple, "object")
        if "type" not in relation:
            function.add_atom(relation, input_variable, output_variable)
        if "isexistential" in triple.attrib and "true" == triple.attrib["isexistential"]:
            function.set_existential_variable(output_variable)
        if triple.attrib["isinput"] == "true":
            self.counter += 1
            function.set_input_variable(input_variable)

    def get_root_xml(self):
        tree = ElementTree.parse(self.filename)
        root = tree.getroot()
        return root

    def get_functions_from_dir(self, directory):
        functions = []
        for filename in os.listdir(directory):
            if filename.endswith(".xml"):
                new_function = self.get_function_from_file(directory + "/" + filename)
                if len(new_function.atoms.nodes) != 0:
                    functions.append(new_function)
        return functions
