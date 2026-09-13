from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal, pyqtSlot, QObject, QUrl
from PyQt6.QtWidgets import (QMainWindow, QApplication, QWidget, QHBoxLayout,
QPushButton
)
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer
from pathlib import Path

import sys

class MainWindow(QMainWindow):
  def __init__(self):
    super().__init__()

    self.setFixedSize(QSize(500,500))
    self.setStyleSheet("background-color: rgb(0,0,0);")

    # Central Widget
    self.centralWidget = QWidget()
    self.setCentralWidget(self.centralWidget)
    ##

    # Assign topLevel as centralWidget
    self.topLevel = QHBoxLayout(self.centralWidget)
    ##

    # Media Controls
    mediaControls = MediaControls()
    self.topLevel.addWidget(mediaControls)
    ##

    # Audio Stuff
    self.player = QMediaPlayer()
    self.audio_output = QAudioOutput()
    self.player.setAudioOutput(self.audio_output)
    self.audio_output.setVolume(1)
    #filename = "music/Watashiwa Watashino Kotoga Suki - HoneyWorks, Kaguya(cv.Yuko Natsuyoshi), Cosmic Princess Kaguya!.mp3"
    #self.player.setSource(QUrl.fromLocalFile(filename))
    ##

    # Media Control Functions 
    mediaControls.pauseButton.clicked.connect(self.playButton)
    ##

    ## Playback Debugging
    self.player.playbackStateChanged.connect(lambda state: print("State Changed", state))
    self.player.mediaStatusChanged.connect(lambda status: print("Status Changed", status))
    self.player.errorOccurred.connect(lambda error, error_string: print("Error:", error,"|", error_string))
    ##

  def playButton(self):
    if self.player.source().isEmpty():
      print("Empty Playlist")
  
  def killApp(self):
    QApplication.quit()



class MediaControls(QWidget):
  def __init__(self):
    super().__init__()

    # Add elements to mainLayout
    self.mainLayout = QHBoxLayout(self)
    ##

    # Media control buttons #
    self.backButton = QPushButton("Back")
    self.backButton.setFixedSize(100,100)

    self.pauseButton = QPushButton("Pause / Play")
    self.pauseButton.setFixedSize(100,100)

    self.nextButton = QPushButton("Forward")
    self.nextButton.setFixedSize(100,100)
    ##

    # Add widgets #
    self.mainLayout.addWidget(self.backButton)
    self.mainLayout.addWidget(self.pauseButton)
    self.mainLayout.addWidget(self.nextButton)
    ##

    self.setStyleSheet("""
      QPushButton {
        color: white;
        border-radius: 40px;
        border: 2px solid white;
      }
    """)

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()