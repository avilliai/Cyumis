
import asyncio
import json

import httpx
import requests

#定义bot类
from avidya.botlogger import newLogger

logger=newLogger()
def givemeLogger():
    return logger
def botOn(func):
    func.is_echo = True
    return func
class Bot:
    # 定义一个构造方法，用来初始化对象的属性
    def __init__(self, botid, botsecret,master,cur_dir):
        self.appId = str(botid)   # 实例变量，用self修饰
        self.appSecret = botsecret  # 实例变量，用self修饰
        self.token=self.getToken()  # 重要变量，自动更新token
        self.wsUrl=self.getWsConnUrl()
        self.ws=None
        self.logger=logger
        self.master=master
        self.cur_dir=cur_dir
        self.mode="channel"

    def getToken(self):
        ass=requests.post(url="https://bots.qq.com/app/getAppAccessToken",headers={'Content-Type': 'application/json'},json={"appId": self.appId,"clientSecret": self.appSecret}).json()
        return ass.get("access_token")
    # 定义一个协程函数，用来每隔60秒更新一次token
    async def update_token(self):
        while True:
            # 调用getToken方法，更新token
            self.token = self.getToken()
            # 暂停60秒
            await asyncio.sleep(60)
    #获取必要headers用于身份认证
    def getHeahers(self):
        headers={'Authorization': "QQBot "+self.token,'X-Union-Appid': self.appId}
        return headers
    def getWsConnUrl(self):
        try:
            wsConn=requests.get("https://api.sgroup.qq.com/gateway",headers=self.getHeahers()).json()
            #logger.info(wsConn)
            wsConn=wsConn.get("url")
            logger.info("获取ws接入点"+wsConn)
            return wsConn
        except Exception as e:
            logger.error(e)
    async def send(self,event,mes):
        if self.mode=="channel":
            await self.send_channel_message(event,mes)
    async def send_channel_message(self,event,mes):
        url="https://api.sgroup.qq.com/channels/"+event.get("d").get("channel_id")+"/messages"
        data={}
        if type(mes)==str:
            data["content"]=mes
        else:
            data=mes
        try:
            data["id"]=event.get("id")
        except:
            pass
        logger.info("发送消息"+str(data))
        #print(requests.post(url,headers=self.getHeahers(),data=data))
        async with httpx.AsyncClient() as client:
            await client.post(url, headers=self.getHeahers(), data=data)

    '''async def send_channel_friend_message(self,event,mes):
        url="https://api.sgroup.qq.com/channels/"+event.get("d").get("channel_id")+"/messages"
        data={}
        if type(mes)==str:
            data["content"]=mes
        else:
            data=mes
        try:
            data["id"]=event.get("id").replace("AT_MESSAGE_CREATE:","")
        except:
            pass
        logger.info("url:"+url+"   发送消息"+str(data))
        requests.post(url,headers=self.getHeahers(),data=data)
        async with httpx.AsyncClient(headers=self.getHeahers()) as client:
            await client.post(url,data=json.dumps(data))'''



#print(a.token)