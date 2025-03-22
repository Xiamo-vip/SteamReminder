import threading
import time
import requests
import json
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

# Steam API URL
STEAM_API_URL = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
API_KEY = "C22290FBE2795C45CCDDC2D80EB74FE3"
STEAM_ID = "76561199241605465"

@register("SteamReminder", "XiaMo", "Steam 状态检测插件", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self._running = False
        self._thread = None
        self._last_personastate = None  # 上一次的 personastate 状态
        self._last_gameextrainfo = None  # 上一次的 gameextrainfo 状态

    def start_thread(self):
        '''启动线程'''
        self._running = True
        self._thread = threading.Thread(target=self._run)
        self._thread.start()

    def stop_thread(self):
        '''停止线程'''
        self._running = False
        if self._thread:
            self._thread.join()

    def _run(self):
        '''线程中执行的逻辑'''
        while self._running:
            try:
                # 访问 Steam API
                response = requests.get(
                    STEAM_API_URL,
                    params={"key": API_KEY, "steamids": STEAM_ID}
                )
                if response.status_code == 200:
                    data = response.json()
                    players = data.get("response", {}).get("players", [])
                    if players:
                        player = players[0]
                        personastate = player.get("personastate", 0)
                        gameextrainfo = player.get("gameextrainfo", "")

                        # 检测 personastate 变化
                        if self._last_personastate is not None:
                            if self._last_personastate == 0 and personastate == 1:
                                from astrbot.api.event import MessageChain
                                message_chain = MessageChain("对方已上线")
                                await self.context.send_message("gewechat:FriendMessage:wxid_vpmipmmgc3vm22", message_chain)

                        # 检测 gameextrainfo 变化
                        if self._last_gameextrainfo is not None:
                            if self._last_gameextrainfo != gameextrainfo:
                                if gameextrainfo:
                                    from astrbot.api.event import MessageChain
                                    message_chain = MessageChain("对方已上线")
                                    await self.context.send_message("gewechat:FriendMessage:wxid_vpmipmmgc3vm22", message_chain)
                                else:
                                    from astrbot.api.event import MessageChain
                                    message_chain = MessageChain("对方已上线")
                                    await self.context.send_message("gewechat:FriendMessage:wxid_vpmipmmgc3vm22", message_chain)

                        # 更新状态
                        self._last_personastate = personastate
                        self._last_gameextrainfo = gameextrainfo

            except Exception as e:
                logger.error(f"访问 Steam API 出错: {e}")

            # 每1秒执行一次
            time.sleep(1)

    @filter.command("startmonitor")
    async def start_monitor(self, event: AstrMessageEvent):
        '''启动 Steam 状态监控'''
        if not self._running:
            self.start_thread()
            yield event.plain_result("Steam 状态监控已启动！")
        else:
            yield event.plain_result("Steam 状态监控已经在运行中！")

    @filter.command("stopmonitor")
    async def stop_monitor(self, event: AstrMessageEvent):
        '''停止 Steam 状态监控'''
        if self._running:
            self.stop_thread()
            yield event.plain_result("Steam 状态监控已停止！")
        else:
            yield event.plain_result("Steam 状态监控未运行！")

    async def terminate(self):
        '''插件卸载/停用时调用'''
        self.stop_thread()
