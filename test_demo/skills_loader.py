#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
skills_loader.py - 两层 Skill 加载器

Layer 1 (廉价): skill 元数据注入 system prompt (~100 token/skill)
Layer 2 (按需): 模型调用 load_skill tool 时返回完整 body

skills/
  pdf/
    SKILL.md   <-- YAML frontmatter (name, description, tags) + body
  code-review/
    SKILL.md
"""

import re
from pathlib import Path
from typing import Dict, Optional


class SkillLoader:
    """扫描 skills/ 目录下的 SKILL.md，提供两层加载能力。"""

    def __init__(self, skills_dir: Path):
        self.skills_dir = skills_dir
        self.skills: Dict[str, dict] = {}
        self._load_all()

    def _load_all(self):
        """启动时扫描所有 SKILL.md 文件。"""
        if not self.skills_dir.exists():
            return
        for f in sorted(self.skills_dir.rglob("SKILL.md")):
            text = f.read_text(encoding="utf-8")
            meta, body = self._parse_frontmatter(text)
            name = meta.get("name", f.parent.name)
            self.skills[name] = {"meta": meta, "body": body, "path": str(f)}

    @staticmethod
    def _parse_frontmatter(text: str) -> tuple:
        """解析 YAML frontmatter 和 body，以 --- 分隔。"""
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", text, re.DOTALL)
        if not match:
            return {}, text
        import yaml
        try:
            meta = yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError:
            meta = {}
        return meta, match.group(2).strip()

    def skill_summary(self) -> str:
        """Layer 1: 返回所有 skill 的摘要，用于注入 system prompt。"""
        if not self.skills:
            return "(no skills available)"
        lines = []
        for name, skill in self.skills.items():
            desc = skill["meta"].get("description", "No description")
            tags = skill["meta"].get("tags", "")
            line = f" - {name}: {desc}"
            if tags:
                line += f" [{tags}]"
            lines.append(line)
        return "\n".join(lines)

    def get_content(self, name: str) -> str:
        """Layer 2: 返回指定 skill 的完整 body，用于 tool_result。"""
        skill = self.skills.get(name)
        if not skill:
            available = ", ".join(self.skills.keys())
            return f"Error: Unknown skill '{name}'. Available: {available}"
        return f"\n{skill['body']}\n"

    def list_skills(self) -> list:
        """返回所有已注册的 skill 名称。"""
        return list(self.skills.keys())


if __name__ == "__main__":
    # 简单测试：打印当前 skills 目录下的摘要
    loader = SkillLoader(Path(__file__).resolve().parent / "skills")
    print("=== Skill Summary (Layer 1) ===")
    print(loader.skill_summary())
    print()
    for name in loader.list_skills():
        print(f"=== {name} Content (Layer 2) ===")
        print(loader.get_content(name)[:200])
        print("...")
        print()
