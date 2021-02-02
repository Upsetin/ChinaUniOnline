'''
Function:
    大学生在线 "四史"自动答题刷分
Author:
    XWhite
GitHub项目地址:
    https://github.com/Upsetin/ChinaUniOnline
更新日期:
    2021-01-10
'''

import requests,csv,re,json,random,time


def ViewQR(url=''):
    html = requests.get(url)
    with open('QR.png', 'wb') as file:
        file.write(html.content)

    import platform
    userPlatform=platform.system()						# 获取操作系统
    fileDir='QR.png'

    if userPlatform == 'Darwin':								# Mac
        import subprocess
        subprocess.call(['open', fileDir])
    elif userPlatform == 'Linux':								# Linux
        import subprocess
        subprocess.call(['xdg-open', fileDir])
    else:																# Windows
        import os
        os.startfile(fileDir)


def ReadFile():
    with open("题库.csv", "r") as f:
        reader = csv.reader(f)
        db = []
        for row in list(reader):
            db.append(row)
    return db


def IntoFile(FileNmae = '题库.csv',Data=[]):
    file = open(FileNmae, 'a', encoding='utf-8')
    f = csv.writer(file)
    f.writerow(
        Data
    )
    print('已写入%s文件:'%(FileNmae),Data)
    file.close()


def GetQuestions(activity_id='5f71e934bcdbf3a8c3ba5061',mode_id='5f71e934bcdbf3a8c3ba51d5'):

    url = "https://ssxx.univs.cn/cgi-bin/race/beginning/?t=1612247769&activity_id=%s&mode_id=%s&way=1"%(activity_id,mode_id)

    payload = {}
    headers = {
        'authority': 'ssxx.univs.cn',
        'sec-ch-ua': '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
        'accept': 'application/json, text/plain, */*',
        'authorization': 'Bearer %s'%(token),
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://ssxx.univs.cn/client/exam/5f71e934bcdbf3a8c3ba5061/1/1/5f71e934bcdbf3a8c3ba51d5',
        'accept-language': 'zh,en;q=0.9,zh-CN;q=0.8',
        'cookie': '_ga=GA1.2.79005828.1612243540; _gid=GA1.2.1602430105.1612243540; tgw_l7_route=be2f17e6fbcb3e6c5202ac57e388ad5a; _gat=1'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    # print(response.json())
    question_ids = response.json()['question_ids']
    num = 0
    SucessNum = 0
    FailNum = 0
    for i in question_ids:
        num += 1
        if GetOption(activity_id=activity_id,question_id=i,mode_id=mode_id):
            SucessNum += 1
        else:
            FailNum += 1
    race_code = response.json()['race_code']
    Finsh(race_code)
    print('此次成功查询%s个题，收录%s个题'%(SucessNum,FailNum))


def GetOption(activity_id='5f71e934bcdbf3a8c3ba5061',question_id='5f17ef305d6fe02504ba5e17',mode_id='5f71e934bcdbf3a8c3ba51d5'):

    url = "https://ssxx.univs.cn/cgi-bin/race/question/?t=1612247250&activity_id=%s&question_id=%s&mode_id=%s&way=1"%(activity_id,question_id,mode_id)

    payload = {}
    headers = {
        'authority': 'ssxx.univs.cn',
        'sec-ch-ua': '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
        'accept': 'application/json, text/plain, */*',
        'authorization': 'Bearer %s'%(token),
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://ssxx.univs.cn/client/exam/5f71e934bcdbf3a8c3ba5061/1/1/5f71e934bcdbf3a8c3ba51d5',
        'accept-language': 'zh,en;q=0.9,zh-CN;q=0.8',
        'cookie': '_ga=GA1.2.79005828.1612243540; _gid=GA1.2.1602430105.1612243540; tgw_l7_route=be2f17e6fbcb3e6c5202ac57e388ad5a'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    # print(response.json())

    options = response.json()['data']['options']
    #选项
    result = {}
    for i in options:
        title = i['title']
        replace1 = re.findall('<.*?>', title)
        for j in range(len(replace1)):
            if 'display:none;' in replace1[j] or 'display: none;' in replace1[j]:
                replace2 = re.findall('%s.*?%s' % (replace1[j], replace1[j + 1]), title)
                title = str(title).replace(replace2[0], '')
        for j in replace1:
            title = str(title).replace(j, '')
        result[title] = i['id']
    # print(result)

    #题目
    title = response.json()['data']['title']
    replace1 = re.findall('<.*?>',title)
    for i in range(len(replace1)):
        if 'display:none;' in replace1[i] or 'display: none;' in replace1[i]:
            replace2 = re.findall('%s.*?%s'%(replace1[i],replace1[i+1]),title)
            title = str(title).replace(replace2[0],'')
    for i in replace1:
        title = str(title).replace(i,'')
    # print(title)

    '''判断题目是否已在题库中'''
    db = ReadFile()
    for i in db:
        #在题库中
        if title in i[0]:
            print('在题库中已搜索到答案: %s - %s'%(i[0],i[1]))
            answer = []
            for j,k in result.items():
                if j in i[1]:
                    answer.append(k)
            #提交答案
            Confire(question_id=question_id,answer=answer)
            return 'Sucess'
    #题库中没有
    print('未在题库中搜索到答案，执行捕获题目模式...')
    results = SreachResult(question_id=question_id, answer=response.json()['data']['options'][0]['id'])
    TrueResult = []
    for i in results:
        for j,k in result.items():
            if i == k:
                TrueResult.append(j)
    num = 0
    for i in db:
        if title in i:
            num += 1
            break
    if not num:
        IntoFile(FileNmae = '题库.csv',Data=[title,TrueResult])
    else:
        print('已存在题库中: ',title[0],TrueResult)


def SreachResult(question_id='5f17ef305d6fe02504ba5e17',answer='5f75fe348e6c9f85d1b6072a',activity_id='5f71e934bcdbf3a8c3ba5061',mode_id='5f71e934bcdbf3a8c3ba51d5'):

    url = "https://ssxx.univs.cn/cgi-bin/race/answer/"

    payload = "{\"activity_id\":\"%s\",\"question_id\":\"%s\",\"answer\":[\"%s\"],\"mode_id\":\"%s\",\"way\":\"1\"}"%(activity_id,question_id,answer,mode_id)
    headers = {
        'authority': 'ssxx.univs.cn',
        'sec-ch-ua': '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
        'accept': 'application/json, text/plain, */*',
        'authorization': 'Bearer %s'%(token),
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36',
        'content-type': 'application/json;charset=UTF-8',
        'origin': 'https://ssxx.univs.cn',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://ssxx.univs.cn/client/exam/5f71e934bcdbf3a8c3ba5061/1/1/5f71e934bcdbf3a8c3ba51d5',
        'accept-language': 'zh,en;q=0.9,zh-CN;q=0.8',
        'cookie': '_ga=GA1.2.79005828.1612243540; _gid=GA1.2.1602430105.1612243540; tgw_l7_route=be2f17e6fbcb3e6c5202ac57e388ad5a'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    data = response.json()
    # print(data)
    return response.json()['data']['correct_ids']


def Confire(question_id='5f17ef305d6fe02504ba5e17',answer=['5f75fe348e6c9f85d1b6072a'],activity_id='5f71e934bcdbf3a8c3ba5061',mode_id='5f71e934bcdbf3a8c3ba51d5'):

    url = "https://ssxx.univs.cn/cgi-bin/race/answer/"

    payload = '{"activity_id":"%s","question_id":"%s","answer":%s,"mode_id":"%s","way":"1"}'%(activity_id,question_id,json.dumps(answer),mode_id)


    headers = {
        'authority': 'ssxx.univs.cn',
        'sec-ch-ua': '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
        'accept': 'application/json, text/plain, */*',
        'authorization': 'Bearer %s'%(token),
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36',
        'content-type': 'application/json;charset=UTF-8',
        'origin': 'https://ssxx.univs.cn',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://ssxx.univs.cn/client/exam/5f71e934bcdbf3a8c3ba5061/1/1/5f71e934bcdbf3a8c3ba51d5',
        'accept-language': 'zh,en;q=0.9,zh-CN;q=0.8',
        'cookie': '_ga=GA1.2.79005828.1612243540; _gid=GA1.2.1602430105.1612243540; tgw_l7_route=be2f17e6fbcb3e6c5202ac57e388ad5a'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    data = response.json()
    # print(data)
    return response.json()['data']['correct_ids']


def Finsh(race_code='6018f697224c6a1526204144'):

    url = "https://ssxx.univs.cn/cgi-bin/race/finish/"

    payload = "{\"race_code\":\"%s\"}"%(race_code)
    headers = {
        'authority': 'ssxx.univs.cn',
        'sec-ch-ua': '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
        'accept': 'application/json, text/plain, */*',
        'authorization': 'Bearer %s'%(token),
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36',
        'content-type': 'application/json;charset=UTF-8',
        'origin': 'https://ssxx.univs.cn',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://ssxx.univs.cn/client/exam/5f71e934bcdbf3a8c3ba5061/1/1/5f71e934bcdbf3a8c3ba51d5',
        'accept-language': 'zh,en;q=0.9,zh-CN;q=0.8',
        'cookie': '_ga=GA1.2.79005828.1612243540; _gid=GA1.2.1602430105.1612243540; tgw_l7_route=be2f17e6fbcb3e6c5202ac57e388ad5a'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    # print(response.json())
    try:
        print('已提交,正确数:%s 用时:%ss'%(response.json()['data']['owner']['correct_amount'],response.json()['data']['owner']['consume_time']))
    except:
        print(response.json())


def PK10(activity_id='5f71e934bcdbf3a8c3ba5061',mode_id='5f71e934bcdbf3a8c3ba51da'):
    import requests

    url = "https://ssxx.univs.cn/cgi-bin/race/beginning/?t=1612260314&activity_id=%s&mode_id=%s&way=1"%(activity_id,mode_id)

    payload = {}
    headers = {
        'authority': 'ssxx.univs.cn',
        'sec-ch-ua': '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
        'accept': 'application/json, text/plain, */*',
        'authorization': 'Bearer %s'%(token),
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://ssxx.univs.cn/client/exam/5f71e934bcdbf3a8c3ba5061/3/1/5f71e934bcdbf3a8c3ba51da',
        'accept-language': 'zh,en;q=0.9,zh-CN;q=0.8',
        'cookie': '_ga=GA1.2.79005828.1612243540; _gid=GA1.2.1602430105.1612243540; tgw_l7_route=09fcb686b72bcf8a19fb9f044a5a52d5; _gat=1'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.json())

    question_ids = response.json()['question_ids']
    num = 0
    SucessNum = 0
    FailNum = 0
    for i in question_ids:
        num += 1
        if GetOption(activity_id=activity_id, question_id=i, mode_id=mode_id):
            SucessNum += 1
        else:
            FailNum += 1
    race_code = response.json()['race_code']
    Finsh(race_code)
    print('此次成功查询%s个题，收录%s个题' % (SucessNum, FailNum))


def Login():
    print('正在获取登陆二维码...')
    Random = ''.join(random.sample('qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890',random.randrange(5,10)))
    url = 'https://oauth.u.hep.com.cn/oauth/wxapp/qrcode/5f582dd3683c2e0ae3aaacee?random=%s&useSelfWxapp=true&enableFetchPhone=false'%(Random)
    a = requests.get(url)
    print("请用微信扫描二维码登陆...")
    ViewQR(a.json()['data']['qrcode'])
    print('\r正在等待扫描二维码...',end='\r')
    time.sleep(3)
    TimeNum = 1
    while True:
        print('\r正在等待扫描二维码,已等待%ss...'%(TimeNum),end='')
        a = requests.post('https://oauth.u.hep.com.cn/oauth/wxapp/confirm/qr?random=%s&useSelfWxapp=true'%(Random))
        if a.json()['data']['code'] == 200:
            _id = a.json()['data']['data']['_id']
            print('\n欢迎你,%s'%(a.json()['data']['data']['username']))
            GetToken(uid=_id)
            break
        time.sleep(1)
        print('\r',end='')
        TimeNum += 1

def GetToken(uid='6018e5d37fc77f3d90194078'):
    url = 'https://ssxx.univs.cn/cgi-bin/authorize/token/?t=1612276118&uid=%s'%(uid)
    a = requests.get(url=url)
    global token
    token = a.json()['token']
    print(token)


token = ''
Login()

# PK10()
EndNum = int(input("暂只适配英雄篇,请输入的刷题次数 (55次稳上1000分): "))
num = 0
while num < EndNum:
    num += 1
    print('\n英雄篇-正在第%s次刷题～'%(num))
    GetQuestions()

