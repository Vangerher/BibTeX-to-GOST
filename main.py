import sys

from PySide6.QtWidgets import QApplication, QMainWindow

from ui_main import Ui_MainWindow

import requests


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
        self.ui.GetBibTeX.clicked.connect(self.GetBibText)

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
            except Exception as ex:
                print(f'Error in getDict {ex}')
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

            except Exception as ex:
                print(f'Error in getDict {ex}')
                print(self.paramDict)

        getDict()
        processNames()

        try:
            if self.paramDict['number'] != '':
                outText = (f'{self.paramDict['author'][0][1]}, {self.paramDict['author'][0][0]}{self.paramDict['title']}. / {', '.join(map(lambda x:''.join(x),self.paramDict['author']))} // {self.paramDict['journal']}. '
                           f'- {self.paramDict['year']}. - Vol. {self.paramDict['volume']}. - № {self.paramDict['number']}. - P. {self.paramDict['pages'].replace("--","-")}.')
            else:
                outText = (
                    f'{self.paramDict['author'][0][1]}, {self.paramDict['author'][0][0]} {self.paramDict['title']}. / {', '.join(map(lambda x:''.join(x),self.paramDict['author']))} // {self.paramDict['journal']}. '
                    f'- {self.paramDict['year']}. - Vol. {self.paramDict['volume']}. - P. {self.paramDict['pages'].replace("--", "-")}.')

            if self.paramDict['DOI'] != '':
                outText += f' DOI: {self.paramDict['DOI']}.'
        except Exception as ex:
            print(f'Error in getDict {ex}')
            print(self.paramDict)

        self.ui.OutputText.setPlainText(outText)
        self.copy()

    def GetBibText(self):
        if self.ui.DOIEntry.text() != '':
            headers = {"Accept": "application/x-bibtex"}
            response = requests.get(f"https://doi.org/{self.ui.DOIEntry.text()}", headers = headers)
            self.ui.InputText.setPlainText(response.text.replace("},",'},\n'))
            print(response)

    def copy(self):
        self.ui.label.setText('Скопировано')
        QApplication.clipboard().setText(self.ui.OutputText.toPlainText())

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = Main()
    window.show()

    sys.exit(app.exec())
