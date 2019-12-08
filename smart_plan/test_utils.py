import unittest

from smart_plan.function import Function
from smart_plan.uid import UID
from smart_plan.utils import turn_functions_into_regex, get_all_relations, deduce_all_uids


class TestUtils(unittest.TestCase):

    def test_conversion_to_regex(self):
        self.assertEqual(sorted(turn_functions_into_regex(self.functions)),
                         sorted("((r1)|(r2))*"))

    def test_deduce_uid(self):
        uids = [
            UID("r1", "r2"),
            UID("r2", "r3"),
            UID("r3", "r4")
        ]
        new_uids = deduce_all_uids(uids)
        self.assertEqual(len(new_uids), 6)
        self.assertIn(UID("r1", "r4"), new_uids)
        self.assertIn(UID("r2", "r4"), new_uids)
        self.assertIn(UID("r1", "r3"), new_uids)
        for uid in uids:
            self.assertIn(uid, new_uids)

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
