import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import name2face as nf  # noqa: E402


def digest(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


class UpstreamTests(unittest.TestCase):
    """Ports of packages/avatar-core/tests/avatar.test.ts (same expected hashes and digests)."""

    def test_rounded_output(self):
        key, h, c = nf.choices_for("Janaki")
        self.assertEqual((key, h), ("janaki", 4_216_952_012_017_202))
        self.assertEqual(c, dict(browI=7, dxI=2, dyI=1, eyeI=0, faceTiltI=20, flip=1, gapI=1, lookI=0,
                                 mouthI=8, shapeI=1, tiltI=0))
        self.assertEqual(digest(nf.avatar("Janaki", ("#f2f1f4", "#7c6cf2"), "rounded")),
                         "48745f125fe596ff9e116476aaaf2295ecca286872dd20ce006bfb6a4782e32a")

    def test_circle_output_and_escaping(self):
        self.assertEqual(nf.choices_for("Blobz <Admin>")[1], 1_665_355_454_956_846)
        svg = nf.avatar("Blobz <Admin>", ("#101828", "#f79009"), "circle")
        self.assertEqual(digest(svg), "c0cf729908dd0791d4d429a22ad26c6b7e3245f442843efd51ca0b0ac17058bd")
        self.assertIn("Blob avatar for blobz &lt;admin&gt;", svg)

    def test_every_manual_choice(self):
        choices = dict(browI=8, dxI=4, dyI=2, eyeI=6, faceTiltI=24, flip=1, gapI=2, lookI=4, mouthI=10, shapeI=16, tiltI=14)
        svg = nf.avatar("custom", ("#ffffff", "#12b76a"), "square", choices)
        self.assertEqual(digest(svg), "39a1de2cad99598136aedcd222e4c7c793ab32357309aff76057c877a2c2ba0f")

    def test_catalogue(self):
        sizes = {k: len(v) for k, v in nf.CHOICES.items()}
        self.assertEqual(sizes, dict(shape=21, eyes=14, look=5, mouth=11, brows=9, gap=3))
        total = 1
        for _, count in nf.ORDER:
            total *= count
        self.assertEqual(total, 4_911_637_500)

    def test_normalizes_names(self):
        self.assertEqual(nf.avatar("  Blobz  ", ("#fffafa", "#7c6cf2")), nf.avatar("blobz", ("#fffafa", "#7c6cf2")))

    def test_ignores_invalid_overrides(self):
        pal = ("#f8fafc", "#14b8a6")
        self.assertEqual(nf.avatar("fallback", pal, "rounded", dict(eyeI=-1, mouthI=1.5, shapeI=99)), nf.avatar("fallback", pal))


class MatchesUpstream(unittest.TestCase):
    def test_golden_svgs(self):
        """29 names written by @blobz/avatar-core that together use every shape, eye, mouth, brow, look,
        gap, tilt, shift, face angle, mirror, frame and 4 palettes (one dark), plus unicode, emoji and XML escapes."""
        rows = [json.loads(line) for line in (ROOT / "tests" / "golden.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(rows), 29)
        for row in rows:
            with self.subTest(row["name"]):
                self.assertEqual(nf.avatar(row["name"], tuple(row["palette"]), row["frame"]), row["svg"])


class Cli(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(ROOT / "name2face.py"), *map(str, args)],
                              capture_output=True, text=True, encoding="utf-8")

    def test_print_files_and_gallery(self):
        r = self.run_cli("Janaki")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), nf.avatar("Janaki"))
        with tempfile.TemporaryDirectory() as d:
            r = self.run_cli("ada", "Grace Hopper", "-o", d, "--html", Path(d) / "g.html", "--frame", "circle")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual((Path(d) / "grace_hopper.svg").read_text(encoding="utf-8"), nf.avatar("Grace Hopper", frame="circle"))
            self.assertEqual((Path(d) / "g.html").read_text(encoding="utf-8").count("<svg"), 2)

    def test_rejects_bad_colour(self):
        self.assertNotEqual(self.run_cli("ada", "--body", "red").returncode, 0)


if __name__ == "__main__":
    unittest.main()
