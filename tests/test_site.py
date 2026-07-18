from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess
import unittest
from urllib.parse import urlparse
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MOBILE_NUMBER = re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")
TEL_SCHEME = "tel" + ":"
VOID_ELEMENTS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}
PUBLICATION_RECORDS = (
    (
        "SHyLA: 3D-Stacked NVM-DRAM Hybrid LLM-Inference Architecture Exploiting Data and Memory Heterogeneity",
        "L. He, F. Zhou, C. Peng, S. Dong, Z. Zhang, H. Yang, Y. Liu, G. Zhang, and H. Jia",
        "53rd ACM/IEEE International Symposium on Computer Architecture (ISCA), 2026",
    ),
    (
        "SASDenSebLE: A Compact Vision Transformer Inference Architecture With Saturation-Approximate Softmax Dataflow Enabling Sequence-Parallelism Boosted Layer-Fusion Execution",
        "L. He, Z. Huang, Y. Wang, S. Fan, C. Tang, S. Zhang, L. Lei, H. Yang, Y. Liu, and H. Jia",
        "IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems (TCAD), 2025",
    ),
    (
        "HyC-LoRA: Memory Efficient LoRA Fine-tuning with Hybrid Activation Compression",
        "Y. Wang, S. Dong, Z. Huang, Y. You, L. He, H. Yang, Y. Liu, and H. Jia",
        "8th Conference on Machine Learning and Systems (MLSys), 2025",
    ),
    (
        "Exploring Approximation and Dataflow Co-Optimization for Scalable Transformer Inference Architecture on the Edge",
        "L. He, Y. Wang, Z. Huang, S. Fan, C. Tang, S. Zhang, L. Lei, H. Yang, Y. Liu, and H. Jia",
        "37th IEEE International System-on-Chip Conference (SOCC), 2024",
    ),
)
EDUCATION_RECORDS = (
    "Tsinghua University Ph.D. in Electronic Science and Technology, September 2023–present Advisor: Associate Professor Hongyang Jia",
    "Tsinghua University B.Eng. in Electronic Engineering, August 2019–June 2023",
)


class SiteHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.end_tags = []
        self.text = []
        self.elements = []
        self._open_elements = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        self.tags.append((tag, attributes))
        if tag not in VOID_ELEMENTS:
            ancestors = tuple(
                (element["tag"], element["attrs"])
                for element in self._open_elements
            )
            self._open_elements.append(
                {"tag": tag, "attrs": attributes, "text": [], "ancestors": ancestors}
            )

    def handle_startendtag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

    def handle_endtag(self, tag):
        self.end_tags.append(tag)
        if self._open_elements and self._open_elements[-1]["tag"] == tag:
            element = self._open_elements.pop()
            text = " ".join("".join(element["text"]).split())
            self.elements.append(
                (element["tag"], element["attrs"], text, element["ancestors"])
            )

    def handle_data(self, data):
        normalized = " ".join(data.split())
        if normalized:
            self.text.append(normalized)
        for element in self._open_elements:
            element["text"].append(data)


def parse_homepage():
    if not INDEX.is_file():
        raise AssertionError("index.html must exist")
    source = INDEX.read_text(encoding="utf-8")
    parser = SiteHTMLParser()
    parser.feed(source)
    parser.close()
    return source, parser, " ".join(parser.text)


def elements_with_class(parser, tag, class_name):
    return [
        element
        for element in parser.elements
        if element[0] == tag
        and class_name in element[1].get("class", "").split()
    ]


class RepositoryPrivacyTests(unittest.TestCase):
    def test_gitignore_excludes_private_and_workflow_sources(self):
        gitignore_path = ROOT / ".gitignore"
        self.assertTrue(gitignore_path.is_file(), ".gitignore must exist")
        ignored = {
            line.strip()
            for line in gitignore_path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        }
        required = {"/CV.pdf", ".worktrees/", ".superpowers/", "docs/superpowers/"}
        missing = required - ignored
        self.assertFalse(missing, f"Missing .gitignore entries: {sorted(missing)}")

    def test_tracked_files_respect_public_privacy_boundary(self):
        result = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=ROOT,
            check=True,
            capture_output=True,
        )
        tracked_paths = [
            path.decode("utf-8")
            for path in result.stdout.split(b"\0")
            if path
        ]
        forbidden_prefixes = (".worktrees/", ".superpowers/", "docs/superpowers/")
        for relative_path in tracked_paths:
            with self.subTest(path=relative_path):
                self.assertNotEqual(relative_path, "CV.pdf")
                self.assertFalse(relative_path.startswith(forbidden_prefixes))

                path = ROOT / relative_path
                if not path.is_file():
                    continue
                try:
                    text = path.read_bytes().decode("utf-8")
                except UnicodeDecodeError:
                    continue
                self.assertIsNone(MOBILE_NUMBER.search(text))
                self.assertNotIn(TEL_SCHEME, text.lower())


class HomepageContentTests(unittest.TestCase):
    def test_document_metadata_and_balanced_sections(self):
        source, parser, _ = parse_homepage()
        html_attributes = [attrs for tag, attrs in parser.tags if tag == "html"]
        self.assertTrue(any(attrs.get("lang") == "en" for attrs in html_attributes))
        self.assertIn(
            "<title>Liu He | Computer Architecture Researcher</title>",
            source,
        )
        descriptions = [
            attrs.get("content", "")
            for tag, attrs in parser.tags
            if tag == "meta" and attrs.get("name") == "description"
        ]
        self.assertTrue(any("Liu He" in description for description in descriptions))
        section_ids = [attrs.get("id") for tag, attrs in parser.tags if tag == "section"]
        self.assertEqual(
            section_ids,
            ["about", "research-interests", "publications", "education"],
        )
        self.assertEqual(sum(tag == "section" for tag, _ in parser.tags), 4)
        self.assertEqual(parser.end_tags.count("section"), 4)
        self.assertEqual(
            sum(tag == "section" for tag, _ in parser.tags),
            parser.end_tags.count("section"),
        )
        self.assertNotIn("<script", source.lower())

    def test_identity_and_public_links(self):
        _, parser, text = parse_homepage()
        self.assertIn("Liu He", text)
        self.assertIn("Ph.D. Student at Tsinghua University", text)
        hrefs = {
            attrs["href"]
            for tag, attrs in parser.tags
            if tag == "a" and "href" in attrs
        }
        required = {
            "mailto:he-l23@mails.tsinghua.edu.cn",
            "https://scholar.google.com/citations?user=Z6jQAUkAAAAJ&hl=en",
            "https://github.com/He-Liu-ooo",
            "https://www.linkedin.com/in/liu-he-ab2730329",
        }
        self.assertTrue(required.issubset(hrefs))

    def test_homepage_stays_within_approved_public_scope(self):
        source, parser, text = parse_homepage()
        hrefs = [
            attrs.get("href", "")
            for tag, attrs in parser.tags
            if tag == "a"
        ]
        checks = {
            "address element": not any(tag == "address" for tag, _ in parser.tags),
            "telephone link": not any(
                TEL_SCHEME in href.lower()
                for href in hrefs
            ),
            "mobile number": MOBILE_NUMBER.search(source) is None,
            "work experience": "Work Experience" not in text,
            "awards": "Awards" not in text,
        }
        for label, allowed in checks.items():
            with self.subTest(boundary=label):
                self.assertTrue(allowed)

    def test_publication_records_are_complete_and_balanced(self):
        _, parser, _ = parse_homepage()
        articles = [
            element
            for element in parser.elements
            if element[0] == "article"
        ]
        self.assertEqual(sum(tag == "article" for tag, _ in parser.tags), 4)
        self.assertEqual(parser.end_tags.count("article"), 4)
        self.assertEqual(
            sum(tag == "article" for tag, _ in parser.tags),
            parser.end_tags.count("article"),
        )
        self.assertEqual(len(articles), 4)
        expected_articles = [" ".join(record) for record in PUBLICATION_RECORDS]
        self.assertEqual([article[2] for article in articles], expected_articles)

    def test_education_contains_only_approved_records(self):
        _, parser, _ = parse_homepage()
        entries = elements_with_class(parser, "div", "education-entry")
        self.assertEqual(len(entries), 2)
        self.assertEqual([entry[2] for entry in entries], list(EDUCATION_RECORDS))

    def test_cv_is_disabled_and_photo_has_alt_text(self):
        _, parser, _ = parse_homepage()
        anchors = [element for element in parser.elements if element[0] == "a"]
        hrefs = [anchor[1].get("href", "") for anchor in anchors]
        self.assertFalse(any("cv" in anchor[2].lower() for anchor in anchors))
        self.assertFalse(
            any(
                not urlparse(href).scheme
                and urlparse(href).path.lower().lstrip("./").startswith("files/cv/")
                for href in hrefs
            )
        )
        self.assertTrue(
            any(
                tag == "span"
                and attrs.get("aria-disabled") == "true"
                and text == "CV (coming soon)"
                and any(
                    ancestor_tag == "nav"
                    and "profile-links" in ancestor_attrs.get("class", "").split()
                    for ancestor_tag, ancestor_attrs in ancestors
                )
                for tag, attrs, text, ancestors in parser.elements
            )
        )
        self.assertTrue(
            any(
                tag == "img" and attrs.get("alt") == "Profile photo placeholder for Liu He"
                for tag, attrs in parser.tags
            )
        )


class PresentationAndResourceTests(unittest.TestCase):
    def test_stylesheet_is_responsive_accessible_and_self_contained(self):
        stylesheet_path = ROOT / "styles.css"
        self.assertTrue(stylesheet_path.is_file(), "styles.css must exist")
        stylesheet = stylesheet_path.read_text(encoding="utf-8")
        for required_rule in ("@media", ":focus-visible", "max-width"):
            with self.subTest(rule=required_rule):
                self.assertIn(required_rule, stylesheet)
        self.assertNotIn("http://", stylesheet)
        self.assertNotIn("https://", stylesheet)

    def test_all_local_homepage_resources_exist(self):
        _, parser, _ = parse_homepage()
        local_paths = []
        for tag, attrs in parser.tags:
            attribute = "href" if tag == "link" else "src" if tag == "img" else None
            if attribute is None or attribute not in attrs:
                continue
            resource = attrs[attribute]
            parsed = urlparse(resource)
            if not parsed.scheme and not resource.startswith("//"):
                local_paths.append(parsed.path)

        self.assertTrue(local_paths, "homepage must reference local resources")
        for local_path in local_paths:
            with self.subTest(path=local_path):
                self.assertTrue((ROOT / local_path).is_file())

    def test_profile_placeholder_is_accessible(self):
        placeholder_path = ROOT / "files/profile/profile-placeholder.svg"
        self.assertTrue(placeholder_path.is_file(), "profile placeholder must exist")
        source = placeholder_path.read_text(encoding="utf-8")
        self.assertIn("<title", source)
        root = ET.parse(placeholder_path).getroot()
        title = root.find("{http://www.w3.org/2000/svg}title")
        self.assertIsNotNone(title)
        self.assertEqual(title.text, "Liu He profile photo placeholder")

    def test_public_download_locations_exist(self):
        for relative_path in (
            "files/cv/.gitkeep",
            "files/papers/.gitkeep",
            "files/slides/.gitkeep",
        ):
            with self.subTest(path=relative_path):
                self.assertTrue((ROOT / relative_path).is_file())


if __name__ == "__main__":
    unittest.main()
