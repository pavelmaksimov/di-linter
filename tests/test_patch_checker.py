import unittest
from pathlib import Path

from di_linter.patch_linter import PatchChecker


class TestPatchChecker(unittest.TestCase):
    def test_patch_visitor_detects_unittest_patch(self):
        # Create a simple test file with unittest.mock.patch
        test_content = """
import unittest
from unittest.mock import patch

class TestExample(unittest.TestCase):
    @patch('module.function')
    def test_function(self, mock_function):
        mock_function.return_value = 'mocked'
        self.assertEqual(mock_function(), 'mocked')
"""
        # Create a temporary file
        temp_file = Path("temp_test_file.py")
        temp_file.write_text(test_content)

        try:
            # Create a TestChecker and analyze the file
            checker = PatchChecker(temp_file)
            issues = checker.analyze_tests()

            # Check that the patch was detected
            self.assertEqual(len(issues), 1)
            self.assertEqual(issues[0].line_num, 6)
            self.assertIn("Patch usage in tests", issues[0].message)
        finally:
            # Clean up
            temp_file.unlink(missing_ok=True)

    def test_patch_visitor_detects_pytest_monkeypatch(self):
        # Create a simple test file with pytest monkeypatch
        test_content = """
import pytest

def test_function(monkeypatch):
    monkeypatch.setattr('module.function', lambda: 'mocked')
    assert module.function() == 'mocked'
"""
        # Create a temporary file
        temp_file = Path("temp_test_file.py")
        temp_file.write_text(test_content)

        try:
            # Create a TestChecker and analyze the file
            checker = PatchChecker(temp_file)
            issues = checker.analyze_tests()

            # Check that the monkeypatch was detected
            self.assertEqual(len(issues), 1)
            self.assertEqual(issues[0].line_num, 5)
            self.assertIn("Patch usage in tests", issues[0].message)
        finally:
            # Clean up
            temp_file.unlink(missing_ok=True)

    def test_patch_visitor_detects_patch_context_manager(self):
        # Create a simple test file with patch as context manager
        test_content = """
import unittest
from unittest.mock import patch

class TestExample(unittest.TestCase):
    def test_function(self):
        with patch('module.function') as mock_function:
            mock_function.return_value = 'mocked'
            self.assertEqual(mock_function(), 'mocked')
"""
        # Create a temporary file
        temp_file = Path("temp_test_file.py")
        temp_file.write_text(test_content)

        try:
            # Create a TestChecker and analyze the file
            checker = PatchChecker(temp_file)
            issues = checker.analyze_tests()

            # Check that the patch was detected
            self.assertEqual(len(issues), 1)
            self.assertEqual(issues[0].line_num, 7)
            self.assertIn("Patch usage in tests", issues[0].message)
        finally:
            # Clean up
            temp_file.unlink(missing_ok=True)

    def test_patch_visitor_respects_skip_comment(self):
        # Create a simple test file with unittest.mock.patch and skip comment
        test_content = """
import unittest
from unittest.mock import patch

class TestExample(unittest.TestCase):
    @patch('module.function')  # di: skip
    def test_function(self, mock_function):
        mock_function.return_value = 'mocked'
        self.assertEqual(mock_function(), 'mocked')
"""
        # Create a temporary file
        temp_file = Path("temp_test_file.py")
        temp_file.write_text(test_content)

        try:
            # Create a TestChecker and analyze the file
            checker = PatchChecker(temp_file)
            issues = checker.analyze_tests()

            # Check that the patch was not detected due to skip comment
            self.assertEqual(len(issues), 0)
        finally:
            # Clean up
            temp_file.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
