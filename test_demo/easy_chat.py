#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单的 DeepSeek API Chat Agent（带 Skill 加载）

使用 OpenAI 兼容格式访问 DeepSeek API，支持多轮对话、流式输出和两层 Skill 加载。

Layer 1: skill 摘要注入 system prompt（廉价）
Layer 2: 模型调用 load_skill tool 时返回完整 body（按需）

使用前:
  1. pip install openai python-dotenv pyyaml
  2. 在本目录下创建 .env 文件，填入: DEEPSEEK_API_KEY=your-api-key
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

from skills_loader import SkillLoader

BASE_URL = "https://api.deepseek.com"
MODEL = "deepseek-v4-flash"

# load_skill tool 定义（OpenAI function calling 格式）
LOAD_SKILL_TOOL = {
    "type": "function",
    "function": {
        "name": "load_skill",
        "description": (
            "加载指定 skill 的完整内容。当你需要处理 PDF、PPT、"
            "代码审查等专业任务时，先调用此工具获取详细指引。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "要加载的 skill 名称",
                }
            },
            "required": ["name"],
        },
    },
}


def create_client(api_key: str) -> OpenAI:
    """创建 OpenAI 兼容客户端。"""
    return OpenAI(api_key=api_key, base_url=BASE_URL)


def build_system_prompt(skill_loader: SkillLoader) -> str:
    """构建 system prompt，注入 Layer 1 skill 摘要。"""
    summary = skill_loader.skill_summary()
    return (
        "你是一个有帮助的AI助手，请用中文回答问题。\n\n"
        "你可以使用以下专业技能（调用 load_skill 加载详细指引）：\n"
        f"{summary}\n\n"
        "当用户的问题涉及上述技能时，请先调用 load_skill 获取详细步骤，"
        "然后按照步骤执行。"
    )


def handle_tool_calls(
    client: OpenAI,
    messages: list,
    tool_calls: list,
    skill_loader: SkillLoader,
) -> Optional[str]:
    """处理模型返回的 tool_calls，返回最终文本回复或 None。"""
    for tool_call in tool_calls:
        func_name = tool_call.function.name
        func_args = json.loads(tool_call.function.arguments)

        if func_name == "load_skill":
            skill_name = func_args.get("name", "")
            content = skill_loader.get_content(skill_name)
            print(f"  [加载技能: {skill_name}]")
        else:
            content = f"未知工具: {func_name}"

        # 将 tool_result 追加到消息列表
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": content,
        })

    # 带上 tool_result 再请求一次，让模型生成最终回复
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        stream=False,
    )
    return response.choices[0].message.content or ""


def chat(
    client: OpenAI,
    messages: list,
    skill_loader: SkillLoader,
) -> str:
    """调用 DeepSeek Chat API，支持流式输出和 tool calling。"""
    # 第一步：发送请求，开启 tool 支持
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=[LOAD_SKILL_TOOL],
        stream=False,
    )

    message = response.choices[0].message

    # 如果模型调用了 tool，处理 tool_calls 后再请求最终回复
    if message.tool_calls:
        messages.append(message)
        final_reply = handle_tool_calls(
            client, messages, message.tool_calls, skill_loader
        )
        print(final_reply)
        return final_reply

    # 普通回复，直接返回
    content = message.content or ""
    print(content)
    return content


def main():
    """主入口：加载配置、初始化 skill、运行交互循环。"""
    load_dotenv(Path(__file__).resolve().parent / ".env")

    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("请在 test_demo/.env 中设置 DEEPSEEK_API_KEY")
        print("  DEEPSEEK_API_KEY=your-api-key")
        sys.exit(1)

    client = create_client(api_key)

    # 初始化 SkillLoader（Layer 1: 摘要注入 system prompt）
    skill_loader = SkillLoader(
        Path(__file__).resolve().parent / "skills"
    )
    system_prompt = build_system_prompt(skill_loader)

    messages = [{"role": "system", "content": system_prompt}]

    skills_list = ", ".join(skill_loader.list_skills()) or "无"
    print(f"DeepSeek Chat Agent (模型: {MODEL})")
    print(f"已加载技能: {skills_list}")
    print("输入 'quit' 或 'exit' 退出，输入 'clear' 清空对话历史\n")

    while True:
        try:
            user_input = input("你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("再见!")
            break
        if user_input.lower() == "clear":
            messages = [messages[0]]
            print("已清空对话历史\n")
            continue

        messages.append({"role": "user", "content": user_input})

        print("AI: ", end="", flush=True)
        try:
            reply = chat(client, messages, skill_loader)
        except Exception as e:
            print(f"\n[错误] {e}")
            messages.pop()
            continue

        messages.append({"role": "assistant", "content": reply})
        print()  # 换行


if __name__ == "__main__":
    main()
