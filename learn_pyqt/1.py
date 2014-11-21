# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtCore, QtGui

# 自定义的窗口类
class TestWindow(QtGui.QWidget):
    # 窗口初始化
    def __init__(self, parent = None):
        super(TestWindow, self).__init__(parent)
        self.setWindowTitle(u'胡桃夹子')

        # 创建按钮
        self.pushButton = QtGui.QPushButton(u'测试按钮')

        # 创建文本框
        self.textEdit = QtGui.QTextEdit()

        # 创建垂直布局
        layout = QtGui.QVBoxLayout()

        # 将控件添加到布局中
        layout.addWidget(self.textEdit)
        layout.addWidget(self.pushButton)

        # 设置窗口布局
        self.setLayout(layout)

        # 设置按钮单击动作
        self.pushButton.clicked.connect(self.sayHello)

    # 按钮动作处理
    def sayHello(self):
        self.textEdit.setText('Hello World!')

# 程序主入口
if __name__=='__main__':
    app = QtGui.QApplication(sys.argv)
    mainWindow = TestWindow()
    mainWindow.show()
    sys.exit(app.exec_())