# ErisPulse-OneBotAdapter

## 模块介绍

### OneBotAdapter
OneBot V11协议适配模块，提供异步的OneBot触发器功能。支持两种运行模式：
- Server模式：作为WebSocket服务器接收OneBot客户端连接
- Connect模式：作为WebSocket客户端连接OneBot服务器

主要功能：
- 支持消息、通知、请求、元事件等事件类型的处理
- 提供触发器注册机制，可灵活扩展事件处理逻辑
- 支持Token验证，确保连接安全性
- 提供消息发送和Action调用接口

### OneBotMessageHandler
OneBot协议消息处理模块，用于处理OneBot的消息事件。

主要功能：
- 提供消息处理器注册机制
- 支持异步消息处理
- 可与其他模块协同工作

### OneBotNoticeHandler  
OneBot协议通知处理模块，用于处理OneBot的通知事件。

主要功能：
- 提供通知处理器注册机制
- 支持异步通知处理
- 完善的错误处理机制

### OneBotRequestHandler
OneBot协议请求处理模块，用于处理OneBot的请求事件。

主要功能：
- 提供请求处理器注册机制
- 支持异步请求处理
- 详细的日志记录

## 使用示例

```python
from ErisPulse import sdk

# 初始化SDK
sdk.init()

async def main():
    # 添加触发器
    sdk.OneBotAdapter.AddTrigger(sdk.OneBotMessageHandler)
    sdk.OneBotAdapter.AddTrigger(sdk.OneBotNoticeHandler)
    sdk.OneBotAdapter.AddTrigger(sdk.OneBotRequestHandler)

    # 启动OneBotAdapter
    await sdk.OneBotAdapter.Run()

# 运行主程序
await main()
```

## 配置说明

在env.py中进行以下配置：

```python
sdk.env.set("OneBotAdapter", {
    "mode": "connect",  # 或 "server"
    "WSServer": {
        "host": "127.0.0.1",
        "port": 8080,
        "path": "/",
        "token": "your_token"
    },
    "WSConnect": {
        "url": "ws://127.0.0.1:3001/",
        "token": "your_token"
    }
})
```

## 参考链接

- [ErisPulse 主库](https://github.com/wsu2059q/ErisPulse/)
- [ErisPulse 开发指南](https://github.com/wsu2059q/ErisPulse/blob/main/%E5%BC%80%E5%8F%91%E6%8C%87%E5%8D%97.md)
# ErisPulse-OneBotAdapter

## 模块介绍

### OneBotAdapter
OneBot V11协议适配模块，提供异步的OneBot触发器功能。支持两种运行模式：
- Server模式：作为WebSocket服务器接收OneBot客户端连接
- Connect模式：作为WebSocket客户端连接OneBot服务器

主要功能：
- 支持消息、通知、请求、元事件等事件类型的处理
- 提供触发器注册机制，可灵活扩展事件处理逻辑
- 支持Token验证，确保连接安全性
- 提供消息发送和Action调用接口

### OneBotMessageHandler
OneBot协议消息处理模块，用于处理OneBot的消息事件。

主要功能：
- 提供消息处理器注册机制
- 支持异步消息处理
- 可与其他模块协同工作

### OneBotNoticeHandler  
OneBot协议通知处理模块，用于处理OneBot的通知事件。

主要功能：
- 提供通知处理器注册机制
- 支持异步通知处理
- 完善的错误处理机制

### OneBotRequestHandler
OneBot协议请求处理模块，用于处理OneBot的请求事件。

主要功能：
- 提供请求处理器注册机制
- 支持异步请求处理
- 详细的日志记录

## 使用示例

```python
from ErisPulse import sdk

# 初始化SDK
sdk.init()

async def main():
    # 添加触发器
    sdk.OneBotAdapter.AddTrigger(sdk.OneBotMessageHandler)
    sdk.OneBotAdapter.AddTrigger(sdk.OneBotNoticeHandler)
    sdk.OneBotAdapter.AddTrigger(sdk.OneBotRequestHandler)

    # 启动OneBotAdapter
    await sdk.OneBotAdapter.Run()

# 运行主程序
await main()
```

## 配置说明

在env.py中进行以下配置：

```python
sdk.env.set("OneBotAdapter", {
    "mode": "connect",  # 或 "server"
    "WSServer": {
        "host": "127.0.0.1",
        "port": 8080,
        "path": "/",
        "token": "your_token"
    },
    "WSConnect": {
        "url": "ws://127.0.0.1:3001/",
        "token": "your_token"
    }
})
```

## 参考链接

- [ErisPulse 主库](https://github.com/wsu2059q/ErisPulse/)
- [ErisPulse 开发指南](https://github.com/wsu2059q/ErisPulse/blob/main/%E5%BC%80%E5%8F%91%E6%8C%87%E5%8D%97.md)
