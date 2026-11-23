import json
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
repo = runpy.run_path(str(ROOT / "scripts/check_repo.py"))
exporter = ROOT / "session-transcripts/export_transcript.py"


class PublicRepoTest(unittest.TestCase):
    def test_skill_headers(self):
        parse = repo["skills_frontmatter"]
        for value, expected in (("plain text", "plain text"), ('"inside: quotes"', "inside: quotes"),
                                (">-\n  A folding\n  description", "A folding description")):
            self.assertEqual(parse(f"---\nname: example\ndescription: {value}\n---"),
                             {"name": "example", "description": expected})
        for opening, description in (("   ---", "description: valid"), ("---", "   description: padded"),
                                     ("---", "description: unquoted: colon"), ("---", "description: '")):
            self.assertFalse(parse(f"{opening}\nname: x\n{description}\n---").get("description"))

    def test_inventory_links_privacy_and_mirrors(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            (root / "example").mkdir()
            (root / "example/SKILL.md").write_text("---\nname: example\ndescription: Test example.\n---\n")
            readme = root / "README.md"
            readme.write_text("# Using skills\n\n[Here](#using-skills) [Example](example/SKILL.md)\n")
            self.assertEqual(repo["check"](root), [])
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            readme.write_text("[absent](absent.md)\n[escape](../outside)\n[ref]: missing.md\n[here](#missing-heading)\n")
            (root / "leak.txt").write_text("/" + "home" + "/reader/private.txt")
            mirror = root / "extract-session-details/references"
            mirror.mkdir(parents=True)
            (mirror / "store.md").write_text("unmirrored\n")
            findings = "\n".join(repo["check"](root))
            for text in ("README.md is missing example/SKILL.md", "absent.md", "../outside",
                         "missing.md", "missing-heading", "private path", "differ at references/store.md"):
                self.assertIn(text, findings)

    def test_real_transcript_export_redacts_both_home_layouts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            native = root / "session.jsonl"
            output = root / "export.md"
            paths = ["/" + folder + "/reader" + suffix for folder, suffix in
                     (("Users", "/Personal Notes/agenda.md"), ("home", "/work/notes.txt"))]
            prompt = f'Read "{paths[0]}" then check {paths[1]} for deadlines.'
            entries = [
                {"type": "session_meta", "payload": {"id": "public-test", "cwd": paths[1]}},
                {"type": "response_item", "payload": {"type": "message", "role": "user",
                 "content": [{"type": "input_text", "text": prompt}]}},
            ]
            native.write_text("".join(json.dumps(e)+"\n" for e in entries))
            proc = subprocess.run([sys.executable, "-I", "-B", str(exporter), str(output), str(native)],
                                  capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            result = output.read_text()
            self.assertIn('Read "[local path]" then check [local path] for deadlines.', result)
            self.assertIn("cwd [local path]", result)
            for part in ("reader", "Personal Notes", "agenda.md", "notes.txt"):
                self.assertNotIn(part, result)
