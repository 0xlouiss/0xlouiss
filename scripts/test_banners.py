"""Dependency-free SVG and README checks: python scripts/test_banners.py."""

from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
SVG = "{http://www.w3.org/2000/svg}"


class ProfileBanners(unittest.TestCase):
    def test_safe_accessible_self_contained_svgs(self):
        for theme in ("dark", "light"):
            with self.subTest(theme=theme):
                source = (ROOT / f"assets/profile-{theme}.svg").read_text(encoding="utf-8")
                root = ET.fromstring(source)
                self.assertEqual(root.tag, SVG + "svg")
                self.assertEqual(root.get("viewBox"), "0 0 1125 536")
                self.assertEqual(root.get("role"), "img")
                ids = [e.get("id") for e in root.iter() if e.get("id")]
                self.assertEqual(len(ids), len(set(ids)), "Duplicate SVG IDs")
                for label in root.get("aria-labelledby", "").split():
                    self.assertTrue(root.find(f".//*[@id='{label}']").text)
                self.assertEqual(root.get("aria-labelledby"), "title description")
                text = " ".join(root.itertext())
                for fact in ("Louis", "0xlouiss", "Student Developer", "Self-taught", "Python", "JavaScript", "Rust", "GitHub", "VS Code"):
                    self.assertIn(fact, text)
                for element in root.iter():
                    self.assertNotIn(element.tag, [SVG + t for t in ("script", "foreignObject", "image", "animate", "animateTransform", "animateMotion", "set")])
                    for name, value in element.attrib.items():
                        self.assertFalse(name.lower().startswith("on"), name)
                        if name.endswith("href"):
                            self.assertTrue(value.startswith("#"), value)
                self.assertNotRegex(source, r"<!DOCTYPE|<!ENTITY|@import")
                for reference in re.findall(r"url\(([^)]+)\)", source):
                    self.assertTrue(reference.startswith("#"), reference)
                    self.assertIn(reference[1:], ids)
                css = root.find(SVG + "style").text
                self.assertIn("@media (prefers-reduced-motion: reduce)", css)
                self.assertIn("animation: none !important", css)
                self.assertNotRegex(css, r"https?://")
                self.assertIn("* { animation: none !important", css)
                self.assertEqual(len(root.findall(f".//{SVG}text[@class='ascii-row']")), 50)
                segments = [e for e in root.iter(SVG + "rect") if "language-segment" in e.get("class", "").split()]
                self.assertEqual(len(segments), 3)
                for effect in ("rainFall", "glitchCyan", "wipePass", "cometRun", "equalize", "satelliteOrbit"):
                    self.assertIn("@keyframes " + effect, css)

    def test_personalized_public_and_private_stats(self):
        expected = [1, 52, 65, 2426, 5, 84, 1, 0]
        for theme in ("dark", "light"):
            root = ET.parse(ROOT / f"assets/profile-{theme}.svg").getroot()
            lines = [e for e in root.iter(SVG + "text") if "info-line" in e.get("class", "").split()]
            text = " ".join("".join(e.itertext()) for e in lines)
            self.assertNotIn("shashanthnetha", text)
            self.assertNotIn("NetWorth", text)
            self.assertIn("github.com/0xlouiss", text)
            self.assertNotIn("?", text)
            finals = [e for e in root.iter(SVG + "text") if "counter-final" in e.get("class", "").split()]
            self.assertEqual([int(e.text.replace(",", "")) for e in finals], expected)
            for label in ("Repos", "Commits", "PRs", "Issues"):
                self.assertIn(label + " (public)", text)
                self.assertIn(label + " (private)", text)
            self.assertIn("last 12 months", text)
            self.assertIn("2026-10-22", "".join(root.itertext()))

    def test_avatar_and_glitch_layers_match(self):
        for theme in ("dark", "light"):
            root = ET.parse(ROOT / f"assets/profile-{theme}.svg").getroot()
            portrait = [e for e in root.iter(SVG + "text") if e.get("class") == "ascii-row"]
            self.assertTrue(all(len(e.text) == 100 for e in portrait))
            self.assertIn("cat beside a laptop", root.find(SVG + "desc").text)
            for e in root.iter(SVG + "text"):
                match = re.search(r"ghost-(?:cyan|magenta)-(\d+)\b", e.get("class", ""))
                if match:
                    self.assertEqual(e.text, portrait[int(match.group(1)) - 1].text)

    def test_readme_theme_selection_and_sections(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for theme in ("dark", "light"):
            self.assertIn(f'media="(prefers-color-scheme: {theme})" srcset="assets/profile-{theme}.svg"', readme)
        self.assertIn('src="assets/profile-light.svg"', readme)
        self.assertIn('alt="Louis (@0xlouiss)', readme)
        for heading in ("About Me", "Tech Stack", "GitHub Activity", "Profile Views"):
            self.assertIn("## " + heading, readme)


if __name__ == "__main__":
    unittest.main()
