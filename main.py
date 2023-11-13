#!/usr/bin/env python
import asyncio
import json
from asyncio import sleep

from websockets.client import connect

# 定义一个装饰器，用来标记使用了@echo注解的异步函数
import test1
from avidya.bot import Bot, botOn


# 定义一个异步函数，用来创建一个WebSocket客户端，并与服务器通信
async def client():
    # 创建一个WebSocket客户端
    async with connect(bot.wsUrl) as ws:
        # 发送一个初始化消息
        logger.info(await ws.recv())
        logger.info("初始化消息发送成功")
        #进行登录鉴权
        await ws.send(paylod)
        await ws.recv()
        logger.info("登录鉴权成功")
        # 每隔 60 秒发送一个心跳包
        asyncio.create_task(HeartBeat(ws))
        bot.ws=ws
        logger.info("开始接收消息")
        # 无限循环，接收服务器的消息
        async for msg in ws:
            # 获取所有使用了@echo注解的异步函数
            if type(msg) != json:
                msg = json.loads(msg)
            if msg!={"op":11}:
                logger.info(msg)
                await asyncio.gather(test1.process1(msg, bot),)
async def HeartBeat(ws):
    while True:
        logger.info("发送心跳包.....")
        await ws.send(json.dumps({
      "op": 1,
      "d": 251
    }
    ))
        logger.info("发送成功")
        await sleep(60)


bot=Bot(botid= ,botsecret="")
#print(bot.token)
logger=bot.logger
mode="channel"
logger.info("当前模式:"+mode)
paylod=json.dumps({
  "op": 2,
  "d": {
    "token": "QQBot "+bot.token,
    "intents": 1073741824,
    "shard": [0, 4],
    "properties": {
      "$os": "linux",
      "$browser": "my_library",
      "$device": "my_library"
    }
  }
})
# 运行客户端
asyncio.run(client()) # 每隔14秒发送一个“ping”命令，如果10秒内没有收到“pong”回应，就关闭连接
