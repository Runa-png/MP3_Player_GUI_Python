from PyQt6.QtCore import (
Qt,
QSize,
QThread,
pyqtSignal,
pyqtSlot,
QObject,
QUrl
)

from PyQt6.QtWidgets import (
QMainWindow,
QApplication,
QWidget,
QHBoxLayout,
QLabel,
QVBoxLayout,
QPushButton,
QGridLayout,
QSlider
)

from PyQt6.QtMultimedia import (
QAudioOutput,
QMediaPlayer
)

from PyQt6.QtGui import (
QPixmap
)

from mutagen import File
import os
import sys
from config import config

class MainWindow(QMainWindow):
  def __init__(self):
    super().__init__()

    configs = config()

    # Main Window Tweaks #
    self.setStyleSheet(f"background-color: {configs.mainWindow.backgroundColor}")

    self.centralWidget = QWidget()
    self.setCentralWidget(self.centralWidget)
    self.setFixedSize(QSize(configs.width,configs.height))
    ##

    # Top level #
    self.topLevel = QGridLayout(self.centralWidget)
    self.topLevel.setContentsMargins(0, 0, 0, 0)
    self.topLevel.setSpacing(0)

    # If you touch this the layout breaks
    for row in range(4):
      self.topLevel.setRowStretch(row, 1)

    for col in range(7):
      self.topLevel.setColumnStretch(col, 1)
    ##
    
    # Media Player #
    self.player = QMediaPlayer()
    self.audio_output = QAudioOutput()
    self.player.setAudioOutput(self.audio_output)
    self.audio_output.setVolume(0.25)

    self.playlist = []
    self.index = 0
    ##

    # Volume Widget #
    self.volumeControl = VolumeSlider()
    self.topLevel.addWidget(self.volumeControl, 0, 1, 1, 3)
    ##

    # Quit Button #
    self.quitButton = CloseButton()
    self.topLevel.addWidget(self.quitButton, 0, 6)
    ##

    # Shuffle Button #
    self.shuffleButton = CloseButton()
    self.topLevel.addWidget(self.shuffleButton, 0, 5)
    self.shuffleButton.closeButton.clicked.connect(self.getAlbumArt)
    ##

    # Previous Button #
    self.previous = PreviousButton()
    self.topLevel.addWidget(self.previous, 2, 1)
    ##

    # Play Button #
    self.playButton = PlayButton()
    self.topLevel.addWidget(self.playButton, 2, 3)
    ##

    # Next Button #
    self.nextButton = NextButton()
    self.topLevel.addWidget(self.nextButton, 2, 5)
    ##

    # Album image label #
    self.albumImage = QLabel("Hello")
    self.topLevel.addWidget(self.albumImage, 1, 2)
    ##



    # Connect emit signals to functionality #
    self.player.mediaStatusChanged.connect(lambda status: print(status)) # When the media playing changes
    self.playButton.PLAY.connect(lambda status: self.playMusic(status)) # Play/Pause button pressed
    self.nextButton.NEXTSONG.connect(self.nextSong) # Next song button pressed
    self.previous.PREVSONG.connect(self.previousSong) # Previous song button pressed
    ##

  def playMusic(self, status):
    if not self.playlist:
      self.generatePlaylist()
    elif status == "Play":
      self.player.pause()
      return
    self.player.play()
    print(len(self.playlist), self.index)

  def generatePlaylist(self):
    configs = config()
    tempPlaylist = []
    for file in os.scandir(configs.mainWindow.musicLocation):
      print(file.path)
      tempPlaylist.append(file.path)
    self.playlist = tempPlaylist
    self.index = 0

    self.player.setSource(QUrl.fromLocalFile(self.playlist[self.index]))

  def nextSong(self):
    print(len(self.playlist)-1, self.index)
    if len(self.playlist) - 1 == self.index:
      self.player.stop()
      self.playlist = []
      self.playButton.endOfPlaylist()
    else:
      self.index += 1
      self.player.setSource(QUrl.fromLocalFile(self.playlist[self.index]))
      
      if self.playButton.paused == "Pause":
        self.player.play()
  
  def previousSong(self):
    if self.index == 0:
      return
    else:
      self.index -= 1
      self.player.setSource(QUrl.fromLocalFile(self.playlist[self.index]))

      if self.playButton.paused == "Pause":
        self.player.play()

  def getAlbumArt(self):
    if not self.playlist:
      return
    
    path = self.playlist[self.index]
    audio = File(path)

    if hasattr(audio.tags, "getall"):
      apic = audio.tags.getall("APIC")

      if apic:
        pixmap = QPixmap()
        if pixmap.loadFromData(apic[0].data):
          self.albumImage.setPixmap(pixmap)
          return
    self.albumImage.setText("")
    return None


class PlayButton(QWidget):
  # Connections #
  PLAY = pyqtSignal(str)
  ##
  
  def __init__(self):
    super().__init__()

    # Keep track of playing or paused #
    self.paused = "Play"
    ##

    # Add elements to main Layout #
    self.mainLayout = QHBoxLayout(self)
    ##

    # Pause button #
    self.pauseButton = QPushButton(self.paused)

    # Click Signals #
    self.pauseButton.clicked.connect(self.pauseButtonPressed)
    ##

    # configs #
    width = config.pauseButton.width
    self.pauseButton.setFixedSize(width, width)
    ##

    # Add buttons to layout #
    self.mainLayout.addWidget(self.pauseButton)
    ##
  
  def pauseButtonPressed(self, *args):
    # You got to remember that its flipped, pause when its playing and play when its paused #
    self.paused = "Play" if self.paused == "Pause" else "Pause"
    
    self.pauseButton.setText(self.paused)
    
    self.PLAY.emit(self.paused)
  
  def endOfPlaylist(self):
    self.paused = "Play"
    self.pauseButton.setText(self.paused)

class NextButton(QWidget):
  # Connections #
  NEXTSONG = pyqtSignal()
  ##
  
  def __init__(self):
    super().__init__()

    configs = config()

    # Add elements to main Layout #
    self.mainLayout = QHBoxLayout(self)
    ##

    # Next song button #
    self.nextButton = QPushButton("Next")
    ##

    # configs #
    width = config.pauseButton.width
    self.nextButton.setFixedSize(width, width)
    ##

    self.mainLayout.addWidget(self.nextButton)

    # Connect the button #
    self.nextButton.clicked.connect(self.nextSongButtonPressed)
    ##
  
  def nextSongButtonPressed(self):
    self.NEXTSONG.emit()

class PreviousButton(QWidget):
  # Connections #
  PREVSONG = pyqtSignal()
  ##
  
  def __init__(self):
    super().__init__()

    configs = config()

    # Add elements to main Layout #
    self.mainLayout = QHBoxLayout(self)
    ##

    # Previous song button #
    self.prevButton = QPushButton("Previous")
    ##

    # configs #
    width = config.pauseButton.width
    self.prevButton.setFixedSize(width, width)
    ##

    self.mainLayout.addWidget(self.prevButton)

    # Connect the button #
    self.prevButton.clicked.connect(self.prevSongButtonPressed)
    ##
  
  def prevSongButtonPressed(self):
    self.PREVSONG.emit()

class VolumeSlider(QWidget):
  def __init__(self):
    super().__init__()

    configs = config()

    # Add elements to main Layout #
    self.mainLayout = QHBoxLayout(self)
    ##

    # Volume slider #
    self.volumeSlider = QSlider(Qt.Orientation.Horizontal)
    self.volumeSlider.setFixedWidth(250)
    ##

    self.mainLayout.addWidget(self.volumeSlider)

class CloseButton(QWidget):
  def __init__(self):
    super().__init__()

    configs = config()

    # Add elements to main Layout #
    self.mainLayout = QHBoxLayout(self)
    ##

    # Close Button #
    self.closeButton = QPushButton("Exit")
    ##

    width = configs.closeButton.width
    self.closeButton.setFixedSize(QSize(width,width))

    self.mainLayout.addWidget(self.closeButton)

    #self.closeButton.clicked.connect(lambda: sys.exit())


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()