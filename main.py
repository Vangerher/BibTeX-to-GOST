import html
import re
import sys
import bibtexparser
import requests

from PySide6.QtWidgets import QApplication, QMainWindow
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
            'doi': '',
        }

    def initConnect(self):
        self.ui.CopyBtn.clicked.connect(self.copy)
        self.ui.ConvertBtn.clicked.connect(self.convert)
        self.ui.GetBibTeX.clicked.connect(self.GetBibText)

    def convert(self):
        self.ui.label.setText('')

        def clean_bibtex_text(text):
            # HTML-сущности → нормальный текст (например, &amp; → &)
            text = html.unescape(text)

            # LaTeX спецсимволы и диакритика → Unicode
            latex_replacements = {
                r"{\\\"a}": "ä", r"{\\\"o}": "ö", r"{\\\"u}": "ü",
                r"{\\\'e}": "é", r"{\\\`e}": "è", r"{\\\^o}": "ô",
                r"{\\\~n}": "ñ", r"{\\\'a}": "á", r"{\\\`a}": "à",
                r"\\&": "&", r"\\%": "%", r"\\_": "_",
                r"\\#": "#", r"\\textendash": "–", r"\\textquoteleft": "‘",
                r"\\textquoteright": "’", r"\\textquotedblleft": "“", r"\\textquotedblright": "”"
            }

            for pattern, replacement in latex_replacements.items():
                text = re.sub(pattern, replacement, text)

            # Удалить лишние фигурные скобки
            # text = re.sub(r"[{}]", "", text)

            return text

        def getDict():
            bib_str = self.ui.InputText.toPlainText()
            dict_str = bibtexparser.loads(clean_bibtex_text(bib_str))
            print(dict_str.entries[0])
            for key in dict_str.entries[0].keys():
                if key in self.paramDict.keys():
                    self.paramDict[key] = dict_str.entries[0][key]

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

            if self.paramDict['doi'] != '':
                outText += f' doi: {self.paramDict['doi']}.'
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
