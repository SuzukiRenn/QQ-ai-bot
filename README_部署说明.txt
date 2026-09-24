QQ-ai-bot Dialogue Style System v1
日期：2026-09-22

目标：
降低角色回复的“AI味”，把“角色事实 / 行为规则 / 语言风格示范”分层。

新增：
- bot/dialogue_retriever.py
- bot/dialogue_formatter.py
- bot/validators/dialogue_validator.py
- tests/test_dialogue_style.py
- 各角色 dialogue_examples.yaml

修改：
- bot/character_loader.py
- bot/ai.py
- bot/chat_service.py
- bot/prompt.py
- bot/proactive_prompt.py
- bot/validators/package_validator.py
- docs/CHARACTER_PACKAGE_SPEC.md

兼容性：
- dialogue_examples.yaml 为可选扩展；旧 Character Package v1.1 没有该文件时仍可加载。
- 当前五个角色都附带 anti_patterns。
- 豆馅馒头附带 6 条 synthetic_style_example，用于验证整个风格检索链路。
- black_cat / maomao / murasame / furina 暂未伪造“官方台词”；后续应使用经整理的真实台词或人工风格样本填充 examples。

当前本地验证：
- py_compile 通过
- 5 个角色 package_validator 全部通过
- Dialogue Style + Prompt + Proactive 相关测试：20/20 通过
