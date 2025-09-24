from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QHBoxLayout, QScrollArea, QVBoxLayout, QMenu, QFileDialog, QFrame, QGridLayout, QPushButton, QListWidgetItem, QSpacerItem, QSizePolicy
)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6 import QtCore, QtWidgets, uic
from PyQt6.QtGui import QPixmap, QImage, QAction, QFont
from PyQt6.QtCore import Qt, QUrl
import textToSpeech
import logging
import sys
import os


logger = logging.getLogger('Main')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('logGUI.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
logger.addHandler(ch)


class AudioPlayer(QWidget):
    def __init__(self, file_path):
        super().__init__()
        self.setWindowTitle("Audio Player")
        self.resize(400, 100)

        layout = QVBoxLayout(self)

        self.label = QLabel(f"Playing: {os.path.basename(file_path)}")
        self.label.setFont(QFont("Arial", 12))
        layout.addWidget(self.label)

        # Audio output
        self.audio_output = QAudioOutput()
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)

        # Load file
        self.player.setSource(QUrl.fromLocalFile(file_path))
        self.audio_output.setVolume(50)
        self.player.play()
    
    def closeEvent(self, event):
        # Stop playback when window is closed
        if self.player:
            self.player.stop()
        event.accept()  

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        logger.info("GUI Started")
        self.pdfFolder = ''
        self.outputFolder = ''
        self.speaker = textToSpeech.textToSpeech()

        self.ui = uic.loadUi('./res/MainGUI.ui', self)

        self.ui.addPDFButton.clicked.connect(lambda: self.ui.inputPDF.setText((QFileDialog.getOpenFileName(self, 'Open File', os.path.expanduser("~")))[0]))
        self.ui.outputFileButton.clicked.connect(lambda: self.setOutputLoc())
        self.ui.runButton.clicked.connect(lambda: self.run())
        self.show()

    def run(self):
        if len(self.ui.outputFileLoc.text()) < 2 or len(self.ui.resultFileName.text()) <= 0:
            logger.error("No Output file name or location given")
            return
        outputfile = os.path.join(self.ui.outputFileLoc.text(), self.ui.resultFileName.text() + '.mp3').replace('\\','/')
        if self.ui.fromFileCheck.isChecked():
            self.speaker.setOutputName(str(outputfile))
            self.speaker.setPDF(str(self.ui.inputPDF.text()))
            self.speaker.setVoice(0)
            self.speaker.createTextFileFromPDF(True, True)
            self.speaker.textToSpeechEdge()
        else:
            self.speaker.setOutputName(str(outputfile))
            self.speaker.setText(self.ui.textInput.toPlainText())
            self.speaker.setVoice(0)
            self.speaker.textToSpeechEdge()
        self.setOutputLoc(True)

        

    def setOutputLoc(self, override=False):
        self.folders = {}
        self.files = []
        self.audioList.clear()
        if not override:
            self.ui.outputFileLoc.setText((QFileDialog.getExistingDirectory(self, 'Open File', os.path.expanduser("~"))))
        if self.outputFolder != self.ui.outputFileLoc.text() or override is True:
            if len(self.ui.outputFileLoc.text()) > 1:
                    
                grid_widget = QWidget()
                grid_layout = QGridLayout(grid_widget)
                grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
                grid_layout.setContentsMargins(10, 10, 10, 10)
                grid_layout.setHorizontalSpacing(20)  # Increase horizontal spacing
                grid_layout.setVerticalSpacing(20) 
                cnt = 0
                for index, dir in enumerate(os.listdir(self.ui.outputFileLoc.text())):
                    if dir.lower().endswith(('.mp3', '.wav', '.ogg', '.flac', '.aac')):
                        self.folders[dir] = QPushButton(dir)
                        self.folders[dir].setFixedSize(75, 75)
                        self.folders[dir].setStyleSheet("background-color:#6793b5; font-size: 10px;")

                        self.files.append(os.path.join(self.ui.outputFileLoc.text(), dir).replace('\\','/'))
                    
                        row = cnt // 6
                        col = cnt % 6
                        grid_layout.addWidget(self.folders[dir], row, col)
                        cnt += 1 
                
                padding_widget = QWidget()
                padding_widget.setFixedHeight(120)
                padding_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                grid_layout.addWidget(padding_widget, (cnt // 6) + 1, 0, 1, 6)   
                                            
                scroll_area = QScrollArea()
                scroll_area.setWidgetResizable(True)
                scroll_area.setWidget(grid_widget)
            
                listItem = QListWidgetItem(self.audioList)
                listItem.setSizeHint(scroll_area.sizeHint())
                self.audioList.setItemWidget(listItem, scroll_area)

            for cnt, i in enumerate(self.folders):
                self.folders[i].clicked.connect(lambda checked, f=self.files[cnt]: self.open_audio_player(f))

            self.outputFolder = self.ui.outputFileLoc.text()

    def open_audio_player(self, file_path):
        self.player_window = AudioPlayer(file_path)
        self.player_window.show()


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()

app.exec()
# Terminating tensorflow process when window closed
window.close()