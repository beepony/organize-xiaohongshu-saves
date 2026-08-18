from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "skill" / "organize-xiaohongshu-saves"


class SkillStructureTest(unittest.TestCase):
    def test_frontmatter_and_name(self) -> None:
        text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        frontmatter = text.split("---", 2)[1]
        names = re.findall(r"^name:\s*(.+)$", frontmatter, re.MULTILINE)
        descriptions = re.findall(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
        self.assertEqual(names, [SKILL_DIR.name])
        self.assertEqual(len(descriptions), 1)
        self.assertGreater(len(descriptions[0]), 40)
        keys = re.findall(r"^([a-z_]+):", frontmatter, re.MULTILINE)
        self.assertEqual(keys, ["name", "description"])

    def test_agent_metadata_mentions_skill(self) -> None:
        metadata = (SKILL_DIR / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn(f"${SKILL_DIR.name}", metadata)

    def test_referenced_files_exist(self) -> None:
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        references = re.findall(r"\]\((references/[^)]+)\)", skill)
        self.assertTrue(references)
        for reference in references:
            self.assertTrue((SKILL_DIR / reference).is_file(), reference)


if __name__ == "__main__":
    unittest.main()
