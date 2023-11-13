import asyncio

from avidya.bot import botOn


async def process1(msg,bot):
    echo_funcs = [func for func in globals().values() if callable(func) and getattr(func, "is_echo", False)]
    # 使用asyncio.gather来同时执行它们，并获取它们的结果
    ass =await asyncio.gather(*[func(msg) for func in echo_funcs])
    print(ass)
    await bot.send_channel_message(msg, "hello")
@botOn
async def test2(event):
    #print("loading........")
    return "hello"
