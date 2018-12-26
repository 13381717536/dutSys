import tkinter as tk
from tkinter import ttk
import tkinter.scrolledtext 
import tkinter.messagebox
import requests
import json
import pickle
import time
import datetime
import re
import os
import threading

class loginPanle():
    
    def __init__(self,root):
        self.root = root
        self.root.title('国联话费外包平台')
        self.winWidth = self.root.winfo_screenwidth()
        self.winHeght = self.root.winfo_screenheight()
        self.username = tk.StringVar()
        #self.username.set('18482322413')
        self.pwd = tk.StringVar()
        #self.pwd.set('z123456')
        self.saveCount = tk.IntVar()
        #是否在抢单中
        self.ISRUNING = False
        self.totalPhones = 0
        self.textIndex = 0
        self.getTimes = 0
        self.header = {
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': 'http://duihuantu.com/',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Content-Type': 'application/json'#这个对于post 的解析不同，可深入研究
            }
        self.setupUI()
        
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
        userPath = 'GLusers.txt'
        if os.path.isfile(userPath):
            with open(userPath,'r') as f:
                            result = f.readline()
                            user , name = result.split('-')
                            self.username.set(user)
                            self.pwd.set(name)
        
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
            code_img = code_img.subsample(3)
            codeLabel.config(image = code_img)
            codeLabel.image = code_img
        def getId():
            
            url = "http://duihuantu.com/Api/Common/SendSms"
            data = {'account' : account.stringVar.get(),"kaptchaCode" :imageCode.stringVar.get() }
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
            isok = True
            data = {}
            data['refererId'] = ''
            myWeight = list(zip(weights_str,weights))
            for name , weight in myWeight:
                if weight == bankName:
                    if bankNameVar.get() == '请选择提现银行':
                        tkinter.messagebox.showinfo('提醒','请选择提现银行')
                        isok = False
                        break
                    else:
                        data[name] = bankNameVar.get()
                           
                else:
                    if weight.stringVar.get() == weight.previouInfo:
                        tkinter.messagebox.showinfo('提醒',weight.previouInfo)
                        isok = False
                        break
                    elif name == 'account':
                        tem = weight.stringVar.get()
                        
                        if  re.match('\d{11}',tem) == None or len(tem) != 11:
                            tkinter.messagebox.showinfo('提醒','11位电话号码填写不正确')
                            isok = False
                            break
                    
                    
                    data[name] = weight.stringVar.get()
            if isok :
                url = 'http://duihuantu.com/Api/User/SignUp'
                response = requests.post(url , data = json.dumps(data) , cookies = temCookies , headers = self.header)
                result = response.json().get('Message')
                tkinter.messagebox.showinfo('消息',result)
        def backLogin(event = None):
            registPanel.destroy()
            self.root.attributes('-disabled',0)
        #内部函数#####
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
        url = 'http://duihuantu.com/assets/images/logo2.png'
        with open(logoFile , 'wb') as f:
            logo = requests.get(url).content
            f.write(logo)
        img = tk.PhotoImage(file = logoFile)
        
        logoLabel = tk.Label(registPanel , image=img)
        logoLabel.pack()
        entry_width = 25
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
        imageCode =myEntry(registPanel , '请输入图片验证码' ,width =entry_width)
        smsCode = myEntry(registPanel , '请输入短信验证码' ,width =entry_width)
        #####完成#####
        #获取验证图片和临时cokies
        imgUrl = 'http://duihuantu.com/Api/Common/GetKaptcha?time=0.25296404468058964'
        response_img = requests.get(imgUrl)
        codeImgFile = 'code.png'
        with open(codeImgFile , 'wb') as f:
            code = response_img.content
            f.write(code)
            f.close()
        code_img = tk.PhotoImage(file = codeImgFile)
        #缩小n倍
        code_img = code_img.subsample(3)
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
        weights = [account , password ,qq ,bankName,idCard ,realName ,bankCardId,imageCode,smsCode]
        weights_str = ['account' , 'password' ,'qq' ,'bankName','idCard' ,'realName' ,'bankCardId','imageCode','smsCode']
        for entry in weights:
            entry.pack(pady = 5)
        
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
        height_ = 610
        operateGroup_height = 120
        orderTableFrame_height = 220
        balancePanle_height = 40
        logPanel_height =220
        
        self.root.geometry('%dx%d+%d+%d'%(width_,height_,(self.winWidth-width_)/2,(self.winHeght-height_)/2))
        self.mainFrame = tk.Frame(self.root)
        
        #************操作区域都放在这里******************#
        
        operateGroup = tk.LabelFrame(self.mainFrame , text = '操作区域' , width = width_ ,height = operateGroup_height )
        #将订单显示部分放入到一个框中
        orderInfoPanel = tk.Frame(operateGroup)
        #订单大小
        self.sizeVar = tk.IntVar()
        #sizeVar.set(10)
        orderInfo = self.getStandbyOrderNum()
        leatestMountLabels = []
        #第一第二部分
        for i ,face in enumerate(orderInfo.items()):
            phoneFaceRadio = tk.Radiobutton(orderInfoPanel , text = face[0].replace('Amount',''),variable = self.sizeVar , value = int(face[0].replace('Amount','')))
            leatestMountLabel = tk.Label(orderInfoPanel , text = ' ' + str(face[1])+'  单')
            phoneFaceRadio.grid(row = 0, column = i ,sticky = tk.W )
            leatestMountLabel.grid(row = 1, column = i ,sticky = tk.W )
            leatestMountLabels.append(leatestMountLabel)
        #第三部分 放入一个  功能  setting 框
        getPhoneSettingPanel = tk.Frame(operateGroup)
        
        getPhoneLabel = tk.Label(getPhoneSettingPanel , text = '抢单数量')
        getPhoneLabel.pack(side = tk.LEFT , padx = 5)
        #下拉列表值
        self.comboVar = tk.StringVar()
        getPhoneNumberCombobox = ttk.Combobox(getPhoneSettingPanel,width = 2 , textvariable = self.comboVar ,values = [ i for i in range(1,11)])
        #getPhoneNumberCombobox.setvar('1')
        getPhoneNumberCombobox.pack(side = tk.LEFT , padx = 5)
        #开始和结束抢单按钮
        beginGetPhoneBt = tk.Button(getPhoneSettingPanel , text = '开始抢单')
        beginGetPhoneBt.config(command = lambda : self.myThreading(self.beginGetPhone ,(beginGetPhoneBt,))) 
        endGetPhoneBt = tk.Button(getPhoneSettingPanel , text = '停止抢单' )
        endGetPhoneBt.config(command = lambda : self.endGetPhoneBt(beginGetPhoneBt)  )
        beginGetPhoneBt.pack(side = tk.LEFT , padx = 5)
        endGetPhoneBt.pack(side = tk.LEFT , padx = 5)
        #刷新订单
        refreshMountBt = tk.Button(getPhoneSettingPanel , text = '刷新订单数量')
        refreshMountBt.config(command = lambda : self.refreshMount(self.getStandbyOrderNum() , leatestMountLabels))
        refreshMountBt.pack(side = tk.LEFT , padx = 5)
        orderInfoPanel.pack(pady = 5 , fill = tk.X)
        getPhoneSettingPanel.pack(fill = tk.X)

        #*************抢单展示区域*****************#
        orderTableFrame = tk.Frame(self.mainFrame, width = width_ ,height = orderTableFrame_height)
        columnsName = ['序号','号码','充值详情','平台需支付你',"充前/充后","订单状态","id"]
        displaycolumns = ['序号','号码','充值详情','平台需支付你',"充前/充后","订单状态"]
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
            self.orderTable.column(index_column  , width = 100 )
            self.orderTable.heading(index_column  , text = columnName)
        temLenth = 40
        self.orderTable.column('序号' , width = temLenth)
        self.orderTable.column('号码' , width = temLenth*2+4)
        self.orderTable.column('充值详情' , width = temLenth*3)
        self.orderTable.column('平台需支付你' , width = temLenth*2)
        self.orderTable.column('id' , width = temLenth*5)
        #初始化面板
        for i in range(10):
            self.orderTable.insert('',i ,values = ['','','',''])
        self.orderTable.bind('<Button-3>',self.showmenu)
        self.orderTable.pack(side = tk.LEFT , fill = tk.X)
        
        self.colorTable(self.orderTable)
        
        
        
        #***********显示总提现额度，和提现功能********#
        balancePanle = tk.LabelFrame(self.mainFrame, width = width_ ,height = balancePanle_height)
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
        #ttk.Notebook 控制tab页的东东
        tabControl = ttk.Notebook(logPanel)
        #tab页
        logPanelTab = tk.LabelFrame(logPanel)
        settingPanelTab = tk.LabelFrame(logPanel )
        tabControl.add(logPanelTab ,text = '日志打印')
        tabControl.add(settingPanelTab, text = '功能设置')
        
        #log打印页面
        self.logTextFelid = tkinter.scrolledtext.ScrolledText(logPanelTab)
        self.logTextFelid.pack(fill = tk.BOTH)
        tabControl.pack()
        #****************模块安装**********#
        for panel in [operateGroup , orderTableFrame ,balancePanle ,logPanel]:
            panel.pack_propagate(False)#固定frame大小
            panel.pack()
            
        
        self.mainFrame.pack()
        




#**************************************************************************#
#                          工具函数部分                                    #
#**************************************************************************#
        
    def showmenu (self,event):
        
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
            self.orderTable.config(displaycolumns = res )
            self.root.attributes('-disable',0)
            menuPanel.destroy()
            self.P = 0
        def canser():
            self.root.attributes('-disable',0)   
            menuPanel.destroy()
            self.P = 0
        def phoneCopy():
            res = ''
            selected = self.orderTable.selection()
            for item in selected:
                it = self.orderTable.item(item , 'values')
                res += it[1]+'\n'
            self.root.clipboard_clear()
            self.root.clipboard_append(res)
        def successConfirm():
            selected = self.orderTable.selection()
            for item in selected:
                it = self.orderTable.item(item , 'values')
                orderId = it[len(it)-1]
                url = 'http://duihuantu.com/Api/Charge/OrderChargeNotify'
                data = {"orderId":orderId}
                result = self.postInfo(url,data)
                self.printLog('充值完成确认：'+result.get("Message"))
            self.refreshTable()
        def failConfirm():
            selected = self.orderTable.selection()
            for item in selected:
                it = self.orderTable.item(item , 'values')
                print(len(it))
                orderId = it[len(it)-1]
                State = it[len(it)-2]
                if State == '充值成功':
                    State = 4
                elif State == "充值失败":
                    State = 5
                elif State == '供货商充值中':
                    State = 10
                elif State == '供货商充值完成':
                    State = 11
               
                if tkinter.messagebox.askyesno('确认失败？','确认失败此笔订单吗'):
                    url = 'http://duihuantu.com/Api/Charge/CancelOrderNotify'
                    data = {"orderId":orderId,"state":State}
                    result = self.postInfo(url,data)
                    self.printLog('失败订单：'+result.get("Message"))
            self.refreshTable()
                
        isWhat = self.orderTable.identify_region(event.x , event.y)
        if isWhat == 'heading':
            menuPanel = tk.Toplevel(takefocus=True)
            menuPanel.overrideredirect(True)
            menuPanel.geometry('+{}+{}'.format(event.x_root , event.y_root))
            F = tk.Button(menuPanel , borderwidth = 2)
            F['state'] = tk.DISABLED
            F.pack()
            top = tk.Frame(F)
            tk.Button(top , text = '全选',command = lambda : selectAll(checkbts)).pack(side = tk.LEFT , padx = 2)
            tk.Button(top , text ='清空',command = lambda : selectNull(checkbts)).pack(side = tk.LEFT, padx =2)
            mid = tk.LabelFrame(F , text ='定制你的专属表头')
            checkbts = []
            checkInfo = []
            for i in self.orderTable['columns']:
                iv = tk.IntVar()
                cb = tk.Checkbutton(mid , text = self.orderTable.heading(i , 'text'),variable = iv)
                cb.pack(side = tk.LEFT)
                if i in self.orderTable['displaycolumns']:
                    cb.select()
                _cb = cb
                _iv = iv
                checkInfo.append(_iv)
                checkbts.append(_cb)                  
            buttom = tk.Frame(F)
            tk.Button(buttom , text = '确定',command =lambda: confirm(checkInfo)).pack(side = tk.LEFT , padx = 2)
            tk.Button(buttom, text ='取消',command = canser).pack(side = tk.LEFT, padx =2)
            top.pack()
            mid.pack()
            buttom.pack()
            self.root.attributes('-disable',1)
        elif isWhat == 'cell':
            menu = tk.Menu(self.orderTable ,tearoff = False)
            menu.add_command(label = '复制' ,command = phoneCopy)
            menu.add_command(label = '确认充值完成' ,command = successConfirm)
            menu.add_separator()
            menu.add_command(label = '确认充值失败' ,command = failConfirm)
            #menu.add_command(label = '导出EXCEL文件', command = exportExcel)
            menu.post(event.x_root ,event.y_root)

                
    def myPost(self,url , data ,cookies = None):
        if cookies:
            response = requests.post(url , headers  = self.header , data = json.dumps(data) ,cookies = cookies)
        else :
            response = requests.post(url , headers  = self.header , data = json.dumps(data),cookies = self.cookies)
        
        return response
    
    def checkCount(self , event = None):
        #网络登录部分
        loginUrl = 'http://duihuantu.com/Api/User/SignIn'
        header = self.header
        user = self.username.get()
        pwd = self.pwd.get()
        if  user and pwd :
            data = {"account":str(user) ,"password":str(pwd) ,"rememberme":""}
            response = requests.post(loginUrl , headers  = header ,data = json.dumps(data))
            #print (response.text)
            result = response.json()
            self.cookies = response.cookies
            #with  open('cookies' , 'wb') as cookiesFile:
            #    pickle.dump(self.cookies,cookiesFile)
            if result.get('Message') != '登录成功':
                tkinter.messagebox.showwarning('警告','用户名或者密码错误！')
            else:
                
                self.loginFrame.destroy()
                self.mainPage(result)
                self.printLog('系统登录成功；用户名：%s'%user)
                if self.saveCount.get() == 1:
                    with open('GLusers.txt','w') as f:
                        f.write(user+'-'+pwd)
            
        else :
            tkinter.messagebox.showinfo('注意','用户名或者密码不能为空')
    def reflashBalance(self):
        balanceInfo = self.getBalance()
        showBalace = '总提现额度:%s ; 可提现余额:%s'%(balanceInfo.get('TotalTradeAmount'),balanceInfo.get('Balance'))
        self.balanceInfoLabel["text"] = showBalace
        self.printLog('刷新余额成功....')
    def refreshTable(self):
        self.deleteTable(self.orderTable)
        orders = self.getPhoneInfo()
        sequence = 0
        for order in orders:
            #排序
            sequence += 1
            #手机号
            phoneNumber = order.get('Account')
            #详情
            ProductName = order.get('ProductName')
            #平台需支付你
            CostPrice = order.get('CostPrice')
            #充值前、后
            PreBalance = str(order.get("PreBalance"))
            PostBlance = str(order.get("PostBlance"))
            #状态
            State = order.get('State')
            #id
            Id = order.get("Id")
            if State == 4:
                State = '充值成功'
            elif State == 5:
                State = '充值失败'
            elif State == 10:
                State = '供货商充值中'
            elif State == 11:
                State = '供货商充值完成'
            self.orderTable.insert('',sequence -1 , values =(sequence ,phoneNumber , ProductName,CostPrice , PreBalance+"/"+PostBlance , State,Id))
        self.colorTable(self.orderTable)
        self.printLog('刷新订单信息成功....')
    def refreshMount(self , orderInfo , leatestMountLabels):
        for i in range((len(leatestMountLabels))):
            leatestMountLabels[i]['text'] = ' ' + str(list(orderInfo.values())[i]) + '  单'
        self.refreshTable()
        self.reflashBalance()
    def getBalance(self):
        '''
        #获取余额，总提现等信息
        {'Data':
        {'Balance': 0.0,
        'FreezeBalance': 0.0,
        'TotalCommissionBalance': 0.0,
        'TotalTradeAmount': 234259.12},
        'Message': '余额查询成功', 'State': 0}
        '''
        url = 'http://duihuantu.com/Api/Finance/GetBalance'
        return self.getInfo(url)
    #########提现功能##################
    def balance2Count(self , amount):
        
        url = "http://duihuantu.com/Api/Finance/TransferApply"
        if not amount:
            balanceInfo = self.getBalance()
            amount = balanceInfo.get('Balance')
        postData = {"amount":float(amount)}
        if tkinter.messagebox.askyesno('提现确认','确认提现%s元吗'%amount):
            result = self.postInfo(url,postData)
            tkinter.messagebox.showinfo("提示",result.get("Message"))
            self.printLog('提现：%s'%amount+'元'+result.get("Message"))
            self.reflashBalance()
    
    def getStandbyOrderNum(self):
        '''
        获取当前的单数
        {'Amount10': 1, 'Amount20': 0, 'Amount30': 0, 'Amount50': 0, 'Amount100': 0,
        'Amount200': 0, 'Amount300': 0, 'Amount500': 0} <class 'dict'>
        '''
        url = 'http://duihuantu.com/Api/Charge/GetStandbyOrderNum'
        return self.getInfo(url)
    def getInfo(self , url):
        '''
        统一处理返回名字为Data 的jon数据
        '''
        response = requests.post(url , headers = self.header , cookies = self.cookies)
        balanceJson = response.json()
        Data = balanceJson.get('Data')
        return Data
    def postInfo(self , url,postData):
        '''
        {"amount":500}
        统一处理返回名字为Data 的jon数据
        '''
        response = requests.post(url , headers = self.header , cookies = self.cookies , data = json.dumps(postData))
        result = response.json()
        return result
    def getPhoneInfo(self):
        '''
        这是一个获取抢到的订单的信息的面板
        
        '''
        today = time.strftime('%Y-%m-%d ',time.localtime(time.time()))
        #今天的n天后的日期。
        
        today=datetime.datetime.now()
        delta=datetime.timedelta(days=0)
        n_days=today-delta
        #print(n_days.strftime('%Y-%m-%d '),today.strftime("%Y-%m-%d "))
        url = 'http://duihuantu.com/Api/Charge/GetPage'
        data = {"pageIndex":1,"pageSize":15,"state":"","startTime":str(n_days.strftime('%Y-%m-%d '))+" 00:00:00","endTime":str(today.strftime("%Y-%m-%d "))+" 23:59:59","account":""}
        response = self.myPost(url,data).json()
        result = response.get('Data').get('Rows')
        self.totalPhones = response.get("Data").get("total")
        return result
        
    def beginGetPhone(self , bt):
        '''
        开始抢单
        postdata格式：{"amount":"500","province":"","num":"1"}
        '''
        #测试
        '''
        ok = self.getPhoneInfo()
        print(type(ok))
        for i in ok:
            print(type(i))
            print(i.get('Id') , i.get('ProductName') , i.get('Account'))
        '''
        self.refreshTable()
        url = 'http://duihuantu.com/Api/Charge/GetOrder'
        amount = self.sizeVar.get()
        num = self.comboVar.get()
        if amount and num:
            num = int(num)
            bt['state'] = tk.DISABLED
            bt['text'] = '抢单ing....'
            data = {"amount":amount,"province":"","num":'1'}
            print(data)
            bt.update()
            self.ISRUNING = True
        else :
            tkinter.messagebox.showinfo('警告','请选择抢单数量和抢单面额')
            return
        nowPhones = self.totalPhones
        nowOrder = 0
        while nowOrder < num:
            #是否点击停止抢单
            if not self.ISRUNING:
                break
            response = requests.post(url , headers = self.header , cookies = self.cookies , data = json.dumps(data))
            result = response.json()
            Message = result.get('Message')
            Data = result.get('Data')
            if Message != '暂无订单':
                self.refreshTable()
                self.printLog( str(result))
                nowOrder = self.totalPhones - nowPhones
                #print(nowOrder)
                #nowOrder += 1
                
                
            self.printLog(str(Message))
        
        self.endGetPhoneBt(bt)
            
    def endGetPhoneBt(self , bt):
        '''
        结束抢单
        '''
        bt['state'] = tk.NORMAL
        bt['text'] = '开始抢单'
        self.ISRUNING = False
    def getNowTime(self):
        return str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
    
  
    def colorTable(self,tree):
        items = tree.get_children()
        for i in range(len(items)):
            if i %2 != 0 :
                self.orderTable.item(items[i] , tags = ('oddrow'))
        tree.tag_configure('oddrow' , background = '#eeeeff')
        tree.update()
    def deleteTable(self,tree):
        items = tree.get_children()
        for i in items:
            self.orderTable.delete(i)
        
    def printLog(self , log):
        #self.logTextFelid['state'] = tk.NORMAL
        myLog = '【' + str(self.textIndex) + '】' + self.getNowTime() + '--INFO--' + log + "\n"
        self.logTextFelid.insert(tk.END , myLog)
        self.logTextFelid.see(tk.END)
        with open('dhtLogs.log','a+') as f:
            f.write(myLog)
        #self.logTextFelid['state'] = tk.DISABLED
        self.logTextFelid.update()
        self.textIndex += 1
        self.getTimes += 1
        if self.getTimes > 1100:
            self.getTimes = 100
            self.logTextFelid.delete('1.0','1000.0')
    def myThreading(self,func,args):
        mythreading = threading.Thread(target = func , args = args)
        mythreading.start()
        self.printLog('抢单线程开启....')
    def closeSys(self):
        if tkinter.messagebox.askyesno('系统确认退出','确定要退出系统吗？'):
            self.printLog('系统退出')
            self.root.destroy()
            
        
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
