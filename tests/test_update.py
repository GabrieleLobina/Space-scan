import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("space_update", ROOT / "scripts" / "update.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def example(status="Go for Launch"):
    return {
        "id": "test-1", "name": "Falcon 9 | Starlink", "net": "2026-11-02T10:00:00Z",
        "status": {"name": status},
        "launch_service_provider": {"name": "SpaceX"},
        "rocket": {"configuration": {"full_name": "Falcon 9 Block 5"}},
        "pad": {"name": "SLC-40"}
    }


class LaunchTests(unittest.TestCase):
    def test_confirmed_launch_has_countdown(self):
        launch = module.normalize_launch(example())
        self.assertEqual(launch["precision"], "datetime")
        self.assertEqual(launch["date"], "2026-11-02T10:00:00Z")

    def test_net_launch_has_no_countdown(self):
        launch = module.normalize_launch(example("To Be Determined"))
        self.assertEqual(launch["precision"], "window")
        self.assertIsNone(launch["date"])
        self.assertTrue(launch["window"].startswith("NET "))

    def test_other_provider_ignored(self):
        item = example()
        item["name"] = "Ariane 6"
        item["launch_service_provider"]["name"] = "Arianespace"
        item["rocket"]["configuration"]["full_name"] = "Ariane 6"
        self.assertIsNone(module.normalize_launch(item))

    def test_cancelled_ignored(self):
        self.assertIsNone(module.normalize_launch(example("Launch Cancelled")))

    def test_missing_results_preserves_snapshot(self):
        data = {"launches": [{"name": "Existing"}], "changes": []}
        with self.assertRaises(ValueError):
            module.update_launches(data, {}, "2026-10-28")
        self.assertEqual(data["launches"][0]["name"], "Existing")

    def test_launch_change_logged(self):
        old = module.normalize_launch(example("To Be Determined"))
        data = {"launches": [old], "changes": []}
        module.update_launches(data, {"results": [example()]}, "2026-10-28")
        self.assertEqual(len(data["changes"]), 1)
        self.assertEqual(data["launches"][0]["precision"], "datetime")


if __name__ == "__main__":
    unittest.main()
