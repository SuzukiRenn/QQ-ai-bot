# Character Package Specification v1

版本：

v1.1


## 1. 概述

Character Package 是 QQ-ai-bot Character Engine 的角色定义标准。

一个角色由：

- 身份
- 世界观
- 经历
- 关系
- 行为模式

共同组成。


角色包只负责：

> 定义角色是谁，以及角色过去经历。


运行时状态：

- 当前情绪
- 用户关系
- 用户记忆

由 Runtime 系统管理。

禁止写入角色包。



---

# 2. 目录结构


characters/

└── character_id/

    ├── card.yaml

    ├── lore.yaml

    ├── memories.yaml

    ├── relationships.yaml

    ├── events.yaml

    └── reply_behavior.yaml



---

# 3. card.yaml

作用：

定义角色身份和人格。



结构：


```yaml
character:

  meta:

    id:
    name:
    nickname:
    description:


  identity:

    species:
    gender:
    age:
    occupation:
    background:


  personality:

    core_traits:

      -


    values:

      -


    weaknesses:

      -


    fears:

      -


  speech_style:

    tone:

      -


    habits:

      -


    forbidden:

      -


  behavior:

    praised:


    teased:


    angry:


    sad:


  goals:

    short_term:


    long_term:

 ---

# 4. lore.yaml

作用：

定义角色所在世界。

结构：

world:

  name:

  description:


rules:

  -


locations:


  location_id:

    description:


culture:

  description:


knowledge:

5. memories.yaml

作用：

定义角色经历。

这些经历会影响长期心理。

结构：

memories:


  - id:


    title:


    description: |



    tags:

      -


    emotional_impact:


      emotion_name: value


    importance:

      high
      medium
      low

说明：

emotional_impact 会进入 Emotion Engine。

例如：

emotional_impact:

  nostalgia:80

  happiness:50

表示：

该经历增强：

怀念
开心
6. relationships.yaml

作用：

定义角色世界中的固定人物关系。

注意：

这里不是用户关系。

用户关系由 Runtime 管理。

结构：

characters:


  character_id:


    name:


    relationship:


    attitude:


    history:

7. events.yaml

作用：

定义重要事件。

结构：

events:


  - id:


    title:


    description:


    tags:


      -


    importance:


    emotional_impact:


      emotion:value

8. reply_behavior.yaml

作用：

定义角色表达方式。

结构：

reply_behavior:


  reply_type_behavior:


    answer:


      description:


      rules:

        -


    chat:


    tease:


    comfort:


    greet:


    share:


    ignore:




  relationship_behavior:


    stranger:


    acquaintance:


    friend:


    close_friend:




  emotion_behavior:


    neutral:


    happy:


    angry:


    sad:


    embarrassed:




  scene_behavior:


    group_chat:


    private_chat:


  proactive:

    enabled: true

    min_context_messages: 2

    min_join_probability: 0.65

    cooldown_seconds: 120

### proactive

作用：

定义角色在群聊中的主动参与倾向。

该字段属于 Character Package v1.1 新增字段。

为了兼容 v1.0 角色：

proactive 为可选字段。

如果角色包没有 proactive，
Runtime 使用默认主动行为参数。


字段说明：

enabled:

是否允许角色主动参与群聊。

类型：

boolean


min_context_messages:

角色开始考虑主动发言前，
至少需要观察到的群成员消息数量。

注意：

只统计 sender_type=user 的消息。

角色自己发送的消息不计入。


min_join_probability:

Scene Analyzer 判断当前场景适合角色加入的最低概率。

范围：

0.0 - 1.0


cooldown_seconds:

角色实际发送消息后，
再次主动发言前需要等待的时间。

单位：

秒。


示例：

proactive:

  enabled: true

  min_context_messages: 2

  min_join_probability: 0.65

  cooldown_seconds: 120

9. Schema 原则
角色定义和运行状态分离

禁止：

card.yaml:

trust:80

原因：

trust 属于：

用户关系状态。

应该：

relationship runtime:

character_id:user_id

禁止：

memory:

current_happiness:80

原因：

当前情绪不是角色经历。

10. 新角色生成要求

使用大模型生成角色时：

必须输出：

character_id/

card.yaml

lore.yaml

memories.yaml

relationships.yaml

events.yaml

reply_behavior.yaml

生成后必须通过：

Character Package Validator。

11. 版本规则

当前版本：

Character Package v1

未来修改：

v1.x:

增加字段，不破坏旧角色。

Character Package v1.1：

新增：

reply_behavior.proactive

该字段为可选字段，
不会破坏 v1.0 角色包兼容性。

v2:

重大结构变化。
---

# 8. dialogue_examples.yaml（可选，Dialogue Style System v1）

作用：

定义角色“怎么说话”的语言示范与需要避免的 AI 式表达习惯。

它与 lore / memories 的职责不同：

- lore / memories：提供角色知道的事实、经历与记忆。
- reply_behavior：规定角色在不同情况下采取什么行为。
- dialogue_examples：只提供语言风格示范，不提供新的事实。

该文件是可选扩展。旧的 Character Package v1.1 即使没有该文件也必须继续可用。

推荐结构：

```yaml
dialogue_style:

  anti_patterns:
    - 不要先复述用户刚说过的话再回应
    - 普通聊天不要习惯性总结

  examples:
    - id: example_001
      source: canonical_or_synthetic

      reply_type:
        - chat

      emotion:
        - happy

      scene:
        - group_chat

      relationship:
        - friend

      keywords:
        - 示例关键词

      situation: |
        这句话通常出现在什么语境。

      style_tags:
        - 短句
        - 反问

      text: |
        角色语言示范。
```

字段说明：

- `id`：唯一 ID，必填。
- `text`：语言示范，必填。
- `reply_type`：适合 answer / chat / tease / comfort / greet / share 等回复模式。
- `emotion`：适合的情绪。
- `scene`：适合的场景，例如 group_chat / private_chat / funny / serious。
- `relationship`：适合的关系等级。
- `keywords`：消息中出现这些词时提高该示范的检索分数。
- `situation`：对示范语境的说明。
- `style_tags`：用于说明表达特征，不作为世界观事实。
- `anti_patterns`：该角色需要避免的高频 AI 式表达习惯。

运行时原则：

1. 只检索少量最匹配示范，默认最多 4 条。
2. `reply_type` 是强约束，不把 tease 示例错误注入 answer。
3. 示例只用于学习语言风格，不得继承其中的人物、事件、地点或经历。
4. 不直接复述或近似照抄示范台词。
5. 角色事实、当前消息和真实聊天上下文始终高于语言示范。
