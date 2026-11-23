"""Exercise the checker through a real store. Each test edits its own copy."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "extract-session-details"
spec = importlib.util.spec_from_file_location("check_store", SKILL / "scripts/check_store.py")
store = importlib.util.module_from_spec(spec)
spec.loader.exec_module(store)


class StoreTest(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name).resolve() / "store"
        shutil.copytree(ROOT / "examples/mini-store", self.root)
        self.raw = self.root / "raw/release-minutes.md"
        self.docs = self.root / "docs"
        self.knowledge = self.docs / "knowledge"
        self.ledger = self.knowledge / "sources.md"
        self.registry = self.knowledge / "subjects.md"
        self.feature = self.knowledge / "features/export-preview.md"
        self.procedure = self.knowledge / "procedures/export-approval.md"
        self.holding = self.knowledge / "unassigned.md"
        self.evidence = self.docs / "extractions/raw/release-minutes.md"
        self.compression = self.root / "compressed/raw/release-minutes.md"
        self.sha = hashlib.sha256(self.raw.read_bytes()).hexdigest()[:12]

    def replace(self, path, old, new):
        text = path.read_text()
        self.assertIn(old, text)
        path.write_text(text.replace(old, new))

    def append(self, path, text):
        with path.open("a") as handle:
            handle.write("\n" + text + "\n")

    def result(self):
        return store.check(self.root)

    def clean(self):
        report = self.result()
        self.assertEqual((report.n_errors, report.n_warnings), (0, 0), report.render(True))

    def error(self, section, message):
        report = self.result()
        self.assertTrue(any(message in err for err in report.sections.get(section, {}).get("errors", [])),
                        report.render(True))

    def test_example_and_export(self):
        self.clean()
        out = self.root / "export"
        report = store.check(self.root, out)
        self.assertEqual(report.n_errors, 0)
        subjects, sources, history = [[json.loads(s) for s in (out / name).read_text().splitlines()]
                                     for name in ("subjects.jsonl", "sources.jsonl", "history.jsonl")]
        self.assertEqual([s["id"] for s in subjects], ["feature/export-preview", "procedure/export-approval"])
        self.assertEqual(sources[0]["sha256_12"], self.sha)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["lines"], ["raw/release-minutes.md#L3"])

    def test_optional_store_and_missing_root(self):
        (self.docs / "index.md").unlink()
        shutil.rmtree(self.knowledge)
        self.clean()
        out = self.root / "empty"
        self.assertEqual(store.check(self.root, out).n_errors, 0)
        self.assertEqual((out / "subjects.jsonl").read_bytes(), b"")
        shutil.rmtree(self.docs)
        self.error("links", "no docs/ folder")

    def test_calendar_dates(self):
        for value in ("0001", "2024", "2024-02", "2024-02-29", "unknown"):
            self.assertTrue(store.valid_date(value), value)
        for value in ("0000", "2026-99-99", "2026-13", "2025-02-29", "2026-2", "26"):
            self.assertFalse(store.valid_date(value), value)
        self.replace(self.ledger, "2026-04-08", "2026-99-99")
        self.replace(self.ledger, "2026-04-09", "unknown")
        self.error("ledger", "Event date")
        self.error("ledger", "Ingested")
        self.replace(self.feature, "2026-04-08", "2026-02-30")
        self.error("registry", "invalid evidence_through date")
        self.replace(self.feature, "2026-04-09 |", "2026-04 |")
        self.error("ledger", "History Event date")
        self.error("ledger", "History Ingested")
        self.replace(self.ledger, "| routed |", "| removed 2026-02-31 |")
        self.error("ledger", "unknown Stage")

    def test_extraction_fields_even_without_knowledge(self):
        (self.docs / "index.md").unlink()
        shutil.rmtree(self.knowledge)
        original = self.evidence.read_text()
        for before, after, message in (
                ("type: source-extraction", "type: project", "type: source-extraction"),
                ("sha256: ", "sha256: x", "64-hex"),
                ("  - raw/release-minutes.md", "", "source must name"),
                ("  - raw/release-minutes.md", "  - missing.md", "source must name"),
                ("  - raw/release-minutes.md", "  - ../store/raw/release-minutes.md\n  - ../else", "source must name")):
            with self.subTest(message=message, after=after):
                self.evidence.write_text(original.replace(before, after))
                self.error("extractions", message)
        self.evidence.write_text(original.replace("source:\n  - raw/release-minutes.md", 'source: ["raw/release-minutes.md"]'))
        self.clean()

    def test_freshness_checks_each_alias(self):
        alias = self.raw.with_name("alias.md")
        shutil.copyfile(self.raw, alias)
        self.replace(self.ledger, "`raw/release-minutes.md`", "`raw/release-minutes.md`; `raw/alias.md`")
        self.replace(self.evidence, "source:\n  - raw/release-minutes.md",
                     'source: ["raw/release-minutes.md", "raw/alias.md"]')
        self.clean()
        self.append(alias, "A new observation")
        self.error("freshness", "stale source hash for raw/alias.md")
        alias.unlink()
        self.replace(self.evidence, ', "raw/alias.md"', "")
        self.error("freshness", "missing source")
        self.replace(self.ledger, "| routed |", "| removed 2026-04-10 |")
        self.clean()

    def test_unfinished_reads(self):
        original = self.ledger.read_text()
        for stage in ("compressed", "extracted", "routed"):
            self.ledger.write_text(original.replace("| routed |", f"| {stage} |"))
            original_read = self.compression.read_text()
            for status in ("lines 1-2 of 3", "lines 1-3 of 3 (unfinished)", "lines 1-2 of 2", "unknown"):
                self.compression.write_text(original_read.replace("lines 1-3 of 3", status))
                with self.subTest(stage=stage, status=status):
                    self.error("coverage", "unfinished or incomplete")
            self.compression.write_text(original_read)
        self.replace(self.ledger, "| routed |", "| listed |")
        self.replace(self.compression, "1-3 of 3", "1-1 of 3 (unfinished)")
        self.clean()

    def test_link_bounds_and_code(self):
        page = self.docs / "index.md"
        self.append(page, '`[missing](gone.md)`\n\n```\n[missing](also-gone.md)\n```\n[raw](../raw/release-minutes.md#L1-L3)')
        self.clean()
        for target, problem in (("gone.md", "no such file"), ("../../x", "points outside"),
                                ("../raw/release-minutes.md#L3-L2", "outside 1-3"),
                                ("../raw/release-minutes.md#L0", "outside 1-3"),
                                ("../raw/release-minutes.md#L4", "outside 1-3")):
            with self.subTest(target=target):
                self.append(page, f"[bad]({target})")
                self.error("links", problem)

    def test_placeholders_match_all_references_and_skip_examples(self):
        tokens = set()
        for path in (SKILL / "references").glob("*.md"):
            tokens.update(re.findall(r"<[^<>\n]+>", path.read_text()))
        self.assertEqual(tokens, store.PLACEHOLDERS)
        self.append(self.feature, '`<title>`\n~~~\n<who>\n~~~')
        self.clean()
        self.append(self.feature, 'Owner is <who>')
        self.error("placeholders", "<who>")

    def test_quote_fidelity(self):
        citation = "[L2](../../../raw/release-minutes.md#L2)"
        original = self.evidence.read_text()
        for text in (f'"signed manifest" {citation}', f'“signed manifest” ({citation})',
                     f'{citation}: `production exports`', f'`policies.json` documents this rule {citation}',
                     f'The owner set a prerequisite {citation}', f'`{citation}` is a sample link.',
                     '```md\n"fabricated" '+citation+'\n```'):
            with self.subTest(text=text):
                self.evidence.write_text(original + "\n" + text + "\n")
                self.clean()
        for text in (f'"seventeen rows" {citation}', f'{citation}: `Approval granted`',
                     f'“14 rows” {citation}', f"'fake claim' — {citation}"):
            with self.subTest(text=text):
                self.evidence.write_text(original + "\n" + text + "\n")
                self.error("quotes", "absent from")

    def test_compression_literal_and_partial_checkpoint(self):
        self.append(self.compression, '"fiction" [L1](../../raw/release-minutes.md#L1)')
        self.error("quotes", "absent from")
        self.replace(self.compression, '"fiction"', '"Minutes by Eli"')
        self.clean()

    def test_all_status_forms(self):
        statuses = ["candidate", "open", "second-hand", "second-hand and reported",
                    "second-hand, reported by Eli", "second-hand and reported by Eli",
                    "decided by Mira (per minutes by Eli)", "superseded",
                    "superseded (inferred from date order)", 'proposed; Mira replied "ok proceed" (L4)']
        for word in ("requested", "submitted", "approved", "rejected", "completed", "verified", "assigned", "accepted"):
            statuses.extend((word, word+" by Eli", word+", reported", word+", reported by Eli"))
        for word in ("claimed", "decided", "stated", "proposed", "reported", "observed", "deferred", "withdrawn"):
            statuses.append(word+" by Eli")
        for word in ("proposed", "reported", "observed", "deferred", "withdrawn"):
            statuses.append(word)
        for value in statuses:
            self.assertIsNotNone(store.ITEM_STATUS_RE.fullmatch(value), value)
        for value in ("candidate decision", "probably approved", "second-hand and reported by",
                      "claimed", "decided by", "illustrative", "replaced by L4", "approved, verified",
                      "decided by Mira (per minutes by)", "decided by Mira (unclear minutes)"):
            self.assertIsNone(store.ITEM_STATUS_RE.fullmatch(value), value)
        self.replace(self.feature, "reported by Eli ·", "inferred success ·")
        self.error("registry", "unknown item status")
        self.replace(self.feature, " · ", " ")
        self.error("registry", "not followed by")

    def test_routing_matches_record_lines_not_just_source(self):
        locator = "[L1](../../../raw/release-minutes.md#L1)"
        self.replace(self.evidence, "## Subjects it names",
                     f"### Assign the review\n{locator} · Eli · assigned\n\n## Subjects it names")
        warnings = self.result().sections["routing"]["warnings"]
        self.assertEqual(len(warnings), 1)
        self.assertIn("Assign the review", warnings[0])
        self.replace(self.evidence, "· assigned", "· illustrative")
        self.clean()
        self.replace(self.evidence, "· illustrative", "· background")
        self.clean()
        self.replace(self.evidence, "· background", "· assigned")
        self.holding.write_text("| " + " | ".join(store.HOLDING_HEADER) + " |\n|---|---|---|---|---|---|\n"
            f"| 2026-04-09 | [minutes](../extractions/raw/release-minutes.md) `{self.sha}` | "
            "[L1](../../raw/release-minutes.md#L1) | Assign the review | - | Subject unclear |\n")
        self.error("ledger", "does not list unassigned")
        self.replace(self.ledger, "procedure/export-approval |", "procedure/export-approval, unassigned |")
        self.clean()
        self.replace(self.holding, "2026-04-09", "2026-00-01")
        self.error("ledger", "invalid holding Added")
        self.replace(self.holding, self.sha, "f"*12)
        self.error("ledger", "not in the ledger")
        self.replace(self.holding, "f"*12, "bogus")
        self.error("ledger", "holding row Source has no")
        self.holding.unlink()
        self.error("ledger", "holding page has no row")

    def test_two_records_on_one_span(self):
        self.replace(self.evidence, "## Subjects it names",
                     "### Production remains untested\n[L3](../../../raw/release-minutes.md#L3) · Eli · reported\n\n## Subjects it names")
        warnings = self.result().sections["routing"]["warnings"]
        self.assertEqual(len(warnings), 1)
        self.assertIn("Production remains untested", warnings[0])
        row = self.feature.read_text().splitlines()[-1]
        anchored = row.replace("release-minutes.md) `", "release-minutes.md#production-remains-untested) `")
        anchored = anchored.replace("Staging preview showed 14 rows |", "Recorded remaining test gap |")
        self.feature.write_text(self.feature.read_text() + anchored + "\n")
        self.clean()

    def test_registry_identity_and_retirement(self):
        self.replace(self.registry, "Export preview | -", "Export preview | Production export approval")
        self.assertIn("shared by active", self.result().sections["registry"]["warnings"][0])
        self.replace(self.registry, "Export preview | Production export approval", "Export preview | -")
        self.replace(self.registry, "| active | [Export preview]", "| merged into procedure/export-approval | [Export preview]")
        self.error("registry", "differs from page")
        self.replace(self.feature, "status: active", "status: merged into procedure/export-approval")
        self.clean()
        self.replace(self.registry, "merged into procedure/export-approval", "split into project/missing, procedure/export-approval")
        self.error("registry", "target project/missing")
        self.replace(self.feature, "status: merged into procedure/export-approval", "status: archived")
        self.error("registry", "unknown status")
        self.replace(self.feature, "id: feature/export-preview", "id: feature/wrong")
        self.error("registry", "front matter id")
        self.replace(self.feature, "type: feature", "type: project")
        self.error("registry", "front matter type")
        self.replace(self.feature, "---", "+++")
        self.error("registry", "no front matter")

    def test_registry_rows_and_index(self):
        row = self.registry.read_text().splitlines()[-1]
        self.registry.write_text(self.registry.read_text().rstrip()+"\n"+row+"\n")
        self.error("registry", "duplicate ID")
        original = self.registry.read_text()
        for old,new,message in (
                ("procedure/export-approval | procedure", "bad_id | procedure", "malformed ID"),
                ("procedure/export-approval | procedure", "procedure/export-approval | project", "does not match ID"),
                ("[Production export approval](procedures/export-approval.md)", "-", "no page link"),
                ("(procedures/export-approval.md)", "(subjects.md)", "page link")):
            with self.subTest(message=message):
                self.registry.write_text(original.replace(old,new))
                self.error("registry", message)
        self.registry.write_text(original)
        self.append(self.knowledge / "features/index.md","- [Export preview](export-preview.md): Wrong description.")
        self.error("registry", "index description")
        self.feature.unlink()
        self.error("registry", "does not exist")
        self.error("ledger", "its page does not exist")
        self.registry.unlink()
        self.error("registry", "subjects.md is missing")
        self.error("registry", "no registry row")

    def test_table_headers(self):
        for path,section in ((self.ledger, "ledger"), (self.registry, "registry"), (self.holding, "ledger")):
            with self.subTest(path=path.name):
                path.write_text("# Something else\n")
                self.error(section, path.name + ": no table")

    def test_ledger_rows(self):
        original = self.ledger.read_text()
        self.replace(self.ledger, self.sha, "e"*12)
        self.error("ledger", "different source hash")
        self.ledger.write_text(original+original.splitlines()[-1]+"\n")
        self.error("ledger", "duplicate sha256 prefix")
        for old,new,message in (
                (self.sha, "invalid", "not 12 lowercase"),
                ("| routed |", "| done |", "unknown Stage"),
                ("(../extractions/raw/release-minutes.md)", "(absent.md)", "does not resolve"),
                ("[minutes](../extractions/raw/release-minutes.md)", "filename", "neither a link nor"),
                ("[minutes](../extractions/raw/release-minutes.md)", "-", "requires an evidence link"),
                ("feature/export-preview,", "project/absent,", "not in the registry")):
            with self.subTest(message=message):
                self.ledger.write_text(original.replace(old,new))
                self.error("ledger", message)
        self.ledger.write_text(original)
        self.replace(self.feature, "| added |", "| invented |")
        self.error("ledger", "Change 'invented'")
        self.replace(self.feature, self.sha, "f"*12)
        self.error("ledger", "not in the ledger")
        self.error("ledger", "History has no row")
        self.replace(self.feature, "f"*12, "bogus")
        self.error("ledger", "Source has no")
        self.replace(self.ledger, "feature/export-preview, ", "")
        self.replace(self.feature, "`bogus`", f"`{self.sha}`")
        self.error("ledger", "does not list feature/export-preview")
        self.ledger.unlink()
        self.error("ledger", "sources.md is missing")
