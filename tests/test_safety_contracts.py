"""Structural safety checks; not a live Home Assistant execution test."""
import pathlib
import unittest
import yaml

class Loader(yaml.SafeLoader):
    pass
Loader.add_constructor("!input", lambda loader, node: {"input": loader.construct_scalar(node)})
ROOT = pathlib.Path(__file__).resolve().parents[1]
def read(name):
    return yaml.load((ROOT / "blueprints" / name).read_text(), Loader=Loader)
def walk(obj):
    if isinstance(obj, dict):
        yield obj
        for value in obj.values():
            yield from walk(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from walk(value)
class SafetyContracts(unittest.TestCase):
    def test_leak_protection_never_opens(self):
        doc = read("water_valve_protection.yaml")
        actions = [item.get("action") for item in walk(doc["actions"])]
        self.assertIn("switch.turn_off", actions)
        self.assertNotIn("switch.turn_on", actions)
        self.assertIn("input_boolean.turn_on", actions)

    def test_test_disabled_by_default(self):
        doc = read("water_valve_monthly_test.yaml")
        self.assertIs(doc["blueprint"]["input"]["enabled"]["default"], False)
        self.assertIn("enabled", doc["conditions"][0]["value_template"])

    def test_both_travel_waits_guard_leak_and_lock(self):
        doc = read("water_valve_monthly_test.yaml")
        waits = [item["wait_template"] for item in walk(doc["actions"]) if "wait_template" in item]
        self.assertEqual(len(waits), 2)
        for template in waits:
            self.assertIn("lock", template)
            self.assertIn("monitored", template)
            self.assertIn("reject('is_state', 'off')", template)
            self.assertIn("has_value(valve)", template)
            self.assertIn("fault_policy", template)

    def test_fault_policy_does_not_gate_leak_close(self):
        doc = read("water_valve_protection.yaml")
        blocks = [item for item in walk(doc["actions"]) if "if" in item]
        closer = next(block for block in blocks if any(
            item.get("action") == "switch.turn_off" for item in walk(block["then"])))
        self.assertNotIn("fault", str(closer["if"]))

if __name__ == "__main__":
    unittest.main()
