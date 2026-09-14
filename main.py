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
QMediaPlayer,
QMediaMetaData
)

from PyQt6.QtGui import (
QPixmap,
QIcon
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
    self.setStyleSheet(f"QMainWindow {{background-color: {configs.mainWindow.backgroundColor}}}")

    self.centralWidget = QWidget()
    self.setCentralWidget(self.centralWidget)
    self.setFixedSize(QSize(configs.width,configs.height))
    self.setContentsMargins(10,0,0,0)
    ##

    # Top level #
    self.topLevel = QGridLayout(self.centralWidget)
    self.topLevel.setContentsMargins(0, 0, 0, 0)
    self.topLevel.setSpacing(0)

    # If you touch this the layout breaks
    for row in range(3):
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

    # Quit Button #
    self.quitButton = CloseButton()
    self.topLevel.addWidget(self.quitButton, 0, 6)
    ##

    # Shuffle Button #
    self.shuffleButton = ShuffleButton()
    self.topLevel.addWidget(self.shuffleButton, 0, 5)
    self.shuffleButton.shuffleButton.clicked.connect(self.getAlbumArt)
    ##

    # Previous Button #
    self.previous = PreviousButton()
    self.topLevel.addWidget(self.previous, 1, 1)
    ##

    # Play Button #
    self.playButton = PlayButton()
    self.topLevel.addWidget(self.playButton, 1, 3)
    ##

    # Next Button #
    self.nextButton = NextButton()
    self.topLevel.addWidget(self.nextButton, 1, 5)
    ##

    # Album image label #
    self.albumImage = QLabel()
    self.albumImage.setFixedSize(QSize(configs.pauseButton.width, configs.pauseButton.width))
    self.topLevel.addWidget(self.albumImage, 2, 0)
    ##

    ## Name and volume slider ##
    self.albumSide = QVBoxLayout()
    self.albumSide.setContentsMargins(10, 0, 0, 0) # 10px padding on the left

    # Songname label #
    self.songName = QLabel()
    self.songName.setContentsMargins(0,30,0,0)
    self.songName.setStyleSheet("color: white; font-weight: 700; font-size: 15px")
    self.albumSide.addWidget(self.songName, Qt.AlignmentFlag.AlignCenter)
    ##
    
    # Volume Widget #
    self.volumeControl = VolumeSlider()
    self.albumSide.addWidget(self.volumeControl, Qt.AlignmentFlag.AlignLeft)
    ##

    self.topLevel.addLayout(self.albumSide, 2, 1, 1, 6)
    ##

    # Connect emit signals to functionality #
    self.player.mediaStatusChanged.connect(self.mediaChanged) # When the media playing changes
    self.volumeControl.volumeSlider.valueChanged.connect(lambda: self.audio_output.setVolume(self.volumeControl.volumeSlider.value() / 100))
    self.playButton.PLAY.connect(lambda status: self.playMusic(status)) # Play/Pause button pressed
    self.nextButton.NEXTSONG.connect(self.nextSong) # Next song button pressed
    self.previous.PREVSONG.connect(self.previousSong) # Previous song button pressed
    ##

  def mediaChanged(self):
    self.albumImage.setStyleSheet("QLabel {border: 2px solid rgb(255,255,255)}")
    artGrabStatus = self.getAlbumArt()
    if not artGrabStatus:
      self.albumImage.setStyleSheet("QLabel {border: none")
    self.songName.setText(self.player.metaData().stringValue(QMediaMetaData.Key.Title))

  def playMusic(self, status):
    if not self.playlist:
      self.generatePlaylist()
    elif status == True:
      self.player.pause()
      return
    self.player.play()

  def generatePlaylist(self):
    configs = config()
    tempPlaylist = []
    try:
      for file in os.scandir(configs.mainWindow.musicLocation):
        tempPlaylist.append(file.path)
    except FileNotFoundError:
      print("Create a folder labeled music in project root")
      return
    self.playlist = tempPlaylist
    self.index = 0

    self.player.setSource(QUrl.fromLocalFile(self.playlist[self.index]))

  def nextSong(self):
    if len(self.playlist) - 1 == self.index:
      self.player.stop()
      self.playlist = []
      self.playButton.endOfPlaylist()
    else:
      self.index += 1
      self.player.setSource(QUrl.fromLocalFile(self.playlist[self.index]))
      
      if self.playButton.paused == False:
        self.player.play()
  
  def previousSong(self):
    if self.index == 0:
      return
    else:
      self.index -= 1
      self.player.setSource(QUrl.fromLocalFile(self.playlist[self.index]))

      if self.playButton.paused == False:
        self.player.play()

  def getAlbumArt(self):
    configs = config()
    
    if not self.playlist:
      return
    
    path = self.playlist[self.index]
    audio = File(path)

    if hasattr(audio.tags, "getall"):
      apic = audio.tags.getall("APIC")

      if apic:
        pixmap = QPixmap()
        if pixmap.loadFromData(apic[0].data):
          pixmap = pixmap.scaled(config.pauseButton.width, config.pauseButton.width, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
          self.albumImage.setPixmap(pixmap)
          return True
    self.albumImage.setText("")
    return False


class PlayButton(QWidget):
  # Connections #
  PLAY = pyqtSignal(bool)
  ##
  configs = config()

  def __init__(self):
    super().__init__()

    # Keep track of playing or paused #
    self.paused = True
    ##

    # Add elements to main Layout #
    self.mainLayout = QHBoxLayout(self)
    self.setStyleSheet(f"background-color: {self.configs.mainWindow.backgroundColor}; color: white; border: none")
    ##

    # Pause button #
    self.pauseButton = QPushButton()
    self.pauseButton.setIcon(QIcon("./assets/play.png"))
    self.pauseButton.setIconSize(self.pauseButton.size())

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
    self.paused = not self.paused
    
    if self.paused == False:
      self.pauseButton.setIcon(QIcon("./assets/pause.png"))
    else:
      self.pauseButton.setIcon(QIcon("./assets/play.png"))
    self.pauseButton.setIconSize(self.pauseButton.size())
    
    self.PLAY.emit(self.paused)
  
  def endOfPlaylist(self):
    self.paused = True
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
    self.setStyleSheet(f"background-color: {configs.mainWindow.backgroundColor}; color: white; border: none")
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
    self.setStyleSheet(f"background-color: {configs.mainWindow.backgroundColor}; color: white; border: none")
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
    
    volumeBarWidth = 200

    # Add elements to main Layout #
    self.mainLayout = QHBoxLayout(self)
    self.mainLayout.setContentsMargins(0, 0, 0, 20)
    self.setFixedWidth(volumeBarWidth)
    ##

    # Volume slider #
    self.volumeSlider = QSlider(Qt.Orientation.Horizontal)
    self.volumeSlider.setFixedWidth(volumeBarWidth)
    self.volumeSlider.setValue(50)
    self.volumeSlider.setMinimum(0)
    self.volumeSlider.setMaximum(100)
    ##

    # Ticks #
    self.volumeSlider.setTickPosition(QSlider.TickPosition.TicksBothSides)
    self.volumeSlider.setTickInterval(20)
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

class ShuffleButton(QWidget):
  def __init__(self):
    super().__init__()

    self.configs = config()
    
    # Add elements to main Layout #
    self.mainLayout = QHBoxLayout(self)
    ##

    # Toggle for visibility #
    self.toggled = False
    ##

    # Shuffle Button #
    self.shuffleButton = QPushButton()
    self.shuffleButton.setIcon(QIcon("./assets/shuffle.png"))
    self.shuffleButton.setIconSize(self.shuffleButton.size())
    ##

    # Configs
    width = self.configs.closeButton.width
    self.shuffleButton.setFixedSize(QSize(width,width))
    self.shuffleButton.setStyleSheet(f"border: none; background-color: {self.configs.mainWindow.backgroundColor}")
    ##

    self.mainLayout.addWidget(self.shuffleButton)

    self.shuffleButton.clicked.connect(self.shuffleClicked)
  
  def shuffleClicked(self):
    self.toggled = not self.toggled
    
    if self.toggled == True:
      self.shuffleButton.setStyleSheet("background-color: rgb(50,0,0)")
    else:
      self.shuffleButton.setStyleSheet(f"border: none; background-color: {self.configs.mainWindow.backgroundColor}")




app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()