import unittest
import xml.etree.ElementTree as ET
from pulse import render, validate

class PulseTests(unittest.TestCase):
    def test_valid_and_escaped(self):
        root = ET.fromstring(render({"projects": [{"name": "A & B < C", "status": "Development", "milestone": "Verified sample"}]}))
        self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
        self.assertIn("A & B < C", "".join(root.itertext()))

    def test_extra_fields_rejected(self):
        with self.assertRaises(ValueError):
            validate({"projects": [{"name": "A", "status": "Active", "milestone": "B", "token": "not allowed"}]})

    def test_empty_projects_rejected(self):
        with self.assertRaises(ValueError):
            render({"projects": []})

    def test_missing_field_rejected(self):
        with self.assertRaises(ValueError):
            render({"projects": [{"name": "A", "status": "Active"}]})

    def test_invalid_control_character(self):
        with self.assertRaises(ValueError):
            render({"projects": [{"name": "A\u0000", "status": "Active", "milestone": "B"}]})

    def test_theme(self):
        data = {"projects": [{"name": "A", "status": "Active", "milestone": "B"}]}
        self.assertNotEqual(render(data), render(data, "slate"))
        with self.assertRaises(ValueError):
            render(data, "unknown")

if __name__ == "__main__":
    unittest.main()
