import os
import json
import pandas as pd
from IPython.display import display, Markdown


class MarkDown:


    def __init__(self, fileName='', filePath='./'):
        self.MarkDownContent = []
        self.fileName = fileName
        self.filePath = filePath
        self.fileAddress = os.path.join(self.filePath, self.fileName)

    def __ifCenter(self, string):
        return '<center>' + string + '</center>'


    def addLine(self, lineContent, rowNum=False, ifCenter=False):
        if not rowNum:
            if ifCenter:
                lineContent = self.__ifCenter(lineContent)
            self.MarkDownContent.append(lineContent + ' \n')


    def addImage(self, imagePath, box=['', ''], ifCenter=True):
        lineContent = '<img src="{}" width="{}" height="{}">'.format(imagePath, box[0], box[1])
        self.addLine(lineContent, ifCenter=ifCenter)


    def addTable(self, df, ifCenter=True):
        self.addLine(df.to_html(), ifCenter=True)


    def addFomula(self, fomula):
        self.addLine('$$\n' + fomula + '\n$$')


    def showMDinNotebook(self, ):
        return display(Markdown(''.join(self.MarkDownContent)))


    def saveMD(self, fileName='newMD.md', filePath='./'):
        fileAddress = os.path.join(filePath, fileName)
        with open(fileAddress, "w") as file:
            file.write('\n'.join(self.MarkDownContent))
        print("\033[32mFile {} saved!\033[0m".format(fileAddress))


    def readMD(self, ):
        if os.path.exists(self.fileAddress):
            with open(self.fileAddress, 'r+') as MarkDownFile:
                self.MarkDownContent = MarkDownFile.readlines()
        else:
            print("\033[32mFile {} does not exist!\033[0m".format(self.fileAddress))
