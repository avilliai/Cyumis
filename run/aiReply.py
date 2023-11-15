# -*- coding: utf-8 -*-
import asyncio
import json
import random
import uuid
from asyncio import sleep

import httpx
#import poe
import yaml

import threading
from asyncio import sleep

import zhipuai

from avidya.bot import givemeLogger, botOn
from plugins.PandoraChatGPT import ask_chatgpt
from plugins.RandomStr import random_str
from plugins.chatGLMonline import chatGLM1

from plugins.rwkvHelper import rwkvHelper
from plugins.vitsGenerate import taffySayTest

logger=givemeLogger()

# 读取api列表
with open('config/api.yaml', 'r', encoding='utf-8') as f:
    result = yaml.load(f.read(), Loader=yaml.FullLoader)
chatGLM_api_key=result.get("chatGLM")
class CListen(threading.Thread):
    def __init__(self, loop):
        threading.Thread.__init__(self)
        self.mLoop = loop

    def run(self):
        asyncio.set_event_loop(self.mLoop)  # 在新线程中开启一个事件循环
        self.mLoop.run_forever()
with open('data/chatGLMCharacters.yaml', 'r', encoding='utf-8') as f:
    result2223 = yaml.load(f.read(), Loader=yaml.FullLoader)
global chatGLMCharacters
chatGLMCharacters = result2223


with open('config/chatGLM.yaml', 'r', encoding='utf-8') as f:
    result222 = yaml.load(f.read(), Loader=yaml.FullLoader)
global chatGLMapikeys
chatGLMapikeys = result222


with open('data/chatGLMData.yaml', 'r', encoding='utf-8') as f:
    cha = yaml.load(f.read(), Loader=yaml.FullLoader)
global chatGLMData
chatGLMData=cha
#logger.info(chatGLMData)
with open('config/noResponse.yaml', 'r', encoding='utf-8') as f:
    noRes1 = yaml.load(f.read(), Loader=yaml.FullLoader)
noRes=noRes1.get("noRes")

#读取用户别称



logger.info("正在启动rwkv对话模型")

logger.info("正在启动pandora_ChatGPT")

global pandoraData
with open('data/pandora_ChatGPT.yaml', 'r', encoding='utf-8') as file:
    pandoraData = yaml.load(file, Loader=yaml.FullLoader)
global totallink
totallink = False
with open('config/settings.yaml', 'r', encoding='utf-8') as f:
    result = yaml.load(f.read(), Loader=yaml.FullLoader)
trustDays=result.get("trustDays")
gptReply = result.get("gptReply")
pandoraa = result.get("pandora")
glmReply = result.get("chatGLM").get("glmReply")
trustglmReply = result.get("chatGLM").get("trustglmReply")
meta = result.get("chatGLM").get("bot_info").get("default")
context= result.get("chatGLM").get("context")
maxPrompt = result.get("chatGLM").get("maxPrompt")
allcharacters=result.get("chatGLM").get("bot_info")
turnMessage=result.get("wReply").get("turnMessage")
maxTextLen = result.get("chatGLM").get("maxLen")
voiceRate = result.get("chatGLM").get("voiceRate")
speaker = result.get("chatGLM").get("speaker")

with open('config.yaml', 'r', encoding='utf-8') as f:
    result = yaml.load(f.read(), Loader=yaml.FullLoader)
botName=result.get("botName")

with open('data/userData.yaml', 'r', encoding='utf-8') as file:
    data = yaml.load(file, Loader=yaml.FullLoader)
global trustUser
global userdict
userdict = data
trustUser = []
for i in userdict.keys():
    data = userdict.get(i)
    times = int(str(data.get('sts')))
    if times > trustDays:
        trustUser.append(str(i))

logger.info('chatglm部分已读取信任用户' + str(len(trustUser)) + '个')

#线程预备
newLoop = asyncio.new_event_loop()
listen = CListen(newLoop)
listen.setDaemon(True)
listen.start()
async def process3(msg,bot):
    logger.info("process3接收指令：")
    logger.info(msg.get("d").get('content').split("> ")[1])
    echo_funcs = [func for func in globals().values() if callable(func) and getattr(func, "is_echo", False)]
    # 使用asyncio.gather来同时执行它们，并获取它们的结果
    ass =await asyncio.gather(*[func(msg,bot) for func in echo_funcs])
    print(ass)
    for i in ass:
        if i!=None:
            await bot.send(msg,i)
            return
'''#私聊使用chatGLM,对信任用户或配置了apiKey的用户开启
@bot.on(FriendMessage)
async def GLMFriendChat(event:FriendMessage):
    global chatGLMData,chatGLMCharacters,trustUser,chatGLMsingelUserKey,userdict
    #如果用户有自己的key
    if msg.get("d").get('author').get("id") in chatGLMsingelUserKey:
        selfApiKey=chatGLMsingelUserKey.get(msg.get("d").get('author').get("id"))
        #构建prompt
    #或者开启了信任用户回复且为信任用户
    elif str(msg.get("d").get('author').get("id")) in trustUser and trustglmReply==True:
        logger.info("信任用户进行chatGLM提问")
        selfApiKey=chatGLM_api_key
    else:
        return
    if msg.get("d").get('content').split("> ")[1] == "/clearGLM":
        return
    text = msg.get("d").get('content').split("> ")[1]
    logger.info("私聊glm接收消息："+text)
    # 构建新的prompt
    tep = {"role": "user", "content": text}
    # print(type(tep))
    # 获取以往的prompt
    if msg.get("d").get('author').get("id") in chatGLMData:
        prompt = chatGLMData.get(msg.get("d").get('author').get("id"))
        prompt.append({"role": "user", "content": text})
    # 没有该用户，以本次对话作为prompt
    else:
        prompt = [tep]
        chatGLMData[msg.get("d").get('author').get("id")] = prompt
    if msg.get("d").get('author').get("id") in chatGLMCharacters:
        meta1 = chatGLMCharacters.get(msg.get("d").get('author').get("id"))
    else:
        logger.warning("读取meta模板")
        with open('config/settings.yaml', 'r', encoding='utf-8') as f:
            resy = yaml.load(f.read(), Loader=yaml.FullLoader)
        meta1 = resy.get("chatGLM").get("bot_info").get("default")

    try:
        setName = userdict.get(str(msg.get("d").get('author').get("id"))).get("userName")
    except:
        setName = event.sender.nickname
    if setName == None:
        setName = event.sender.nickname

    meta1["user_name"] = meta1.get("user_name").replace("指挥", setName)
    meta1["user_info"] = meta1.get("user_info").replace("指挥", setName).replace("yucca",botName)
    meta1["bot_info"] = meta1.get("bot_info").replace("指挥", setName).replace("yucca",botName)
    meta1["bot_name"] = botName

    try:
        logger.info("当前meta:" + str(meta1))
        #st1 = await chatGLM(selfApiKey, meta1, prompt)
        asyncio.run_coroutine_threadsafe(asyncchatGLM(selfApiKey, meta1, prompt, event, setName, text), newLoop)

    except:
        await bot.send(event, "chatGLM启动出错，请联系master检查apiKey或重试")

# 私聊中chatGLM清除本地缓存
@bot.on(FriendMessage)
async def clearPrompt(event: FriendMessage):
    global chatGLMData
    if msg.get("d").get('content').split("> ")[1] == "/clearGLM":
        try:
            chatGLMData.pop(msg.get("d").get('author').get("id"))
            # 写入文件
            with open('data/chatGLMData.yaml', 'w', encoding="utf-8") as file:
                yaml.dump(chatGLMData, file, allow_unicode=True)
            await bot.send(event,"已清除近期记忆")
        except:
            await bot.send(event, "清理缓存出错，无本地对话记录")

@bot.on(FriendMessage)
async def setChatGLMKey(event: FriendMessage):
    global chatGLMsingelUserKey
    if msg.get("d").get('content').split("> ")[1].startswith("设置密钥#"):
        key12 = msg.get("d").get('content').split("> ")[1].split("#")[1] + ""
        try:
            prompt = [{"user": "你好"}]
            st1 = chatGLM1(key12, meta, prompt)
            #st1 = st1.replace("yucca", botName).replace("liris", str(event.sender.nickname))
            await bot.send(event, st1, True)
        except:
            await bot.send(event, "chatGLM启动出错，请联系检查apiKey或重试")
            return
        chatGLMsingelUserKey[msg.get("d").get('author').get("id")] = key12
        with open('config/chatGLMSingelUser.yaml', 'w', encoding="utf-8") as file:
            yaml.dump(chatGLMsingelUserKey, file, allow_unicode=True)
        await bot.send(event, "设置apiKey成功")

@bot.on(FriendMessage)
async def setChatGLMKey(event: FriendMessage):
    global chatGLMsingelUserKey
    if msg.get("d").get('content').split("> ")[1].startswith("取消密钥") and msg.get("d").get('author').get("id") in chatGLMsingelUserKey:
        chatGLMsingelUserKey.pop(msg.get("d").get('author').get("id"))
        with open('config/chatGLMSingelUser.yaml', 'w', encoding="utf-8") as file:
            yaml.dump(chatGLMsingelUserKey, file, allow_unicode=True)
        await bot.send(event, "设置apiKey成功")
#私聊设置bot角色
# print(trustUser)
@bot.on(FriendMessage)
async def showCharacter(event:FriendMessage):
    if msg.get("d").get('content').split("> ")[1]=="可用角色模板" or "角色模板" in msg.get("d").get('content').split("> ")[1]:
        st1=""
        for isa in allcharacters:
            st1+=isa+"\n"
        await bot.send(event,"对话可用角色模板：\n"+st1+"\n发送：设定#角色名 以设定角色")
@bot.on(FriendMessage)
async def setCharacter(event:FriendMessage):
    global chatGLMCharacters
    if msg.get("d").get('content').split("> ")[1].startswith("设定#"):
        if msg.get("d").get('content').split("> ")[1].split("#")[1] in allcharacters:

            meta1 = allcharacters.get(msg.get("d").get('content').split("> ")[1].split("#")[1])

            try:
                setName = userdict.get(str(msg.get("d").get('author').get("id"))).get("userName")
            except:
                setName = event.sender.nickname
            if setName == None:
                setName = event.sender.nickname
            meta1["user_info"] = meta1.get("user_info").replace("指挥", setName).replace("yucca", botName)
            meta1["bot_info"] = meta1.get("bot_info").replace("指挥", setName).replace("yucca", botName)
            meta1["bot_name"] = botName
            meta1["user_name"] = setName
            chatGLMCharacters[msg.get("d").get('author').get("id")] = meta1

            logger.info("当前：",chatGLMCharacters)
            with open('data/chatGLMCharacters.yaml', 'w', encoding="utf-8") as file:
                yaml.dump(chatGLMCharacters, file, allow_unicode=True)
            await bot.send(event,"设定成功")
        else:
            await bot.send(event,"不存在的角色")'''



# print(trustUser)
@botOn
async def showCharacter(msg,bot):
    if msg.get("d").get('content').split("> ")[1]=="角色模板":
        st1=""
        for isa in allcharacters:
            st1+=isa+"\n"
        return "对话可用角色模板：\n"+st1+"\n发送：设定#角色名 以设定角色"
@botOn
async def setCharacter(msg,bot):
    global chatGLMCharacters,userdict
    if msg.get("d").get('content').split("> ")[1].startswith("设定#"):
        if msg.get("d").get('content').split("> ")[1].split("#")[1] in allcharacters:
            meta1=allcharacters.get(msg.get("d").get('content').split("> ")[1].split("#")[1])

            try:
                setName = userdict.get(str(msg.get("d").get('author').get("id"))).get("userName")
            except:
                setName = msg.get("d").get('author').get("id")
            if setName == None:
                setName = msg.get("d").get('author').get("id")
            meta1["user_name"] = meta1.get("user_name").replace("指挥", setName)
            meta1["user_info"] = meta1.get("user_info").replace("指挥", setName).replace("yucca", botName)
            meta1["bot_info"] = meta1.get("bot_info").replace("指挥", setName).replace("yucca", botName)
            meta1["bot_name"] = botName

            chatGLMCharacters[msg.get("d").get('author').get("id")] =meta1
            logger.info("当前：",chatGLMCharacters)
            with open('data/chatGLMCharacters.yaml', 'w', encoding="utf-8") as file:
                yaml.dump(chatGLMCharacters, file, allow_unicode=True)
            return "设定成功"
        else:
            return "不存在的角色"

'''@bot.on(Startup)
async def upDate(event: Startup):
    while True:
        await sleep(360)
        with open('config/chatGLM.yaml', 'r', encoding='utf-8') as f:
            result222 = yaml.load(f.read(), Loader=yaml.FullLoader)
        global chatGLMapikeys
        chatGLMapikeys = result222
        with open('data/userData.yaml', 'r', encoding='utf-8') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
        global trustUser
        global userdict
        userdict = data
        trustUser = []
        for i in userdict.keys():
            data = userdict.get(i)
            times = int(str(data.get('sts')))
            if times > trustDays:
                trustUser.append(str(i))
        logger.info('已读取信任用户' + str(len(trustUser)) + '个')'''


#群内chatGLM回复
@botOn
async def atReply(msg,bot):
    global trustUser, chatGLMapikeys,chatGLMData,chatGLMCharacters,chatGLMsingelUserKey,userdict
    if gptReply == True:
        asyncio.run_coroutine_threadsafe(askGPTT(msg),newLoop)

    elif glmReply == True:
        text = msg.get("d").get('content').split("> ")[1]
        logger.info("分支1")
        for saa in noRes:
            if text==saa or text=="/"+saa:
                logger.warning("与屏蔽词匹配，chatGLM不回复")
                return
        if text=="" or text==" ":
            text="在吗"
        #构建新的prompt
        tep={"role": "user","content": text}
        #print(type(tep))
        #获取以往的prompt
        if msg.get("d").get('author').get("id") in chatGLMData and context==True:
            prompt=chatGLMData.get(msg.get("d").get('author').get("id"))
            prompt.append({"role": "user","content": text})

        #没有该用户，以本次对话作为prompt
        else:
            prompt=[tep]
            chatGLMData[msg.get("d").get('author').get("id")] =prompt
        #logger.info("当前prompt"+str(prompt))

        selfApiKey = chatGLM_api_key

        #获取角色设定
        if msg.get("d").get('author').get("id") in chatGLMCharacters:
            meta1=chatGLMCharacters.get(msg.get("d").get('author').get("id"))
        else:
            logger.warning("读取meta模板")
            with open('config/settings.yaml', 'r', encoding='utf-8') as f:
                resy = yaml.load(f.read(), Loader=yaml.FullLoader)
            meta1 = resy.get("chatGLM").get("bot_info").get("default")
        try:
            setName = userdict.get(str(msg.get("d").get('author').get("id"))).get("userName")
        except:
            setName = msg.get("d").get('author').get('username')
        if setName == None:
            setName = msg.get("d").get('author').get('username')
        meta1["user_name"] = meta1.get("user_name").replace("指挥", setName)
        meta1["user_info"] = meta1.get("user_info").replace("指挥", setName).replace("yucca",botName)
        meta1["bot_info"]=meta1.get("bot_info").replace("指挥",setName).replace("yucca",botName)
        meta1["bot_name"]=botName

        logger.info("chatGLM接收提问:" + text)
        try:
            logger.info("当前meta:"+str(meta1))
            asyncio.run_coroutine_threadsafe(asyncchatGLM(selfApiKey, meta1, prompt, msg, setName, text,bot), newLoop)
            #st1 = await chatGLM(selfApiKey, meta1, prompt)


        except:
            return "chatGLM启动出错，请联系master检查apiKey或重试"

#用于chatGLM清除本地缓存
@botOn
async def clearPrompt(msg,bot):
    global chatGLMData
    if msg.get("d").get('content').split("> ")[1]=="/clearGLM":
        try:
            chatGLMData.pop(msg.get("d").get('author').get("id"))
            # 写入文件
            with open('data/chatGLMData.yaml', 'w', encoding="utf-8") as file:
                yaml.dump(chatGLMData, file, allow_unicode=True)
            return "已清除近期记忆"
        except:
            return "清理缓存出错，无本地对话记录"
'''@botOn
async def setChatGLMKey(msg):
    global chatGLMapikeys
    if msg.get("d").get('content').split("> ")[1].startswith("设置密钥#"):
        key12=msg.get("d").get('content').split("> ")[1].split("#")[1]+""
        try:
            prompt=[{"user":"你好"}]
            st1 = chatGLM1(key12, meta,prompt)
            #asyncio.run_coroutine_threadsafe(asyncchatGLM(key1, meta1, prompt, event, setName, text), newLoop)
            st1 = st1.replace("yucca", botName).replace("liris", str(msg.get("d").get('author').get("id")))
            return st1
        except:
            return "chatGLM启动出错，请联系检查apiKey或重试"

        chatGLMapikeys[event.group.id]=key12
        with open('config/chatGLM.yaml', 'w', encoding="utf-8") as file:
            yaml.dump(chatGLMapikeys, file, allow_unicode=True)
        await bot.send(event, "设置apiKey成功")

@botOn
async def setChatGLMKey(msg):
    global chatGLMapikeys
    if msg.get("d").get('content').split("> ")[1].startswith("取消密钥") and event.group.id in chatGLMapikeys:
        chatGLMapikeys.pop(event.group.id)
        with open('config/chatGLM.yaml', 'w', encoding="utf-8") as file:
            yaml.dump(chatGLMapikeys, file, allow_unicode=True)
        await bot.send(event, "设置apiKey成功")'''
@botOn
async def pandoraSever(msg,bot):
    global pandoraData

    if msg.get("d").get('content').split("> ")[1].startswith("/p"):
        if pandoraa:
            asyncio.run_coroutine_threadsafe(askGPTT(msg,bot), newLoop)
        return

@botOn
async def gpt3(msg,bot):
    if msg.get("d").get('content').split("> ")[1].startswith("/chat"):
        s = msg.get("d").get('content').split("> ")[1].replace("/chat", "")
        try:
            logger.info("gpt3.5接收信息：" + s)
            url = "https://api.lolimi.cn/API/AI/mfcat3.5.php?sx=你是一个可爱萝莉&msg="+s+"&type=json"
            async with httpx.AsyncClient(timeout=40) as client:
                # 用get方法发送请求
                response = await client.get(url=url)
            s=response.json().get("data")

            logger.info("gpt3.5:" + s)
            return s
        except:
            logger.error("调用gpt3.5失败，请检查网络或重试")
            return s
#科大讯飞星火ai
@botOn
async def gpt3(msg,bot):
    if msg.get("d").get('content').split("> ")[1].startswith("/xh"):
        s = msg.get("d").get('content').split("> ")[1].replace("/xh", "")
        try:
            logger.info("讯飞星火接收信息：" + s)
            url = "https://api.lolimi.cn/API/AI/xh.php?msg=" + s
            async with httpx.AsyncClient(timeout=40) as client:
                # 用get方法发送请求
                response = await client.get(url=url)
            s = response.json().get("data").get("output")

            logger.info("讯飞星火:" + s)
            return s
        except:
            logger.error("调用讯飞星火失败，请检查网络或重试")
            return "无法连接到讯飞星火，请检查网络或重试"

# 文心一言
@botOn
async def gpt3(msg,bot):
    if msg.get("d").get('content').split("> ")[1].startswith("/wx"):
        s = msg.get("d").get('content').split("> ")[1].replace("/wx", "")
        try:
            logger.info("文心一言接收信息：" + s)
            url = "https://api.lolimi.cn/API/AI/wx.php?msg=" + s
            async with httpx.AsyncClient(timeout=40) as client:
                # 用get方法发送请求
                response = await client.get(url=url)
            s = response.json().get("data").get("output")

            logger.info("文心一言:" + s)
            return s
        except:
            logger.error("调用文心一言失败，请检查网络或重试")
            return "无法连接到文心一言，请检查网络或重试"

@botOn
async def rwkv(msg,bot):
    if msg.get("d").get('content').split("> ")[1].startswith("/rwkv"):
        s = msg.get("d").get('content').split("> ")[1].replace("/rwkv", "")
        try:
            logger.info("rwkv接收信息：" + s)
            s = await rwkvHelper(s)
            logger.info("rwkv:" + s)
            return s
        except:
            logger.error("调用rwkv失败，请检查本地rwkv是否启动或端口是否配置正确(8000)")
            return "无法连接到本地rwkv"

async def askGPTT(msg,bot):
    global trustUser, chatGLMapikeys, chatGLMData, chatGLMCharacters, chatGLMsingelUserKey, userdict
    if msg.get("d").get('content').startswith("/"):
        prompt=msg.get("d").get('content').replace("/","")
    else:
        prompt = msg.get("d").get('content').split("> ")[1]


    message_id = str(uuid.uuid4())
    model = "text-davinci-002-render-sha"
    logger.info("ask:" + prompt)
    if msg.get("d").get('author').get("id") in pandoraData.keys():
        pub = msg.get("d").get('author').get("id")
        conversation_id = pandoraData.get(msg.get("d").get('author').get("id")).get("conversation_id")
        parent_message_id = pandoraData.get(msg.get("d").get('author').get("id")).get("parent_message_id")
    else:
        if len(pandoraData.keys()) < 10:
            pub = msg.get("d").get('author').get("id")
            conversation_id = None
            parent_message_id = "f0bf0ebe-1cd6-4067-9264-8a40af76d00e"
        else:
            try:
                pub = random.choice(pandoraData.keys())
                conversation_id = pandoraData.get(pub).get("conversation_id")
                parent_message_id = pandoraData.get(pub).get("parent_message_id")
            except:
                return "当前服务器负载过大，请稍后再试"
    try:
        loop = asyncio.get_event_loop()
        # 使用 loop.run_in_executor() 方法来将同步函数转换为异步非阻塞的方式进行处理
        # 第一个参数是执行器，可以是 None、ThreadPoolExecutor 或 ProcessPoolExecutor
        # 第二个参数是同步函数名，后面跟着任何你需要传递的参数
        # result=chatGLM(apiKey,bot_info,prompt)
        parent_message_id, conversation_id, response_message = await loop.run_in_executor(None, ask_chatgpt, prompt, model, message_id,parent_message_id,conversation_id)

        logger.info("answer:" + response_message)
        logger.info("conversation_id:" + conversation_id)
        await bot.send(msg,response_message)

        pandoraData[pub] = {"parent_message_id": parent_message_id, "conversation_id": conversation_id}
        with open('data/pandora_ChatGPT.yaml', 'w', encoding="utf-8") as file:
            yaml.dump(pandoraData, file, allow_unicode=True)
    except:
        await bot.send(msg, "当前服务器负载过大，请稍后再试")





#CharacterchatGLM部分
def chatGLM(api_key,bot_info,prompt,model1):
    logger.info("当前模式:"+model1)
    zhipuai.api_key = api_key
    if model1=="chatglm_pro":
        response = zhipuai.model_api.sse_invoke(
            model="chatglm_pro",
            prompt=prompt,
            temperature=0.95,
            top_p=0.7,
            incremental=True
        )
    elif model1=="chatglm_std":
        response = zhipuai.model_api.sse_invoke(
            model="chatglm_std",
            prompt=prompt,
            temperature=0.95,
            top_p=0.7,
            incremental=True
        )
    elif model1=="chatglm_lite":
        response = zhipuai.model_api.sse_invoke(
            model="chatglm_lite",
            prompt=prompt,
            temperature=0.95,
            top_p=0.7,
        )
    else:
        response = zhipuai.model_api.sse_invoke(
            model="characterglm",
            meta= bot_info,
            prompt= prompt,
            incremental=True
        )
    str1=""
    for event in response.events():
      if event.event == "add":
          str1+=event.data
          #print(event.data)
      elif event.event == "error" or event.event == "interrupted":
          str1 += event.data
          #print(event.data)
      elif event.event == "finish":
          str1 += event.data
          #print(event.data)
          print(event.meta)
      else:
          str1 += event.data
          #print(event.data)
    logger.info(str1)
    return str1
# 创建一个异步函数
async def asyncchatGLM(apiKey,bot_info,prompt,msg,setName,text,bot):
    global chatGLMData

    loop = asyncio.get_event_loop()
    # 使用 loop.run_in_executor() 方法来将同步函数转换为异步非阻塞的方式进行处理
    # 第一个参数是执行器，可以是 None、ThreadPoolExecutor 或 ProcessPoolExecutor
    # 第二个参数是同步函数名，后面跟着任何你需要传递的参数
    #result=chatGLM(apiKey,bot_info,prompt)
    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    model1 = result.get("chatGLM").get("model")
    logger.info("发送提问请求......")
    st1 = await loop.run_in_executor(None, chatGLM,apiKey,bot_info,prompt,model1)

    if len(st1)<maxTextLen and random.randint(0,100)<voiceRate:
        with open('config/bert_vits2.yaml', 'r', encoding='utf-8') as f:
            result = yaml.load(f.read(), Loader=yaml.FullLoader)
        data1=result.get(speaker)
        logger.info("调用bert_vits语音回复")
        path = bot.cur_dir.replace("\\", "/") + "/data/voices/" + random_str() + ".wav"
        print(path)
        data1["text"] = st1
        data1["out"] = path
        await taffySayTest(data1)
    else:
        logger.info("接收回复：" + st1)
        await bot.send(msg,st1)
    if len(st1) > 670:
        await bot.send(msg, "system:当前prompt过长，将不记录本次回复\n建议发送 /clearGLM 以清除聊天内容")
        try:
            prompt.remove(prompt[-1])
            chatGLMData[msg.get("d").get('author').get("id")]=prompt
        except:
            logger.error("chatGLM删除上一次对话失败")
        return

    logger.info("chatGLM:" + st1)

    if context == True:
        # 更新该用户prompt
        prompt.append({"role": "assistant", "content": st1})
        # 超过10，移除第一个元素

        if len(prompt) > maxPrompt:
            logger.error("glm prompt超限，移除元素")
            del prompt[0]
            del prompt[0]
        chatGLMData[msg.get("d").get('author').get("id")] = prompt
        # 写入文件
        with open('data/chatGLMData.yaml', 'w', encoding="utf-8") as file:
            yaml.dump(chatGLMData, file, allow_unicode=True)


    # 运行异步函数




if __name__ == '__main__':



    while True:
        input("任意键以结束")