import unittest
from unittest.mock import patch, MagicMock
import vote

class TestMainFunction(unittest.TestCase):
    @patch('vote.argparse.ArgumentParser.parse_args')
    @patch('vote.generate_ballots_csv')
    @patch('vote.get_winner')
    @patch('vote.generate_sankey')
    def test_main(self, mock_generate_sankey, mock_get_winner, mock_generate_ballots_csv, mock_parse_args):
        mock_args = MagicMock()
        mock_args.input = 'test.csv'
        mock_args.output = 'test.html'
        mock_args.show = False
        mock_parse_args.return_value = mock_args

        mock_generate_ballots_csv.return_value = ['1', '2', '3', '4', '5', '6', '7', '8']
        mock_get_winner.return_value = (['1', '2', '3', '4', '5', '6', '7', '8'], '1')

        vote.main(mock_args)

        mock_generate_ballots_csv.assert_called_once_with('test.csv')
        mock_get_winner.assert_called_once_with(['1', '2', '3', '4', '5', '6', '7', '8'], ['1', '2', '3', '4', '5', '6', '7', '8'])
        mock_generate_sankey.assert_called_once_with(['1', '2', '3', '4', '5', '6', '7', '8'], ['1', '2', '3', '4', '5', '6', '7', '8'], save_file_path='test.html', show_figure=False)

if __name__ == '__main__':
    unittest.main()
    