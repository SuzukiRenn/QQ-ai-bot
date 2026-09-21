from .character_manager import CharacterManager

from bot.conversation_state import conversation_state
from bot.scene_analyzer import scene_analyzer
from bot.proactive_behavior import proactive_behavior



class Runtime:


    def __init__(self):

        self.character_manager = CharacterManager()


        # 群聊状态

        self.conversation_state = conversation_state


        # 场景分析

        self.scene_analyzer = scene_analyzer


        # 主动行为

        self.proactive_behavior = proactive_behavior



    def init(self):

        self.character_manager.load_all_characters()


        print(
            "Character runtime initialized:"
        )


        print(
            self.character_manager.list_loaded()
        )



runtime = Runtime()



def init_runtime():

    runtime.init()


character_manager = runtime.character_manager