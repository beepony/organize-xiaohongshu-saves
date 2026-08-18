from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "skill" / "organize-xiaohongshu-saves" / "scripts" / "xhs_project.py"


class ProjectCliTest(unittest.TestCase):
    def run_cli(self, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            check=check,
            text=True,
            capture_output=True,
        )

    def test_complete_project_and_generated_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = root / "project"
            self.run_cli(
                "init",
                "--project",
                str(project),
                "--source-type",
                "album",
                "--source-name",
                "示例专辑",
                "--limit",
                "2",
                "--field",
                "地址",
                "--field",
                "停车",
                "--output-title",
                "示例报告",
            )

            template = root / "item-001.json"
            self.run_cli(
                "template",
                "--project",
                str(project),
                "--order",
                "1",
                "--output",
                str(template),
            )
            self.assertEqual(json.loads(template.read_text(encoding="utf-8"))["decision"], "pending")

            included = {
                "order": 1,
                "title": "示例地点",
                "decision": "include",
                "decision_reason": "与主题相关",
                "media_reviewed": ["caption", "image-1"],
                "records": [
                    {
                        "name": "示例地点",
                        "fields": {
                            "地址": {
                                "value": "示例入口",
                                "evidence": "图片 1",
                                "confidence": "confirmed",
                            },
                            "停车": {
                                "value": "原帖未提及",
                                "evidence": "已检查正文和图片",
                                "confidence": "not-mentioned",
                            },
                        },
                    }
                ],
            }
            template.write_text(json.dumps(included, ensure_ascii=False), encoding="utf-8")
            self.run_cli("upsert", "--project", str(project), "--item-file", str(template))

            excluded_path = root / "item-002.json"
            excluded_path.write_text(
                json.dumps(
                    {
                        "order": 2,
                        "title": "无关内容",
                        "decision": "exclude",
                        "decision_reason": "与主题无关",
                        "media_reviewed": ["caption"],
                        "records": [],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            self.run_cli("upsert", "--project", str(project), "--item-file", str(excluded_path))

            validation = self.run_cli("validate", "--project", str(project))
            status = json.loads(validation.stdout)
            self.assertTrue(status["complete"])
            self.assertEqual(status["included_records"], 1)
            self.assertEqual(status["excluded_sources"], 1)
            self.assertIn("示例地点", (project / "report.md").read_text(encoding="utf-8"))

            with (project / "included.csv").open(encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(rows[0]["地址"], "示例入口")

    def test_invalid_confidence_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = root / "project"
            self.run_cli(
                "init",
                "--project",
                str(project),
                "--source-type",
                "favorites",
                "--source-name",
                "示例",
                "--limit",
                "1",
                "--field",
                "地址",
            )
            item = root / "invalid.json"
            item.write_text(
                json.dumps(
                    {
                        "order": 1,
                        "title": "示例",
                        "decision": "include",
                        "records": [
                            {
                                "name": "示例",
                                "fields": {
                                    "地址": {
                                        "value": "示例入口",
                                        "evidence": "正文",
                                        "confidence": "guessed",
                                    }
                                },
                            }
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            result = self.run_cli(
                "upsert",
                "--project",
                str(project),
                "--item-file",
                str(item),
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("confidence must be one of", result.stderr)


if __name__ == "__main__":
    unittest.main()
