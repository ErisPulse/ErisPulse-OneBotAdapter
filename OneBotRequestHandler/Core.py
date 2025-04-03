class Main:
    def __init__(self, sdk, logger):
        self.on = "request"
        self.sdk = sdk
        self.logger = logger
        self.handles: list[object] = []

    def AddHandle(self, handle):
        self.handles.append(handle)
        self.logger.debug(f"成功注册OneBot请求处理器: {handle}")

    async def OnRecv(self, data):
        self.logger.debug(f"开始处理OneBot请求事件: {data}")
        for handle in self.handles:
            try:
                await handle(data)
            except Exception as e:
                self.logger.error(f"处理OneBot请求事件时出错: {str(e)}")
