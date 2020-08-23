#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
描述：一个简单的串口交互界面，可根据需要自己定义按键
依赖项: python3, serial, pyqt5
支持系统： windows, linux
linux建议采用apt命令安装
windows可采用pip命令安装
"""

from PyQt5.QtWidgets import QApplication,QWidget,QLineEdit,QTextEdit,QTextBrowser,QPushButton,QInputDialog,QLabel,QHBoxLayout,QVBoxLayout,QGridLayout
from PyQt5.Qt import QTextOption, QTextCursor
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor
from queue import Queue
import queue
import serial, threading
import sys
 
class SerialGuiDemo(QWidget):
    sinOut = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        # 多线程相关设置
        self.isworking = False
        self.sendQueue = Queue(20)
        self.sinOut.connect(self.updateReceive)

        #设置窗口名称
        self.setWindowTitle('串口调试助手')
        #定义窗口的初始大小
        self.setGeometry(50, 50, 900, 600)

        #串口信息输入
        self.label1 = QLabel("串口号")
        self.label2 = QLabel("波特率")
        self.serial_com = QLineEdit()
        self.serial_com.setFixedWidth(80)
        self.serial_baud = QLineEdit()
        self.serial_baud.setFixedWidth(80)

        #定义按键
        self.openSerialButton = QPushButton("打开串口")
        self.closeSerialButton = QPushButton("关闭串口")
        self.clearReceiveButton = QPushButton("清除接收")
        self.sendButton = QPushButton("发送")
        self.clearSendButton = QPushButton("清除")
        self.riseButton = QPushButton("上升")
        self.fallButton = QPushButton("下降")
        self.stopButton = QPushButton("停止")
        self.grabButton = QPushButton("抓取")
        self.dropButton = QPushButton("投放")
        self.closeSerialEnabledSetting()

        #接收框
        self.receiveDialog = QTextBrowser()
        self.receiveDialog.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.receiveDialog.setStyleSheet("QTextBrowser{background:black;color:green;}")
        #发送框
        self.sendDialog = QTextEdit()
        self.sendDialog.setFixedHeight(120)
        self.sendDialog.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        #将按钮的点击信号与相关的槽函数进行绑定，点击即触发
        self.openSerialButton.clicked.connect(self.openSerialButton_clicked)
        self.closeSerialButton.clicked.connect(self.closeSerialButton_clicked)
        self.clearReceiveButton.clicked.connect(self.receiveDialog.clear)
        self.sendButton.clicked.connect(self.sendButton_clicked)
        self.clearSendButton.clicked.connect(self.sendDialog.clear)
        self.riseButton.clicked.connect(lambda:self.sendQueue.put('8'))
        self.fallButton.clicked.connect(lambda:self.sendQueue.put('9'))
        self.stopButton.clicked.connect(lambda:self.sendQueue.put('0'))
        self.grabButton.clicked.connect(lambda:self.sendQueue.put('3'))
        self.dropButton.clicked.connect(lambda:self.sendQueue.put('1'))

        # 设置2x2串口波特率Grid
        grid = QGridLayout()
        grid.addWidget(self.label1, 0, 0)
        grid.addWidget(self.serial_com, 0, 1)
        grid.addWidget(self.label2, 1, 0)
        grid.addWidget(self.serial_baud, 1, 1)

        # 右上侧垂直布局
        vbox1 = QVBoxLayout()
        vbox1.addLayout(grid)
        vbox1.addWidget(self.openSerialButton)
        vbox1.addWidget(self.closeSerialButton)
        vbox1.addWidget(self.clearReceiveButton)
        vbox1.addWidget(self.riseButton)
        vbox1.addWidget(self.fallButton)
        vbox1.addWidget(self.stopButton)
        vbox1.addWidget(self.grabButton)
        vbox1.addWidget(self.dropButton)
        vbox1.addStretch(1)
 
        # 上侧水平布局
        hbox1=QHBoxLayout()
        hbox1.addWidget(self.receiveDialog, 1)
        hbox1.addLayout(vbox1, 0)

        # 右下侧垂直布局
        vbox2 = QVBoxLayout()
        vbox2.addWidget(self.sendButton)
        vbox2.addStretch(1)
        vbox2.addWidget(self.clearSendButton)

        # 下侧水平布局
        hbox2=QHBoxLayout()
        hbox2.addWidget(self.sendDialog)
        hbox2.addLayout(vbox2)

        # 整体水平布局
        vbox3 = QVBoxLayout()
        vbox3.addLayout(hbox1, 1)
        vbox3.addLayout(hbox2, 0)
        self.setLayout(vbox3)

    # 关闭软件事件发生时，先解除串口占用
    def closeEvent(self, event):
        self.closeSerialButton_clicked()
        event.accept()

    # 按键回调函数
    def openSerialButton_clicked(self):
        com = self.serial_com.text().lower()
        baud = self.serial_baud.text()
        if com and baud:
            try:
                self.tty = serial.Serial(com, baud, timeout=0.1)
            except:
                return
            else:
                self.tty.flushInput() #清空缓冲区
                self.isworking = True
                self.receiveThread = threading.Thread(target=self.ComRecvDeal)
                self.receiveThread.start()
                self.sendThread = threading.Thread(target=self.ComSendDeal)
                self.sendThread.start()
                self.openSerialEnabledSetting() #按键可用性
    
    # 按键回调函数
    def closeSerialButton_clicked(self):
        self.isworking = False
        # 如果有发送线程，则结束该线程
        try:
            self.sendThread
        except AttributeError:
            pass
        else:
            if self.sendThread.is_alive():
                self.sendThread.join()
        # 如果有接收线程，则结束该线程
        try:
            self.receiveThread
        except AttributeError:
            pass
        else:
            if self.receiveThread.is_alive():
                self.receiveThread.join()
        # 如果有未关闭的串口实例，关闭
        try:
            self.tty
        except AttributeError:
            pass
        else:
            if self.tty.isOpen():
                self.tty.close()
 
        self.closeSerialEnabledSetting() #按键可用性

    # 按键回调函数
    def sendButton_clicked(self):
        _input = self.sendDialog.toPlainText()
        if _input:
            self.sendQueue.put(_input)

    def updateReceive(self, serial_str):
        self.receiveDialog.moveCursor(QTextCursor.End)
        self.receiveDialog.append(serial_str)

    def ComRecvDeal(self):
        buffer = str()
        while self.isworking:
            ch = self.tty.read()
            if ch:
                #self.sinOut.emit(str(ch, 'utf-8'))
                ch = str(ch, 'utf-8')
                buffer = buffer + ch
                if buffer[-1] == '\n':
                    self.sinOut.emit(buffer[:-2])
                    buffer = str()

    def ComSendDeal(self):
        while self.isworking:
            try:
                content = self.sendQueue.get(timeout=0.1)
            except queue.Empty:
                continue
            self.tty.write(bytes(content, encoding='utf-8'))

    # 当开启串口后，按键的可用性设置，不可用为灰色
    def openSerialEnabledSetting(self):
        self.openSerialButton.setEnabled(False)
        self.closeSerialButton.setEnabled(True)
        self.sendButton.setEnabled(True)
        self.riseButton.setEnabled(True)
        self.fallButton.setEnabled(True)
        self.stopButton.setEnabled(True)
        self.grabButton.setEnabled(True)
        self.stopButton.setEnabled(True)

    # 当开启关闭后，按键的可用性设置，不可用为灰色
    def closeSerialEnabledSetting(self):
        self.openSerialButton.setEnabled(True)
        self.closeSerialButton.setEnabled(False)
        self.sendButton.setEnabled(False)
        self.riseButton.setEnabled(False)
        self.fallButton.setEnabled(False)
        self.stopButton.setEnabled(False)
        self.grabButton.setEnabled(False)
        self.dropButton.setEnabled(False)
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = SerialGuiDemo()
    win.show()
    sys.exit(app.exec_())