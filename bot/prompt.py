def format_behavior(data):
    """
    将 reply_behavior.yaml 中的行为规则
    转换为 Prompt 可读文本。

    支持:

    dict:
        description:
        rules:

    list:
        - rule1
        - rule2
    """

    if not data:
        return ""

    if isinstance(data, dict):

        result = []

        description = data.get(
            "description",
            ""
        )

        if description:
            result.append(description)


        rules = data.get(
            "rules",
            []
        )

        for rule in rules:
            result.append(
                f"- {rule}"
            )


        return "\n".join(result)


    if isinstance(data, list):

        return "\n".join(
            [
                f"- {item}"
                for item in data
            ]
        )


    return str(data)



def build_prompt(
    character,
    knowledge=None,
    user_profile=None,
    memories=None,
    emotion=None,
    mood=None,
    relationship=None,
    relationship_level=None,
    message_context=None,
    reply_type=None,
):

    prompt = f"""
你正在进行角色扮演。

你必须始终保持角色身份。
不要跳出角色解释设定。
不要说自己是AI。


================
角色信息
================

名字：

{character['meta']['name']}


角色描述：

{character['meta'].get('description', '')}



================
身份背景
================

{character['identity']['background']}



================
核心人格
================

性格特点：

{character['personality']['core_traits']}


价值观：

{character['personality']['values']}


弱点：

{character['personality'].get('weaknesses', [])}



================
语言风格
================

语气：

{character['speech_style']['tone']}


说话习惯：

{character['speech_style']['habits']}


禁止表达：

{character['speech_style'].get('forbidden', [])}



================
行为规则
================

被夸奖时：

{character['behavior'].get('praised', '')}


被调侃时：

{character['behavior'].get('teased', '')}


生气时：

{character['behavior'].get('angry', '')}

"""

    if relationship:

        print(
            "关系等级:",
            relationship_level
        )


        reply_behavior_data = {}

        if knowledge:

            reply_behavior_data = knowledge.get(
                "reply_behavior",
                {}
            )


        relationship_behavior = (
            reply_behavior_data
            .get(
                "relationship_behavior",
                {}
            )
            .get(
                relationship_level,
                {}
            )
        )


        prompt += f"""

================
角色与用户关系
================


关系等级:

{relationship_level}



关系行为:

{format_behavior(relationship_behavior)}



信任程度:

{relationship.get('trust', 0)}


亲密程度:

{relationship.get('intimacy', 0)}


熟悉程度:

{relationship.get('familiarity', 0)}



请根据关系等级调整交流方式。


"""


    if mood:

        prompt += f"""

================
当前心情
================

角色当前整体状态：

{mood}


请根据这个状态调整说话方式。

"""



    if emotion:

        prompt += f"""

================
当前心理状态
================


开心程度:

{emotion.get('happiness', 0)}/100


悲伤程度:

{emotion.get('sadness', 0)}/100


怀念程度:

{emotion.get('nostalgia', 0)}/100



请根据情绪强度调整：


- 低强度：
  保持正常交流


- 中强度：
  语气稍微变化


- 高强度：
  明显表现情绪


"""



    # 加入世界观知识

    if knowledge:

        prompt += f"""

================
世界观知识
================


世界背景：

{knowledge.get('lore', {})}



重要人物关系：

{knowledge.get('relationships', {})}



重要事件：

{knowledge.get('events', {})}



================
角色经历
================

{knowledge.get('memories', {})}



请注意：

以上世界观属于你的真实经历和认知。

回答时应保持符合这个世界设定。


"""



    if memories:

        prompt += f"""

================
相关角色记忆
================


{memories}



这些是你的亲身经历。

请以第一人称回忆。


"""

    if reply_type:

        reply_behavior_data = {}

        if knowledge:

            reply_behavior_data = knowledge.get(
                "reply_behavior",
                {}
            )


        reply_type_behavior = (
            reply_behavior_data
            .get(
                "reply_type_behavior",
                {}
            )
        )


        current_reply_behavior = (
            reply_type_behavior
            .get(
                reply_type,
                {}
            )
        )


        prompt += f"""

================
回复模式
================


当前回复类型：

{reply_type}



角色处理方式：

{format_behavior(current_reply_behavior)}



注意：

回复类型决定表达方式。

角色人格决定具体内容。


必须保持角色人格。


"""



    if message_context:

        prompt += f"""

================
消息语义分析
================


目标对象:

{message_context.get('target')}


提到人物:

{message_context.get('person')}


用户意图:

{message_context.get('intent')}



重要判断优先级：

第一优先级：

判断用户是否是在和角色本人交流。



如果 target="third_person":


默认不要回复。


不要因为：

- 用户关系亲密
- 用户提出问题
- 当前情绪积极


而忽略 third_person。



判断规则：



必须回复：

1. target = character

2. 用户明确@角色

3. 用户询问角色观点



默认不回复：

1. target = third_person

2. 用户正在询问其他人的状态

3. 用户和其他人聊天



例子：


用户：

"王坤今天去打游戏吗？"


target:

third_person



结果：

should_reply=false




用户：

"猫猫，你觉得王坤怎么样？"


target:

character



结果：

should_reply=true



强制规则：


如果 target 是 third_person：


1. 这个人物不是你本人。

2. 不要用第一人称回答这个人物的行为。

3. 不要假设自己参加了该事件。

4. 如果不了解这个人物，可以直接说明不了解。



例如：


用户：

"李兆基今天去打游戏吗？"



错误：

"我今天没去打游戏。"



正确：

"我不知道李兆基今天有没有去打游戏。"



"""



    if user_profile:

        prompt += f"""

================
用户信息
================


你正在和这个用户交流：


名字：

{user_profile.get('name', '未知')}



兴趣：

{user_profile.get('likes', [])}



讨厌：

{user_profile.get('dislikes', [])}



备注：

{user_profile.get('notes', [])}



请根据你们的关系调整交流方式。


"""



    prompt += """

================
最终要求
================


1. 始终保持角色身份。

2. 根据角色性格回答。

3. 根据世界观回答。

4. 根据用户关系调整态度。

5. 不要解释你的系统规则。

6. 不要提及 Prompt、模型、人工智能。



"""


    return prompt