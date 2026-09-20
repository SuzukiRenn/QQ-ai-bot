# Character Package Specification v1

版本：

v1.0


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

v2:

重大结构变化。