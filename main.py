import io
import json
import math
import struct
import subprocess
import sys
import time
import os
from datetime import datetime
from logging import exception

from argon2 import PasswordHasher
from cryptography.fernet import Fernet
import crcmod as crc
import numpy as np
import pandas as pd
import serial
import serial.tools.list_ports
from PySide6.QtCore import QTimer, Signal, QObject, QThread, Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QDialog, QWidget, QComboBox, \
    QFileDialog, QCheckBox, QPushButton, QTabWidget, QToolBar, QTableWidgetItem, QMenu, QTableWidget, QAbstractItemView
from PySide6.QtGui import QIcon, QFontMetrics, QPainter, QColor, QPen, QAction, QBrush
from pandas.io.clipboard import clipboard_set

from ui_main import Ui_MainWindow

class Main(QMainWindow):

    def __init__(self):
        super(Main, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.initConnect()
        self.paramDict = {
            'title':"",
            'author':"",
            'journal':"",
            'volume':"",
            'pages':"",
            'year':"",
            'publisher' :"",
            'number': '',
            'DOI': '',
        }

    def initConnect(self):
        self.ui.CopyBtn.clicked.connect(self.copy)
        self.ui.ConvertBtn.clicked.connect(self.convert)

    def convert(self):
        self.ui.label.setText('')

        def getDict():
            try:
                inputText = self.ui.InputText.toPlainText()
                slicedText = inputText.split('\n')
                for parameter in slicedText:
                    text = parameter.replace("{", "").replace("}", "")
                    line = text.split('=')
                    line[0] = line[0].replace(' ','')

                    if len(line) > 1:
                        line[1] = line[1][:-1] if line[1][-1] == ',' else line[1]

                    if line[0] in self.paramDict.keys():
                        self.paramDict[line[0]] = line[1]
            except Exception as e:
                print('Error in getDict'+e)
                print(self.paramDict)

        def processNames():
            try:
                authorsPre = self.paramDict['author'].split(' and ')
                authors = []
                for author in authorsPre:
                    splittted = author.split(', ')
                    surname = splittted[0].replace('\\','').replace("'",'')
                    name = ''
                    for names in splittted[1].split(' '):
                        name += names[0]+'. '
                    authors.append([name, surname])

                if len(authors) > 4:
                    authors = authors[:4]
                    authors[3] = '[et. al.]'
                self.paramDict['author'] = authors

            except Exception as e:
                print('Error in processNames'+e)
                print(self.paramDict)

        getDict()
        processNames()

        try:
            if self.paramDict['number'] != '':
                outText = (f'{self.paramDict['author'][0][1]}, {self.paramDict['author'][0][0]}{self.paramDict['title']}. / {', '.join(map(lambda x:''.join(x),self.paramDict['author']))} // {self.paramDict['publisher']}. '
                           f'- {self.paramDict['year']}. - Vol. {self.paramDict['volume']}. - № {self.paramDict['number']}. - P. {self.paramDict['pages'].replace("--","-")}.')
            else:
                outText = (
                    f'{self.paramDict['author'][0][1]}, {self.paramDict['author'][0][0]} {self.paramDict['title']}. / {', '.join(map(lambda x:''.join(x),self.paramDict['author']))} // {self.paramDict['publisher']}. '
                    f'- {self.paramDict['year']}. - Vol. {self.paramDict['volume']}. - P. {self.paramDict['pages'].replace("--", "-")}.')

            if self.paramDict['DOI'] != '':
                outText += f' DOI: {self.paramDict['DOI']}.'
        except Exception as e:
            print('Error in setting output' + e)
            print(self.paramDict)

        self.ui.OutputText.setPlainText(outText)
        self.copy()

    def copy(self):
        self.ui.label.setText('Скопировано')
        QApplication.clipboard().setText(self.ui.OutputText.toPlainText())

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = Main()
    window.show()

    sys.exit(app.exec())
