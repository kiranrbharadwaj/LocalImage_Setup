import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("models", ROOT / "scripts/models.py")
models = importlib.util.module_from_spec(spec)
spec.loader.exec_module(models)


class IntegrityTests(unittest.TestCase):
    def test_corruption_is_detected_even_at_same_size(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "weight"
            file.write_bytes(b"good")
            item = {"size": 4, "sha256": hashlib.sha256(b"good").hexdigest()}
            self.assertTrue(models.verify(file, item))
            file.write_bytes(b"evil")
            self.assertFalse(models.verify(file, item))
            file.unlink()
            self.assertFalse(models.verify(file, item))

    def test_unsafe_manifest_is_rejected(self):
        for destination in ["../outside", "/absolute"]:
            with self.subTest(destination=destination), patch.object(Path, "read_text", return_value=json.dumps([{"path": destination}])):
                with self.assertRaises(ValueError):
                    models.manifest()

    def test_verify_only_never_downloads(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(models.subprocess, "run") as download:
            with self.assertRaises(RuntimeError):
                models.install(Path(directory), verify_only=True)
            download.assert_not_called()

    def test_pinned_manifest_has_unique_paths(self):
        entries = models.manifest()
        self.assertEqual(len(entries), len({x["path"] for x in entries}))
        self.assertTrue(all(x["size"] > 0 for x in entries))


class WorkflowTests(unittest.TestCase):
    def test_connections_and_assets(self):
        outputs = {"UNETLoader": 1, "CLIPLoader": 1, "VAELoader": 1, "LoadImage": 2,
                   "TextEncodeQwenImage21": 3, "KSampler": 1, "VAEDecodeTiled": 1,
                   "SaveImage": 0, "LoraLoaderModelOnly": 1}
        available = {Path(x["path"]).name for x in models.manifest()}
        for file in (ROOT / "workflows").glob("*-api.json"):
            with self.subTest(workflow=file.name):
                graph = json.loads(file.read_text())
                ui = json.loads(file.with_name(file.name.replace("-api", "-workflow")).read_text())
                self.assertEqual({str(x["id"]): x["type"] for x in ui["nodes"]},
                                 {key: value["class_type"] for key, value in graph.items()})
                for node in graph.values():
                    self.assertIn(node["class_type"], outputs)
                    for name, value in node["inputs"].items():
                        if isinstance(value, list):
                            self.assertIn(value[0], graph)
                            self.assertLess(value[1], outputs[graph[value[0]]["class_type"]])
                        if name in {"unet_name", "clip_name", "vae_name", "lora_name"}:
                            self.assertIn(value, available)
                    if node["class_type"] == "LoadImage":
                        self.assertTrue((ROOT / "examples" / node["inputs"]["image"]).is_file())
                    if node["class_type"] == "CLIPLoader":
                        self.assertEqual(node["inputs"]["type"], "qwen_image")

    def test_reference_workflow_has_two_distinct_images(self):
        graph = json.loads((ROOT / "workflows/reference-edit-api.json").read_text())
        encoder = next(x for x in graph.values() if x["class_type"] == "TextEncodeQwenImage21")
        self.assertNotEqual(encoder["inputs"]["images.image_1"], encoder["inputs"]["images.image_2"])
        self.assertIn("<image1>", encoder["inputs"]["prompt"])
        self.assertIn("<image2>", encoder["inputs"]["prompt"])

class PrivacyTests(unittest.TestCase):
    def test_launcher_keeps_network_and_plugin_guards(self):
        launcher = (ROOT / "Start-ComfyUI.command").read_text()
        for flag in ["--listen 127.0.0.1", "--offline", "--disable-all-custom-nodes", "--disable-metadata", "sandbox-exec"]:
            self.assertIn(flag, launcher)
        self.assertNotIn("0.0.0.0", launcher)
        profile = (ROOT / "scripts/local-only.sb").read_text()
        self.assertIn("(deny network*)", profile)
        self.assertIn('localhost:*', profile)


if __name__ == "__main__":
    unittest.main()
