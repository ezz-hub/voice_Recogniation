import UI as ui
from PyQt5 import QtWidgets, QtGui
import logging
from loader import mp3ToData
from functools import partial
from Spectrogram import spectrogram
from helpers import mixSongs, createPerceptualHash, getHammingDistance, mapRanges
from updateDB import readJson

class voiceRecognizer(ui.Ui_MainWindow):
    """
    Audio and Voice Recognition Application implements the following :

    - Creating a Spectral Hash for each Song/Audio in a huge database
    - Identifying new Audio/Sound Added to the application
    - Mixing different Audio/Sound with selected ratios and finding that bizarre output in the database
    """
    def __init__(self, starterWindow: QtWidgets.QMainWindow):
        # Initializer
        super(voiceRecognizer, self).setupUi(starterWindow)
        self.spectroHashKey = "spectrohash"  # Key used to get the spectrogram Hash
        self.featureKey = "features"  # key used to get mel Hash
        self.audFiles = [None, None]  # List Containing both songs
        self.audRates = [None, None]  # List contains Songs Rates which must be equal
        self.lineEdits = [self.aud1Text, self.aud2Text]
        self.testHash = None  # The Mix output resulted hash
        self.audMix = None  # The Mix output resulted Audio File
        self.featureMixHash = []  # Holds the features extracted from Mix
        self.results = []  # Holds the Results with each song
        self.songsPath = "Songs/"  # path to songs directory
        self.dbPath = "Database/db.json"  # path to database directory
        self.spectrogram = spectrogram()._spectrogram  # Spectrogram Extraction function
        self.extractFeatures = spectrogram().spectralFeatures  # Feature Extraction function
        self.loadBtns = [self.audLoad1, self.audLoad2]  # loading buttons collected
        self.logger = logging.getLogger()  # Logger maintainer
        self.logger.setLevel(logging.DEBUG)

        # CONNECTIONS
        for btn in self.loadBtns:
            btn.clicked.connect(partial(self.loadFile, btn.property("indx")))
 
        self.finderBtn.clicked.connect(self.__extract)

        self.resultsTable.hide()
        self.label_2.hide()



    def loadFile(self, indx):
        """
        Responsible for the following :

        - Showing a dialog for choosing desired file
        - Convert the loaded file into array and insert it in the system
        - load only the first minute of any song
        """
        self.statusbar.showMessage("Loading Audio File %s"%indx)
        audFile, audFormat = QtWidgets.QFileDialog.getOpenFileName(None, "Load Audio File %s"%(indx),
                                                                                 filter="*.mp3")
        self.logger.debug("Audio File %s Loaded"%indx)

        # CHECK CONDITIONS
        if audFile == "":
            self.logger.debug("loading cancelled")
            self.statusbar.showMessage("Loading cancelled")
            pass
        else:
            self.logger.debug("starting extraction of data")
            audData, audRate = mp3ToData(audFile, 60000)
            self.logger.debug("extraction successful")
            self.audFiles[indx-1] = audData
            self.audRates[indx-1] = audRate
            self.lineEdits[indx-1].setText(audFile.split('/')[-1])
            self.statusbar.showMessage("Loading Done")
            self.logger.debug("Loading done")

    def __extract(self):
        """
        Responsible for the following :

        - Read the slider value and mix the loaded songs if any with the selected ratio
        - Extract the spectrogram of the resulted mix and it`s features
        - hash the resulted extractions
        """
        print("Slider Value is %s"%self.ratioSlider.value())
        self.statusbar.showMessage("Finding Matches ...")
        self.logger.debug("starting searching process")

        if (self.audFiles[0] is not None) and (self.audFiles[1] is not None):
            self.logger.debug("loaded two different songs ")
            self.audMix = mixSongs(self.audFiles[0], self.audFiles[1], w=self.ratioSlider.value()/100)

        else:
            self.logger.debug("loaded only one song")
            if self.audFiles[0] is not None : self.audMix = self.audFiles[0]
            if self.audFiles[1] is not None: self.audMix = self.audFiles[1]
            if self.audFiles[0] is None and self.audFiles[1] is None:
                self.showMessage("Warning", "You need to at least load one Audio File",
                                 QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Warning)

        if self.audMix is not None:
            self.logger.debug("starting Extraction")

            self.spectro = self.spectrogram(self.audMix, self.audRates[0])[-1]
            self.testHash = createPerceptualHash(self.spectro)

            for feature in self.extractFeatures(self.audMix, self.spectro, self.audRates[0]):
                self.featureMixHash.append(createPerceptualHash(feature))

            self.__compareHash()
        self.statusbar.clearMessage()

    def __compareHash(self):
        """
        Responsible for the following :

        - Reading the database's saved hashes
        - Compare the resulted hashesh with those saved in database
        - Sorting the results and sending data to Table
        """
        self.logger.debug("staring comparisons ... ")
        self.statusbar.showMessage("Loading results .. ")

        for songName, songHashes in readJson(self.dbPath):
            self.spectroDiff = getHammingDistance(songHashes[self.spectroHashKey], self.testHash)
            self.featureDiff = 0

            for i, feature in enumerate(songHashes[self.featureKey]):
                self.featureDiff += getHammingDistance(feature, self.featureMixHash[i])

            self.avg = (self.spectroDiff + self.featureDiff)/4
            self.results.append((songName, (abs(1 - mapRanges(self.avg, 0, 255, 0, 1)))*100))

        self.results.sort(key= lambda x: x[1], reverse=True)

        self.statusbar.clearMessage()

        self.__startTable()

    def __startTable(self):
        """
        Responsible for the following :

        - Setting TableWidget Parameters, Columns and Rows
        - Clearing the Results Buffer
        """
        self.label_2.show()
        self.resultsTable.setColumnCount(2)
        self.resultsTable.setRowCount(len(self.results))

        for row in range(len(self.results)):
            self.resultsTable.setItem(row, 0, QtWidgets.QTableWidgetItem(self.results[row][0]))
            self.resultsTable.setItem(row, 1, QtWidgets.QTableWidgetItem(str(round(self.results[row][1], 2))+"%"))
            self.resultsTable.item(row, 0).setBackground(QtGui.QColor(57, 65, 67))
            self.resultsTable.item(row, 1).setBackground(QtGui.QColor(57, 65, 67))
            self.resultsTable.verticalHeader().setSectionResizeMode(row, QtWidgets.QHeaderView.Stretch)

        self.resultsTable.setHorizontalHeaderLabels(["Found Matches", "Percentage"])

        for col in range(2):
            self.resultsTable.horizontalHeader().setSectionResizeMode(col, QtWidgets.QHeaderView.Stretch)
            self.resultsTable.horizontalHeaderItem(col).setBackground(QtGui.QColor(57, 65, 67))

        self.resultsTable.show()

        self.results.clear()

    def showMessage(self, header, message, button, icon):
        """
        Responsible for showing message boxes

        ============= ===================================================================================
        **Arguments**
        header:       Box header title.
        message       the informative message to be shown.
        button:       button type.
        icon:         icon type.
        ============= ===================================================================================
        """
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle(header)
        msg.setText(message)
        msg.setIcon(icon)
        msg.setStandardButtons(button)
        self.logger.debug("messege shown with %s %s "%(header, message))
        msg.exec_()

if __name__ == '__main__':
    import sys
    logging.basicConfig(filename="logs/logfile.log",
                        format='%(asctime)s %(message)s',
                        filemode='w')

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = voiceRecognizer(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
