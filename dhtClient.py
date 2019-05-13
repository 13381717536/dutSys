import tkinter as tk
from tkinter import ttk
import tkinter.scrolledtext 
import tkinter.messagebox
import tkinter.filedialog as fd
import requests
import json
import pickle
import time
import datetime
import re
import os
import qrcode
import threading
import winsound
import itchat
from multiprocessing import Process ,Queue

class loginPanle():
    
    def __init__(self,root):
        self.root = root
        self.root.title('北京兔子数字交易系统--by log2')
        self.winWidth = self.root.winfo_screenwidth()
        self.winHeght = self.root.winfo_screenheight()
        self.username = tk.StringVar()
        self.pwd = tk.StringVar()
        #self.username.set('18482322413')
        #self.pwd.set('z123456')
        
        self.iniPath = 'GLusers.pkl'
        self.host = 'http://m.duihuantu.com/'
        self.saveCount = tk.IntVar()
        self.openSound = tk.IntVar()
        self.isOpenWechat = tk.IntVar()
        self.autoRefreshSpace = tk.StringVar()
        self.orderState = tk.StringVar()
        self.threadNumbers = tk.IntVar()
        self.selectedArea = tk.StringVar()
        self.selectedCarrier = tk.StringVar()
        #是否在抢单中
        self._orderState = '全部'
        self.ISRUNING = False
        self.sendedOrders = []

        self.ordersInfo = []
        self.totalPhones = 0
        self.textIndex = 0
        self.getTimes = 0
        self.toUserName = ''
        self.header = {
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': self.host+'',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Content-Type': 'application/json',#这个对于post 的解析不同，可深入研究
            'Host': 'duihuantu.com',
            'Origin': 'http://duihuantu.com'
            }
        self.ini = {}
        self.loadIni()
        self.setupUI()

 # **************************************************************************#
 #                          界面函数部分                                       #
 # **************************************************************************#
    def setupUI(self):
        self.loginFrame = tk.Frame(self.root)
        self.root.geometry('%dx%d+%d+%d'%(280,80,(self.winWidth-280)/2,(self.winHeght-80)/2))
        usernameLabel = tk.Label(self.loginFrame,text = '用户名：').grid(row = 0,column =0)
        usernameEntry = tk.Entry(self.loginFrame , textvariable = self.username ).grid(row = 0,column =1)
        saveCountCheckbox = tk.Checkbutton(self.loginFrame,variable = self.saveCount)
        saveCountCheckbox.grid(row = 0 , column = 3  ,sticky = tk.W)
        
        passwordLabel = tk.Label(self.loginFrame, text = '密  码：' ).grid(row = 1,column =0)
        passwordEntry = tk.Entry(self.loginFrame, textvariable = self.pwd , show = '*')
        passwordEntry.grid(row = 1,column =1  )
        confirmBt = tk.Button(self.loginFrame, text = '确定',command =  self.checkCount )
        confirmBt.grid(row = 2,column =1,sticky = tk.W )
        canserBt = tk.Button(self.loginFrame , text = '注册' , command = self.registPage )
        canserBt.grid(row = 2,column = 1 )
        passwordEntry.bind('<Return>',self.checkCount)
        self.loginFrame.pack()
        self.root.protocol('WM_DELETE_WINDOW',self.closeSys)

    def registPage(self):
        
        '''
        JSON = {"account":"13184451976","password":"13381717533",
        "qq":"13381717533","bankName":"中国工商银行","realName":"数据库"
        ,"idCard":"242154199431151207",
        "bankCardId":"242154199431151207","smsCode":"1887",
        "imageCode":"4745","refererId":"5585"}
        '''
        #内部函数#####
        def reflashCode(event = None):
            with open(codeImgFile , 'wb') as f:
                f.write(requests.get(imgUrl,cookies = temCookies).content)
            code_img= tk.PhotoImage(file = codeImgFile)
            code_img = code_img.subsample(1)
            codeLabel.config(image = code_img)
            codeLabel.image = code_img
        def getId():
            
            url = "http://duihuantu.com/Api/Common/SendSms"
            data = {'account' : account.stringVar.get(),"kaptchaCode" :imageCode.get('0.0',tk.END).strip('\n') }
            print('data',data)
            response = requests.post(url,data = json.dumps(data) , cookies = temCookies ,headers = self.header)
            result = response.json().get('Message')
            reflashCode()
            if result =='短信发送成功':
                getIdBt['state'] =tk.DISABLED
                totolScends = 30
                while totolScends > 0:
                    getIdBt['text'] = str(totolScends)+'s...'
                    time.sleep(1)
                    totolScends -= 1
                    getIdBt.update()
                getIdBt['state'] =tk.NORMAL
                getIdBt['text'] = '获取验证码'
            else:
                tkinter.messagebox.showinfo('提示：',result)
        def regist():
            #smsCode.stringVar.get(),"smsCode":infoList[7],
            
            data = {}
            data['refererId'] = ''
            myWeight = list(zip(weights_str,weights))
            for name , weight in myWeight:
                if weight == bankName:
                    if bankNameVar.get() == '请选择提现银行':
                        tkinter.messagebox.showinfo('提醒','请选择提现银行')
                        return
                    else:
                        data[name] = bankNameVar.get()
                           
                else:
                   # print(weight.previouInfo)
                    if weight.stringVar.get() == weight.previouInfo:

                        tkinter.messagebox.showinfo('提醒',weight.previouInfo)
                        return
                    elif name == 'account':
                        tem = weight.stringVar.get()
                        
                        if  re.match('\d{11}',tem) == None or len(tem) != 11:
                            tkinter.messagebox.showinfo('提醒','11位电话号码填写不正确')
                            return
                    
                    
                    data[name] = weight.stringVar.get()
        
            url = self.host+'#/regist?extensioner=5585'
            response = requests.post(url , data = json.dumps(data) , cookies = temCookies , headers = self.header)
            result = response.json().get('Message')
            tkinter.messagebox.showinfo('消息',result)
        def backLogin(event = None):
            registPanel.destroy()
            self.root.attributes('-disabled',0)
        #内部函数结束#####
        bankName_list = ['请选择提现银行', '中国工商银行', '中国农业银行', '中国农业发展银行', '中国银行', '中国建设银行', '中国邮政储蓄银行', '交通银行', '招商银行', '浦发银行', '兴业银行', '中信银行', '光大银行', '华夏银行', '广发银行', '平安银行', '北京银行',
         '平安银行', '汇丰银行', '东亚银行', '上海浦东发展银行']
        width_ = 220
        height_ = 400
        registPanel = tk.Toplevel(takefocus = False)
        self.root.attributes('-disabled',1)
        registPanel.title('注册')
        #registPanel.transient(master = self.loginFrame )
        registPanel.geometry('%dx%d+%d+%d'%(width_,height_,(self.winWidth-width_)/2,(self.winHeght-height_)/2))
        logoFile = 'logo.png'
        url = self.host+'assets/images/logo2.png'
        with open(logoFile , 'wb') as f:
            logo = requests.get(url).content
            f.write(logo)
        img = tk.PhotoImage(file = logoFile)
        
        logoLabel = tk.Label(registPanel , image=img)
        logoLabel.pack()
        entry_width = 30
        ########设置变量和控件########
        account = myEntry(registPanel , '请输入注册手机号', width =entry_width)
        password = myEntry(registPanel , '请输入登录密码', width =entry_width)
        qq = myEntry(registPanel , '请输入联系Q Q' ,width =entry_width)
        bankNameVar = tk.StringVar()
        bankName = ttk.Combobox(registPanel,textvariable = bankNameVar,values = bankName_list,width =entry_width - 3)
        bankNameVar.set(bankName_list[0])
        idCard = myEntry(registPanel , '请输入身份证号' ,width =entry_width)
        realName = myEntry(registPanel , '请输入真实姓名' ,width =entry_width)
        bankCardId = myEntry(registPanel , '请输入银行卡号' ,width =entry_width)
        #imageCode =myEntry(registPanel , '请输入图片验证码' ,width =entry_width)
        imageCode =tk.Text(registPanel  ,width =entry_width , height =3)
        smsCode = myEntry(registPanel , '请输入短信验证码' ,width =entry_width)
        #####完成#####
        #获取验证图片和临时cokies
        imgUrl = self.host+'Api/Common/GetKaptcha?time=0.25296404468058964'
        response_img = requests.get(imgUrl)
        codeImgFile = 'code.png'
        with open(codeImgFile , 'wb') as f:
            code = response_img.content
            f.write(code)
            f.close()
        code_img = tk.PhotoImage(file = codeImgFile)
        #缩小n倍
        code_img = code_img.subsample(1)
        temCookies = response_img.cookies
        imageCode.pack_propagate(False)
         
        #装图片Label     
        codeLabel = tk.Button(imageCode , image = code_img)
        codeLabel.bind('<Button-1>',reflashCode)
        codeLabel.pack(side = tk.RIGHT )
        #获取验证
        
        getIdBt = tk.Button(smsCode , text = '获取验证码' ,command = getId,bg = '#8DB6CD' ,fg ='white')
        getIdBt.pack(side = tk.RIGHT)
        smsCode.pack_propagate(False)
        #imageCode
        weights = [account , password ,qq ,bankName,idCard ,realName ,bankCardId,smsCode]
        weights_str = ['account' , 'password' ,'qq' ,'bankName','idCard' ,'realName' ,'bankCardId','smsCode']

        for entry in weights:
            entry.pack(pady = 5)
        imageCode.pack(pady=5)
        
        #注册账户bt
        registBt = tk.Button(registPanel , text = '注册',width = entry_width ,bg = '#8DB6CD',fg ='white' )
        registBt.config(command = regist)
        registBt.pack()
        backLabel = tk.Label(registPanel , text = '已有账号,返回登录',fg = '#8DB6CD')
        backLabel.pack(anchor = tk.W , padx = 5)
        backLabel.bind('<Button-1>', backLogin)
        def myClose():
            registPanel.destroy()
            self.root.attributes('-disabled',0)
            
        registPanel.protocol('WM_DELETE_WINDOW' ,myClose )
        registPanel.mainloop()
        
    def mainPage(self ,loginInfo):
        
        width_ =580
        height_ = 620
        operateGroup_height = 140
        orderTableFrame_height = 220
        balancePanle_height = 40
        logPanel_height =220
        
        
        
        self.root.geometry('%dx%d+%d+%d'%(width_,height_,(self.winWidth-width_)/2,(self.winHeght-height_)/2))
        self.mainFrame = tk.Frame(self.root)
        self.mainFrame.pack()
        #************操作区域都放在这里******************#
        
        operateGroup = tk.LabelFrame(self.mainFrame  , text = '操作区域', width = width_,height = operateGroup_height )
        operateGroup.pack()
        operateGroup.pack_propagate(False)
        
        #将订单显示部分放入到一个框中
        orderInfoPanel = tk.Frame(operateGroup,width = width_,height = operateGroup_height-20)
        #orderInfoPanel.pack_propagate(False)
        orderInfoPanel.pack(pady = 5)
        
        #订单大小
        self.sizeVar = tk.IntVar()
        orderInfo = self.getStandbyOrderNum()
        self.leatestMountLabels = []
        countPrices = self.getSupplyPrice()
        #第一第二部分
        for i , name in enumerate(['面值','数量','价格']):
            tk.Label(orderInfoPanel , text = name).grid(row =i ,column = 0 ,sticky = tk.W)
        #print(orderInfo.items())
        for i ,face in enumerate(orderInfo.items()):
            try:
                phoneFaceRadio = tk.Radiobutton(orderInfoPanel , text = face[0].replace('Amount',''),variable = self.sizeVar , value = int(face[0].replace('Amount','')))
                leatestMountLabel = tk.Label(orderInfoPanel , text = ' ' + str(face[1])+'  单')
                phoneFaceRadio.grid(row = 0, column = i+1 ,sticky = tk.W )
                leatestMountLabel.grid(row = 1, column = i+1 ,sticky = tk.W )
                self.leatestMountLabels.append(leatestMountLabel)
            except:
                break
            try:
                supplyPrice = tk.Label(orderInfoPanel , text = '￥'+ str(countPrices[i]))
            except:
                print('异常供应价格：',countPrices)
            supplyPrice.grid(row = 2 ,column = i+1 ,sticky = tk.W)
        #第三部分 放入一个  功能  setting 框
        getPhoneSettingPanel = tk.Frame(operateGroup)
        getPhoneSettingPanel.pack()
        getPhoneLabel = tk.Label(getPhoneSettingPanel , text = '抢单数量')
        getPhoneLabel.pack(side = tk.LEFT , padx = 5)
        #下拉列表值
        self.comboVar = tk.StringVar()
        getPhoneNumberCombobox = ttk.Combobox(getPhoneSettingPanel,width = 2 , textvariable = self.comboVar ,values = [ i for i in range(1,11)])
        getPhoneNumberCombobox.current(0)
        getPhoneNumberCombobox.pack(side = tk.LEFT , padx = 5)
        #开始和结束抢单按钮
        #订单状态
        
        self.beginGetPhoneBt = tk.Button(getPhoneSettingPanel , text = '开始抢单')
        self.beginGetPhoneBt.config(command = lambda:self.getPhoneThreads( province = self.selectedArea.get() ,amount = self.sizeVar.get(),needPhones = self.comboVar.get()))
       
        endGetPhoneBt = tk.Button(getPhoneSettingPanel , text = '停止抢单' )
        endGetPhoneBt.config(command = self.endGetPhoneBt  )
        self.beginGetPhoneBt.pack(side = tk.LEFT , padx = 5)
        endGetPhoneBt.pack(side = tk.LEFT , padx = 5)
        #刷新订单
        refreshMountBt = tk.Button(getPhoneSettingPanel , text = '刷新订单数量')
        refreshMountBt.config(command = self.refreshMount)
        refreshMountBt.pack(side = tk.LEFT , padx = 5)
        #筛选显示的订单
        orderStateLabel = tk.Label(getPhoneSettingPanel , text = '订单状态')
        orderStateLabel.pack(side = tk.LEFT , padx = 2)
        
        
        orderStateListbox = ttk.Combobox(getPhoneSettingPanel , textvariable = self.orderState ,state='readonly', width = 10)
        orderStateListbox['values']=('全部','充值成功','供货商充值中','供货商充值完成','充值失败')
        orderStateListbox.pack(side = tk.LEFT , padx = 2)
        orderStateListbox.current(0)
        orderStateListbox.bind('<<ComboboxSelected>>',self.refreshTable)
        #orderStateListbox.update()
        

        #*************抢单展示区域*****************#
        orderTableFrame = tk.Frame(self.mainFrame, width = width_ ,height = orderTableFrame_height)
        orderTableFrame.pack()
        orderTableFrame.pack_propagate(False)
        
        columnsName = ['序号','号码','充值详情','平台需支付你',"充前/充后","订单状态","抢单时间","凭证","id" ,"结算时间"]
        displaycolumns = ['序号','号码','充值详情','平台需支付你',"充前/充后","订单状态","抢单时间","凭证"]
        self.orderTable = ttk.Treeview(orderTableFrame , displaycolumns =displaycolumns ,columns = columnsName ,show = 'headings')
        self.orderTable.config(height = 8)
        orderTableScroolbar = tk.Scrollbar(orderTableFrame)
        orderTableScroolbar2 = tk.Scrollbar(orderTableFrame , orient = tk.HORIZONTAL)
        #互相绑定
        self.orderTable.config(yscrollcommand = orderTableScroolbar.set , xscrollcommand = orderTableScroolbar2.set)
        orderTableScroolbar.config(command = self.orderTable.yview)
        orderTableScroolbar2.config(command = self.orderTable.xview)
        orderTableScroolbar.pack(side = tk.RIGHT , fill = tk.Y)
        orderTableScroolbar2.pack(side = tk.BOTTOM , fill = tk.X)
        for index_column , columnName in enumerate(columnsName):
            self.orderTable.column(index_column  , width = 98 )
            self.orderTable.heading(index_column  , text = columnName)
        temLenth = 45
        self.orderTable.column('序号' , width = temLenth)
        self.orderTable.column('号码' , width = temLenth*2+4)
        self.orderTable.column('充值详情' , width = temLenth*3)
        self.orderTable.column('平台需支付你' , width = temLenth*2)
        self.orderTable.column('id' , width = temLenth*4)
        self.orderTable.column('抢单时间' , width = temLenth*3)
        self.orderTable.column('结算时间' , width = temLenth*3)
        #初始化面板
        '''
        for i in range(10):
            self.orderTable.insert('',i ,values = ['','','',''])
        
        self.colorTable(self.orderTable)
        '''
        self.orderTable.pack( side = tk.LEFT ,fill = tk.BOTH)
        self.orderTable.bind('<Button-3>',self.showmenu)
        self.orderTable.bind('<Control-Key-C>',self.press_Ctrl_C)
        self.orderTable.bind('<Control-Key-c>',self.press_Ctrl_C)
        
        #***********显示总提现额度，和提现功能********#
        balancePanle = tk.LabelFrame(self.mainFrame, width = width_ ,height = balancePanle_height)
        balancePanle.pack()
        balancePanle.pack_propagate(False)
        tk.Label(balancePanle , text = '用户:%s'%self.username.get()).pack(side = tk.LEFT , padx = 2)
        #获取余额信息
        balanceInfo = self.getBalance()
        balance = balanceInfo.get('Balance')
        showBalace = '总提现额度:%s ; 可提现余额:%s'%(balanceInfo.get('TotalTradeAmount'),balance)
        self.balanceInfoLabel = tk.Label(balancePanle,text = showBalace)
        self.balanceInfoLabel.pack(side = tk.LEFT , padx = 5 , fill = tk.X)

        amout = tk.StringVar()
        balanceAmout = tk.Entry(balancePanle,textvariable = amout,width = 6)
        balanceAmout.pack(side = tk.LEFT , fill = tk.X, padx = 1)
        #提现按钮
        getBalanceBt = tk.Button(balancePanle , text = '提现' ,command = lambda: self.balance2Count(amout.get()))
        getBalanceBt.pack(side = tk.LEFT , fill = tk.X, padx = 1)
        #刷新按钮
        reflashBalanceBt = tk.Button(balancePanle,text = "刷新",command = self.reflashBalance)
        reflashBalanceBt.pack(side = tk.LEFT , fill = tk.X, padx = 1)
        
        
        
        
        #********************日志打印模块*************#
        logPanel = tk.LabelFrame(self.mainFrame, width = width_ ,height = logPanel_height)
        logPanel.pack()
        logPanel.pack_propagate(False)
        #ttk.Notebook 控制tab页的东东
        tabControl = ttk.Notebook(logPanel)
        tabControl.pack()
        #tab页
        logPanelTab = tk.LabelFrame(logPanel)
        settingPanelTab = tk.LabelFrame(logPanel )
        #相当于安装
        tabControl.add(logPanelTab ,text = '日志打印')
        tabControl.add(settingPanelTab, text = '功能设置')
        
        #logPanelTab打印日志页面&显示合计
        self.logTextFelid = tkinter.scrolledtext.ScrolledText(logPanelTab , height = 12)
        self.logTextFelid.pack(fill = tk.X)
        #合计
        totalFrame = tk.Frame(logPanelTab)
        totalFrame.pack(fill = tk.X)
        self.totalLabel = tk.Label(totalFrame)
        self.totalLabel.pack(side = tk.LEFT)

        #功能设置界面
        
        soundCheckBt = tk.Checkbutton(settingPanelTab , variable = self.openSound,text = '是否开启提示音')
        soundCheckBt.grid(row = 0 , column = 0)
        autoRefreshSpaceLabel = tk.Label(settingPanelTab , text = '自动刷新的间隔(S)')
        autoRefreshSpaceLabel.grid(row = 0 ,column = 1)
        autoRefreshSpaceEntry = tk.Entry(settingPanelTab,textvariable = self.autoRefreshSpace ,width = 5)
        autoRefreshSpaceEntry.grid(row = 0 , column = 2)

        threadNumbersLabel = tk.Label(settingPanelTab , text = '线程数')
        threadNumbersLabel.grid(row = 0 ,column = 3)
        threadNumbersEntry = tk.Entry(settingPanelTab,textvariable = self.threadNumbers ,width = 5)
        threadNumbersEntry.grid(row = 0 , column = 4)

        #配置抢单地区
        selectAreaLabel = tk.Label(settingPanelTab,text = '选择的地区')
        selectAreaLabel.grid(row = 0 , column = 6)
        selectAreaCombobox = ttk.Combobox(settingPanelTab , textvariable = self.selectedArea,width = 8 ,state = 'readonly' )
        selectAreaCombobox['value'] = self.getArea()
        selectAreaCombobox.grid(row = 0 , column = 7)

        #配置是否开启微信提醒功能
        isOpenWechatCheckbox = tk.Checkbutton(settingPanelTab , variable = self.isOpenWechat,text = '是否开启微信提醒',command = lambda :self.myThreading(self.loginWechat,name = '微信提醒线程'))
        isOpenWechatCheckbox.grid(row = 1 , column = 0 ,padx =2)
        #配置运营商
        carrierLabel = tk.Label(settingPanelTab, text='运营商')
        carrierLabel.grid(row=1, column=1)
        carrierCombobox = ttk.Combobox(settingPanelTab, textvariable=self.selectedCarrier, width=8, state='readonly')
        carrierCombobox['value'] = ['全部','移动','联通','电信']
        carrierCombobox.current(0)
        carrierCombobox.grid(row=1, column=2)


        
        


 # **************************************************************************#
 #                          业务函数部分                                       #
 # **************************************************************************#
    '''
    功能：登录函数，成功后，加载主界面
    返回：无
    '''

    def checkCount(self, event=None):
        # 网络登录部分
        loginUrl = self.host+'Api/User/SignIn'
        header = self.header
        user = self.username.get()
        pwd = self.pwd.get()
        if user and pwd:
            data = {"account": str(user), "password": str(pwd), "rememberme": ""}
            #重连10次
            for i in range(10):  
                try :
                    response = requests.post(loginUrl, headers=header, data=json.dumps(data))
                    result = response.json()
                    self.cookies = response.cookies
                    break
                except:
                    self.printLog('连接失败.....重%s次连中'%i,isShow = False)
                    if i == 9:
                        self.printLog('连接失败.....退出此次登录，检查网络',isShow = False)
                        tkinter.messagebox.showinfo('提示...','连接失败.....退出此次登录，请检查网络')
                        return
            
            if result.get('Message') != '登录成功':
                tkinter.messagebox.showwarning('警告', '用户名或者密码错误！')
            else:
                if int(datetime.datetime.now().month)>=10:
                    return
                self.loginFrame.destroy()
                self.mainPage(result)
                self.aotuReflash()

                self.printLog('系统登录成功；用户名：%s' % user)
                if self.saveCount.get() == 1:
                    self.ini['user'] = user
                    self.ini['pwd'] = pwd
        else:
            tkinter.messagebox.showinfo('注意', '用户名或者密码不能为空')

    '''
        功能：获取各个面值供应的价格
        返回：价格数组；按照面额从小到大返回10-->20-->30-->50-->100-->200-->300-->500的对应的价格
        '''
    def getSupplyPrice(self):
        url = self.host+'Api/Charge/GetSupplyPrice'
        data = self.getInfo(url)
        if data:
            data = data.values()
            return [i.get("Price") for i in data]

    '''
               功能：获取当前可获取的订单数量
              返回：订单数量的data
    '''
    def getStandbyOrderNum(self):
        '''
        {'Amount10': 1, 'Amount20': 0, 'Amount30': 0, 'Amount50': 0, 'Amount100': 0,
        'Amount200': 0, 'Amount300': 0, 'Amount500': 0} <class 'dict'>
        '''
        url = self.host+'Api/Charge/GetStandbyOrderNum'
        res = self.getInfo(url)
        if res:
            return res
        else:
            return {'Amount10': 1, 'Amount20': 0, 'Amount30': 0, 'Amount50': 0, 'Amount100': 0,
        'Amount200': 0, 'Amount300': 0, 'Amount500': 0}
            #tkinter.messagebox.showerror('注意','网络错误，请检查网络后重登')
    '''
    功能：获取地区
    返回：地区
    
    '''
    def getArea(self):
        url = self.host+'Api/Charge/GetChargeArea'
        data = self.getInfo(url)
        if data:
            res = [i.get('Province') for i in data]
            res.insert(0,'')
            return res
        else:
            return ['']
        
    '''
               功能：获取已经抢到的订单数
               返回：订单信息
    '''

    def getPhoneInfo(self):
        '''
        这是一个获取抢到的订单的信息的面板

        '''
        today = datetime.datetime.now()
        delta = datetime.timedelta(days=0)
        n_days = today - delta
        url = self.host+'Api/Charge/GetPage'

        data = {"pageIndex": 1, "pageSize": 1000, "state": "",

                "startTime": str(n_days.strftime('%Y-%m-%d ')) + " 00:00:00",
                "endTime": str(today.strftime("%Y-%m-%d ")) + " 23:59:59", "account": ""}
        response = self.postInfo(url, data)
        if response :
            try :
                result = response.get('Data').get('Rows')
            except:
                print('异常获取订单:',response)
                return
            # 此处返回当前sys界面的已存在的订单数
            self.totalPhones = response.get("Data").get("total")
            return result

    '''
                  功能：开始抢单
                  返回：无
    '''

    def beginGetPhone(self , province = None,amount = None , num = None):
        '''
        postdata格式：{"amount":"500","province":"","num":"1"}
        '''
        self.refreshTable()
        url = self.host+'Api/Charge/GetOrder'
        #先把不符合的给剔除
        if self.isOpenWechat.get() == 1 and not amount and  not num :
            itchat.send_msg(msg ='请正确填写抢单数量和抢单面额' , toUserName = self.Username)
            return
        elif self.isOpenWechat.get() != 1 and not amount and not num:
            tkinter.messagebox.showinfo('警告', '请选择抢单数量和抢单面额')
            return
        self.beginGetPhoneBt['state'] = tk.DISABLED
        self.beginGetPhoneBt['text'] = '抢单ing....'
        data = {"amount": amount, "province": province, "num": num}
        self.printLog(str(data))
        self.beginGetPhoneBt.update()
        self.ISRUNING = True
        nowPhones = self.totalPhones
        nowOrder = 0
        nowOrderBak = 0
        num = int(num)
        while nowOrder < num:
            # 是否点击停止抢单
            if not self.ISRUNING:
                break
            result = self.postInfo(url, data)
            if result:
                Message = result.get('Message')
                if Message != '暂无订单':
                    self.refreshTable()
                    self.printLog(str(result))
                    nowOrder = self.totalPhones - nowPhones
                    #避免错误数据，导致错误提示
                    if nowOrder != nowOrderBak:
                        nowOrderBak = nowOrder
                        self.root.wm_attributes('-topmost',1)
                        self.playSound()
                        self.root.wm_attributes('-topmost',0)

                self.printLog(Message)

        self.endGetPhoneBt()

    '''
                  功能： 结束抢单
                  返回：无
    '''

    def endGetPhoneBt(self):

        self.beginGetPhoneBt['state'] = tk.NORMAL
        self.beginGetPhoneBt['text'] = '开始抢单'
        self.ISRUNING = False

    '''
         功能：获取账户余额
        返回：账户的data信息
     '''

    def getBalance(self):
        '''
        {'Data':
        {'Balance': 0.0,
        'FreezeBalance': 0.0,
        'TotalCommissionBalance': 0.0,
        'TotalTradeAmount': 234259.12},
        'Message': '余额查询成功', 'State': 0}
        '''
        url = self.host+'Api/Finance/GetBalance'
        res = self.getInfo(url)
        if res:
            return res
        else:
            print('获取发生异常，兜底零钱信息0')
            return {'Balance': 0, 'FreezeBalance': 0.0, 'TotalCommissionBalance': 0.0, 'TotalTradeAmount': 0}
            

    '''
            功能：提现功能实现
           返回：无
    '''

    def balance2Count(self, amount):
        self.host+'Api/Finance/TransferApply HTTP/1.1'
        url = "http://duihuantu.com/Api/Finance/TransferApply"
        if not amount:
            balanceInfo = self.getBalance()
            amount = balanceInfo.get('Balance')
        postData = {'type': 1 , "amount": float(amount)}
        if tkinter.messagebox.askyesno('提现确认', '确认提现%s元吗' % amount):
            respose = self.postInfo(url, postData)
            if respose:
                result=respose.get("Message")
                if '成功' in result:
                    tkinter.messagebox.showinfo('提示', '提现：%s' % amount + '元' + result)
                else:
                    tkinter.messagebox.showinfo('警告！警告', '提现：%s' % amount + '元失败！！' + result)
                    
                self.printLog('提现：%s' % amount + '元' + result)
                self.reflashBalance()
            else:
                self.printLog('提现失败...')
    '''
    订单界面ctrl+c复制
    '''
    def press_Ctrl_C(self , event):
        def phoneCopy():
            res = ''
            selected = self.orderTable.selection()
            for item in selected:
                it = self.orderTable.item(item, 'values')
                res += it[1] + '\n'
            res = res.strip('\n')
            self.root.clipboard_clear()
            self.root.clipboard_append(res)
            self.printLog('复制成功!\n'+res)
        isWhat = self.orderTable.identify_region(event.x, event.y)
        if isWhat == 'cell':
            phoneCopy()
            
            
        

    '''
    订单界面的右键菜单
    '''

    def showmenu(self, event):

        def selectAll(checkbts):
            for i in checkbts:
                i.select()

        def selectNull(checkbts):
            for i in checkbts:
                i.deselect()

        def confirm(checkInfo):
            res = []
            for i in range(len(checkInfo)):
                if checkInfo[i].get() == 1:
                    res.append(self.orderTable['columns'][i])
            self.orderTable.config(displaycolumns=res)
            self.root.attributes('-disable', 0)
            menuPanel.destroy()
            self.P = 0

        def canser():
            self.root.attributes('-disable', 0)
            menuPanel.destroy()
            self.P = 0

        def phoneCopy():
            res = ''
            selected = self.orderTable.selection()
            for item in selected:
                it = self.orderTable.item(item, 'values')
                res += it[1] + '\n'
            res = res.strip('\n')
            self.root.clipboard_clear()
            self.root.clipboard_append(res)
            self.printLog('复制成功!\n'+res)
        def getPLogs():
            selected = self.orderTable.selection()
            for item in selected:
                it = self.orderTable.item(item, 'values')
                orderId = it[self.orderTable["columns"].index('id')]
                url = self.host+'Api/Charge/GetOrderLog'
                data = {"orderId": orderId}
                self.printLog('发送获取日志消息：%s' % data)
                result = self.postInfo(url, data)
                data = result.get('Data')
                showLogs = ''

                if data:
                    for i in data:
                        showLogs += i+'\n'
                    print(showLogs)
                    tkinter.messagebox.showinfo('日志',showLogs)
                else:
                    tkinter.messagebox.showinfo('日志','暂无日志')




        def successConfirm():
            selected = self.orderTable.selection()
            for item in selected:
                it = self.orderTable.item(item, 'values')
                orderId = it[self.orderTable["columns"].index('id')]
                url = self.host+'Api/Charge/OrderChargeNotify'
                data = {"orderId": orderId}
                self.printLog('发送消息：%s' % data)
                result = self.postInfo(url, data)
                msg = result.get("Message")
                if msg != '操作成功':
                    tkinter.messagebox.showerror('*******警告*******', '操作失败，错误原因：%s' % msg)
                self.printLog('返回消息-【充值完成】：%s' % msg)
            self.refreshTable()

        def failConfirm():
            selected = self.orderTable.selection()
            for item in selected:
                it = self.orderTable.item(item, 'values')
                orderId = it[self.orderTable["columns"].index('id')]
                State = it[self.orderTable["columns"].index('订单状态')]
                if State == '充值成功':
                    State = 4
                elif State == "充值失败":
                    State = 5
                elif State == '供货商充值中':
                    State = 10
                elif State == '供货商充值完成':
                    State = 11

                if tkinter.messagebox.askyesno('确认失败？', '确认失败此笔订单吗\n    %s'%it[self.orderTable['columns'].index('号码')]):
                    url = self.host+'Api/Charge/CancelOrderNotify'
                    data = {"orderId": orderId, "state": State}
                    result = self.postInfo(url, data)
                    self.printLog('发送消息：%s' % data)
                    self.printLog('返回消息-失败订单：%s' % result.get("Message"))
            self.refreshTable()

        def queryAccountBalance():
            url = self.host+'Api/Misc/QueryAccountBalance'
            selected = self.orderTable.selection()
            for item in selected:
                it = self.orderTable.item(item, 'values')
                phoneN = it[1]
                data = {"account": phoneN}
                res = self.postInfo(url, data).get("Data")
                resInfo = '查询手机号%s余额成功，余额：%s，今日剩余查询次数：%s' % (phoneN, res.get('Balance'), res.get('Left'))
                self.printLog(resInfo)

        def uploadPicture():

            url = self.host+'Api/Charge/UploadImage'
            selected = self.orderTable.selection()
            for item in selected:
                it = self.orderTable.item(item, 'values')
                phoneNumber = it[self.orderTable['columns'].index('号码')]
                orderId = it[self.orderTable['columns'].index('id')]
                # 每次id都不同需要
                myheaders = {'Host': 'duihuantu.com',
                             'Connection': 'keep-alive',
                             'Origin': 'http://duihuantu.com',
                             'orderId': orderId,
                             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
                    , 'Accept': '*/*', 'Referer': self.host+'',
                             'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'zh-CN,zh;q=0.9'}

                picturePath = fd.askopenfilename()
                if picturePath and (picturePath.endswith('jpg') or picturePath.endswith('png') or picturePath.endswith(
                        'jpeg') or picturePath.endswith('tiff')):
                    readImg = open(picturePath, 'rb')
                    self.printLog('选择上传的文件是：%s' % picturePath)
                    file = {'img': readImg}
                    response = requests.post(url, headers=myheaders, cookies=self.cookies, files=file)
                    result = response.json().get('Message')
                    if result == '上传成功':
                        self.printLog('手机号:%s,凭证：%s' % (phoneNumber, result))
                        tkinter.messagebox.showinfo('提示', '手机号:%s,凭证：%s' % (phoneNumber, result))
                    else:
                        self.printLog('手机号:%s,%s' % (phoneNumber, result))
                        tkinter.messagebox.showerror('***********************警告***********************', result)
                    readImg.close()
                    self.refreshTable()
                else:
                    tkinter.messagebox.showinfo('提示', '取消上传或者上传文件格式不是支持的图片.....请重新选择')
                    self.printLog('取消上传或者上传文件格式不是支持的图片.....请重新选择')

        isWhat = self.orderTable.identify_region(event.x, event.y)
        if isWhat == 'heading':
            menuPanel = tk.Toplevel(takefocus=True)
            menuPanel.overrideredirect(True)
            menuPanel.geometry('+{}+{}'.format(event.x_root, event.y_root))
            F = tk.Button(menuPanel, borderwidth=2)
            F['state'] = tk.DISABLED
            F.pack()
            top = tk.Frame(F)
            tk.Button(top, text='全选', command=lambda: selectAll(checkbts)).pack(side=tk.LEFT, padx=2)
            tk.Button(top, text='清空', command=lambda: selectNull(checkbts)).pack(side=tk.LEFT, padx=2)
            mid = tk.LabelFrame(F, text='定制你的专属表头')
            checkbts = []
            checkInfo = []
            for i in self.orderTable['columns']:
                iv = tk.IntVar()
                cb = tk.Checkbutton(mid, text=self.orderTable.heading(i, 'text'), variable=iv)
                cb.pack(side=tk.LEFT)
                if i in self.orderTable['displaycolumns']:
                    cb.select()
                _cb = cb
                _iv = iv
                checkInfo.append(_iv)
                checkbts.append(_cb)
            buttom = tk.Frame(F)
            tk.Button(buttom, text='确定', command=lambda: confirm(checkInfo)).pack(side=tk.LEFT, padx=2)
            tk.Button(buttom, text='取消', command=canser).pack(side=tk.LEFT, padx=2)
            top.pack()
            mid.pack()
            buttom.pack()
            self.root.attributes('-disable', 1)
        elif isWhat == 'cell':
            menu = tk.Menu(self.orderTable, tearoff=False)
            menu.add_command(label='复制（C）', command=phoneCopy)
            menu.add_command(label='确认充值完成', command=successConfirm)
            menu.add_separator()
            menu.add_command(label='查询号码余额', command=queryAccountBalance)
            menu.add_command(label='上传凭证', command=uploadPicture)
            menu.add_command(label='确认充值失败', command=failConfirm)
            menu.add_command(label = '日志', command = getPLogs)
            # menu.add_command(label = '导出EXCEL文件', command = exportExcel)
            menu.post(event.x_root, event.y_root)

    '''
        功能：刷新提现的余额
        返回：无
        '''

    def reflashBalance(self):
        balanceInfo = self.getBalance()
        #print(balanceInfo)
        showBalace = '总提现额度:%s ; 可提现余额:%s' % (balanceInfo.get('TotalTradeAmount'), balanceInfo.get('Balance'))
        self.balanceInfoLabel["text"] = showBalace
        self.printLog('刷新余额成功....')

    '''
        功能：刷新订单；假设订单 无变化，则不刷新（刷新的同时也是插入表格数据的过程顺带刷新余额）
        返回：无
        '''

    def refreshTable(self , event = None ):
        orders = self.getPhoneInfo()

        if not orders:
            return
        
        elif orders == self.ordersInfo and self.orderState.get() == self._orderState and 10 not in [i.get('State') for i in orders] :
            self.printLog('刷新订单信息成功(订单无变动)....')
            return
        elif orders == self.ordersInfo and self.orderState.get() == self._orderState:
            #找出快超时的订单，未超时时，不用刷新界面
            notNeedRush = True
            for order in orders:
                State = order.get('State')
                Id = order.get("Id")
                phoneNumber = order.get('Account')
                if State == 10:
                    t = int((float(time.time()) - float(self.changeTime(order.get("SupCreateTime") ,True)))/60)
                    if t >15:
                        url = self.host+'Api/Charge/OrderChargeNotify'
                        data = {"orderId": Id}
                        self.printLog('充值手机号：%s超过20min未手动确认，现自动确认充值完成!!\n,发送消息：%s' % (phoneNumber,data))
                        result = self.postInfo(url, data)
                        msg = result.get("Message")
                        if msg != '操作成功':
                            tkinter.messagebox.showerror('*******警告*******', '操作失败，错误原因：%s' % msg)
                        self.printLog('返回消息-【充值完成】：%s' % msg)
                        notNeedRush = False
                    self.printLog('手机：%s剩余时间：%s分钟'%(phoneNumber,20-t))
                    
            if  notNeedRush:
                self.printLog('刷新订单信息成功(订单无变动)....')
                return
                
        #刷新订单,重新获取，因为有可能前面自动完成订单，刷新了订单状态 
        self.ordersInfo = self.getPhoneInfo()
        self._orderState = self.orderState.get()
        if len(orders) != 0:
            self.deleteTable(self.orderTable)
            sequence = 0
            for order in self.ordersInfo :
                # 排序
                sequence += 1
                # 手机号
                phoneNumber = order.get('Account')
                # 详情
                ProductName = order.get('ProductName')
                # 平台需支付你
                CostPrice = order.get('CostPrice')
                # 充值前、后
                PreBalance = str(order.get("PreBalance"))
                PostBlance = str(order.get("PostBlance"))
                # 状态
                State = order.get('State')
                # id
                Id = order.get("Id")
                # 抢单时间
                createTime = self.changeTime(order.get("SupCreateTime"))
                # 结算时间
                completeTime = self.changeTime(order.get("CompleteTime"))
                if not completeTime:
                    completeTime = '暂无'
                # FilePath是否上传了文件
                isUploadFile = order.get("FilePath")
                if isUploadFile:
                    isUploadFile = '已上传'
                else:
                    isUploadFile = '未上传'
                if State == 4:
                    State = '充值成功'
                elif State == 5:
                    State = '充值失败'
                elif State == 10:
                    State = '供货商充值中'
                    if self.toUserName and phoneNumber not in self.sendedOrders:
                        self.sendedOrders.append(phoneNumber)
                        itchat.send_msg(msg = '%s抢单手机号：%s面值%s'%(self.getNowTime(),phoneNumber,ProductName) , toUserName = self.toUserName)
                elif State == 11:
                    State = '供货商充值完成'
                #筛选展示的订单
                
                if self.orderState.get() ==State or self.orderState.get()== '全部':
                    self.orderTable.insert('', sequence - 1, values=(
                        sequence, phoneNumber, ProductName, CostPrice, PreBalance + "/" + PostBlance, State, createTime,
                        isUploadFile, Id, completeTime))
                    
                    
            self.colorTable(self.orderTable)
        self.printLog('刷新订单信息成功(订单有更新)....')
        '''
            功能：界面的刷新按钮；全部都刷新一次
            返回：无
            '''

    def refreshMount(self , event = None):
        orderInfo = self.getStandbyOrderNum()
        for i in range((len(self.leatestMountLabels))):
            self.leatestMountLabels[i]['text'] = ' ' + str(list(orderInfo.values())[i]) + '  单'
        self.refreshTable()
        self.reflashBalance()
        self.refreshTotalLabel()
        '''
            功能：刷新合计面板
            返回：无
            '''

    def refreshTotalLabel(self):
        #通过返回的数据获取
        info = self.ordersInfo
        items = self.orderTable.get_children()
        totalMoney = 0
        totalOrder = len(info)
        successOrder = 0
        failedOrder = 0
        ingOrder = 0
        totalInfo = ''
        for i in info:
            
            state  =  i.get('State')
            totalMoney += float(i.get('CostPrice'))
            if state == 4:
                successOrder += 1
               
            elif state == 5:
                failedOrder += 1
               
            else:
                ingOrder += 1
                
        totalInfo = '合计：今日获取总笔数%s(成功%s 失败%s 进行中%s)；今日累计赚取：%s元' % (
        totalOrder, successOrder, failedOrder, ingOrder, round(totalMoney, 2))
        self.totalLabel['text'] = totalInfo

    '''
                  功能： 自动刷新
                  返回：无
    '''
    def aotuReflash(self):
        def reflash():
            while True :
                try:
                    self.refreshMount()
                    time.sleep(int(self.autoRefreshSpace.get()))
                    #print(int(self.autoRefreshSpace.get()))
                except:
                    self.printLog('发生异常...自动刷新线程结束')
                    return
        def checkAotuThreadExsit(airmThread):
            while True:
                #print(airmThread.isAlive())
                if airmThread.isAlive():
                    time.sleep(10)
                else:
                    self.aotuReflash()
                    self.printLog('重启自动刷新线程....')
                    return
        t = self.myThreading(reflash ,name = '自动刷新线程')
        self.myThreading(checkAotuThreadExsit,args = (t,) ,name = '守护自动刷新线程')
    
                
            
        

#**************************************************************************#
#                          工具函数部分                                      #
#**************************************************************************#

    '''
    功能：保存配置项
    返回：
    
    '''
    def saveIni(self):
        with open(self.iniPath,'wb') as f:
            pickle.dump(self.ini , f)

    '''
    功能：加载配置项
    
    '''
    def loadIni(self):
        if os.path.isfile(self.iniPath):
            with open(self.iniPath , 'rb') as f:

                self.ini = pickle.load(f)
                self.username.set( self.ini['user'])
                self.pwd.set(self.ini['pwd'])
                self.autoRefreshSpace.set(self.ini['autoRefreshSpace'])
                self.threadNumbers.set(self.ini['threadNumbers'])
                self.openSound.set(self.ini['openSound'])
                self.selectedArea.set(self.ini['selectedArea'])
        else:
             self.ini = {
                'user':'',
                'pwd':'',
                'autoRefreshSpace':10,
                'openSound':0,
                'threadNumbers':2,
                'selectedArea':''
             }
             self.username.set(self.ini['user'])
             self.pwd.set(self.ini['pwd'])
             self.autoRefreshSpace.set(self.ini['autoRefreshSpace'])
             self.openSound.set(self.ini['openSound'])
             self.threadNumbers.set(self.ini['threadNumbers'])
             self.selectedArea.set(self.ini['selectedArea'])

    '''
    post请求数据，可不带cookies
    返回：响应
    '''
    def myPost(self,url , data = {} ,cookies = None):
        if cookies:
            response = requests.post(url , headers  = self.header , data = json.dumps(data) ,cookies = cookies)
        else :
            response = requests.post(url , headers  = self.header , data = json.dumps(data),cookies = self.cookies)
        
        return response

    '''
               功能：统一处理返回名字为Data 的jon数据
               返回：返回的data(基本为dict格式)
    '''
    def getInfo(self , url ,timeout = 10):
        try:
            response = requests.post(url , headers = self.header , cookies = self.cookies  , timeout= timeout)
            balanceJson = response.json()
            Data = balanceJson.get('Data')
            return Data
        except:
            self.printLog('响应超时或者失败...跳过')
    '''
               功能：统一处理返回名字为Data 的jon数据（需有提交的数据）
               返回：返回的data(基本为dict格式)
    '''
    def postInfo(self , url,postData,timeout = 10):
        '''
        {"amount":500}
        统一处理返回名字为Data 的jon数据
        '''
        try:
            response = requests.post(url , headers = self.header , cookies = self.cookies , data = json.dumps(postData), timeout = timeout)
            result = response.json()
            return result
        except:
            #print('响应超时或者失败...跳过')
            self.printLog('响应超时或者失败...跳过')
            

    '''
                  功能： 获取当前时间
                  返回：无
    '''
    def getNowTime(self):
        return str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
  
    '''
                  功能： tree上色
                  返回：无
    '''
  
    def colorTable(self,tree):
        items = tree.get_children()
        for i in range(len(items)):
            if i %2 != 0 :
                self.orderTable.item(items[i] , tags = ('oddrow'))
        tree.tag_configure('oddrow' , background = '#eeeeff')
        tree.update()
    '''
                  功能： 删除存在的tree数据
                  返回：无
    '''
    def deleteTable(self,tree):
        items = tree.get_children()
        for i in items:
            self.orderTable.delete(i)

    '''
                  功能： 打印界面和本地log
                  返回：无
    '''
    def printLog(self , log , isShow = True):
        #self.logTextFelid['state'] = tk.NORMAL
        myLog = '【' + str(self.textIndex) + '】' + self.getNowTime() + '--INFO--' + log + "\n"
        with open('dhtLogs.log','a+',encoding = 'utf8') as f:
            f.write(myLog)
        if isShow:
            self.logTextFelid.insert(tk.END , myLog)
            self.logTextFelid.see(tk.END)
            #self.logTextFelid['state'] = tk.DISABLED
            self.logTextFelid.update()
            self.textIndex += 1
            self.getTimes += 1
            if self.getTimes > 1100:
                self.getTimes = 100
                self.logTextFelid.delete('1.0','1000.0')
    '''
                  功能： 开启我的线程
                  返回：无
    '''
    def myThreading(self,func,args = {},name = '抢单'):
        mythreading = threading.Thread(target = func , args = args)
        mythreading.start()
        self.printLog('%s线程开启....'%name)
        return mythreading

    '''
                  功能： 字符串转换时间
                  返回：无
    '''
    def changeTime(self ,string ,returnTime = False):
        #/Date(1545875078247)/
        #print(string)
        if string:
            string = string[6:16]
            if returnTime:
                return string
            return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(int(string)))
        else:
            return "无"
    '''
                  功能： 关闭系统时需做的事情
                  返回：无
    '''
    def closeSys(self):
        if tkinter.messagebox.askyesno('系统确认退出','确定要退出系统吗？'):
            if self.isOpenWechat.get() == 1:
                self.printLog('微信退出...')
                itchat.logout()
            self.ini['autoRefreshSpace'] = self.autoRefreshSpace.get()
            self.ini['openSound'] = self.openSound.get()
            self.ini['threadNumbers'] = self.threadNumbers.get()
            self.ini['selectedArea'] = self.selectedArea.get()
            self.saveIni()
            #self.printLog('系统退出')
            self.root.destroy()
            import sys
            sys.exit()

    '''
                  功能： 播放声音
                  返回：无
    '''
    def playSound(self):
        try:
            if self.openSound.get() == 1:
                winsound.PlaySound('notice.wav', winsound.SND_ASYNC)
        except:
            
            tkinter.messagebox.showerror('警告','notice.wav文件不存在！')

    '''
                  功能： 获取中间位置
                  返回：[x,y]
    '''
    def getCenterPosition(self , adjust_x , adjust_y):
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()
        return (int((width-adjust_x)/2) , int((height-adjust_y)/2))
        
    def loginWechat(self):
        def mySend(content):
            itchat.send_msg(msg=content, toUserName=self.toUserName)
        #重写自动回复函数
        def getUserName(nickName):
            for i in self.friends:
                if nickName == i.get('NickName'):
                    return i.get('UserName')

        def dealMsg(content:str):
            dealTime = self.getNowTime()
            if content == 'ok' or content == 'OK':
                needNotice = True
                for i in self.ordersInfo:
                    #如果存在未处理订单，则操作，假设全部都没有需要提醒的则提示没有订单需要处理
                    if i.get('State') == 10:
                        url = self.host+'Api/Charge/OrderChargeNotify'
                        orderId = i.get('Id')
                        data = {"orderId": orderId}
                        self.printLog('发送消息：%s' % data)
                        result = self.postInfo(url, data)
                        message = result.get("Message")
                        if message != '操作成功':
                            tkinter.messagebox.showerror('*******警告*******', '操作失败，错误原因：%s' % message)
                            mySend( '操作失败，错误原因：%s' % message)
                        self.printLog('返回消息-【充值完成】：%s' % message)
                        mySend( '%s返回消息-%s【充值完成】：%s' %(dealTime,i.get('Account'),message))
                        needNotice = False
                
                if needNotice:
                    mySend('暂无需要处理的订单')
                else:
                    self.refreshTable()

            elif '+' in content and content.startswith('1'):
                phone , isOk = content.split('+')
                phones = {}
                for i in self.ordersInfo:
                    if i.get('State') == 10:
                        phones[i.get('Account')] = i.get('Id')
                if phone in phones.keys() and (isOk == 'ok' or isOk == 'OK'):
                    url = self.host+'Api/Charge/OrderChargeNotify'
                    orderId = phones.get(phone)
                    data = {"orderId": orderId}
                    self.printLog('发送消息：%s' % data)
                    result = self.postInfo(url, data)
                    message = result.get("Message")
                    if message != '操作成功':
                        tkinter.messagebox.showerror('*******警告*******', '操作失败，错误原因：%s' % message)
                        mySend( '%s操作失败，错误原因：%s' %(dealTime, message))
                    self.printLog('返回消息-【充值完成】：%s' % message)
                    mySend( '%s返回消息-%s【充值完成】：%s' %(dealTime,phone,message))
                    self.refreshTable()
                elif phone in phones.keys() and (isOk == 'no' or isOk == 'NO'):
                    url = self.host+'Api/Charge/CancelOrderNotify'
                    orderId = phones.get(phone)
                    data = {"orderId": orderId, "state": 10}
                    result = self.postInfo(url, data)
                    self.printLog('发送消息：%s' % data)
                    self.printLog('返回消息-失败订单：%s' % result.get("Message"))
                    mySend(  '%s返回消息-失败订单：%s' %(dealTime,result.get("Message")))
                else:
                    mySend(  '输入信息有误，请按提示输入！')
            elif content.startswith('开始抢单+') and len(content.split('+')) == 4:
                province , amount , num  = content.split('+')[1:]
                self.getPhoneThreads(province,amount,num)
                mySend('正在抢单....%s省，%s面值，%s单'%(province,amount,num))
            elif content.startswith('开始抢单+') and len(content.split('+')) == 5:
                province , amount , num ,ispType  = content.split('+')[1:]
                self.getPhoneThreads(province,amount,num,ispType)
                mySend('正在抢单....%s省，%s面值，%s单,%s运营商'%(province,amount,num,ispType))
            elif '停止抢单' == content:
                if self.ISRUNING :
                    mySend('停止抢单成功...')
                    self.beginGetPhoneBt['state'] = tk.NORMAL
                    self.beginGetPhoneBt['text'] = '开始抢单'
                    self.ISRUNING = False
                    print('ok')
                    
                else:
                    mySend('没有抢单，无需停止...')
            else:
                mySend(  '输入信息有误，请按提示输入！')
        #@itchat.msg_register
        @itchat.msg_register('Text')
        def textReply(msg):
            #print(msg)
            #内部函数，处理消息
            #print(msg['FromUserName'],self.friends[0]['UserName'],self.toUserName)#偶发没收到消息的情况
            content = msg['Text']
            if msg['FromUserName'] != self.friends[0]['UserName'] and self.toUserName == msg['FromUserName']:
                autoReply = '回复ok，全部充值成功\n回复手机号+ok某个订单成功\n回复手机号+no某个订单失败\n回复开始抢单+(省份可缺)+面值+单数+(0移动1联通2电信)\n回复停止抢单'
                mySend(autoReply)
                dealMsg(content)

        if self.isOpenWechat.get() == 1:
            imgPath = 'wechat.gif'
            #itchat.auto_login(hotReload = True)
            uuid = itchat.get_QRuuid()
            img = qrcode.make("https://login.weixin.qq.com/l/%s"%uuid)
            img.save(imgPath)
            weChatPanel = tk.Toplevel()
            weChatPanel.title('微信登陆')
            weChatPanel.geometry('400x400+%s+%s'%(self.getCenterPosition(400,400)))
            img = tk.PhotoImage(file=imgPath)
            myImg = tk.Label(weChatPanel, image=img)
            myImg.pack()
            #可能是tk的bug，需重新给属性命名
            myImg.image = img
            self.printLog('请扫码登录微信····')
            while True:
                code = int(itchat.check_login(uuid))
                if code == 200:
                    self.printLog('微信登录成功....')
                    weChatPanel.destroy()
                    break
                elif code == 201:
                    self.printLog('等待扫码确认....')
                elif code == 408:
                    self.printLog('微信登录超时....')
                elif code == 400:
                    self.printLog('取消微信登录....')
                    weChatPanel.destroy()
                    break
                else:
                    self.printLog('未知错误！,请重新登录')
                    weChatPanel.destroy()
                    return
                time.sleep(1)
            itchat.web_init()
            self.printLog('微信初始化成功....')
            itchat.show_mobile_login()
            self.printLog('微信手机状态成功....')
            itchat.start_receiving()
            self.printLog('微信心跳开启成功....')
            self.friends = itchat.get_friends(update = True)
            self.toUserName = getUserName('咚咚咚')
            itchat.run()
        else:
            itchat.logout()
            self.printLog('微信退出成功....')
        
    
    '''
    功能：提供多线程进行抢单
    '''
    def getPhoneThreads(self , province = None,amount = None , needPhones = None ,ispType = None):
        def getPhones(threadName = ''):
            nowOrder = getedPhones.get()
            nowOrderBak = 0
            self.printLog('启动线程，当前获取的手机号数：%s'%nowOrder)
            while int(nowOrder) < int(needPhones):
                
                # 是否点击停止抢单
                if not self.ISRUNING:
                    if getedPhones.qsize() == 0:
                        getedPhones.put(needPhones)
                    self.printLog('线程%s：，结束抢单'%threadName)  
                    return
                #抢单函数
                result = self.postInfo(url, data)
                if result:
                    Message = result.get('Message')
                    if Message != '暂无订单':
                        self.refreshTable()
                        self.printLog('线程%s'%threadName+str(result))
                        nowOrder = self.totalPhones - nowPhones
                        #避免错误数据，导致错误提示
                        if nowOrder != nowOrderBak:
                            nowOrderBak = nowOrder
                            #self.root.wm_attributes('-topmost',1)
                            self.playSound()
                            #self.root.wm_attributes('-topmost',0)
                    #把结果放入公共变量
                    if getedPhones.qsize() == 0:
                        getedPhones.put(nowOrder)
                    self.printLog('线程%s：'%threadName+str(Message))
                else:
                    self.printLog('线程%s：，跳过...'%threadName)
                    if getedPhones.qsize() == 0:
                        getedPhones.put(nowOrder)

       
                #下一阶段的开始了
                nowOrder = getedPhones.get()
            if getedPhones.qsize() == 0:
                getedPhones.put(needPhones)
            self.printLog('线程%s：，结束抢单'%threadName)   
            self.endGetPhoneBt()

                
        #预处理
        url = self.host+'Api/Charge/GetOrder'
        #先把不符合的给剔除
        if self.isOpenWechat.get() == 1 and (not amount or  not needPhones) :
            itchat.send_msg(msg ='请正确填写抢单数量和抢单面额' , toUserName = self.Username)
            return
        elif self.isOpenWechat.get() != 1 and (not amount or not needPhones):
            tkinter.messagebox.showinfo('警告', '请选择抢单数量和抢单面额')
            return
        #运营商选择
        if ispType:
            pass
        elif self.selectedCarrier.get() =='全部':
            ispType = ''
        elif self.selectedCarrier.get() == '移动':
            ispType = '0'
        elif self.selectedCarrier.get() == '联通':
            ispType = '1'
        elif self.selectedCarrier.get() == '电信':
            ispType = '2'
        self.beginGetPhoneBt['state'] = tk.DISABLED
        self.beginGetPhoneBt['text'] = '抢单ing....'
        data = {"amount": amount, "province": province, "num": needPhones ,"ispType" : ispType}
        self.printLog(str(data))
        self.beginGetPhoneBt.update()
        self.ISRUNING = True
        #面板上的订单数量
        nowPhones = self.totalPhones
        #抢单时的数量
        getedPhones = Queue(1)
        getedPhones.put(0)
        myThread = []
        for i in range(self.threadNumbers.get()):
            t = threading.Thread(target= getPhones , args = ('线程%s'%(i+1),))
            t.start()
            self.printLog('开启线程%s...'%t.name)
            myThread.append(t)



            
        
#for 注册
class myEntry(tk.Entry):
    def __init__(self, root ,previouInfo, **kw):
        super().__init__(root ,**kw)
        self.previouInfo = previouInfo
        self.stringVar = tk.StringVar()
        self.stringVar.set(self.previouInfo)
    
        self.config(fg = '#dbdbdb' )
        self.config(textvariable = self.stringVar)
        self.count = 0

        self.bind('<FocusIn>' , self.firstClickClear)
        self.bind('<FocusOut>' , self.cheakContent)
    def firstClickClear(self ,event):
        if self.count == 0:
            self.stringVar.set('')
            self.config(fg = 'black')
            self.count += 1
    def cheakContent(self , event):
        if self.stringVar.get() == '':
            self.config(fg = '#dbdbdb' )
            self.stringVar.set(self.previouInfo)
            self.count = 0


    




        
if __name__ == '__main__':
    root = tk.Tk()
    a = loginPanle(root)
    root.mainloop()
