import codecs

class Logger:

    def __init__(self, entityType, logType):
        self.entityType = entityType
        self.logType = logType
        self.loadedSet = set()
        try:
            self.loadFileOnce()
        except FileNotFoundError:
            self.isCompleteFile('first')

    def log(self, text, errorText = False, printLog = True):
        if (self.logType == 'err'):
            if (errorText):
                text = text + ';' + errorText
            self.logError(text)
        else:
            self.logComplete(text)

        self.text = text
        if printLog:
            self.printLog()

    def printLog(self):
        if (self.logType == 'err'):
            splits = self.text.split(';')
            print('Error: ' + splits[1] + ' - ' + splits[0])
        else:
            print('OK: ' + self.text)

    def logComplete(self, title):
        file = codecs.open("log_" + self.entityType + ".txt", "a", "utf-8")
        file.write(title + '\n')
        self.loadedSet.add(title)
        file.close()

    def logError(self, title):
        file = codecs.open("log_err_" + self.entityType + ".txt", "a", "utf-8")
        file.write(title + '\n')
        file.close()

    def loadFileOnce(self):
        f = codecs.open("log_" + self.entityType + ".txt")
        lines = f.readlines()
        for line in lines:
            self.loadedSet.add(line.strip())
        f.close()

    def isCompleteFile(self, entity):
        try:
            if entity in self.loadedSet:
                return True
            else:
                return False
        except IOError:
            print("Not exist file")
            codecs.open('log_' + self.entityType + '.txt', 'w', 'utf-8')
