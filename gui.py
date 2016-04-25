#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import (QApplication, QWidget,
        QPushButton, QToolTip, QMessageBox)
from PyQt5.QtGui import (QIcon, QFont)
from PyQt5.QtCore import QCoreApplication

class Example(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        QToolTip.setFont(QFont('SansSerif', 10))

        self.setToolTip('This is a <b>QWidget</b> widget')

        btn = QPushButton('Button', self)
        btn.setToolTip('This is a <b>QPushButton</b> widget')
        btn.resize(btn.sizeHint())
        btn.move(50, 50)

        qbtn = QPushButton('Quit', self)
        qbtn.clicked.connect(QCoreApplication.instance().quit)
        qbtn.resize(qbtn.sizeHint())
        qbtn.move(150, 50)

        self.setGeometry(300, 300, 300, 220)
        self.setWindowTitle('Tooltips')
        self.setWindowIcon(QIcon('web.png'))

        self.show()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',
                "Are you sure to quit?", QMessageBox.Yes | 
                QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
