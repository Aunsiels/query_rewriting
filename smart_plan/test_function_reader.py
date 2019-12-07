import unittest

from smart_plan.function_reader import FunctionReader

DIR = "definition/Books/"
EXAMPLE = DIR + "FUNABEGetBookInfoByISBN.xml"


class TestFunctionReader(unittest.TestCase):

    def setUp(self) -> None:
        self.function_reader = FunctionReader()

    def test_get_function(self):
        function = self.function_reader.get_function_from_file(EXAMPLE)
        print(function)
        self.assertEqual(function.get_number_atoms(), 3)
        self.assertEqual(function.get_number_variables(), 4)
        self.assertEqual(function.get_number_existential_variables(), 1)

    def test_get_function_from_dir(self):
        functions = self.function_reader.get_functions_from_dir(DIR)
        self.assertEqual(len(functions), 12)


if __name__ == '__main__':
    unittest.main()
