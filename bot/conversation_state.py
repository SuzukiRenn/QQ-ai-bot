import time
from collections import defaultdict, deque


class ConversationState:

    def __init__(self):

        self.groups = defaultdict(
            self._create_state
        )


    def _create_state(self):

        return {

            # 最近聊天记录
            "messages": deque(
                maxlen=20
            ),


            # 当前话题
            "topic": None,


            # 当前场景
            "scene": "normal",


            # 活跃用户
            "active_users": set(),


            # 最后消息时间
            "last_message_time": 0,


            # 沉默时间
            "silence_time": 0

        }



    def update(
        self,
        group_id,
        user_id,
        message,
        sender_type="user"
    ):

        if not group_id:
            return


        state = self.groups[
            group_id
        ]


        now = time.time()


        state["messages"].append(

            {
                "user_id": user_id,

                "message": message,

                "time": now,

                "sender_type": sender_type
            }

        )


        # active_users 只统计真实群成员
        # 不把角色自己算进去

        if sender_type == "user":

            state["active_users"].add(
                user_id
            )


        state["silence_time"] = (

            now
            - state["last_message_time"]

            if state["last_message_time"]

            else 0
        )


        state["last_message_time"] = now


    def get(
        self,
        group_id
    ):

        return self.groups[group_id]



    def clear(
        self,
        group_id
    ):

        if group_id in self.groups:

            del self.groups[group_id]



conversation_state = ConversationState()