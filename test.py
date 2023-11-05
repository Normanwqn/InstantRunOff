import unittest
from vote import number_to_ordinal, ordinal_to_number, generate_ballot_from_row

class TestVote(unittest.TestCase):
    def test_number_to_ordinal(self):
        self.assertEqual(number_to_ordinal(1), '1st')
        self.assertEqual(number_to_ordinal(2), '2nd')
        self.assertEqual(number_to_ordinal(3), '3rd')
        self.assertEqual(number_to_ordinal(4), '4th')
        self.assertEqual(number_to_ordinal(11), '11th')
        self.assertEqual(number_to_ordinal(21), '21st')

    def test_ordinal_to_number(self):
        self.assertEqual(ordinal_to_number('1st'), 1)
        self.assertEqual(ordinal_to_number('2nd'), 2)
        self.assertEqual(ordinal_to_number('3rd'), 3)
        self.assertEqual(ordinal_to_number('4th'), 4)
        self.assertEqual(ordinal_to_number('11th'), 11)
        self.assertEqual(ordinal_to_number('21st'), 21)
        with self.assertRaises(ValueError):
            ordinal_to_number('1')

    def test_generate_ballot_from_row(self):
        self.assertEqual(generate_ballot_from_row(['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th']), ['1', '2', '3', '4', '5', '6', '7', '8'])
        self.assertEqual(generate_ballot_from_row(['8th', '7th', '6th', '5th', '4th', '3rd', '2nd', '1st']), ['8', '7', '6', '5', '4', '3', '2', '1'])
        self.assertEqual(generate_ballot_from_row(['1st', '', '3rd', '', '5th', '', '7th', '']), ['1', '3', '5', '7'])
        self.assertEqual(generate_ballot_from_row(['', '2nd', '', '4th', '', '6th', '', '8th']), ['2', '4', '6', '8'])

if __name__ == '__main__':
    unittest.main()