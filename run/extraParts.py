# -*- coding: utf-8 -*-
import asyncio
import json
import os
import datetime
import random
import re
import time
import sys
import socket
from asyncio import sleep

import httpx
import requests
import yaml

from avidya.bot import givemeLogger, botOn
from plugins.RandomStr import random_str
from plugins.arkOperator import arkOperator
from plugins.genshinGo import genshinDraw, qianCao
from plugins.historicalToday import hisToday
from plugins.jokeMaker import get_joke
from plugins.newsEveryDay import sd
from plugins.picGet import picDwn
from plugins.translater import translate

'''from plugins import weatherQuery
from plugins.RandomStr import random_str
from plugins.arkOperator import arkOperator
from plugins.cpGenerate import get_cp_mesg
from plugins.gacha import arkGacha, starRailGacha
from plugins.genshinGo import genshinDraw, qianCao
from plugins.historicalToday import hisToday
from plugins.imgDownload import dict_download_img
from plugins.jokeMaker import get_joke

#from plugins.modelsLoader import modelLoader
from plugins.newsEveryDay import news, moyu, xingzuo, sd
from plugins.picGet import pic, setuGet, picDwn
from plugins.tarot import tarotChoice
from plugins.translater import translate
from plugins.vitsGenerate import voiceGenerate
from plugins.webScreenShoot import webScreenShoot, screenshot_to_pdf_and_png'''

logger=givemeLogger()

# 读取api列表
with open('config/api.yaml', 'r', encoding='utf-8') as f:
    result = yaml.load(f.read(), Loader=yaml.FullLoader)
app_id = result.get("youdao").get("app_id")
app_key = result.get("youdao").get("app_key")  # 有道翻译api
proxy = result.get("proxy")
nasa_api = result.get("nasa_api")
api_KEY=result.get("weatherXinZhi")
with open('config/settings.yaml', 'r', encoding='utf-8') as f:
    resulta = yaml.load(f.read(), Loader=yaml.FullLoader)
pandora = resulta.get("pandora")

logger.info("读取到apiKey列表")
logger.info("额外的功能 启动完成")
with open("data/odes.json",encoding="utf-8") as fp:
    odes=json.loads(fp.read())
with open("data/IChing.json",encoding="utf-8") as fp:
    IChing=json.loads(fp.read())
global data
with open('data/nasaTasks.yaml', 'r',encoding='utf-8') as file:
    data = yaml.load(file, Loader=yaml.FullLoader)
with open('data/userData.yaml', 'r',encoding='utf-8') as file:
    data1 = yaml.load(file, Loader=yaml.FullLoader)
global trustUser
userdict = data1
trustUser = []
for i in userdict.keys():
    data2 = userdict.get(i)
    times = int(str(data2.get('sts')))
    if times > 8:
        trustUser.append(str(i))
with open('config/settings.yaml', 'r', encoding='utf-8') as f:
    result1 = yaml.load(f.read(), Loader=yaml.FullLoader)
r18 = result1.get("r18Pic")
global picData
picData={}
async def process2(msg,bot):
    logger.info("process2接收指令：")
    logger.info(msg.get("d").get('content').split("> ")[1])
    echo_funcs = [func for func in globals().values() if callable(func) and getattr(func, "is_echo", False)]
    # 使用asyncio.gather来同时执行它们，并获取它们的结果
    ass =await asyncio.gather(*[func(msg) for func in echo_funcs])
    print(ass)
    for i in ass:
        if i!=None:
            await bot.send(msg,i)
            return

'''@botOn
async def update(msg):
    while True:
        await sleep(300)
        logger.info("更新用户数据")
        with open('data/userData.yaml', 'r', encoding='utf-8') as file:
            data1 = yaml.load(file, Loader=yaml.FullLoader)
        global trustUser
        userdict = data1
        trustUser = []
        for i in userdict.keys():
            data3 = userdict.get(i)
            times = int(str(data3.get('sts')))
            if times > 20:
                trustUser.append(str(i))'''

@botOn
async def handle_group_message(msg):
    pattern = r".*壁纸|壁纸.*"
    if msg.get("d").get('content').startswith("/"):
        string=msg.get("d").get('content').replace("/","")
    else:
        string = msg.get("d").get('content').split("> ")[1]
    match = re.search(pattern, string)
    if match:
        url="https://iw233.cn/api.php?sort=random"
        return {"image":url}


# 整点正则
pattern = r".*(壁纸|图|pic).*(\d+).*|.*(\d+).*(壁纸|图|pic).*"

# 定义一个函数，使用正则表达式检查字符串是否符合条件，并提取数字
def get_number(string):
    # 使用re.match方法，返回匹配的结果对象
    match = re.match(pattern, string)
    # 如果结果对象不为空，返回捕获的数字，否则返回None
    if match:
        # 如果第二个分组有值，返回第二个分组，否则返回第三个分组
        if match.group(2):
            return match.group(2)
        else:
            return match.group(3)
    else:
        return None
'''@bot.on(GroupMessage)
async def setuHelper(event:GroupMessage):
    pattern1 = r'(\d+)张(\w+)'
    global picData
    if At(bot.qq) in event.message_chain:
        text1=msg.get("d").get('content').split(">")[1].replace("壁纸","").replace("涩图","").replace("色图","").replace("图","").replace("r18","")
        match1 = re.search(pattern1, text1)
        if match1:
            logger.info("提取图片关键字。 数量: "+str(match1.group(1))+" 关键字: "+match1.group(2))
            data={"tag":""}
            if "r18" in msg.get("d").get('content').split(">")[1] or "色图" in msg.get("d").get('content').split(">")[1] or "涩图" in msg.get("d").get('content').split(">")[1]:
                if str(event.sender.id) in trustUser and r18==True :
                    data["r18"]=1
                else:
                    await bot.send(event,"r18模式已关闭")
            picData[event.sender.id]=[]
            data["tag"]=match1.group(2)
            data["size"] = "regular"
            logger.info("组装数据完成："+str(data))
            a=int(match1.group(1))
            if int(match1.group(1))>6:
                a=5
                await bot.send(event,"api访问限制，修改获取张数为 5")
            for i in range(a):
                try:
                    path=await setuGet(data)
                except:
                    logger.error("涩图请求出错")
                    await bot.send(event,"请求出错，请稍后再试")
                    return
                logger.info("发送图片: "+path)
                try:
                    await bot.send(event, Image(url=path))
                    logger.info("图片发送成功")
                except:
                    logger.error("图片发送失败")
                    await bot.send(event,path)'''
                


@botOn
async def historyToday(msg):
    pattern = r".*史.*今.*|.*今.*史.*"
    if msg.get("d").get('content').startswith("/"):
        string = msg.get("d").get('content').replace("/", "")
    else:
        string = msg.get("d").get('content').split("> ")[1]
    match = re.search(pattern, string)
    if match:
        dataBack=await hisToday()
        logger.info("获取历史上的今天")
        logger.info(str(dataBack))
        sendData=str(dataBack.get("result")).replace("["," ").replace("{'year': '","").replace("'}","").replace("]","").replace("', 'title': '"," ").replace(",","\n").replace("\n 2023 感谢 www.ipip5.com 提供数据支持!","")
        return sendData

'''@botOn
async def weather_query(msg):
    # 从消息链中取出文本
    msg = "".join(map(str, event.message_chain[Plain]))
    # 匹配指令
    m = re.match(r'^查询\s*(\w+)\s*$', msg.strip())
    if m:
        # 取出指令中的地名
        city = m.group(1)
        logger.info("查询 "+city+" 天气")
        await bot.send(event, '查询中……')
        # 发送天气消息
        await bot.send(event, await weatherQuery.querys(city,api_KEY))
@bot.on(GroupMessage)
async def newsToday(event:GroupMessage):
    if ("新闻" in msg.get("d").get('content').split(">")[1] and At(bot.qq) in event.message_chain) or msg.get("d").get('content').split(">")[1]=="新闻":
        logger.info("获取新闻")
        path=await news()
        logger.info("成功获取到今日新闻")
        await bot.send(event,Image(path=path))

@bot.on(GroupMessage)
async def moyuToday(event: GroupMessage):
    if ("摸鱼" in msg.get("d").get('content').split(">")[1] and At(bot.qq) in event.message_chain) or msg.get("d").get('content').split(">")[1]=="摸鱼":
        logger.info("获取摸鱼人日历")
        path = await moyu()
        logger.info("成功获取到摸鱼人日历")
        await bot.send(event, Image(path=path))

@bot.on(GroupMessage)
async def moyuToday(event: GroupMessage):
    if ("星座" in msg.get("d").get('content').split(">")[1] and At(bot.qq) in event.message_chain) or msg.get("d").get('content').split(">")[1] == "星座":
        logger.info("获取星座运势")
        path = await xingzuo()
        logger.info("成功获取到星座运势")
        await bot.send(event, Image(path=path))'''

@botOn
async def make_jokes(msg):
    if msg.get("d").get('content').split("> ")[1].endswith('笑话'):
        x = msg.get("d").get('content').split(">")[1].strip()[1:-2]
        joke = get_joke(x)
        logger.info(joke)
        return joke

# 凑个cp
@botOn
async def make_cp_mesg(msg):
    if msg.get("d").get('content').split(">")[1].startswith("/cp "):
        x = msg.get("d").get('content').split(">")[1].replace('/cp ', '', 1)
        x = x.split(' ')
        if len(x) != 2:
            #path = '../data/voices/' + random_str() + '.wav'
            text='エラーが発生しました。再入力してください'
            return text
            '''tex = '[JA]' + text + '[JA]'
            logger.info("启动文本转语音：text: " + tex + " path: " + path[3:])
            await voiceGenerate({"text": tex, "out": path})
            await bot.send(event, Voice(path=path))'''

        mesg = get_cp_mesg(x[0], x[1])
        return mesg

@botOn
async def NasaHelper(msg):
    global data
    if "今日天文" in msg.get("d").get('content').split(">")[1]:
        logger.info(str(data.keys()))
        if datetime.datetime.now().strftime('%Y-%m-%d') in data.keys():
            todayNasa=data.get(datetime.datetime.now().strftime('%Y-%m-%d'))
            path=todayNasa.get("path")
            txt=todayNasa.get("transTxt")
            return txt
            '''try:
                await bot.send(event, (Image(path=path), txt))
            except:
                await bot.send(event,txt)'''
        else:
            proxies = {
                "http://": proxy,
                "https://": proxy
            }
            # Replace the key with your own
            dataa = {"api_key": nasa_api}
            logger.info("发起nasa请求")
            try:
                # 拼接url和参数
                url = "https://api.nasa.gov/planetary/apod?" + "&".join([f"{k}={v}" for k, v in dataa.items()])
                async with httpx.AsyncClient(proxies=proxies) as client:
                    # 用get方法发送请求
                    response = await client.get(url=url)
                # response = requests.post(url="https://saucenao.com/search.php", data=dataa, proxies=proxies)
                logger.info("获取到结果" + str(response.json()))
                # logger.info("下载缩略图")
                filename = await picDwn(response.json().get("url"), "data/pictures/nasa/"+response.json().get("date")+".png")
                txta=await translate(response.json().get("explanation"),app_id=app_id,app_key=app_key,ori="en",aim="zh-CHS")
                txt = response.json().get("date") + "\n" + response.json().get("title") + "\n" + txta
                temp={"path":"data/pictures/nasa/"+response.json().get("date")+".png","oriTxt":response.json().get("explanation"),"transTxt":txt}

                data[datetime.datetime.now().strftime('%Y-%m-%d')]=temp

                with open('data/nasaTasks.yaml', 'w', encoding="utf-8") as file:
                    yaml.dump(data, file, allow_unicode=True)
                return txt
                #await bot.send(event,(Image(path=filename),txt))

            except:
                logger.warning("获取每日天文图片失败")
                return "获取失败，请联系master检查代理或api_key是否可用"
@botOn
async def arkGene(msg):
    if "干员" in msg.get("d").get('content').split(">")[1] and "生成" in msg.get("d").get('content').split(">")[1]:
        logger.info("又有皱皮了，生成干员信息中.....")
        o=arkOperator()
        o=o.replace("为生成",msg.get("d").get("member").get('nick'))
        return o

@botOn
async def genshin12(msg):
    pattern = r".*原神抽签"
    if msg.get("d").get('content').startswith("/"):
        string=msg.get("d").get('content').replace("/","")
    else:
        string = msg.get("d").get('content').split("> ")[1]
    match = re.search(pattern, string)
    if match:
        url = "https://iw233.cn/api.php?sort=random"
        return {"image": url}
        logger.info("有原皮！获取抽签信息中....")
        o = genshinDraw()
        logger.info("\n"+o)
        return o

@botOn
async def genshin1(msg):
    pattern = r".*抽签|抽签.*"
    if msg.get("d").get('content').startswith("/"):
        string=msg.get("d").get('content').replace("/","")
    else:
        string = msg.get("d").get('content').split("> ")[1]
    match = re.search(pattern, string)
    if match:
        url = "https://iw233.cn/api.php?sort=random"
        return {"image": url}
        logger.info("获取浅草百签")
        o = qianCao()
        logger.info(o)
        return o
@botOn
async def shijing(msg):
    pattern = r".*诗经|诗经.*"
    if msg.get("d").get('content').startswith("/"):
        string=msg.get("d").get('content').replace("/","")
    else:
        string = msg.get("d").get('content').split("> ")[1]
    match = re.search(pattern, string)
    if match:
        url = "https://iw233.cn/api.php?sort=random"
        return {"image": url}
        logger.info("获取一篇诗经")
        ode=random.choice(odes.get("诗经"))
        logger.info("\n"+ode)
        return ode

@botOn
async def NasaHelper(msg):
    pattern = r".*周易|周易.*"
    if msg.get("d").get('content').startswith("/"):
        string=msg.get("d").get('content').replace("/","")
    else:
        string = msg.get("d").get('content').split("> ")[1]
    match = re.search(pattern, string)
    if match:
        logger.info("获取卦象")
        IChing1 = random.choice(IChing.get("六十四卦"))
        logger.info("\n" + IChing1)
        return IChing1

'''@bot.on(GroupMessage)
async def screenShoot(event: GroupMessage):
    if msg.get("d").get('content').split(">")[1].startswith("截图#"):
        url=msg.get("d").get('content').split(">")[1].split("#")[1]
        path="data/pictures/cache/"+random_str()+".png"
        logger.info("接收网页截图任务url:"+url)
        try:
            await screenshot_to_pdf_and_png(url, path)
        except:
            logger.error("截图失败!")
        await bot.send(event, Image(path=path), True)'''


@botOn
async def jiangzhuang(msg):
    if msg.get("d").get('content').split("> ")[1].startswith("奖状"):
        try:
            t=msg.get("d").get('content').split(">")[1][3:].split("#").replace(" ","")
            url="https://api.pearktrue.cn/api/certcommend/?name="+t[0]+"&title="+t[1]+"&classname="+t[2]

            #p=await sd(url,"data/pictures/cache/"+random_str()+".png")
            return {"image":url}
        except:
            return "出错，格式请按照：奖状 孙笑川#天皇#阳光小学一年级2班"
'''@bot.on(GroupMessage)
async def moyuToday(event: GroupMessage):
    if ("方舟十连" in msg.get("d").get('content').split(">")[1] and At(bot.qq) in event.message_chain) or msg.get("d").get('content').split(">")[1] == "方舟十连":
        logger.info("获取方舟抽卡结果")
        try:
            path = await arkGacha()
            logger.info("成功获取到抽卡结果")
            await bot.send(event, Image(path=path),True)
        except:
            logger.error("皱皮衮")
            await bot.send(event,"获取抽卡结果失败，请稍后再试")
@bot.on(GroupMessage)
async def moyuToday(event: GroupMessage):
    if ("星铁十连" in msg.get("d").get('content').split(">")[1] and At(bot.qq) in event.message_chain) or msg.get("d").get('content').split(">")[1] == "星铁十连":
        logger.info("获取星铁抽卡结果")
        try:
            path = await starRailGacha()
            logger.info("成功获取到星铁抽卡结果")
            await bot.send(event, Image(path=path),True)
        except:
            logger.error("穹批衮")
            await bot.send(event,"获取抽卡结果失败，请稍后再试")'''
