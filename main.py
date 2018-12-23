#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import sys
import commands
import re
#从PyQt库导入QtWidget通用窗口类,基本的窗口集在PyQt5.QtWidgets模块里.
from PyQt5.QtWidgets import QApplication, QWidget,QSystemTrayIcon,QAction,QMenu,qApp,QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QCoreApplication

DEBUG = False

def getUSBHostInfo():
    result = []
    ret, info = commands.getstatusoutput("VBoxManage list usbhost")

    for aa in str(info).split("\n\n"):
        uuid = None
        product = None
        state = None
        for aaa in aa.split("\n"):
            uuidpattern = re.compile(
            r"(?:UUID:)(?:\s*)(?P<UUID>[A-Z0-9]{8}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{12})",
            re.IGNORECASE|re.DOTALL)
            m = re.search(uuidpattern, str(aaa))
            if m is not None:
                uuid=m.group('UUID')
                continue
            productpattern = re.compile(
            r"(?:Product:)(?:\s*)(?P<PRODUCT>[^\n]+)",
            re.IGNORECASE|re.DOTALL)
            m = re.search(productpattern, str(aaa))
            if m is not None:
                product=m.group('PRODUCT')
                continue
            statepattern = re.compile(
            r"(?:Current State:)(?:\s*)(?P<STATE>[^\n]+)",
            re.IGNORECASE|re.DOTALL)
            m = re.search(statepattern, str(aaa))
            if m is not None:
                state=m.group('STATE')
                continue
        if uuid == None or product == None or state == None or state == "Busy":
            continue
        result.append([product, uuid, state])
    return result

if DEBUG:
    for usbinfo in getUSBHostInfo():
        print(usbinfo)
    exit(0)

tpactions = []
if __name__ == '__main__':
    # pyqt窗口必须在QApplication方法中使用
    # 每一个PyQt5应用都必须创建一个应用对象.sys.argv参数是来自命令行的参数列表.Python脚本可以从shell里运行.这是我们如何控制我们的脚本运行的一种方法.
    app = QApplication(sys.argv)
    # 关闭所有窗口,也不关闭应用程序
    QApplication.setQuitOnLastWindowClosed(False)
    from PyQt5 import QtWidgets
    tp = QSystemTrayIcon()
    tp.setIcon(QIcon('./usb.png'))

    tpMenu = QMenu()

    class UsbSwitch(QAction):
        def __init__(self, name, uuid, state):
            QAction.__init__(self, name)
            self.setCheckable(True)
            self.setVisible(True)
            self.triggered.connect(self.usbswitch)
            self.name = name
            self.uuid = uuid
            self.state = state
            if (self.state == "Captured"):
                self.setChecked(True)
            pass
        
        def usbswitch(self, switched):
            cmd = "VBoxManage controlvm Ubuntu "
            #ret, info = commands.getstatusoutput(cmd)
            print
            if switched:
                print("attach " + self.name)
                cmd = cmd + "usbattach "
            else:
                print("deattach " + self.name)
                cmd = cmd + "usbdetach "
            cmd = cmd + self.uuid
            print(cmd)
            commands.getstatusoutput(cmd)
            return
            
    def addUSBHostlist():
        actions = []
        usbinfos = getUSBHostInfo()
        for info in usbinfos:
            actions.append(UsbSwitch(info[0], info[1], info[2]))
        return actions
    def quitApp():
        QCoreApplication.instance().quit()
            # 在应用程序全部关闭后，TrayIcon其实还不会自动消失，
            # 直到你的鼠标移动到上面去后，才会消失，
            # 这是个问题，（如同你terminate一些带TrayIcon的应用程序时出现的状况），
            # 这种问题的解决我是通过在程序退出前将其setVisible(False)来完成的。
        tp.setVisible(False)
    a2 = QAction('&退出(Exit)',triggered = quitApp) # 直接退出可以用qApp.quit

    def tpCliecked(action):
        global tpactions
        tpMenu.clear()
        tpactions = addUSBHostlist()
        tpMenu.addActions(tpactions)
        tpMenu.addAction(a2)
        tpMenu.addAction(QAction('&退出(Exit)',triggered = quitApp))
        return
    tp.activated.connect(tpCliecked)
    tp.setContextMenu(tpMenu)
    tp.show()
    sys.exit(app.exec_())
