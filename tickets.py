# -*- coding: utf-8 -*-

from splinter import Browser
from time import sleep
import time, sys, splinter
import traceback

"""
此脚本仅支持firefox，此脚本仅在windows上测试过
需要下载WebDriver,详情参考https://splinter.readthedocs.io/en/latest/drivers/firefox.html
使用到的python库:splinter,six
请用管理员劝权限，使用pip install [package]命令安装
"""

class tickets(object):
    # 用户名，密码
    username = None
    passwd = None
    # 起始站和终点站
    starts = None
    ends = None
    # 时间格式2019-02-20
    dtime = None
    # 车次
    order = None
    # 乘客名
    passenger = None
    # 席位
    seatType =  None
    # 是否学生票
    isStudent = False
    # 刷新周期
    refresh_period = 5
    # 座位类型对照表
    __seatTypeList=[None,"YZ_",None,"YW_"]

    """网址"""
    ticket_url = "https://kyfw.12306.cn/otn/leftTicket/init"
    login_url = "https://kyfw.12306.cn/otn/resources/login.html"
    initmy_url = "https://kyfw.12306.cn/otn/view/index.html"
    buy_url="https://kyfw.12306.cn/otn/confirmPassenger/initDc"

    def __init__(self):
        self.driver_name='firefox'

    def login(self):
        self.driver.visit(self.login_url)
        sleep(1)
        # 填充密码
        self.driver.find_by_text("账号登录")[0].click()
        self.driver.find_by_id("J-userName")[0].fill(self.username)
        self.driver.find_by_id("J-password")[0].fill(self.passwd)
        print("等待验证码，自行输入...")
        while True:
            if self.driver.url != self.initmy_url:
                sleep(1)
            else:
                break

    def start(self):
        # 检测参数是否为空
        if not self.username or not self.passwd or not self.starts or not self.ends \
            or not self.dtime or not self.order or not self.passenger or not self.seatType:
            print("请初始化参数username,passwd,starts,ends,dtime,order,passenger,seatType...")
            return
        # 打开浏览器 
        self.driver=Browser(driver_name=self.driver_name)
        # 登陆
        self.login()
        # 开始抢票
        self.driver.visit(self.ticket_url)

        print("购票页面开始...")
        # 修改cookie
        self.driver.cookies.add({"_jc_save_fromStation": self.starts})
        self.driver.cookies.add({"_jc_save_toStation": self.ends})
        self.driver.cookies.add({"_jc_save_fromDate": self.dtime})
        # 重新载入
        self.driver.reload()

        while self.driver.url==self.ticket_url:
            # 点击查询按钮
            try:
                sleep(self.refresh_period)
                if self.driver.is_element_present_by_id("query_ticket",5):
                    self.driver.click_link_by_id("query_ticket")
                
                    if self.driver.is_element_present_by_id("ticket_"+self.order,3):
                        train_info=self.driver.find_by_id("ticket_"+self.order)
                        train_seat=train_info.find_by_id(self.__seatTypeList[self.seatType]+self.order)[0]
                
                        if train_seat.text!="无" and train_seat.text!="--":
                            print("有票，准备预订...")
                            train_info.find_by_text("预订")[0].click()
                else:
                    self.driver.reload()
            except:
                self.driver.reload()

        print('开始选择用户...')
        # 等待加载
        if self.driver.is_element_present_by_id("normal_passenger_id",5):
            if self.driver.is_element_present_by_text(self.passenger,5):
                psg_list=self.driver.find_by_id("normal_passenger_id")
                psg_list.find_by_text(self.passenger)[0].click()
                if "学生" in self.passenger:
                    self.driver.is_element_present_by_id("dialog_xsertcj_ok",5)
                    self.driver.find_by_id("dialog_xsertcj_ok")[0].click()

                print("开始选座...")
                # 3:硬卧，1:硬座
                self.driver.is_element_present_by_id("seatType_1",5)
                # select要求元素必须有name属性，由于12306只指定了选项的id
                # 我们模仿select函数的定义，构造select_by_id
                self.driver.find_by_xpath(
                    '//select[@id="%s"]//option[@value="%s"]' % ("seatType_1",str(self.seatType))
                    ).first._element.click()

                print('提交订单...')
                self.driver.is_element_present_by_id("submitOrder_id",5)
                #self.driver.find_by_id('submitOrder_id').click()

                #self.driver.is_element_present_by_id("qr_submit_id",5)
                #self.driver.find_by_id('qr_submit_id').click()
            else:
                print('找不到text为\"%s\"的元素，程序即将退出...'%self.passenger)
                

cities={
    '洛阳':'%u6D1B%u9633%2CLYF',
    '南京':'%u5357%u4EAC%2CNJH',
    '上海':'%u4E0A%u6D77%2CSHH'
}

trains={
    'k736':'400000K7360I',
    'k2668':'27000K26650A',
    'k558':'4a0000K5590X',
    'k738':'550000K73865',
    'k2666':'55000K266622'
}

seats={
    '硬座': 1,
    '硬卧': 3
}

if __name__ == '__main__':
    myticket=tickets()
    # 自行修改下列参数
    myticket.starts=cities['洛阳']
    myticket.ends = cities['上海']
    myticket.order = trains['k736']
    myticket.dtime = '2019-02-20'
    myticket.passenger="段胜青(学生)"
    myticket.isStudent=True
    myticket.seatType=seats['硬座']
    myticket.username = '12303账号'
    myticket.passwd = '密码'
    myticket.refresh_period = 5 # 刷新时间间隔(秒)
    myticket.start()
