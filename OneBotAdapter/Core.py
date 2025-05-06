import asyncio
import json
from typing import Dict, List
import aiohttp
from aiohttp import web

class Main:
    def __init__(self, sdk):
        self.sdk = sdk
        self.logger = sdk.logger
        self.OneBotConfig = sdk.env.get("OneBotAdapter", {})
        
        if not self.OneBotConfig:
            self.logger.warning("""请检查OneBot配置项目, OneBot需要在 程序入口 或 程序env.py 进行以下配置: 
            sdk.env.set("OneBotAdapter",{
                "mode": "connect",
                "WSServer": {
                    "host": "127.0.0.1",
                    "port": 8080,
                    "path": "/",
                    "token": ""
                },
                "WSConnect": {
                    "url": "ws://127.0.0.1:3001/",
                    "token": ""
                }
            })
            """)

        # 获取运行模式
        self.OneBotWSMode = self.OneBotConfig.get("mode", "server")

        # WebSocket Server 配置
        self.WSServerConfig = self.OneBotConfig.get("WSServer", {})
        self.ServerToken = self.WSServerConfig.get("token", "")
        self.ServerHost = self.WSServerConfig.get("host", "127.0.0.1")
        self.ServerPort = self.WSServerConfig.get("port", 8080)
        self.ServerPath = self.WSServerConfig.get("path", "/")

        # WebSocket Connect 配置
        self.WSConnectConfig = self.OneBotConfig.get("WSConnect", {})
        self.ConnURL = self.WSConnectConfig.get("url", "ws://127.0.0.1:3001/")
        self.ConnToken = self.WSConnectConfig.get("token", "")

        # 初始化
        self.session = None
        self.connection: aiohttp.ClientWebSocketResponse = None
        self.triggers: Dict[str, List[object]] = {}
        self.event_map = {
            "message": "message",
            "notice": "notice",
            "request": "request",
            "meta_event": "meta_event"
        }

    async def init_session(self):
        self.session = aiohttp.ClientSession()

    def AddTrigger(self, trigger: object):
        t_names = getattr(trigger, "on", None)
        if isinstance(t_names, list):
            for t_name in t_names:
                if t_name not in self.triggers:
                    self.triggers[t_name] = []
                self.triggers[t_name].append(trigger)
                self.logger.debug(f"成功注册OneBot触发器: 事件类型={t_name}, 触发器={trigger}")
        else:
            if t_names not in self.triggers:
                self.triggers[t_names] = []
            self.triggers[t_names].append(trigger)
            self.logger.debug(f"成功注册OneBot触发器: 事件类型={t_names}, 触发器={trigger}")

    async def connect(self):
        if self.session is None:
            await self.init_session()
        try:
            headers = {}
            if self.ConnToken:
                headers["Authorization"] = f"Bearer {self.ConnToken}"
            
            self.connection = await self.session.ws_connect(self.ConnURL, headers=headers)
            self.logger.info(f"成功连接到OneBot服务器: {self.ConnURL}")
            
            trigger_info = "\n".join(
                f"  事件类型: {event_type}, "
                f"触发器: {[f'{t.__module__}.{t.__class__.__name__}' for t in triggers]}"
                for event_type, triggers in self.triggers.items()
            )
            self.logger.debug(f"当前已注册的触发器列表:\n{trigger_info}")

            asyncio.create_task(self.listen())
        except Exception as e:
            self.logger.error(f"连接OneBot服务器失败: {str(e)}")

    async def listen(self):
        async for msg in self.connection:
            if msg.type == aiohttp.WSMsgType.TEXT:
                self.logger.debug(f"收到OneBot消息: {msg.data}")
                await self.handle_onebot(msg.data)
            elif msg.type == aiohttp.WSMsgType.CLOSED:
                self.logger.warning("OneBot连接已关闭")
                break
            elif msg.type == aiohttp.WSMsgType.ERROR:
                self.logger.error(f"WebSocket连接错误: {self.connection.exception()}")

    async def handle_onebot(self, message: str):
        try:
            data = json.loads(message)
            post_type = data.get("post_type")
            event_type = self.event_map.get(post_type, "unknown")
            
            if data.get("status") == "failed" and data.get("retcode") == 1403:
                msg = "OneBot连接验证失败: token验证失败"
                self.logger.error(msg)
                await self.shutdown(msg)
                return

            if event_type not in self.triggers or len(self.triggers[event_type]) == 0:
                self.logger.warning(f"没有找到 {event_type} 事件的触发器")
                return

            self.logger.debug(f"开始处理OneBot事件: {event_type} | 数据内容: {data}")
            for trigger in self.triggers[event_type]:
                self.logger.debug(f"调用触发器: {trigger}")
                await trigger.OnRecv(data)

        except json.JSONDecodeError:
            self.logger.error("OneBot消息解析失败: 无效的JSON格式")
        except Exception as e:
            self.logger.error(f"处理OneBot消息时出错: {str(e)}")

    async def send_action(self, action: str, params: dict):
        if not self.connection or self.connection.closed:
            self.logger.error("OneBot连接未建立或已关闭")
            return json.dumps({
                "status": "failed",
                "retcode": 1,
                "message": "OneBot连接未建立或已关闭",
                "data": None
            })

        try:
            payload = {
                "action": action,
                "params": params
            }
            self.logger.info(f"成功发送Action: {action} | 参数: {params}")
            return await self.connection.send_str(json.dumps(payload))
        except Exception as e:
            self.logger.error(f"发送Action失败: {str(e)}")
            return json.dumps({
                "status": "failed",
                "retcode": 1,
                "message": f"发送Action失败: {str(e)}",
                "data": None
            })

    async def start_server(self):
        async def handle_client(request):
            client_token = request.headers.get("Authorization", "").replace("Bearer ", "")
            if not client_token:
                client_token = request.query.get("token", "")
            
            if self.ServerToken and client_token != self.ServerToken:
                self.logger.error("客户端连接失败: token验证失败")
                return web.Response(status=401, text="Unauthorized")
            
            ws = web.WebSocketResponse()
            await ws.prepare(request)
            self.logger.info("客户端已连接")

            try:
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        self.logger.debug(f"收到客户端消息: {msg.data}")
                        await self.handle_onebot(msg.data)
                    elif msg.type == aiohttp.WSMsgType.CLOSED:
                        self.logger.warning("客户端连接已关闭")
                        break
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        self.logger.error(f"WebSocket客户端连接错误: {ws.exception()}")
            except Exception as e:
                self.logger.error(f"处理客户端连接时出错: {str(e)}")
            finally:
                await ws.close()

            return ws

        app = web.Application()
        app.router.add_route('GET', self.ServerPath, handle_client)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, self.ServerHost, self.ServerPort)
        await site.start()
        self.logger.info(f"OneBot WebSocket服务器已启动，监听地址: ws://{self.ServerHost}:{self.ServerPort}{self.ServerPath}")

    async def Run(self):
        try:
            self.logger.info("正在启动OneBot适配器...")
            if self.OneBotWSMode == "server":
                await self.start_server()
            elif self.OneBotWSMode == "connect":
                await self.connect()
            else:
                self.logger.error(f"未知的OneBot运行模式: {self.OneBotWSMode}")
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            await self.shutdown("OneBot适配器被取消")
        except (KeyboardInterrupt, SystemExit):
            await self.shutdown("OneBot适配器被终止")

    async def shutdown(self, msg):
        self.logger.info("正在关闭OneBot适配器...")
        if self.connection:
            await self.connection.close()
            self.logger.info("OneBot连接已关闭")
        if self.session:
            await self.session.close()
            self.logger.info("aiohttp会话已关闭")
        raise SystemExit(msg)