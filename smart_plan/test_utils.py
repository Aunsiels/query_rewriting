import unittest

from smart_plan.function import Function
from smart_plan.utils import turn_functions_into_regex, get_all_relations


class TestUtils(unittest.TestCase):

    def test_conversion_to_regex(self):
        self.assertEqual(sorted(turn_functions_into_regex(self.functions)),
                         sorted("((r1)|(r2))*"))

    def setUp(self):
        self.f0 = Function()
        self.f0.add_atom("r1", "x", "y")
        self.f1 = Function()
        self.f1.add_atom("r2", "z", "t")
        self.functions = [self.f0, self.f1]

    def test_get_all_relations(self):
        self.assertEqual(get_all_relations([]), set())
        self.assertEqual(get_all_relations(self.functions), {"r1", "r1-", "r2", "r2-"})


if __name__ == '__main__':
    unittest.main()
