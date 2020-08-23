#!/usr/bin/python3
# -*- coding: utf-8 -*-
import serial
import pyqtgraph as pg
import threading
from time import sleep
import sys

"""
ReadMe:

需要安装pyserial、pyqtgraph
windows用户在管理员模式下使用`py -m pip install pyserial pyqtgraph`命令即可

使用方法
方法1. 命令行。示例:`py myplot.pyw com3 9600`
方法2. 修改源文件中78和79行的串口和波特率后，双击即可运行

"""

# 采用环形线性表结构
# data_index指向data_list中最旧的数据
# data_index-1指向data_list中最新的数据
Max_count = 200 #页面最多显示的数据个数
data_list = [0] * 200#存放所有收到的数据
data_index = 0
data_t = [0.1*i for i in range(200)]
isDrawing = False
isRunning = True

app = pg.mkQApp()
win = pg.GraphicsWindow()
win.setWindowTitle(u'python示波器')
p = win.addPlot()#win.addPlot()添加一个波形窗口，多次调用会将窗口分成多个界面
curve = p.plot()#为新的变量添加新的曲线
#配置波形显示信息 
p.showGrid(x=True, y=True, alpha=0.5)
p.setLabels(left='voltage', bottom='t/ms', title='串口波形')#left纵坐标名 bottom横坐标名
#设置坐标范围
p.setRange(yRange=(0,3))

# 要改变界面显示的曲线，只需改变curve存储的数据即可
def addToDisplay():
    global isDrawing, data_list, data_index, data_t, Max_count, curve
    isDrawing = True
    _idx = data_index
    _data = []

    for i in range(_idx, _idx + Max_count):
        _data.append(data_list[i%Max_count]/256*3)

    isDrawing = False
    curve.setData(data_t, _data)
    

 
def ComRecvDeal(com, baud, readtime):
    global isDrawing, isRunning,  data_list, data_index, Max_count
    
    try:
        tty = serial.Serial(com, baud, timeout=readtime)
    except:
        print("串口 " + com + " 打开失败")
        sys.exit()

    tty.flushInput() #先清空一下缓冲区
    while isRunning:
        if not isDrawing:
            ch = tty.read()
			#判断是否读取到字节
            if ch:
                num = ord(ch) # 转为数字
				# 更新环形线性表
                data_index = (data_index - 1) % Max_count
                data_list[data_index] = num
    tty.close()   

if __name__ == "__main__":
    com = "com4"
    baud = 9600
    readtime = 0.1
    if len(sys.argv) > 2:
        com = sys.argv[1]
        baud = sys.argv[2]

    th = threading.Thread(target=ComRecvDeal, args=(com, baud, readtime))#创建串口接收线程
    th.start()
    timer = pg.QtCore.QTimer()
    timer.timeout.connect(addToDisplay) #定时刷新数据显示
    timer.start(10)
    try:
        sys.exit(app.exec_())        
    except:
        print("Program End.")
    finally:
        timer.stop()
        isRunning = False
        th.join()
