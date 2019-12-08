import unittest

from smart_plan.function import Function
from smart_plan.uid import UID


class TestFunction(unittest.TestCase):

    def setUp(self) -> None:
        self.function = Function()
    
    def test_create_empty_function(self):
        self.assertEqual(self.function.get_number_variables(), 0)
        self.assertEqual(self.function.get_number_atoms(), 0)

    def test_add_atom(self):
        self.function.add_atom("r", "x", "x")
        self.assertEqual(self.function.get_number_variables(), 1)
        self.assertEqual(self.function.get_number_atoms(), 1)

        self.function.add_atom("r", "y", "y")
        self.assertEqual(self.function.get_number_variables(), 2)
        self.assertEqual(self.function.get_number_atoms(), 2)

        self.function.add_atom("r", "x", "y")
        self.assertEqual(self.function.get_number_variables(), 2)

        self.function.add_atom("r", "t", "u")
        self.assertEqual(self.function.get_number_variables(), 4)

    def test_get_linear_paths(self):
        self.assertEqual(self.function.get_linear_paths(), [])

        self.function.add_atom("r1", "x", "y")
        self.assertEqual(sorted(self.function.get_linear_paths()),
                         sorted([["r1"]]))

        self.function.add_atom("r2", "y", "z")
        self.assertEqual(sorted(self.function.get_linear_paths()),
                         sorted([["r1"], ["r1", "r2"]]))

        self.function.add_atom("r3", "x", "z")
        self.assertEqual(sorted(self.function.get_linear_paths()),
                         sorted([["r1"], ["r1", "r2"], ["r3"], ["r3", "r2-"]]))

        self.function.add_atom("r4-", "z", "y")
        self.assertEqual(sorted(self.function.get_linear_paths()),
                         sorted([["r1"], ["r1", "r2"], ["r3"], ["r3", "r2-"], ["r1", "r4"], ["r3", "r4-"]
                                 ]))

    def test_real_linear(self):
        self.function.add_atom("r1", "x", "y")
        self.function.add_atom("r2", "y", "z")
        self.assertTrue(self.function.is_linear())

    def test_false_linear(self):
        self.function.add_atom("r1", "x", "y")
        self.function.add_atom("r2", "y", "z")
        self.function.add_atom("r2", "x", "z")
        self.assertFalse(self.function.is_linear())

    def test_false_linear2(self):
        self.function.add_atom("r1", "x", "y")
        self.function.add_atom("r2", "z", "t")
        self.assertFalse(self.function.is_linear())

    def test_get_all_linear_subfunctions(self):
        self.function.add_atom("r1", "x", "y")
        self.function.add_atom("r2", "y", "z")
        self.function.add_atom("r3", "y", "t")
        self.assertEqual(len(self.function.get_linear_subfunctions()), 3)
        for function in self.function.get_linear_subfunctions():
            self.assertTrue(function.is_linear())

    def test_existential(self):
        self.assertEqual(self.function.get_number_existential_variables(), 0)

        self.function.add_atom("r1", "x", "y")
        self.function.set_existential_variable("y")

        self.assertEqual(self.function.get_linear_paths(), [])

        self.function.add_atom("r2", "y", "z")
        self.assertEqual(sorted(self.function.get_linear_paths()),
                         sorted([["r1", "r2"]]))

    def test_set_input_variable(self):
        self.function.add_atom("r1", "x", "y")
        self.function.set_input_variable("y")
        self.assertEqual(self.function.get_linear_paths(), [["r1-"]])

    def test_get_longest_query(self):
        self.assertEqual(self.function.get_longest_query(), [])

        self.function.add_atom("r1", "x", "y")
        self.assertEqual(self.function.get_longest_query(), ["r1"])

    def test_grammar(self):
        self.function.add_atom("r1", "x", "y")
        relations = ["r1", "r2", "r1-", "r2-"]
        uids = [UID("r1", "r2")]
        cfg = self.function.get_longest_query_grammar(relations, uids)
        self.assertTrue(cfg.contains(["r1"]))
        self.assertTrue(cfg.contains(["r2", "r2-", "r1"]))
        self.assertFalse(cfg.contains(["r2", "r1"]))

    def test_get_relations_and_inverses(self):
        self.assertEqual(self.function.get_relations_and_inverses(), set())

        self.function.add_atom("r1", "x", "y")
        self.assertEqual(self.function.get_relations_and_inverses(), {"r1", "r1-"})


if __name__ == '__main__':
    unittest.main()
