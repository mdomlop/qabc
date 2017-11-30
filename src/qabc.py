#!/usr/bin/python3
# Depends: abcm2ps, abc2midi, timidity, ffmpeg, qmmp
import os
import gettext
import subprocess

from PyQt5.QtCore import (QSettings, QSize, QUrl,
                          Qt, QT_VERSION_STR)
from PyQt5.QtGui import QIcon, QKeySequence, QFont, QPalette, QColor
from PyQt5.QtWidgets import (QWidget, QAction, QApplication, QComboBox,
                             QMainWindow, QLabel, QFileDialog, QScrollArea,
                             QTabWidget, QGridLayout, QVBoxLayout, QSplitter,
                             QHBoxLayout, QMessageBox, QTextEdit, QPushButton, QSizePolicy)
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer

PROGRAM_NAME = "Qabc"
EXECUTABLE_NAME = "qabc"

gettext.translation("qabc", localedir="/usr/share/locale",
                    fallback=True).install()

DESCRIPTION = _("A abc music files manager")
VERSION = "0.1a"
AUTHOR = "Manuel Domínguez López"  # See AUTHORS file
MAIL = "mdomlop@gmail.com"
SOURCE = "https://github.com/mdomlop/qabc"
LICENSE = "GPLv3+"  # Read LICENSE file.

COPYRIGHT = '''
Copyright: 2017 Manuel Domínguez López <mdomlop@gmail.com>
License: GPL-3.0+

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.
 .
 This package is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.
 .
 You should have received a copy of the GNU General Public License
 along with this program. If not, see <https://www.gnu.org/licenses/>.
 .
 On Debian systems, the complete text of the GNU General
 Public License version 3 can be found in "/usr/share/common-licenses/GPL-3".
'''


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.tunebook = []

        self.statusT = QLabel()
        self.statusR = QLabel()

        self.comboIndex = QComboBox()
        self.comboIndex.setEditable(False)
        self.comboIndex.currentIndexChanged[str].connect(self.setComboIndex)

        self.comboTempo = QComboBox()
        self.comboTempo.setEditable(False)
        self.comboTempo.currentIndexChanged[str].connect(self.setComboTempo)

        self.svgWidget = QSvgWidget()
        self.svgWidget.setAutoFillBackground(True)
        p = self.svgWidget.palette()
        p.setColor(self.svgWidget.backgroundRole(), Qt.white)
        self.svgWidget.setPalette(p)

        self.mediaPlayer = QMediaPlayer()

        self.textEdit = QTextEdit()
        self.textEdit.textChanged.connect(self.updateInterface)
        #self.textEdit.setReadOnly(True)

        self.setCentralWidget(self.textEdit)

        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()

        self.index = 0
        self.showTune()  # Starts showing a tune

        self.readSettings()

    def loadABC(self, s):
        abc = {}
        keys = ('A:', 'B:', 'C:', 'D:', 'F:', 'G:', 'H:', 'I:', 'K:',
                'L:', 'M:', 'm:', 'N:', 'O:', 'P:', 'Q:', 'R:', 'r:',
                'S:', 's:', 'T:', 'U:', 'V:', 'W:', 'v:', 'X:', 'Z:')
        for l in s.split('\n'):
            for k in keys:
                if l.startswith(k):
                    v = l.split(':')[1]
                    abc.update({k: v})
                    next
                else:
                    abc.update({'notes': l})
        return(abc)


    def openFile(self):
        select = QFileDialog.getOpenFileName(self, _("Open file"))
        if select:
            self.loadFile(select[0])
            self.showTune()

    def loadFile(self, path):
        ''' Adds a tune file to the tunebook DB '''
        if not path:
            return(0)
        self.tunebookFile = path
        self.tunebook = []  # Database containing all tunes
        self.tunebookSaved = []
        self.comboIndex.clear()

        if not os.path.isfile(path):
            return(1)
        try:
            with open(path, "r") as f:
                text = f.read()
        except:
            text = None
        f.close()

        if text:
            aux = []
            for line in text.split('\n'):
                if line.startswith('X:'):
                    if aux:
                        self.tunebook.append('\n'.join(aux))
                        aux = []
                if line:
                    aux.append(line)
        self.tunebook.append('\n'.join(aux))  # Add last

        for i in self.tunebook:
            self.tunebookSaved.append(i)
            self.comboIndex.addItem(self.getField('T', i))
        self.comboIndex.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.comboTempo.addItem(_("Default"))
        for i in range(60, 305, 5):
            self.comboTempo.addItem(str(i))

    def setComboIndex(self):
        self.index = self.comboIndex.currentIndex()
        self.showTune()

    def firstTune(self):
        self.index = 0
        self.showTune()

    def lastTune(self):
        self.index = len(self.tunebook) - 1
        self.showTune()

    def nextTune(self):
        self.index += 1
        if self.index >= len(self.tunebook):
            self.index = 0  # Go to the beginning
        self.showTune()

    def prevTune(self):
        self.index -= 1
        if self.index < 0:
            self.index = len(self.tunebook) - 1  # Go to the end
        self.showTune()

    def copyTune(self):
        self.textEdit.selectAll()
        self.textEdit.copy()
        self.textEdit.clearFocus()
        self.updateInterface()

    def isCopied(self):
        if QApplication.clipboard().text() == self.tune:
            return((True, _("Copied")))
        return((False, ""))

    def isFirst(self):
        if self.index == 0:
            return(True)
        return(False)

    def isLast(self):
        if self.index == len(self.tunebook) - 1:
            return(True)
        return(False)

    def getField(self, key, tune=None):
        sep = ':'
        keysep = key + sep
        if not tune:
            tune = self.textEdit.toPlainText()
        for i in tune.split('\n'):
            if i.startswith(keysep):
                k, v = i.split(sep)
                return(v.strip())
        return('')

    def setField(self, key, value, tune_text=None):
        startkey = '\n' + key
        tune = []
        aux = []
        haskey = False

        if value == 'Default':
            return(0)
        if not tune_text:
            tune_text = self.textEdit.toPlainText()
        for l in tune_text.split('\n'):
            if l.startswith(key):
                haskey = True
            tune.append(l)

        if haskey:
            print('Found key')
            for l in tune:
                if l.startswith(key):
                    l = key + value
                aux.append(l)
        else:
            print('No key')
            for l in tune:
                if l.startswith('X:'):
                    aux.append(l)
                    l = key + value  # Insert value line
                    aux.append(l)
                else:
                    aux.append(l)

        #self.textEdit.setText('\n'.join(aux))
        self.tunebook[self.index] = '\n'.join(aux)

    def setComboTempo(self):
        if self.tunebook:
            self.setField('Q:', self.comboTempo.currentText())
        self.showTune()

    def updateStatus(self):
        t = self.getField('T')
        o = self.getField('O')
        r = self.getField('R')
        self.statusT.setText(t)
        self.statusR.setText(r)

    def updateSvg(self):
        if not self.showSheetAct.isChecked():
            return(0)
        buff = self.textEdit.toPlainText().encode()
        svg = subprocess.run(
            ('abcm2ps', '-F', 'format.fmt', '-g', '-', '-O', '-'),
            input=buff, stdout=subprocess.PIPE)
        self.svgWidget.load(svg.stdout)

    def updateMIDI(self):
        if not self.togglePlayAct.isChecked():
            return(0)
        outfile = '/tmp/qabc.mid'
        buff = self.textEdit.toPlainText().encode()
        midi = subprocess.run(
            ('abc2midi', '-', '-o', outfile),
            input=buff)
        url = QUrl.fromLocalFile(outfile)
        mediaContent = QMediaContent(url)
        self.mediaPlayer.setMedia(mediaContent)
        if self.togglePlayAct.isChecked():
            self.mediaPlayer.play()

    def updateTitle(self):
        if self.textEdit.toPlainText() == self.tunebookSaved[self.index]:
            self.setWindowTitle(PROGRAM_NAME)
        else:
            self.setWindowTitle(PROGRAM_NAME + '*')

    def updateInterface(self):
        self.comboIndex.setCurrentIndex(self.index)
        self.comboTempo.setCurrentIndex(0)
        self.firstAct.setEnabled(not self.isFirst())
        self.prevAct.setEnabled(not self.isFirst())

        self.lastAct.setEnabled(not self.isLast())
        self.nextAct.setEnabled(not self.isLast())

        self.copyAct.setEnabled(not self.isCopied()[0])

        self.updateStatus()
        self.updateTitle()

        self.updateSvg()
        self.updateMIDI()

    def showAbout(self):
        aboutDialog.show()

    def showSheet(self):
        if self.showSheetAct.isChecked():
            self.updateSvg()
            sheetWin.show()
        else:
            sheetWin.hide()

    def showTune(self):
        if not self.tunebook:
            return(1)
        self.tune = self.tunebook[self.index]
        self.textEdit.setText(self.tune)
        self.updateInterface()

    def closeApp(self):
        sheetWin.close()
        aboutDialog.close()
        self.close()

    def indexTool(self):
        n = 0
        for i in self.tunebook:
            tune = []
            n += 1
            for l in i.split('\n'):
                if l.startswith('X:'):
                    l = 'X: ' + str(n)
                tune.append(l)
            self.tunebook[n - 1] = '\n'.join(tune)

    def toggleTearOff(self):
        if self.toggleTearOffAct.isChecked():
            self.fileMenu.setTearOffEnabled(True)
            self.navMenu.setTearOffEnabled(True)
            self.viewMenu.setTearOffEnabled(True)
            self.helpMenu.setTearOffEnabled(True)
        else:
            self.fileMenu.setTearOffEnabled(False)
            self.navMenu.setTearOffEnabled(False)
            self.viewMenu.setTearOffEnabled(False)
            self.helpMenu.setTearOffEnabled(False)

    def togglePlay(self):
        if self.togglePlayAct.isChecked():
            self.updateMIDI()
            self.mediaPlayer.stop()
            self.mediaPlayer.play()
        else:
            self.mediaPlayer.stop()

    def save(self):
        self.tunebook[self.index] = self.textEdit.toPlainText()
        try:  # Populate tunebook with a fortune database file
            with open(self.tunebookFile, "w") as f:
                for i in self.tunebook:
                    f.write(i + '\n')
        except:
            print('No puedo guardar el archivo')
        f.close()
        self.tunebookSaved[self.index] = self.tunebook[self.index]
        self.updateTitle()

    def createActions(self):
        self.firstAct = QAction(QIcon.fromTheme('go-first'),
                                _("&First"),
                                self, shortcut=QKeySequence.MoveToStartOfLine,
                                statusTip=_("Show first tune"),
                                triggered=self.firstTune)

        self.lastAct = QAction(QIcon.fromTheme('go-last'),
                               _("&Last"),
                               self, shortcut=QKeySequence.MoveToEndOfLine,
                               statusTip=_("Show last tune"),
                               triggered=self.lastTune)

        self.nextAct = QAction(QIcon.fromTheme('go-next'),
                               _("&Next"),
                               self, shortcut=QKeySequence.MoveToNextPage,
                               statusTip=_("Show next tune"),
                               triggered=self.nextTune)

        self.prevAct = QAction(QIcon.fromTheme('go-previous'),
                               _("&Previous"),
                               self, shortcut=QKeySequence.MoveToPreviousPage,
                               statusTip=_("Show previous tune"),
                               triggered=self.prevTune)

        self.exitAct = QAction(QIcon.fromTheme('window-close'), _("E&xit"),
                               self, shortcut=QKeySequence.Quit,
                               statusTip=_("Exit the application"),
                               triggered=self.closeApp)

        self.copyAct = QAction(QIcon.fromTheme('edit-copy'),
                               _("&Copy"),
                               self, shortcut=QKeySequence.Copy,
                               statusTip=_("Copy tune to the clipboard"),
                               triggered=self.copyTune)

        self.aboutAct = QAction(QIcon.fromTheme(EXECUTABLE_NAME),
                                _("&About") + " " + PROGRAM_NAME, self,
                                statusTip=_("Information about"
                                            " this application"),
                                triggered=self.showAbout)

        self.aboutQtAct = QAction(QIcon.fromTheme('help-about'),
                                  _("About &Qt"), self,
                                  statusTip=_("Show information about"
                                              " the Qt library"),
                                  triggered=QApplication.instance().aboutQt)

        self.openAct = QAction(QIcon.fromTheme('document-open'),
                               _("&Open"),
                               self, shortcut=QKeySequence.Open,
                               statusTip=_("Open a tune file"),
                               triggered=self.openFile)

        self.showSheetAct = QAction(QIcon.fromTheme('view-media-lyrics'),
                                 _("&Show sheet music"),
                                 self, shortcut='F4',
                                 statusTip=_("View sheet music"),
                                 triggered=self.showSheet)
        self.showSheetAct.setCheckable(True)

        self.indexAct = QAction(QIcon.fromTheme('database-index'),
                                    _("&Indexize"),
                                    self, shortcut='Ctrl+I',
                                    statusTip=_("Reformat indices"),
                                    triggered=self.indexTool)

        self.toggleTearOffAct = QAction(QIcon.fromTheme('application-menu'),
                                    _("&Tear off menus"),
                                    self, shortcut=QKeySequence.InsertLineSeparator,
                                    statusTip=_("Tear off menus"),
                                    triggered=self.toggleTearOff)
        self.toggleTearOffAct.setCheckable(True)

        self.saveAct = QAction(QIcon.fromTheme('document-save'),
                                    _("&Save"),
                                    self, shortcut=QKeySequence.Save,
                                    statusTip=_("Save tunebook"),
                                    triggered=self.save)

        self.togglePlayAct = QAction(QIcon.fromTheme('media-playback-start'),
                                    _("&Play"),
                                    self, shortcut='Alt+Intro',
                                    statusTip=_("Play tune"),
                                    triggered=self.togglePlay)
        self.togglePlayAct.setCheckable(True)



    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu(_("&File"))
        #self.fileMenu.setTearOffEnabled(True)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.copyAct)
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.navMenu = self.menuBar().addMenu(_("&Navigation"))
        #self.navMenu.setTearOffEnabled(True)
        self.navMenu.addAction(self.prevAct)
        self.navMenu.addAction(self.nextAct)
        self.navMenu.addAction(self.firstAct)
        self.navMenu.addAction(self.lastAct)

        self.viewMenu = self.menuBar().addMenu(_("View"))
        #self.viewMenu.setTearOffEnabled(True)
        self.viewMenu.addAction(self.showSheetAct)
        self.viewMenu.addAction(self.toggleTearOffAct)

        self.toolMenu = self.menuBar().addMenu(_("&Tools"))
        self.toolMenu.addAction(self.indexAct)

        self.helpMenu = self.menuBar().addMenu(_("&Help"))
        #self.helpMenu.setTearOffEnabled(True)
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

    def createToolBars(self):
        self.fileToolBar = self.addToolBar(_("File"))
        self.fileToolBar.addAction(self.openAct)
        self.fileToolBar.addAction(self.copyAct)
        self.fileToolBar.addAction(self.saveAct)

        self.viewToolBar = self.addToolBar(_("View"))
        self.viewToolBar.addAction(self.showSheetAct)

        self.navToolBar = self.addToolBar(_("Navigation"))
        self.navToolBar.addAction(self.firstAct)
        self.navToolBar.addAction(self.prevAct)
        self.navToolBar.addAction(self.nextAct)
        self.navToolBar.addAction(self.lastAct)

        self.playToolBar = self.addToolBar(_("Play"))
        self.playToolBar.addWidget(self.comboIndex)
        self.playToolBar.addAction(self.togglePlayAct)
        self.playToolBar.addWidget(self.comboTempo)


    def createStatusBar(self):
        self.statusBar().addWidget(self.statusR, Qt.AlignLeft)
        self.statusBar().addWidget(self.statusT, Qt.AlignRight)

    def readSettings(self):
        settings = QSettings(PROGRAM_NAME, _("Settings"))
        size = settings.value("size", QSize(700, 400))
        self.setWindowTitle(PROGRAM_NAME)
        self.setWindowIcon(QIcon.fromTheme(EXECUTABLE_NAME))
        self.resize(size)

class SheetMusic(QMainWindow):
    def __init__(self, parent=None):
        super(SheetMusic, self).__init__(parent)
        self.setCentralWidget(mainWin.svgWidget)
        self.statusBar = mainWin.statusBar

        self.navToolBar = self.addToolBar(_("Navigation"))
        self.navToolBar.addAction(mainWin.showSheetAct)
        self.navToolBar.addAction(mainWin.firstAct)
        self.navToolBar.addAction(mainWin.prevAct)
        self.navToolBar.addAction(mainWin.nextAct)
        self.navToolBar.addAction(mainWin.lastAct)
        #self.navToolBar.addWidget(mainWin.comboIndex)

class AboutDialog(QWidget):
    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent)

        font = QFont()
        font.setPointSize(18)
        font.setBold(False)
        labelIcon = QLabel()
        pixmap = QIcon.fromTheme(EXECUTABLE_NAME).pixmap(QSize(64, 64))
        labelIcon.setPixmap(pixmap)
        labelText = QLabel(PROGRAM_NAME)
        labelText.setFont(font)

        tabWidget = QTabWidget()
        tabWidget.addTab(AboutTab(), _("About"))
        tabWidget.addTab(VersionTab(), _("Version"))
        tabWidget.addTab(AuthorsTab(), _("Authors"))
        tabWidget.addTab(ThanksTab(), _("Thanks"))
        tabWidget.addTab(TranslationTab(), _("Translation"))

        btn = QPushButton(_("Close"), self)
        btn.setIcon(QIcon.fromTheme("window-close"))
        btn.setToolTip(_("Close this window"))
        btn.clicked.connect(self.close)

        labelLayout = QHBoxLayout()
        labelLayout.addWidget(labelIcon)
        labelLayout.addWidget(labelText, Qt.AlignLeft)

        mainLayout = QGridLayout()
        mainLayout.addLayout(labelLayout, 0, 0)
        mainLayout.addWidget(tabWidget, 1, 0)
        mainLayout.addWidget(btn, 2, 0, Qt.AlignRight)
        self.setLayout(mainLayout)

        self.setWindowTitle(_("About") + " " + PROGRAM_NAME)
        self.setWindowIcon(QIcon.fromTheme(EXECUTABLE_NAME))


class AboutTab(QWidget):
    def __init__(self, parent=None):
        super(AboutTab, self).__init__(parent)

        blank = QLabel()
        description = QLabel(DESCRIPTION)
        copyright = QLabel("© 2017, " + AUTHOR)
        source = QLabel(_("Source:") + " "
                        + "<a href='" + SOURCE + "'>" + SOURCE + "</a>")
        license = QLabel(_("License:") + " "
                         + "<a href='https://www.gnu.org/licenses/"
                         "gpl-3.0.en.html'>"
                         + _("GNU General Public License, version 3") + "</a>")

        source.setTextInteractionFlags(Qt.TextBrowserInteraction)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(blank)
        mainLayout.addWidget(blank)
        mainLayout.addWidget(blank)
        mainLayout.addWidget(description)
        mainLayout.addWidget(blank)
        mainLayout.addWidget(copyright)
        mainLayout.addWidget(source)
        mainLayout.addWidget(license)
        mainLayout.addStretch()
        self.setLayout(mainLayout)


class VersionTab(QWidget):
    def __init__(self, parent=None):
        super(VersionTab, self).__init__(parent)

        version = QLabel("<b>" + _("Version") + " " + VERSION + "<b>")
        using = QLabel(_("Using:") + " ")
        pyver = ".".join((
            str(sys.version_info[0]),
            str(sys.version_info[1]),
            str(sys.version_info[2])))
        python = QLabel("<ul><li>Python " + pyver)
        pyqt = QLabel("<ul><li>PyQt " + QT_VERSION_STR)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(version)
        mainLayout.addWidget(using)
        mainLayout.addWidget(python)
        mainLayout.addWidget(pyqt)
        mainLayout.addStretch(1)
        self.setLayout(mainLayout)


class AuthorsTab(QWidget):
    def __init__(self, parent=None):
        super(AuthorsTab, self).__init__(parent)

        blank = QLabel()
        notice = QLabel(_("Mail me if you found bugs."))
        name1 = QLabel("<b>" + AUTHOR + "<b>")
        task1 = QLabel("<i>" + _("Principle author") + "</i>")
        mail1 = QLabel("<pre>" + MAIL + "</pre>")

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(notice)
        mainLayout.addWidget(blank)
        mainLayout.addWidget(name1)
        mainLayout.addWidget(task1)
        mainLayout.addWidget(mail1)
        mainLayout.addStretch(1)
        self.setLayout(mainLayout)


class ThanksTab(QWidget):
    def __init__(self, parent=None):
        super(ThanksTab, self).__init__(parent)

        blank = QLabel()
        notice = QLabel(_("Thank you for using my program."))

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(blank)
        mainLayout.addWidget(notice)
        mainLayout.addStretch(1)
        self.setLayout(mainLayout)


class TranslationTab(QWidget):
    def __init__(self, parent=None):
        super(TranslationTab, self).__init__(parent)

        blank = QLabel()
        notice = QLabel(_("Please, mail me if you want to") + " "
                        + _("improve the translation."))
        name1 = QLabel("<b>" + AUTHOR + "<b>")
        task1 = QLabel("<i>" + _("Spanish and english translation") + "</i>")
        mail1 = QLabel("<pre>" + MAIL + "</pre>")

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(notice)
        mainLayout.addWidget(blank)
        mainLayout.addWidget(name1)
        mainLayout.addWidget(task1)
        mainLayout.addWidget(mail1)
        mainLayout.addStretch(1)
        self.setLayout(mainLayout)


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    mainWin = MainWindow()
    aboutDialog = AboutDialog()
    sheetWin = SheetMusic()
    mainWin.show()
    sys.exit(app.exec_())
