import asyncio
import uuid

from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect
)

from ..message_handler import handle_message
from ..outbound_lifecycle import commit_sent_message


router = APIRouter()


# ============================================================
# OneBot Connection Manager
# ============================================================

class OneBotConnection:

    def __init__(self):

        self.websocket = None

        # echo -> Future
        #
        # 用于匹配：
        #
        # send_group_msg
        #       ↓
        # OneBot API Response
        self.pending_requests = {}

        # 防止多个协程同时写 WebSocket
        self.send_lock = asyncio.Lock()


    def is_connected(self):

        return (
            self.websocket is not None
        )


    async def connect(
        self,
        websocket: WebSocket
    ):

        self.websocket = websocket


    async def disconnect(
        self,
        websocket=None
    ):

        # 如果已经有新的 WebSocket 连接，
        # 旧连接断开时不能把新连接清掉。

        if (
            websocket is not None
            and self.websocket is not websocket
        ):

            return


        self.websocket = None


        # 如果连接突然断开，
        # 所有正在等待 OneBot API 响应的请求
        # 都应该结束。

        for future in list(
            self.pending_requests.values()
        ):

            if not future.done():

                future.set_exception(
                    ConnectionError(
                        "OneBot WebSocket disconnected"
                    )
                )


        self.pending_requests.clear()


    async def send_action(
        self,
        action,
        params,
        timeout=10
    ):

        websocket = self.websocket


        if websocket is None:

            raise ConnectionError(
                "OneBot WebSocket is not connected"
            )


        # 每次 OneBot API 调用生成唯一 echo
        echo = str(
            uuid.uuid4()
        )


        loop = (
            asyncio.get_running_loop()
        )


        future = loop.create_future()


        self.pending_requests[
            echo
        ] = future


        payload = {

            "action": action,

            "params": params,

            "echo": echo

        }


        try:

            # =====================
            # 发送 OneBot Action
            # =====================

            async with self.send_lock:

                # 防止连接在等待锁时已经被替换

                if self.websocket is not websocket:

                    raise ConnectionError(
                        "OneBot WebSocket connection changed"
                    )


                await websocket.send_json(
                    payload
                )


            # =====================
            # 等待对应 echo 的响应
            # =====================

            response = await asyncio.wait_for(

                future,

                timeout=timeout

            )


            return response


        finally:

            self.pending_requests.pop(
                echo,
                None
            )


    def resolve_response(
        self,
        data
    ):

        """
        尝试判断当前数据是否为：

        OneBot API Response

        如果有对应 echo，
        就唤醒等待 send_action() 的 Future。
        """

        echo = data.get(
            "echo"
        )


        if echo is None:

            return False


        echo = str(
            echo
        )


        future = (
            self.pending_requests.get(
                echo
            )
        )


        if future is None:

            return False


        if not future.done():

            future.set_result(
                data
            )


        return True


onebot_connection = OneBotConnection()


# ============================================================
# Per-Group Processing Locks
# ============================================================
#
# 为什么需要这个：
#
# 群里可能连续收到：
#
# A: ...
# B: ...
# C: ...
#
# WebSocket 主循环会为三条消息分别 create_task。
#
# 如果没有 Group Lock：
#
# A/B/C 可能同时调用：
#
# ConversationState
# SceneAnalyzer
# ProactiveBehavior
#
# 最终可能出现：
#
# - 消息顺序错乱
# - 两个主动行为同时触发
# - 同一个群连续发送两条 AI 消息
#
# 所以：
#
# 同一个 group_id → 串行
# 不同 group_id → 可以并行
# ============================================================

group_locks = {}


def get_group_lock(
    group_id
):

    group_id = str(
        group_id
    )


    lock = group_locks.get(
        group_id
    )


    if lock is None:

        lock = asyncio.Lock()

        group_locks[
            group_id
        ] = lock


    return lock


# ============================================================
# OneBot API
# ============================================================

async def send_group_message(
    group_id,
    message
):

    """
    调用 OneBot:

    send_group_msg
    """

    response = (
        await onebot_connection.send_action(

            action="send_group_msg",

            params={

                "group_id": int(
                    group_id
                ),

                "message": message

            }

        )
    )


    success = (

        response.get(
            "status"
        ) == "ok"

        and

        response.get(
            "retcode"
        ) == 0

    )


    return (
        success,
        response
    )


# ============================================================
# Group Message Handler
# ============================================================

async def process_group_message(
    event
):

    """
    群消息统一入口。

    同一个群里的所有消息，
    必须严格按顺序处理。
    """

    group_id = str(
        event.get(
            "group_id"
        )
    )


    if not group_id:

        return


    lock = get_group_lock(
        group_id
    )


    # =====================
    # 同一个群串行处理
    # =====================

    async with lock:

        await process_group_message_locked(
            event
        )


async def process_group_message_locked(
    event
):

    """
    真正的群消息处理流程。

    该函数执行时，
    已经持有当前 group_id 的 Lock。
    """


    self_id = str(
        event.get(
            "self_id"
        )
    )


    group_id = str(
        event.get(
            "group_id"
        )
    )


    user_id = str(
        event.get(
            "user_id"
        )
    )


    raw_message = event.get(
        "raw_message",
        ""
    )


    # ========================================================
    # 1. 防御性检查
    # ========================================================

    if not group_id:

        return


    if not user_id:

        return


    # 不处理机器人自己的消息
    #
    # 即使未来 NapCat 开启了
    # reportSelfMessage，也不会造成循环。

    if user_id == self_id:

        return


    if not raw_message:

        return


    # ========================================================
    # 2. 打印真实 QQ 消息
    # ========================================================

    print(
        "\n"
        "========== QQ GROUP MESSAGE =========="
    )

    print(
        "self_id:",
        self_id
    )

    print(
        "group_id:",
        group_id
    )

    print(
        "user_id:",
        user_id
    )

    print(
        "raw_message:",
        raw_message
    )

    print(
        "======================================"
        "\n"
    )


    # ========================================================
    # 3. Character Engine
    # ========================================================
    #
    # handle_message() 是同步函数。
    #
    # 内部包含：
    #
    # Redis
    # DeepSeek
    # MessageAnalyzer
    # SceneAnalyzer
    #
    # 这些都会阻塞。
    #
    # 所以放入线程，
    # 避免阻塞 asyncio Event Loop。
    # ========================================================

    try:

        result = await asyncio.to_thread(

            handle_message,

            user_id,

            raw_message,

            group_id

        )


    except Exception as e:

        print(
            "❌ Character Engine Error:",
            repr(e)
        )

        return


    # 防御性检查

    if result is None:

        print(
            "❌ Character Engine returned None"
        )

        return


    # ========================================================
    # 4. MessageResult
    # ========================================================

    print(
        "MessageResult:",
        {
            "action":
                result.action,

            "content":
                result.content,

            "character_id":
                result.character_id,

            "behavior":
                result.behavior,

            "priority":
                result.priority,

            "should_send":
                result.should_send
        }
    )


    # ========================================================
    # 5. Character Engine 决定保持沉默
    # ========================================================

    if not result.should_send:

        return


    if not result.content:

        return


    # ========================================================
    # 6. 真正发送 QQ 消息
    # ========================================================

    try:

        success, response = (
            await send_group_message(

                group_id=group_id,

                message=result.content

            )
        )


    except Exception as e:

        print(
            "❌ QQ Send Error:",
            repr(e)
        )

        return


    # ========================================================
    # 7. QQ发送失败
    # ========================================================

    if not success:

        print(
            "❌ QQ Send Failed:",
            response
        )

        return


    # ========================================================
    # 8. QQ发送成功
    # ========================================================

    print(
        "✅ QQ Message Sent:",
        result.content
    )


    # ========================================================
    # 9. Outbound Commit
    # ========================================================
    #
    # 只有真实 QQ 发送成功以后：
    #
    # - 记录 cooldown
    # - 写入 ConversationState
    #
    # 发送失败绝对不能 commit。
    # ========================================================

    try:

        committed = commit_sent_message(

            group_id,

            result

        )


    except Exception as e:

        print(
            "❌ Outbound Commit Error:",
            repr(e)
        )

        return


    print(
        "Outbound Commit:",
        committed
    )


# ============================================================
# WebSocket
# ============================================================

@router.websocket(
    "/onebot/v11/ws"
)
async def onebot_websocket(
    websocket: WebSocket
):

    # ========================================================
    # 1. Accept Connection
    # ========================================================

    await websocket.accept()


    await onebot_connection.connect(
        websocket
    )


    print(
        "✅ OneBot WebSocket connected"
    )


    try:

        while True:

            # =================================================
            # 2. Receive
            # =================================================

            data = (
                await websocket.receive_json()
            )


            # =================================================
            # 3. OneBot API Response
            # =================================================
            #
            # send_group_msg 等 Action 的响应
            # 会携带 echo。
            #
            # 找到对应 Future 后，
            # 直接交给 send_action()。
            # =================================================

            if onebot_connection.resolve_response(
                data
            ):

                continue


            # =================================================
            # 4. OneBot Event
            # =================================================

            post_type = data.get(
                "post_type"
            )


            # =================================================
            # Message Event
            # =================================================

            if post_type == "message":

                message_type = data.get(
                    "message_type"
                )


                # =====================
                # Group Message
                # =====================

                if message_type == "group":

                    # 这里不能：
                    #
                    # await process_group_message(...)
                    #
                    # 因为 Character Engine 可能调用 DeepSeek，
                    # 要等待几秒。
                    #
                    # 如果阻塞这里，
                    # WebSocket 就无法继续接收：
                    #
                    # - heartbeat
                    # - send_group_msg response
                    #
                    # 因此必须独立 Task。

                    asyncio.create_task(

                        process_group_message(
                            data
                        )

                    )


                # =====================
                # Private Message
                # =====================

                elif message_type == "private":

                    print(
                        "OneBot Private Message:",
                        data.get(
                            "raw_message"
                        )
                    )


            # =================================================
            # Meta Event
            # =================================================

            elif post_type == "meta_event":

                # heartbeat
                # lifecycle
                #
                # 属于正常事件。
                #
                # 不打印，
                # 避免日志刷屏。

                pass


            # =================================================
            # Notice / Request / Other
            # =================================================

            else:

                print(
                    "OneBot Event:",
                    post_type
                )


    # ========================================================
    # WebSocket disconnected normally
    # ========================================================

    except WebSocketDisconnect:

        print(
            "❌ OneBot WebSocket disconnected"
        )


    # ========================================================
    # Unexpected error
    # ========================================================

    except Exception as e:

        print(
            "❌ OneBot WebSocket Error:",
            repr(e)
        )


    # ========================================================
    # Cleanup
    # ========================================================

    finally:

        await onebot_connection.disconnect(
            websocket
        )