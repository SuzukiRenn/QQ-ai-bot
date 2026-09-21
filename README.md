# QQ-ai-bot

## Character Engine Framework

一个面向 QQ / 群聊 AI Agent 的可扩展角色引擎。

本项目通过标准化 Character Package，实现：

-   多角色加载
-   角色包自动验证
-   自动发现与注册
-   长期记忆
-   情绪系统
-   关系系统
-   动态 Prompt 构建

## Architecture

``` text
Character Package

card.yaml
lore.yaml
memories.yaml
relationships.yaml
events.yaml
reply_behavior.yaml

        ↓

Character Validator

        ↓

Character Loader

        ↓

Character Manager

        ↓

Runtime

        ↓

Prompt Builder

        ↓

LLM
```

## Character Package

角色目录：

``` text
characters/

└── character_id/

    ├── card.yaml
    ├── lore.yaml
    ├── memories.yaml
    ├── relationships.yaml
    ├── events.yaml
    └── reply_behavior.yaml
```

### card.yaml

定义角色身份：

-   基础信息
-   人格
-   语言风格
-   行为规则
-   角色目标

### lore.yaml

定义角色世界：

-   世界背景
-   世界规则
-   地点
-   文化
-   扩展知识

### memories.yaml

定义角色经历：

``` yaml
emotional_impact:

  nostalgia: 80

  happiness: 50
```

经历会影响角色长期心理倾向。

### relationships.yaml

定义角色世界关系。

不保存用户关系。

### events.yaml

定义重要事件。

事件可以影响角色经历和情绪。

### reply_behavior.yaml

定义角色表达方式：

-   reply_type_behavior
-   relationship_behavior
-   emotion_behavior
-   scene_behavior

## Runtime

启动流程：

``` text
扫描角色目录

↓

Validator 验证

↓

Loader 加载

↓

Manager 注册

↓

Chat Runtime 使用
```

## Validator

验证角色包：

``` bash
python -m bot.validators.package_validator character_id
```

示例：

``` bash
python -m bot.validators.package_validator black_cat
```

## Add New Character

1.  使用：

``` text
docs/CHARACTER_PACKAGE_SPEC.md

docs/CHARACTER_GENERATION_PROMPT.md
```

生成角色包。

2.  放入：

``` text
bot/characters/
```

3.  验证：

``` bash
python -m bot.validators.package_validator new_character
```

4.  启动：

``` bash
python -m bot.main
```

## Installation

创建环境：

``` bash
python -m venv .venv
```

安装依赖：

``` bash
pip install -r requirements.txt
```

## Project Structure

``` text
QQ-ai-bot/

├── bot/

├── characters/

├── docs/

│   ├── CHARACTER_PACKAGE_SPEC.md
│   └── CHARACTER_GENERATION_PROMPT.md

├── requirements.txt

└── README.md
```

## Roadmap

Completed:

-   Character Package System
-   Character Schema v1
-   Package Validator
-   Character Discovery
-   Character Loader
-   Character Manager
-   Memory System
-   Emotion System
-   Relationship System
-   Prompt Builder

Future:

-   Proactive Behavior System
-   Group Conversation Awareness
-   Advanced Memory Retrieval
-   Character Evolution System

## License

MIT
