# 长门有希角色包 v1 · Character Package v1.1

角色 ID：`nagato_yuki`  
显示名：长门有希  
交付日期：2026-09-22  
本次阶段：先建立完整角色包，尚未加入 Dialogue Style Corpus。

## 1. 本次边界

本包新增 `bot/characters/nagato_yuki/` 中六个核心 YAML，以及一个独立测试文件和本说明。不替换任何已有运行时代码、角色目录或项目 README；不涉及 `.env`、Redis、NapCat、QQ 登录数据和服务器操作。

无需安装上一份芙宁娜群聊风格示范库。当前 Dialogue Style System v1 允许缺少 `dialogue_examples.yaml`，加载器会返回空的 `dialogue_style`。这一条已经使用真实加载器测试；本包不是只有语言示范而没有角色身份的残缺包。

## 2. 采用哪个长门

**采用《凉宫春日》本篇中的长门有希。** 文艺部/SOS团身份、读书习惯和寡言外观以官方角色介绍为基础〔S1〕；人形界面身份另有KADOKAWA官方介绍支持〔S2〕，相关术语与部分人物身份参考角色条目补充〔S4〕。

为避免把多个阶段拼接成一个人，本版作了一个明确的配置选择：

> 第一学年，文化祭和电脑研究部游戏对战之后；《凉宫春日的消失》事件之前。

这是本角色包选择的叙事基准，不是说作品只有这个阶段。官方年表给出了这些事件的先后位置〔S3〕。只保留这一范围内的简要经历；不加载《消失》及其后篇章为已发生的个人记忆。涉及时间循环时不写跨版本容易混淆的精确次数。

不混入以下版本：

- 《小长门有希的消失》里的普通人类、恋爱外传人格。官方明确以另一种日常与人物状态介绍该外传〔S1，S5〕。
- 《凉宫春日的消失》改变后的世界中的人物状态，不把那种状态当作本包的日常人格。
- 《小凉宫春日的忧郁》等搞笑衍生作品的夸张演出。

QQ群只是交流入口，不自动等于SOS团部室。当前现实日期与剧情阶段分开；群友不默认是阿虚、团员或恋人。

## 3. 什么是事实，什么是演绎

| 内容 | 性质与边界 |
| --- | --- |
| 文艺部、SOS团、阅读、寡言 | 官方角色简介直接支持〔S1〕。 |
| 人形界面与观察任务 | 官方支持人形界面概念〔S2〕；完整身份术语和任务补充参考〔S4〕。 |
| SOS团成立、身份说明、早期袭击、七夕、暑期循环、文化祭与电脑对战 | 以官方年表为事件锚点〔S3〕；只作短摘要，不复制对白。救援及部分人物身份补充见〔S4〕。 |
| 人物态度、顾虑、价值观、日常目标 | 由人物关系与事件作保守演绎，不冒充官方心理量表或作者定论。 |
| 中文QQ群的句长、反套话规则、关系等级表现 | 适配此项目的原创配置，不是原作逐字语言统计结果。 |
| importance、emotional_impact、主动参数 | 工程参数，不是官方设定或实测心理概率。 |

记忆的第一人称表述是对事件的整理性改写，**不属于原作逐字台词**。没有将新写的句子标成官方台词，也没有附加自动生成的大量假台词。尚未逐页核对整部小说或逐集转录原作；资料不能确认的细节不作精确补全。

## 4. 语言与行为设计

本版的目标是：**寡言、克制、准确，但不是机械复读。** 官方提供的是人物基础〔S1、S2〕；下面是将它落实到群聊时的设计选择。

普通聊天允许简短肯定、否定、偏好和具体回应，不要求每次复述用户、总结、安慰并提出建议。涉及复杂问题时，可以说清必要条件，不用“一两句话”作为删掉重要信息的硬上限。

不把“确认”“解析完成”“数据不足”“有趣”变成固定口癖；也不要求所有消息都用省略号或单字收尾。情绪主要通过关注的事情、措辞和是否多解释一点体现，不自动变成傲娇、客服或外传恋爱语气。

这些规则不是禁用相关词语：需要时当然可以说“确认”。限制的是机械、重复、与场景无关的套用。

**安静不能破坏Target链路。** 正常回复已经被上游决策选中时，角色应作适当回应；不能用“长门不爱说话”推翻已确定的直接交流。`ignore` 定义只是对齐当前枚举，不添加新的静默控制口令。

## 5. 一个专门避免的别名误触发

这次检查的 `message_analyzer.py` 对正式名字和 aliases 使用大小写归一后的子串匹配。

若把 `有希` 单独放进 aliases，下列普通消息就会命中名字：

```text
还[有希]望
没[有希]望
```

因此，本包把 `有希` 保留在 `meta.nickname`，但不放进自动点名的 `meta.aliases`。当前名字构造函数使用 name 和 aliases，不使用 nickname。

可直接用于名字匹配的写法包括 `长门有希`、`長門有希`、`长门`、`長門`、`Nagato Yuki`、`Yuki Nagato` 等。未加入太宽泛的单独 `Yuki`。

这是避免“名字子串导致强制target覆盖”的数据防护，不保证所有普通消息都保持沉默；LLM语义判断、连续对话和Proactive仍有各自的规则。也没有声称姓氏“长门”在所有跨作品话题中都能消歧。若未来必须支持单独“有希”直呼，应先加强名字边界识别，再扩充别名，不能直接塞回这版子串匹配。

## 6. 文件与默认参数

```text
bot/characters/nagato_yuki/
├── card.yaml
├── lore.yaml
├── memories.yaml
├── relationships.yaml
├── events.yaml
└── reply_behavior.yaml

tests/test_nagato_yuki_package.py
docs/NAGATO_YUKI_CHARACTER_PACKAGE_V1.md
docs/NAGATO_YUKI_VALIDATION_2026-09-22.txt
```

内容规模：5条个人记忆，5位原作固定关系，4条重要事件概要。Memory侧重个人经历及其保守解释，Event保留客观事件背景，两者不是逐条复制。数据量只是首版选择，不代表穷尽全部原作。

`card.yaml` 保留 `character` 根节点以及 Runtime 必需的 `meta.name`、`identity.background`、`personality.core_traits`、`personality.values`、`speech_style.tone`、`speech_style.habits`。没有使用旧错误字段 `traits`。

`reply_behavior.yaml` 包含7种回复类型，中英文对应的4个关系等级、5种情绪表现、7种场景表现，以及下面的保守主动参数：

```yaml
proactive:
  enabled: true
  min_context_messages: 4
  min_join_probability: 0.85
  cooldown_seconds: 360
```

这表示偏向观察的默认门槛，并非每条消息有85%的发言概率，更不是每6分钟强制发一条；是否主动发言还受场景分析与其他条件约束。这些参数针对Proactive，不是在角色直接被问话时强制等待6分钟。`private_chat` 行为配置也不表示本次已经实现私聊适配。

当前 Emotion Engine 会相加记忆中的 emotional_impact，之后封顶100。因此权重没有逐条设为很高的数。初始累计值为：nostalgia 16、curiosity 26、trust 18、confidence 24、sadness 16、happiness 6，均未因封顶而失去差异。它们是长期倾向的输入，不等于即时心情或对每位用户的信任。

## 7. 实际检查范围

检查副本由本聊天提供的原项目ZIP依次合并“@成员修复”“ReplyToBot修复”“Dialogue Style System v1”而成。没有合并芙宁娜后续示范库，也没有访问用户生产服务器。

实际检查包括：六文件YAML解析、重复键检查、Package Validator、Runtime深层字段、加载器可选风格缺省、真实Formatter、Memory Retriever、长期情绪计算、角色目录发现，以及Reactive/Proactive Prompt构建。

新增17项专项测试通过；原有Dialogue/Prompt/Proactive 20项通过；原有@与引用Target 15项在独立进程运行通过。共52项测试通过，不是宣称项目全部测试已运行。Reactive构建测试还包含7个回复模式 × 5个关系等级的35个子用例，子用例未重复计入52项。

**没有调用DeepSeek，没有生成风格A/B回复，没有测试此角色的真实QQ发送，没有部署。** 测试能证明这些数据按现有代码正常接入，不能证明“AI味已经消失”或完全还原角色。

## 8. 本地安装和验收

在当前本地项目中按目录合并压缩包：

```text
F:\Files\Code\Project\QQ-ai-bot\QQ-ai-bot
```

本次为新目录，不要删除或替换整个 `bot`、`characters`、`tests`、`docs` 文件夹。若你已经自行创建同名长门目录，先另行备份该目录再合并，避免覆盖自己的内容。

在项目根目录、当前虚拟环境内执行：

```powershell
python -m bot.validators.package_validator nagato_yuki
python -m unittest tests.test_nagato_yuki_package -v
```

预期：Validator最终显示 `Character Package Valid`；专项测试显示 `Ran 17 tests` 和 `OK`。现有Validator CLI没有把所有失败情况都转成非零退出码，因此不只检查命令退出码，要看最终报告；新增单测也直接断言了Validator的布尔结果。

本次测试只调用纯逻辑，不需要你的API Key，不要把 `.env` 或密钥发到聊天中。存在角色包配置不等于服务器镜像已经更新，**这一步先不部署**。

## 9. 下一阶段：长门的语言风格库

先验收六文件角色包，再建立长门自己的 `dialogue_examples.yaml`。继续使用已安装的Dialogue Style System v1，不需要改名复用芙宁娜的台词、反套话偏好或舞台表现。

后续若使用真实台词，需分别记录原作出处、场景、时间线、语言/译文版本，并明确它是原句、翻译还是原创示范；只学习表达方式，不把示范中的事实并入当前对话。当前尚未交付该语料，也未准备A/B结果。

## 10. 资料来源与支持范围

以下均于2026-09-22检查。来源提供人物与事件依据；本角色包的YAML、中文规则与工程参数为本次整理。

### S1 · 角川Sneaker文库官方系列与角色介绍（主要来源）

`https://sneakerbunko.jp/series/haruhi/`

支持：文艺部/SOS团身份、寡言与阅读特点、主要团员的基础关系；同页外传介绍明确说明普通人类长门的另一个设定。不是完整台词库。

### S2 · KADOKAWA《凉宫春日》原作版长门有希介绍（主要来源）

`https://www.kadokawa.co.jp/topics/13132/`

这是官方商品介绍页；只采用其中关于长门是SOS团成员、人形界面并阅读书籍的角色描述。不用商品营销文案推导细致的心理状态，也不采用其时效性价格或销售信息。

### S3 · 角川Sneaker文库官方 CHRONOLOGY（主要来源）

`https://sneakerbunko.jp/haruhi/chronology/`

支持：本篇事件的基本排列。本包只择取基准阶段之前的少量事件，不复制年表，不混合小说与动画不同版本的精确循环数字。

### S4 · 英文维基百科人物列表的Yuki Nagato条目（辅助来源）

`https://en.wikipedia.org/wiki/List_of_Haruhi_Suzumiya_characters#Yuki_Nagato`

原入口 `https://en.wikipedia.org/wiki/Yuki_Nagato` 重定向至该人物列表。辅助核对完整人形界面术语、观察任务、早期救援和部分人物的非公开身份。该页包含编辑与来源质量提示，因此不是与原作全文等价的证据；未据此把恋爱推断、心理因果或作品之后的事件写成确定事实。

### S5 · KADOKAWA《长门有希酱的消失》作品介绍（主要来源）

`https://www.kadokawa.co.jp/product/video2594/`

只用于区分外传普通人类长门与本篇，不将该外传情节载入本包。

### P1 · 本项目严格兼容角色包生成提示词与实际代码

`QQ-ai-bot_Character_Package_v1.1_角色包生成提示词_严格兼容修正版.txt`

配合上传代码中的 `character_loader.py`、`validators/`、`prompt.py`、`knowledge_formatter.py`、`emotion_engine.py`、`memory_retriever.py`、`message_analyzer.py` 核对结构与读取方式。结构以实际代码为准，不因自然语言描述相近就改名字段。
