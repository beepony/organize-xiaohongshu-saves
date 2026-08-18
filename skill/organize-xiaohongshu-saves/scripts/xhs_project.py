#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VERSION = "1.1.0"
DECISIONS = {"include", "exclude", "pending"}
CONFIDENCE = {
    "confirmed",
    "author-comment",
    "comment-only",
    "conflicting",
    "not-mentioned",
    "image-unreadable",
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def stringify(value: Any) -> str:
    if isinstance(value, list):
        return "；".join(stringify(item) for item in value)
    if isinstance(value, bool):
        return "是" if value else "否"
    if value is None:
        return ""
    return str(value)


def project_paths(project_dir: Path) -> tuple[Path, Path]:
    return project_dir / "project.json", project_dir / "items.json"


def load_project(project_dir: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    config_path, items_path = project_paths(project_dir)
    if not config_path.exists():
        raise SystemExit(f"Project not initialized: {project_dir}")
    config = read_json(config_path)
    items = read_json(items_path) if items_path.exists() else []
    return config, items


def validate_item(item: dict[str, Any], config: dict[str, Any], final: bool = False) -> list[str]:
    errors: list[str] = []
    order = item.get("order")
    if not isinstance(order, int) or not 1 <= order <= config["limit"]:
        errors.append(f"order must be 1..{config['limit']}")
    decision = item.get("decision")
    if decision not in DECISIONS:
        errors.append(f"decision must be one of {sorted(DECISIONS)}")
    if final and decision == "pending":
        errors.append("decision is still pending")
    if not str(item.get("title", "")).strip():
        errors.append("title is required")
    if decision == "exclude" and not str(item.get("decision_reason", "")).strip():
        errors.append("excluded item requires decision_reason")
    records = item.get("records", [])
    if decision == "include" and not records:
        errors.append("included item requires at least one record")
    for record_index, record in enumerate(records, 1):
        if not str(record.get("name", "")).strip():
            errors.append(f"record {record_index}: name is required")
        fields = record.get("fields", {})
        for label in config["fields"]:
            if label not in fields:
                errors.append(f"record {record_index}: missing field {label!r}")
                continue
            field = fields[label]
            if not isinstance(field, dict):
                errors.append(f"record {record_index}/{label}: must be an object")
                continue
            if stringify(field.get("value")).strip() == "":
                errors.append(f"record {record_index}/{label}: value is empty")
            if not str(field.get("evidence", "")).strip():
                errors.append(f"record {record_index}/{label}: evidence is required")
            if field.get("confidence") not in CONFIDENCE:
                errors.append(
                    f"record {record_index}/{label}: confidence must be one of {sorted(CONFIDENCE)}"
                )
    return errors


def write_report(project_dir: Path, config: dict[str, Any], items: list[dict[str, Any]]) -> None:
    ordered = sorted(items, key=lambda value: value["order"])
    included = [item for item in ordered if item.get("decision") == "include"]
    excluded = [item for item in ordered if item.get("decision") == "exclude"]
    pending = [item for item in ordered if item.get("decision") == "pending"]
    record_count = sum(len(item.get("records", [])) for item in included)

    lines = [
        f"# {config['output_title']}",
        "",
        f"> 来源：{config['source_type']}｜{config['source_name']}",
        f"> 目标：审阅前 {config['limit']} 条；当前已记录 {len(ordered)} 条",
        f"> 结果：{record_count} 个保留记录，{len(excluded)} 条排除，{len(pending)} 条待处理",
        "",
        "## 筛选规则",
        "",
        f"- 保留：{config.get('include_filter') or '按用户要求'}",
        f"- 排除：{config.get('exclude_filter') or '按用户要求'}",
        "- 信息缺失时不猜测，使用统一缺失标记。",
        "",
        "## 整理结果",
        "",
    ]

    for item in included:
        for record in item.get("records", []):
            lines.extend(
                [
                    f"### {record['name']}",
                    "",
                    f"来源条目：第 {item['order']} 条《{item['title']}》",
                    "",
                ]
            )
            if item.get("url"):
                lines.extend([f"原帖：{item['url']}", ""])
            for label in config["fields"]:
                field = record["fields"][label]
                value = stringify(field["value"])
                lines.extend(
                    [
                        f"#### {label}",
                        "",
                        value,
                        "",
                        f"_依据：{field['evidence']}；状态：{field['confidence']}_",
                        "",
                    ]
                )
            notes = record.get("notes", [])
            if notes:
                lines.extend(["#### 补充说明", ""])
                lines.extend(f"- {stringify(note)}" for note in notes)
                lines.append("")

    lines.extend(["## 已排除的来源条目", ""])
    if excluded:
        for item in excluded:
            lines.append(f"- 第 {item['order']} 条《{item['title']}》：{item['decision_reason']}")
    else:
        lines.append("- 暂无")
    lines.append("")

    if pending or len(ordered) < config["limit"]:
        present = {item["order"] for item in ordered}
        missing = [str(order) for order in range(1, config["limit"] + 1) if order not in present]
        lines.extend(["## 未完成", ""])
        if pending:
            lines.append("- 待处理：" + "、".join(str(item["order"]) for item in pending))
        if missing:
            lines.append("- 尚未记录：" + "、".join(missing))
        lines.append("")

    (project_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")

    included_csv = project_dir / "included.csv"
    with included_csv.open("w", encoding="utf-8-sig", newline="") as handle:
        fieldnames = ["source_order", "source_title", "source_url", "record_name", *config["fields"]]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for item in included:
            for record in item.get("records", []):
                row = {
                    "source_order": item["order"],
                    "source_title": item["title"],
                    "source_url": item.get("url", ""),
                    "record_name": record["name"],
                }
                for label in config["fields"]:
                    row[label] = stringify(record["fields"][label]["value"])
                writer.writerow(row)

    with (project_dir / "excluded.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["source_order", "source_title", "reason", "source_url"])
        writer.writeheader()
        for item in excluded:
            writer.writerow(
                {
                    "source_order": item["order"],
                    "source_title": item["title"],
                    "reason": item.get("decision_reason", ""),
                    "source_url": item.get("url", ""),
                }
            )


def command_init(args: argparse.Namespace) -> None:
    project_dir = Path(args.project).resolve()
    project_dir.mkdir(parents=True, exist_ok=True)
    config_path, items_path = project_paths(project_dir)
    if config_path.exists() and not args.force:
        raise SystemExit(f"Project already exists: {project_dir}; pass --force to replace it")
    fields = list(dict.fromkeys(args.field))
    if not fields:
        raise SystemExit("At least one --field is required")
    config = {
        "schema_version": 1,
        "source_type": args.source_type,
        "source_name": args.source_name,
        "limit": args.limit,
        "fields": fields,
        "include_filter": args.include,
        "exclude_filter": args.exclude,
        "not_mentioned_label": args.not_mentioned_label,
        "output_title": args.output_title,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    atomic_json(config_path, config)
    atomic_json(items_path, [])
    write_report(project_dir, config, [])
    print(project_dir)


def command_upsert(args: argparse.Namespace) -> None:
    project_dir = Path(args.project).resolve()
    config, items = load_project(project_dir)
    item = read_json(Path(args.item_file))
    errors = validate_item(item, config, final=False)
    if errors:
        raise SystemExit("Invalid item:\n- " + "\n- ".join(errors))
    by_order = {existing["order"]: existing for existing in items}
    by_order[item["order"]] = item
    updated = [by_order[key] for key in sorted(by_order)]
    atomic_json(project_dir / "items.json", updated)
    write_report(project_dir, config, updated)
    print(json.dumps(status_payload(config, updated), ensure_ascii=False))


def status_payload(config: dict[str, Any], items: list[dict[str, Any]]) -> dict[str, Any]:
    present = {item["order"] for item in items}
    included = [item for item in items if item.get("decision") == "include"]
    excluded = [item for item in items if item.get("decision") == "exclude"]
    pending = [item for item in items if item.get("decision") == "pending"]
    missing = [order for order in range(1, config["limit"] + 1) if order not in present]
    return {
        "target_sources": config["limit"],
        "reviewed_sources": len(items),
        "included_sources": len(included),
        "included_records": sum(len(item.get("records", [])) for item in included),
        "excluded_sources": len(excluded),
        "pending_orders": [item["order"] for item in pending],
        "missing_orders": missing,
        "complete": not pending and not missing,
    }


def command_status(args: argparse.Namespace) -> None:
    config, items = load_project(Path(args.project).resolve())
    print(json.dumps(status_payload(config, items), ensure_ascii=False, indent=2))


def command_template(args: argparse.Namespace) -> None:
    project_dir = Path(args.project).resolve()
    config, _ = load_project(project_dir)
    if not 1 <= args.order <= config["limit"]:
        raise SystemExit(f"--order must be 1..{config['limit']}")
    item = {
        "order": args.order,
        "title": "",
        "url": "",
        "author": "",
        "published_at": "",
        "decision": "pending",
        "decision_reason": "",
        "media_reviewed": [],
        "records": [],
        "source_notes": [],
        "reviewed_at": "",
    }
    rendered = json.dumps(item, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output = Path(args.output).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        print(output)
    else:
        print(rendered, end="")


def command_build(args: argparse.Namespace) -> None:
    project_dir = Path(args.project).resolve()
    config, items = load_project(project_dir)
    write_report(project_dir, config, items)
    print(project_dir / "report.md")


def command_validate(args: argparse.Namespace) -> None:
    project_dir = Path(args.project).resolve()
    config, items = load_project(project_dir)
    errors: list[str] = []
    present = {item["order"] for item in items}
    for order in range(1, config["limit"] + 1):
        if order not in present:
            errors.append(f"missing source order {order}")
    for item in items:
        for error in validate_item(item, config, final=True):
            errors.append(f"order {item.get('order', '?')}: {error}")
    if errors:
        raise SystemExit("Validation failed:\n- " + "\n- ".join(errors))
    write_report(project_dir, config, items)
    print(json.dumps(status_payload(config, items), ensure_ascii=False, indent=2))


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Checkpoint and report Xiaohongshu saved-post review projects")
    root.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    sub = root.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init")
    init.add_argument("--project", required=True)
    init.add_argument("--source-type", choices=["likes", "favorites", "album"], required=True)
    init.add_argument("--source-name", required=True)
    init.add_argument("--limit", type=int, required=True)
    init.add_argument("--field", action="append", default=[])
    init.add_argument("--include", default="")
    init.add_argument("--exclude", default="")
    init.add_argument("--not-mentioned-label", default="原帖未提及")
    init.add_argument("--output-title", default="小红书收藏整理")
    init.add_argument("--force", action="store_true")
    init.set_defaults(func=command_init)

    upsert = sub.add_parser("upsert")
    upsert.add_argument("--project", required=True)
    upsert.add_argument("--item-file", required=True)
    upsert.set_defaults(func=command_upsert)

    status = sub.add_parser("status")
    status.add_argument("--project", required=True)
    status.set_defaults(func=command_status)

    template = sub.add_parser("template")
    template.add_argument("--project", required=True)
    template.add_argument("--order", type=int, required=True)
    template.add_argument("--output")
    template.set_defaults(func=command_template)

    build = sub.add_parser("build")
    build.add_argument("--project", required=True)
    build.set_defaults(func=command_build)

    validate = sub.add_parser("validate")
    validate.add_argument("--project", required=True)
    validate.set_defaults(func=command_validate)
    return root


def main() -> None:
    args = parser().parse_args()
    if getattr(args, "limit", 1) < 1:
        raise SystemExit("--limit must be a positive integer")
    args.func(args)


if __name__ == "__main__":
    main()
