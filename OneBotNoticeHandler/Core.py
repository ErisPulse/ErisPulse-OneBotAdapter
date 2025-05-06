class Main:
    def __init__(self, sdk):
        self.sdk = sdk
        self.logger = sdk.logger
        self.on = "notice"
        self.handles: list[object] = []
    def AddHandle(self, handle):
        self.handles.append(handle)
        self.logger.debug(f"成功注册OneBot通知处理器: {handle}")

    async def OnRecv(self, data):
        self.logger.debug(f"开始处理OneBot通知: {data}")
        for handle in self.handles:
            try:
                await handle(data)
            except Exception as e:
                self.logger.error(f"处理OneBot通知时出错: {str(e)}")
