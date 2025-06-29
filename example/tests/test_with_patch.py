import unittest
from unittest.mock import patch

import pytest

class TestExample(unittest.TestCase):
    @patch('module.function')
    def test_function(self, mock_function):
        mock_function.return_value = 'mocked'
        self.assertEqual(mock_function(), 'mocked')

    def test_function_with_context_manager(self):
        with patch('module.function') as mock_function:
            mock_function.return_value = 'mocked'
            self.assertEqual(mock_function(), 'mocked')


def test_with_monkeypatch(monkeypatch):
    monkeypatch.setattr('module.function', lambda: 'mocked')
    assert 'mocked' == 'mocked'