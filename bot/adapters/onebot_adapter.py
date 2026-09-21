from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect
)


router = APIRouter()


@router.websocket(
    "/onebot/v11/ws"
)
async def onebot_websocket(
    websocket: WebSocket
):

    await websocket.accept()

    print(
        "✅ OneBot WebSocket connected"
    )


    try:

        while True:

            event = (
                await websocket.receive_json()
            )


            post_type = event.get(
                "post_type"
            )


            # 生命周期 / heartbeat 等事件
            if post_type != "message":

                print(
                    "OneBot Event:",
                    post_type
                )

                continue


            message_type = event.get(
                "message_type"
            )


            # =====================
            # 群消息
            # =====================

            if message_type == "group":

                print(
                    "\n"
                    "========== QQ GROUP MESSAGE =========="
                )

                print(
                    "self_id:",
                    event.get(
                        "self_id"
                    )
                )

                print(
                    "group_id:",
                    event.get(
                        "group_id"
                    )
                )

                print(
                    "user_id:",
                    event.get(
                        "user_id"
                    )
                )

                print(
                    "raw_message:",
                    event.get(
                        "raw_message"
                    )
                )

                print(
                    "======================================"
                    "\n"
                )


            # =====================
            # 私聊消息
            # =====================

            elif message_type == "private":

                print(
                    "\n"
                    "========== QQ PRIVATE MESSAGE =========="
                )

                print(
                    "user_id:",
                    event.get(
                        "user_id"
                    )
                )

                print(
                    "raw_message:",
                    event.get(
                        "raw_message"
                    )
                )

                print(
                    "========================================"
                    "\n"
                )


    except WebSocketDisconnect:

        print(
            "❌ OneBot WebSocket disconnected"
        )