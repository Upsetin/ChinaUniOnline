import os
import sys
import sqlite3
import json
import base64
import random
import time
import string
import logging
import requests
from PyQt6 import QtGui
from PyQt6.QtGui import QMouseEvent, QPixmap, QRegularExpressionValidator
from PyQt6.QtCore import QObject, QRegularExpression, QThread, Qt, pyqtBoundSignal, pyqtSignal
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto.Cipher import PKCS1_v1_5 as Cipher
from Crypto.Signature import PKCS1_v1_5 as Signature
from PyQt6.QtWidgets import QApplication, QCheckBox, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget
from bs4 import BeautifulSoup
os.chdir(os.path.split(os.path.realpath(__file__))[0])
# 将工作目录转移到脚本所在目录，保证下面的相对路径都能正确找到文件
class EnhancedEdit(QLineEdit):
    # 一个自定义QLineEdit，可以在失去焦点时传递信号，用于更新配置
    lostFocus=pyqtSignal()
    def __init__(self):
        super().__init__()
    def focusOutEvent(self, a0: QtGui.QFocusEvent) -> None:
        self.lostFocus.emit()
        return super().focusOutEvent(a0)
class QLogger(logging.Handler):
    # 一个自定义logging handler，用于在GUI中显示日志内容
    def __init__(self,update_signal:pyqtBoundSignal):
        super().__init__()
        self.widget=QPlainTextEdit()
        self.widget.setReadOnly(True)
        self.update_signal=update_signal
    def emit(self,record):
        msg=self.format(record)
        self.update_signal.emit(msg)
    def scroll_widget_to_bottom(self):
        self.widget.verticalScrollBar().setSliderPosition(self.widget.verticalScrollBar().maximum())
class TestProcessor():
    def __init__(self,show_qr_signal:pyqtBoundSignal,close_qr_signal:pyqtBoundSignal):
        self.logger=logging.getLogger(__name__)
        with open(file="config.json",mode="r",encoding="utf-8") as conf_reader:
            self.conf=json.loads(conf_reader.read())
        self.session=requests.sessions.session()
        default_headers={
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.74",
            "Referer":"https://ssxx.univs.cn/",
            "Accept":"application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin":"https://ssxx.univs.cn"
            }
        self.session.headers.update(default_headers)
        proxy=self.conf["proxy"]
        if proxy!="":
            self.session.proxies.update({"http":proxy,"https":proxy})
        self.activity_id="5f71e934bcdbf3a8c3ba5061"
        self.client="5f582dd3683c2e0ae3aaacee"
        while True:
            random_="".join(random.sample(string.digits+string.ascii_letters,random.randrange(20,21))) # FAJ25n9gl2mXEkGgrljtq
            self.logger.debug("random=%s" %random_)
            self.logger.info("正在获取二维码")
            # fxxk腾讯！这参数的True和False得用文本，还区分大小写
            params={"random":random_,"useSelfWxapp":"true","enableFetchPhone":"false"}
            json_response=self.session.get("https://oauth.u.hep.com.cn/oauth/wxapp/qrcode/%s" %self.client,params=params).json()
            self.logger.debug("response=%s" %json_response)
            if json_response["data"]["success"]==True:
                self.logger.error("此二维码已被使用过")
            else:
                self.logger.debug("此二维码未被使用过")
                break
            time.sleep(0.5)
        qr=json_response["data"]["qrcode"]
        self.logger.debug("qr=%s" %qr)
        oauth=json_response["data"]["oauth"] # 5a8009b491d78d0001d43ed3
        oauth_with_application=json_response["data"]["oauthWithApplication"] # 5f59d15b513ef417b544c0ed
        self.session.headers.update({"Accept":"image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8"})
        show_qr_signal.emit(self.session.get(qr).content)
        self.session.headers.update({"Accept":"application/json, text/plain, */*"})
        while True:
            try:
                post_data={"random":random_,"useSelfWxapp":"true"}
                json_response=self.session.post("https://oauth.u.hep.com.cn/oauth/wxapp/confirm/qr",params=post_data).json()
            except:
                self.logger.error("确认QR码扫描状态过程中传输数据出错，将继续")
            else:
                if json_response["data"]["code"]==200:
                    salt=json_response["data"]["data"]["salt"] # 0kibedg2ei2b5
                    _id=json_response["data"]["data"]["_id"] # 5fc8400785e70a5d71bd2c44
                    unionid=json_response["data"]["data"]["unionid"] # oTzSV0g53KTuiT5utMgMvvzgB1qw
                    username=json_response["data"]["data"]["username"] # zhanghua
                    self.token=json_response["data"]["data"]["token"]
                    params={"t":str(int(time.time())),"uid":_id}
                    json_response=self.session.get("https://ssxx.univs.cn/cgi-bin/authorize/token/",params=params).json()
                    self.token=json_response["token"]
                    self.refresh_token=json_response["refresh_token"]
                    self.logger.info("用户 %s 登陆成功" %(username))
                    self.logger.debug("token=%s" %self.token)
                    close_qr_signal.emit()
                    break
                elif json_response["data"]["code"]==500:
                    self.logger.debug("本次轮询二维码验证结果失败，继续等待")
                time.sleep(1.0)
            finally:
                self.logger.debug("response=%s" %json_response)
        headers={
            "Referer":"https://ssxx.univs.cn/clientLogin?redirect=/client/detail/%s" %self.activity_id,
            "Authorization":"Bearer %s" %self.token}
        self.session.headers.update(headers)
        params={"t":str(int(time.time()))}
        json_response=self.session.get("https://ssxx.univs.cn/cgi-bin/portal/user/",params=params).json()
        self.logger.debug("获取用户信息：%s" %json_response)
        name=json_response["data"]["name"]
        university_name=json_response["data"]["university_name"]
        id_=json_response["data"]["id"]
        code=json_response["data"]["code"]
        zip_=json_response["data"]["zip"]
        mobile=json_response["data"]["mobile"]
        self.logger.info("用户 %s 来自 %s，手机号 %s" %(name,university_name,zip_+" "+mobile))
        self.session.headers.update({"Referer": "https://ssxx.univs.cn/client/detail/%s" %(self.activity_id)})
        params={"t":str(int(time.time())),"id":self.activity_id}
        json_response=self.session.get("https://ssxx.univs.cn/cgi-bin/portal/activity/",params=params).json()
        self.activity_id=json_response["data"]["id"]
        params={"t":str(int(time.time())),"activity_id":self.activity_id}
        json_response=self.session.get("https://ssxx.univs.cn/cgi-bin/portal/race/mode/",params=params).json()
        modes=json_response["data"]["modes"]
        self.ids={}
        for mode in modes:
            self.ids[mode["id"]]={"title":mode["title"],"enabled":self.is_enabled(title=mode["title"]),"times":self.times(title=mode["title"])}
    def is_enabled(self,title:str):
        for key in self.conf.keys():
            if type(self.conf[key])==dict and self.conf[key]["title"]==title:
                return True
        return False
    def times(self,title:str):
        for key in self.conf.keys():
            if type(self.conf[key])==dict and self.conf[key]["title"]==title:
                return int(self.conf[key]["times"])
    def start(self):
        conn=sqlite3.connect("answers.db")
        self.cur=conn.cursor()
        self.logger.debug("已启动数据库连接")
        for key in self.ids.keys():
            title=self.ids[key]["title"]
            enabled=self.ids[key]["enabled"]
            times=self.ids[key]["times"]
            if enabled==True:
                for i in range(times):
                    self.logger.info("正在处理第 %d 次的 %s" %(i+1,title))
                    self.process(mode_id=key)
            else:
                self.logger.info("%s 已跳过" %title)
        self.session.close()
        self.logger.debug("已关闭Session")
        conn.commit()
        self.cur.close()
        conn.close()
        self.logger.debug("已关闭数据库连接")
    def process(self,mode_id:str):
        headers={"Referer":"https://ssxx.univs.cn/client/exam/%s/1/1/%s" %(self.activity_id,mode_id),}
        self.session.headers.update(headers)
        params={"t":str(int(time.time())),"activity_id":self.activity_id,"mode_id":mode_id,"way":"1"}
        json_response=self.session.get("https://ssxx.univs.cn/cgi-bin/race/beginning/",params=params).json()
        self.logger.debug("获取题目数据：%s" %json_response)
        question_ids=json_response["question_ids"]
        num=0
        SuccessNum=0
        FailNum=0
        for question_id in question_ids:
            i=question_ids.index(question_id)
            num=num+1
            if i==10:
                if self.check_verify(mode_id=mode_id)==True:
                    self.logger.info("验证码已通过或无验证码")
                else:
                    self.submit_verify(mode_id=mode_id)
                    self.logger.info("当前验证码状态：%s" %self.check_verify(mode_id=mode_id))
            if self.get_option(activity_id=self.activity_id,question_id=question_id,mode_id=mode_id)==True:
                SuccessNum=SuccessNum+1
                self.logger.info("第 %d 道题目成功" %(i+1))
            else:
                FailNum=FailNum+1
                self.logger.info("第 %d 道题目失败" %(i+1))
        race_code=json_response["race_code"]
        self.finish(race_code=race_code,activity_id=self.activity_id,mode_id=mode_id)
        self.logger.info("此次成功查询 %d 个题，收录 %d 个题" %(SuccessNum,FailNum))
    def check_verify(self,mode_id):
        # 这里的code和下面的code应该是利用self.encrypt_with_pubkey()加密的结果
        timestamp=int(time.time())
        string_=str(timestamp)
        code=self.encrypt_with_pubkey(string=string_,time_=timestamp)
        self.logger.debug("encrypted_code=%s" %code)

        code="E5ZKeoD8xezW4TVEn20JVHPFVJkBIfPg+zvMGW+kx1s29cUNFfNka1+1Fr7lUWsyUQhjiZXHDcUhbOYJLK4rS5MflFUvwSwd1B+1kul06t1z9x0mfxQZYggbnrJe3PKEk4etwG/rm3s3FFJd/EbFSdanfslt41aULzJzSIJ/HWI="

        post_data={"activity_id":self.activity_id,"mode_id":mode_id,"way":"1","code":code}
        json_response=self.session.post("https://ssxx.univs.cn/cgi-bin/check/verification/code/",json=post_data).json()
        return bool(json_response["status"])
    def submit_verify(self,mode_id):

        code="HD1bhUGI4d/FhRfIX4m972tZ0g3jRHIwH23ajyre9m1Jxyw4CQ1bMKeIG5T/voFOsKLmnazWkPe6yBbr+juVcMkPwqyafu4JCDePPsVEbVSjLt8OsiMgjloG1fPKANShQCHAX6BwpK33pEe8jSx55l3Ruz/HfcSjDLEHCATdKs4="

        post_data={"activity_id":self.activity_id,"mode_id":mode_id,"way":"1","code":code}
        json_response=self.session.post("https://ssxx.univs.cn/cgi-bin/save/verification/code/",json=post_data).json()
        if json_response["code"]!=0:
            self.logger.error("提交验证码失败")
            self.submit_verify(mode_id=mode_id)
        else:
            self.logger.info("提交验证码成功")
    def get_option(self,activity_id,question_id,mode_id):
        params={"t":str(int(time.time())),"activity_id":activity_id,"question_id":question_id,"mode_id":mode_id,"way":"1"}
        json_response=self.session.get("https://ssxx.univs.cn/cgi-bin/race/question/",params=params).json()
        self.logger.debug("获取选项信息：%s" %json_response)
        # 选项
        options_=json_response["data"]["options"]
        op_result={}
        title=str()
        answers=list()
        for option_ in options_:
            answers.append(option_["id"])
            op_title=self.clean_element(string_=option_["title"])
            op_result[option_['id']] = op_title
            # {id:title}
        self.logger.debug("获取选项信息：%s" %op_result)
        # 题目
        title=self.clean_element(string_=json_response['data']['title'])
        self.logger.debug("获取标题信息：%s" %title)
        answer=self.search_ans(mode_id=mode_id,question=title)
        self.logger.debug("选择项目：%s" %op_result)
        if answer!=[]:
            self.logger.info("来自数据库的答案：%s" %answer)
            answer_ids=list()
            for answer_title in answer:
                for answer_id in answers:
                    if answer_title in op_result[answer_id]:
                        answer_ids.append(answer_id)
            self.logger.debug("正确答案的ID列表：%s" %answer_ids)
            return self.process_ans(question_id=question_id,answer_ids=answer_ids,mode_id=mode_id,activity_id=self.activity_id,catch=False)
        else:
            caught_answer=self.process_ans(question_id=question_id,activity_id=activity_id,mode_id=mode_id,answer_ids=answers,catch=True)
            if caught_answer!=None:
                self.logger.debug("已捕获的答案：%s" %caught_answer)
                answer_titles=list()
                for caught_answer_id in caught_answer:
                    for answer_id in op_result.keys():
                        if answer_id==caught_answer_id:
                            answer_titles.append(op_result[caught_answer_id].strip())
                self.logger.info("正确答案的可读名称列表：%s" %answer_titles)
                if len(answer_titles)==1:
                    answer_str=answer_titles[0]
                else:
                    answer_str="#".join(answer_titles)
                self.update_database(question=title,mode_id=mode_id,answer=answer_str)
                self.logger.info("捕获正确答案并更新数据库成功")
            else:
                raise RuntimeError("捕获答案出错，查看日志以获得更多信息")
    def update_database(self,question:str,mode_id:str,answer:str):
        self.logger.debug("正在加入条目 QUESTION=%s,ANSWER=%s 到表%s中" %(question,answer,mode_id))
        try:
            res=self.cur.execute("SELECT ANSWER FROM '%s' WHERE QUESTION='%s'" %(mode_id,question)).fetchone()
        except sqlite3.OperationalError:
            self.logger.error("查询数据库失败，正在尝试创建表")
            try:
                self.cur.execute("CREATE TABLE '%s' (QUESTION TEXT NOT NULL UNIQUE,ANSWER TEXT NOT NULL)" %mode_id)
            except sqlite3.OperationalError:
                self.logger.error("数据库内已存在表，数据库受损？")
                raise RuntimeError("数据库已受损，需要手动修复")
            else:
                self.cur.execute("INSERT INTO '%s' (QUESTION,ANSWER) VALUES ('%s','%s')" %(mode_id,question,answer))
                self.logger.debug("已创建表并加入数据库条目")
        else:
            self.logger.debug("search_result=%s" %res)
            if res==None:
                self.cur.execute("INSERT INTO '%s' (QUESTION,ANSWER) VALUES ('%s','%s')" %(mode_id,question,answer))
                self.logger.debug("已加入数据库条目")
            else:
                self.cur.execute("UPDATE '%s' SET QUESTION = '%s', ANSWER = '%s'" %(mode_id,question,answer))
                self.logger.debug("已更新数据库条目")
    def process_ans(self,question_id:str,activity_id:str,mode_id:str,answer_ids:list,catch:bool=False):
        data={"activity_id":activity_id,"question_id":question_id,"answer":None,"mode_id":mode_id,"way":"1"}
        if catch==True:
            data["answer"]=[random.choice(answer_ids)]
            prefix="catch"
        else:
            data["answer"]=answer_ids
            prefix="submit"
        self.logger.debug("data=%s" %data)
        json_response=self.session.post("https://ssxx.univs.cn/cgi-bin/race/answer/",json=data).json()
        self.logger.debug("%s_response=%s" %(prefix,json_response))
        if json_response["code"]==0 and catch==True:
            return json_response["data"]["correct_ids"]
        elif json_response["code"]==0 and catch==False:
            return json_response["data"]["correct"]
    def clean_element(self,string_:str):
        # 清除元素中不显示（contains(@style,display:none)）的部分以获得正常的题目和选项
        # 使用 BeautifilSoup解析
        cleaned=0
        soup=BeautifulSoup(string_,"html.parser")
        selectors=["display:none;","display: none"]
        for each_selector in selectors:
            elements=soup.select("[style*=\"%s\"]" %each_selector)
            for element in elements:
                element.extract()
                cleaned=cleaned+1
        self.logger.debug("共清理 %d 个干扰元素" %cleaned)
        return soup.get_text()
    def search_ans(self,mode_id:str,question:str):
        # 数据要求：一个问题对应一个答案，整张表内应该不存在同名问题，
        # 多个答案用#组合为一个字符串，查询时将自动按#切割为列表，无答案返回空列表
        try:
            res=self.cur.execute("SELECT ANSWER from '%s' WHERE QUESTION='%s'" %(mode_id,question)).fetchone()
        except sqlite3.OperationalError:
            self.logger.error("查询SQL数据库出错")
        else:
            if res!=None:
                return str(res[0]).split("#")
        return []
    def finish(self,activity_id:str,mode_id:str,race_code:str):
        payload={
            "race_code":race_code
        }
        json_response=self.session.post("https://ssxx.univs.cn/cgi-bin/race/finish/",json=payload).json()
        self.logger.debug(json_response)
        if json_response["code"]==4823:
            self.submit_verify(mode_id=mode_id)
            self.finish(activity_id=activity_id,mode_id=mode_id,race_code=race_code)
        elif json_response["code"]==0:
            owner=json_response["data"]["owner"]
            self.logger.info("执行完成，正确数：%d，答题用时：%d 秒" %(owner["correct_amount"],owner["consume_time"]))
            if json_response["data"]["opponent"]!={}:
                opponent=json_response["data"]["opponent"]
                self.logger.info("处于对战模式，对方信息：来自 %s 的 %s，正确数 %d，用时 %d秒" %(opponent["univ_name"],opponent["name"],opponent["correct_amount"],opponent["consume_time"]))
        else:
            self.logger.error("提交失败，请在调试模式下查看服务器返回数据以确定问题")
    def encrypt_with_pubkey(self,string:str,time_:int=int(time.time())):
        params={"t":time_}
        json_response=self.session.get("https://ssxx.univs.cn/cgi-bin/base/public/key/",params=params).json()
        pubkey=RSA.import_key(json_response["data"]["public_key"])
        cipher=Cipher.new(pubkey)
        string_e=base64.b64encode(cipher.encrypt(string.encode())).decode()
        return string_e
    def verify_with_pubkey(self,string:str,signature:str,time_:int=int(time.time())):
        params={"t":time_}
        json_response=self.session.get("https://ssxx.univs.cn/cgi-bin/base/public/key/",params=params).json()
        pubkey=RSA.import_key(json_response["data"]["public_key"])
        verifier=Signature.new(pubkey)
        digest=SHA.new()
        digest.update(string.encode())
        try:
            verifier.verify(digest,signature.encode())
        except ValueError:
            return False
        else:
            return True
class Work(QObject):
    def __init__(self,show_qr_signal:pyqtBoundSignal,finish_signal:pyqtBoundSignal,close_qr_signal:pyqtBoundSignal):
        super().__init__()
        self.finish_signal=finish_signal
        self.show_qr_signal=show_qr_signal
        self.close_qr_signal=close_qr_signal
        self.logger=logging.getLogger(__name__)
    def start(self):
        self.logger.debug("正在启动子线程")
        self.processor=TestProcessor(show_qr_signal=self.show_qr_signal,close_qr_signal=self.close_qr_signal)
        self.logger.debug("已实例化处理类")
        self.processor.start()
        self.finish_signal.emit()
        self.logger.debug("已提交终止信号")
class SettingWindow(QDialog):
    def __init__(self,parent:QWidget):
        super().__init__()
        self.logger=logging.getLogger(__name__)
        with open(file="config.json",mode="r",encoding="utf-8") as conf_reader:
            self.conf=json.loads(conf_reader.read())
        self.logger.debug("初始化设置界面。设置内容：%s" %self.conf)
        layout=QGridLayout()
        self.setLayout(layout)
        self.setModal(True)
        self.setParent(parent)
        self.resize(400,300)
        title=QLabel("设置")
        title.setStyleSheet("QLabel{border:none;border-radius:5px;background:transparent;color:#9AD3BC;font-size:20px;}")
        title.setAlignment(Qt.Alignment.AlignCenter)
        layout.addWidget(title,0,1,Qt.Alignment.AlignCenter)
        control_close=QPushButton()
        control_close.setStyleSheet("QPushButton{background:#FFE3ED;border-radius:5px;border:none;}QPushButton:hover{background:#EC524B;}")
        control_close.setToolTip("关闭")
        control_close.setFixedHeight(20)
        control_close.clicked.connect(self.close_callback)
        layout.addWidget(control_close,0,0)
        debug_check=QCheckBox("调试模式")
        debug_check.setChecked(self.conf["debug"])
        debug_check.setToolTip("单击切换开关状态")
        debug_check.setStyleSheet("QCheckBox::indicator{width:10px;height:10px;border:none;border-radius:5px;background:#9BE3DE;}QCheckBox::indicator:unchecked{background:#BEEBE9;}QCheckBox::indicator:unchecked:hover{background:#9AD3BC;}QCheckBox::indicator:checked{background:#95E1D3;}QCheckBox::indicator:checked:hover{background:#98DED9;}")
        self.content=QGridLayout()
        (x,y)=self.show_setting(conf=self.conf,layout=self.content)# 返回content的最后一个元素的x,y
        proxy=QGroupBox()
        proxy.setObjectName("proxy")
        proxy_layout=QVBoxLayout()
        proxy_label=QLabel("代理地址：")
        proxy_label.setStyleSheet("QLabel{background:transparent;border:none;}")
        proxy_input=EnhancedEdit()
        proxy_input.setText(self.conf["proxy"])
        proxy_input.setToolTip("格式为协议://IP:端口，留空保持直连")
        proxy_input.setStyleSheet("QLineEdit{border:1px solid #F3EAC2;border-radius:5px;background:transparent;}QLineEdit:hover{border:1px solid #F5B461;}")
        proxy_layout.addWidget(proxy_label)
        proxy_layout.addWidget(proxy_input)
        proxy.setLayout(proxy_layout)
        proxy.setStyleSheet("QGroupBox{border-radius:5px;}")
        proxy.setToolTip("代理设置")
        if y+1>=3:
            y_=0
            x_=x+1
        else:
            y_=y+1
            x_=x
        self.content.addWidget(proxy,x_,y_)
        self.content.addWidget(debug_check)
        layout.addLayout(self.content,1,1)
    def close_callback(self):
        self.save_settings()
        self.logger.debug("已保存设置")
        self.close()
    def save_settings(self):
        settings=dict()
        enabled=True
        times=1
        for i in range(self.content.count()):
            layoutitem=self.content.itemAt(i)
            if type(layoutitem.widget())==QCheckBox:
                settings["debug"]=layoutitem.widget().isChecked()
            elif type(layoutitem.widget())==QGroupBox:
                group=layoutitem.widget()
                for j in group.children():
                    if group.objectName()=="proxy":
                        data=""
                        if type(j)==EnhancedEdit:
                            data=str(j.text())
                    else:
                        if type(j)==QCheckBox:
                            enabled=j.isChecked()
                        elif type(j)==EnhancedEdit:
                            times=int(j.text())
                        data={"title":group.title(),"enabled":enabled,"times":times}
                    settings[group.objectName()]=data
        self.logger.debug("设置数据：%s" %settings)
        with open(file="config.json",mode="w",encoding="utf-8") as conf_writer:
            conf_writer.write(json.dumps(settings,ensure_ascii=False,sort_keys=True,indent=4))
    def show_setting(self,conf:dict,layout:QGridLayout):
        groups=list()
        x=0
        y=0
        shape=3
        for key in conf.keys():
            if type(conf[key])==bool or type(conf[key])==str:
                continue
            conf_title=conf[key]["title"]
            conf_enabled=conf[key]["enabled"]
            conf_times=conf[key]["times"]
            group=QGroupBox(conf_title)
            group.setStyleSheet("QGroupBox{border-radius:5px;}")
            group.setToolTip(conf_title+"  的设置")
            enabled=QCheckBox("启用")
            enabled.setObjectName(key)
            enabled.setToolTip("单击切换开关状态")
            enabled.setChecked(conf_enabled)
            enabled.setStyleSheet("QCheckBox::indicator{width:10px;height:10px;border:none;border-radius:5px;background:#9BE3DE;}QCheckBox::indicator:unchecked{background:#BEEBE9;}QCheckBox::indicator:unchecked:hover{background:#9AD3BC;}QCheckBox::indicator:checked{background:#95E1D3;}QCheckBox::indicator:checked:hover{background:#98DED9;}")
            times=QHBoxLayout()
            times_label=QLabel("次数：")
            times_label.setStyleSheet("QLabel{background:transparent;border:none;border-radius:5px;}")
            times_input=EnhancedEdit()
            times_input.setObjectName(key)
            times_input.setText(str(conf_times))
            times_input.setToolTip("仅限正整数")
            times_input.setValidator(QRegularExpressionValidator(QRegularExpression("^[1-9][0-9]{1,8}$")))
            times_input.setStyleSheet("QLineEdit{border:1px solid #F3EAC2;border-radius:5px;background:transparent;}QLineEdit:hover{border:1px solid #F5B461;}")
            times.addWidget(times_label)
            times.addWidget(times_input)
            group_layout=QVBoxLayout()
            group_layout.addWidget(enabled)
            group_layout.addLayout(times)
            group.setLayout(group_layout)
            group.setObjectName(key)
            groups.append(group)
        for group in groups:
            if y>=shape:
                x=x+1
                y=0
            layout.addWidget(group,x,y)
            y=y+1
        self.logger.debug("最后的元素位置：(%d,%d)" %(x,y))
        return (x,y)
class UI(QWidget):
    update_signal=pyqtSignal(str)
    show_qr_signal=pyqtSignal(bytes)
    finish_signal=pyqtSignal()
    close_qr_signal=pyqtSignal()
    def __init__(self):
        super().__init__()
        self.logger=logging.getLogger(__name__)
        formatter=logging.Formatter(fmt="%(asctime)s-%(levelname)s-%(message)s",datefmt="%Y-%m-%d %H:%M:%S")
        filehandler=logging.FileHandler(filename="logs.log",mode="w",encoding="utf-8")
        handler=QLogger(update_signal=self.update_signal)
        handler.setLevel(logging.INFO)
        filehandler.setLevel(logging.INFO)
        self.logger.setLevel(logging.INFO)
        if os.path.exists("config.json")==False:
            self.gen_conf()
        with open(file="config.json",mode="r",encoding="utf-8") as conf_reader:
            conf=json.loads(conf_reader.read())
        debug=bool(conf["debug"])
        if debug==True:
            handler.setLevel(logging.DEBUG)
            filehandler.setLevel(logging.DEBUG)
            self.logger.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)
        filehandler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.addHandler(filehandler)
        self.logger.debug("当前调试状态：%s" %debug)
        self.resize(1024,768)
        self.setWindowOpacity(0.9)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlag(Qt.WindowFlags.FramelessWindowHint)
        self.setAutoFillBackground(True)
        self.work=Work(show_qr_signal=self.show_qr_signal,finish_signal=self.finish_signal,close_qr_signal=self.close_qr_signal)
        self.work_thread=QThread()
        self.work.moveToThread(self.work_thread)
        self.main_layout=QGridLayout()
        self.setLayout(self.main_layout)
        self.title=QLabel("ChinaUniOnlineGUI")
        self.title.setStyleSheet("QLabel{border:none;border-radius:5px;background:transparent;color:#9AD3BC;font-size:60px;}")
        self.title.setAlignment(Qt.Alignment.AlignCenter)
        handler.widget.setStyleSheet("QPlainTextEdit{font-family:Microsoft YaHei;background:#F3EAC2;border:none;border-radius:5px;}QScrollBar:vertical,QScrollBar::handle:vertical{background:#F3EAC2;border:none;border-radius:8px;width:16px;}QScrollBar::handle:vertical:hover{background:#F5B461;}QScrollBar::add-page:vertical,QScrollBar::sub-page:vertical{background:#FFFDF9;border:none;border-radius:8px;width:16px;}QScrollBar::down-arrow:vertical,QScrollBar::up-arrow:vertical{background:#F5B461;border:none;border-radius:8px;width:16px;height:16px;}QScrollBar::sub-line:vertical,QScrollBar::add-line:vertical{background:transparent;border:none;}")
        self.control=QVBoxLayout()
        self.control_close=QPushButton()
        self.control_close.setToolTip("关闭")
        self.control_close.setStyleSheet("QPushButton{background:#FFE3ED;border-radius:5px;border:none;}QPushButton:hover{background:#EC524B;}")
        self.contron_max=QPushButton()
        if self.isMaximized()==False:
            self.contron_max.setToolTip("最大化")
        else:
            self.contron_max.setToolTip("还原")
        self.contron_max.setStyleSheet("QPushButton{background:#FFFDF9;border-radius:5px;border:none;}QPushButton:hover{background:#F5B461;}")
        self.control_min=QPushButton()
        self.control_min.setToolTip("最小化")
        self.control_min.setStyleSheet("QPushButton{background:#BEEBE9;border-radius:5px;border:none;}QPushButton:hover{background:#F3EAC2;}")
        self.start_button=QPushButton("开始(&S)")
        self.start_button.setStyleSheet("QPushButton{background:#9BE3DE;border:none;border-radius:5px;font-size:20px;font-family:DengXian;}QPushButton:hover{background:#9AD3BC;}")
        self.start_button.setToolTip("开始")
        self.start_button.setFixedSize(120,60)
        self.start_button.setDefault(True)
        setting_button=QPushButton("设置")
        setting_button.setToolTip("设置")
        setting_button.setFixedSize(60,60)
        setting_button.setStyleSheet("QPushButton{background:#9BE3DE;border:none;border-radius:5px;font-size:20px;font-family:DengXian;}QPushButton:hover{background:#9AD3BC;}")
        setting_button.clicked.connect(self.setting_callback)
        start=QHBoxLayout()
        start.addWidget(self.start_button,2)
        start.addWidget(setting_button,1)
        self.control_close.clicked.connect(self.close)
        self.control_min.clicked.connect(self.min_callback)
        self.contron_max.clicked.connect(self.max_callback)
        self.start_button.clicked.connect(self.start_callback)
        self.work_thread.started.connect(self.work.start)
        self.finish_signal.connect(self.finish_callback)
        self.close_qr_signal.connect(self.close_qr)
        self.control.addWidget(self.control_min)
        self.control.addWidget(self.contron_max)
        self.control.addWidget(self.control_close)
        self.main_layout.addLayout(self.control,0,0)
        self.main_layout.addWidget(self.title,0,1)
        self.main_layout.addLayout(start,0,2)
        self.main_layout.addWidget(handler.widget,1,1)
        self.update_signal.connect(handler.widget.appendPlainText)
        handler.widget.textChanged.connect(handler.scroll_widget_to_bottom)
        self.show_qr_signal.connect(self.show_qr)
        self.logger.debug("已初始化UI")
    def min_callback(self):
        if self.isMinimized()==False:
            self.showMinimized()
    def max_callback(self):
        if self.isMaximized()==False:
            self.showMaximized()
            self.contron_max.setToolTip("还原")
        else:
            self.showNormal()
            self.contron_max.setToolTip("最大化")
    def start_callback(self):
        self.start_time=time.time()
        self.work_thread.start()
        self.start_button.setEnabled(False)
        self.start_button.setText("执行中...")
    def finish_callback(self):
        self.start_button.setEnabled(True)
        self.start_button.setText("开始")
        passed_time=time.time()-self.start_time
        mins,secs=divmod(passed_time,60)
        hours,mins=divmod(mins,60)
        self.logger.info("执行完成，共计用时 {:0>2d}:{:0>2d}:{:0>2d}".format(int(hours),int(mins),int(secs)))
    def show_qr(self,qr:bytes):
        title_label=QLabel("请使用微信扫描小程序码完成登陆")
        title_label.setStyleSheet("QLabel{color:#ffe3ed;border:none;background-color:transparent;border-radius:5px;}")
        title_label.setAlignment(Qt.Alignment.AlignCenter)
        title_label.setFixedHeight(20)
        qr_label=QLabel()
        pixmap=QPixmap()
        pixmap.loadFromData(qr)
        qr_label.setPixmap(pixmap)
        qr_label.setStyleSheet("QLabel{color:#ffe3ed;border:none;background-color:transparent;border-radius:5px;}")
        layout_=QVBoxLayout()
        layout_.addWidget(title_label,1)
        layout_.addWidget(qr_label,9)
        self.qr_dialog=QWidget(self)
        self.qr_dialog.setLayout(layout_)
        self.main_layout.addWidget(self.qr_dialog,1,1,Qt.Alignment.AlignCenter)
        self.qr_dialog.show()
    def close_qr(self):
        self.qr_dialog.close()
    def setting_callback(self):
        setting=SettingWindow(parent=self)
        setting.setStyleSheet("QDialog{border:none;border-radius:5px;background:#F3EAC2;}")
        setting.show()
    def gen_conf(self):
        default_conf={
            "debug":False,
            "hero":{
                "title":"英雄篇",
                "enabled":True,
                "times":1
                },
            "revival":{
                "title":"复兴篇",
                "enabled":True,
                "times":1
            },
            "creation":{
                "title":"创新篇",
                "enabled":True,
                "times":1
            },
            "belief":{
                "title":"信念篇",
                "enabled":True,
                "times":1
            },
            "limit_time":{
                "title":"限时赛",
                "enabled":True,
                "times":1
            },
            "rob":{
                "title":"抢十赛",
                "enabled":True,
                "times":1
            }
        }
        with open(file="config.json",mode="w",encoding="utf-8") as conf_writer:
            conf_writer.write(json.dumps(default_conf,indent=4,sort_keys=True,ensure_ascii=False))
        self.logger.info("已生成默认配置文件")
    def mousePressEvent(self, event:QMouseEvent):
        self.logger.debug("触发鼠标按压事件")
        super().mousePressEvent(event)
        self.setFocus()
        self.m_flag=True
        if event.button()==Qt.MouseButtons.LeftButton and self.isMaximized()==False and self.hasFocus()==True:
            self.old_pos=event.globalPosition() #获取鼠标相对窗口的位置
            self.logger.debug("已获取鼠标位置")
            self.setCursor(QtGui.QCursor(Qt.CursorShape.SizeAllCursor))  #更改鼠标图标
    def mouseMoveEvent(self, event:QMouseEvent):
        self.logger.debug("触发鼠标移动事件")
        super().mouseMoveEvent(event)
        if self.m_flag==True:
            delta_x=int(event.globalPosition().x()-self.old_pos.x())
            delta_y=int(event.globalPosition().y()-self.old_pos.y())
            self.move(self.x()+delta_x,self.y()+delta_y)#更改窗口位置
            self.logger.debug("已更改窗口位置")
            self.old_pos=event.globalPosition()
    def mouseReleaseEvent(self, event:QMouseEvent):
        self.logger.debug("触发鼠标释放事件")
        super().mouseReleaseEvent(event)
        self.m_flag=False
        self.setCursor(QtGui.QCursor(Qt.CursorShape.ArrowCursor))
if __name__=="__main__":
    app=QApplication(sys.argv)
    ui=UI()
    ui.show()
    sys.exit(app.exec())