import asyncio
import re
from avidya.bot import botOn, givemeLogger
#如果你希望这段代码可以生效，去看main.py

#如果你不需要logger，可以把下面这样注释掉，logger和print差不多，但它是彩色的
logger=givemeLogger()
#你可以这样用
logger.info("hello")
logger.error("hello")
logger.warning("hello")
#尽量别动这个
async def process1(msg,bot):
    echo_funcs = [func for func in globals().values() if callable(func) and getattr(func, "is_echo", False)]
    # 使用asyncio.gather来同时执行它们，并获取它们的结果
    ass =await asyncio.gather(*[func(msg) for func in echo_funcs])
    #ass = await asyncio.gather(*[func(msg,bot) for func in echo_funcs]) #如果你习惯在函数内发送消息，可以在msg旁边加一个bot参数
    print(ass)
    for i in ass:
        if i != None:
            await bot.send(msg, i) #遍历返回的结果，选择一个不为None，即有响应的函数返回的结果。
            return            #结束

#所有带有botOn注解的函数会同时被执行，然后返回结果。
@botOn
async def test2(msg):               #你艾特bot时，它就会回复你hello
    return "hello"

#如果你用了上面的ass = await asyncio.gather(*[func(msg,bot) for func in echo_funcs])，也可以像这样写，直接在函数内发送消息了
'''@botOn
async def test2(msg,bot):            #你艾特bot时，它就会回复你hello,和上面的效果一样
    await bot.send(msg,"hello")'''

#给回复加上判断
@botOn
async def genshinpppp(msg):               #注意函数不能重名
    #下面几行是正则判断，只要有 原神，就会触发回复一个 opg
    pattern = r".*原神.*"   #你要改的话改这里就行了，别的直接复制就行
    if msg.get("d").get('content').startswith("/"):
        string=msg.get("d").get('content').replace("/","")
    else:
        string = msg.get("d").get('content').split("> ")[1]
    match = re.search(pattern, string)
    if match:
        #如果包含原神就回复 opg

        return "opg"
