#!/usr/bin/python3

import os
import gettext
import subprocess
import uuid

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtSvg import *
from PyQt5.QtMultimedia import *

PROGRAM_NAME = "Qabc"
EXECUTABLE_NAME = "qabc"

gettext.translation(EXECUTABLE_NAME, localedir="/usr/share/locale",
                    fallback=True).install()

DESCRIPTION = _("A abc music files manager")
VERSION = "0.2a"
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

class TuneBook():
    def __init__(self):
        self.tunes = []
        self.index = 0
        self.path = None

    def loadFile(self, path):
        ''' Adds a tune file to the tunes DB '''
        if not path:
            return(0)
        if not os.path.isfile(path):
            return(1)

        self.path = path
        self.tunes = []  # Database containing all tunes
        self.tunesSaved = []

        try:
            with open(self.path, "r") as f:
                text = f.read()
        except:
            text = None

        f.close()

        if text:
            aux = []
            for line in text.split('\n'):
                if line.startswith('X:'):
                    if aux:
                        self.tunes.append('\n'.join(aux))
                        aux = []
                if line:
                    aux.append(line)

            self.tunes.append('\n'.join(aux))  # Add last
            self.ntunes = len(self.tunes)
            # list.copy() is like list[:]
            self.backup = self.tunes.copy()  # Backup tunebook for restore().

    def save(self, text):
        self.tunes[self.index] = text

        try:
            with open(self.path, "w") as f:
                for i in self.tunes:
                    f.write(i + '\n')
        except:
            print("I can't save the tunebook file")

        f.close()
        self.tunesSaved[self.index] = self.tunes[self.index]

    def reindex(self):
        n = 0
        for i in self.tunes:
            tune = Tune()
            tune.load(i)
            tune.setField('X:', n + 1)
            self.tunes[n] = tune.text
            n += 1

    def sort(self):
        aux = []
        aux2 = []
        n = 0
        for i in self.tunes:
            tune = Tune()
            tune.load(i)
            aux.append((tune.getField('T'), n))
            n += 1
        # Sorting array by first member (Title):
        aux = sorted(aux, key=lambda t: t[0])
        for i in aux:
            aux2.append(self.tunes[i[1]])
        self.tunes = aux2.copy()

    def restore(self):
        self.tunes = self.backup.copy()

    def add(self, tune):  # To the last
        self.tunes.append(tune)
        self.ntunes += 1

    def insert(self, pos, tune):  # At the position + 1
        self.tunes.insert(pos, tune)
        self.ntunes += 1

    def remove(self, pos):
        self.tunes.pop(pos)
        self.ntunes -= 1


class Tune():
    def __init__(self):
        self.load()

    def load(self, text=None):
        if text:
            self.text = text
        else:
            self.text = ''
        self.original = tuneBook.tunes[tuneBook.index]

    def hasField(self, key):
        for i in self.text.split('\n'):
            if i.startswith(key):
                return(True)
        return(False)

    def getField(self, key):
        sep = ':'
        comment = '%'
        for i in self.text.split('\n'):
            if i.startswith(key):
                v = i.split(sep)[1]
                if comment in v:
                    v = v.split(comment)[0]
                return(v.strip())
        return('')

    def setField(self, key, value):
        lines = []

        if value == 'Default':
            return(0)

        if self.hasField(key):
            for l in self.text.split('\n'):
                if l.startswith(key):
                    l = key + str(value)
                lines.append(l)
        else:
            for l in self.text.split('\n'):
                if l.startswith('X:'):
                    lines.append(l)
                    l = key + str(value)  # Insert value line
                    lines.append(l)
                else:
                    lines.append(l)

        self.text = '\n'.join(lines)

    def transpose(self, semitones):
        buff = self.original.encode()
        t = subprocess.run(
            ('abc2abc', '-', '-t', str(semitones)),
            input=buff, stdout=subprocess.PIPE)
        self.text = t.stdout.decode()


class NewTuneForm(QWidget):
    def __init__(self, parent=None):
        super(NewTuneForm, self).__init__(parent)

        self.setWindowTitle(PROGRAM_NAME + ' ' + _("(New tune)"))
        self.setWindowIcon(QIcon.fromTheme(EXECUTABLE_NAME))

        self.textEdit = QTextEdit()
        label = QLabel(_("New tune"))
        self.resize(QSize(500, 400))

        btnAccept = QPushButton(_("Accept"), self)
        btnAccept.setIcon(QIcon.fromTheme("dialog-ok"))
        btnAccept.setToolTip(_("Add this tune to tunebook"))
        btnAccept.clicked.connect(self.accept)

        btnClose = QPushButton(_("Cancel"), self)
        btnClose.setIcon(QIcon.fromTheme("dialog-cancel"))
        btnClose.setToolTip(_("Exit without applying the changes"))
        btnClose.clicked.connect(self.close)

        btnLayout = QHBoxLayout()
        btnLayout.addWidget(btnClose)
        btnLayout.addWidget(btnAccept)

        self.addRadioButton = QRadioButton(self)
        self.addRadioButton.setToolTip(_("Add to the end of tunebook"))
        self.addRadioButton.setText(_("Add"))
        self.insertRadioButton = QRadioButton(self)
        self.insertRadioButton.setText(_("Insert"))
        self.insertRadioButton.setToolTip(_("Insert before current tune"))
        self.addRadioButton.setChecked(True)

        radioLayout = QHBoxLayout()
        radioLayout.addWidget(self.addRadioButton)
        radioLayout.addWidget(self.insertRadioButton)
        radioLayout.addStretch()

        mainLayout = QGridLayout()
        mainLayout.addWidget(label, 0, 0)
        mainLayout.addLayout(radioLayout, 1, 0)
        mainLayout.addWidget(self.textEdit, 2, 0)
        mainLayout.addLayout(btnLayout,3, 0, Qt.AlignRight)
        self.setLayout(mainLayout)

    def accept(self):
        tune = self.textEdit.toPlainText()
        if self.addRadioButton.isChecked():
            mainWindow.addTune(tune)
        else:
            mainWindow.insertTune(tune)
        self.textEdit.clear()
        self.close()



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


class TuneTable(QWidget):

    X, T, R, K = range(4)

    def __init__(self):
        super(TuneTable, self).__init__()

        self.proxyModel = QSortFilterProxyModel()
        self.proxyModel.setDynamicSortFilter(True)
        self.proxyModel.setFilterKeyColumn(self.T)

        self.proxyView = QTableView()
        self.proxyView.setModel(self.proxyModel)
        self.proxyView.setSortingEnabled(True)
        self.proxyView.verticalHeader().setVisible(False)
        self.proxyView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.proxyView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.proxyView.setSelectionMode(QAbstractItemView.SingleSelection)
        #self.proxyView.setEditable(False)
        self.proxyView.selectionModel().selectionChanged.connect(self.itemSelected)

        self.filterCaseSensitivityCheckBox = QCheckBox("Case sensitive")

        self.filterPatternLineEdit = QLineEdit()
        self.filterPatternLineEdit.setClearButtonEnabled(True)
        self.filterPatternLabel = QLabel("&Filter:")
        self.filterPatternLabel.setBuddy(self.filterPatternLineEdit)

        self.filterSyntaxComboBox = QComboBox()
        self.filterSyntaxComboBox.addItem("Fixed string", QRegExp.FixedString)
        self.filterSyntaxComboBox.addItem("Wildcard", QRegExp.Wildcard)
        self.filterSyntaxComboBox.addItem("Regular expression", QRegExp.RegExp)

        self.filterColumnComboBox = QComboBox()
        self.filterColumnComboBox.addItem("Title")
        self.filterColumnComboBox.addItem("Rhythm")
        self.filterColumnComboBox.addItem("Meter")
        self.filterColumnComboBox.addItem("Key")

        self.filterPatternLineEdit.textChanged.connect(self.filterRegExpChanged)
        self.filterSyntaxComboBox.currentIndexChanged.connect(self.filterRegExpChanged)
        self.filterColumnComboBox.currentIndexChanged.connect(self.filterColumnChanged)
        self.filterCaseSensitivityCheckBox.toggled.connect(self.filterRegExpChanged)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.proxyView)
        self.setLayout(mainLayout)

        #self.resize(500, 450)

        self.proxyView.sortByColumn(self.T, Qt.AscendingOrder)
        self.filterColumnComboBox.setCurrentIndex(0)

        #self.filterPatternLineEdit.setText("Andy|Grace")
        self.filterCaseSensitivityCheckBox.setChecked(False)

    def setSourceModel(self, model):
        self.proxyModel.setSourceModel(model)

    def filterRegExpChanged(self):
        syntax_nr = self.filterSyntaxComboBox.itemData(self.filterSyntaxComboBox.currentIndex())
        syntax = QRegExp.PatternSyntax(syntax_nr)

        if self.filterCaseSensitivityCheckBox.isChecked():
            caseSensitivity = Qt.CaseSensitive
        else:
            caseSensitivity = Qt.CaseInsensitive

        regExp = QRegExp(self.filterPatternLineEdit.text(),
                caseSensitivity, syntax)
        self.proxyModel.setFilterRegExp(regExp)

    def filterColumnChanged(self):
        self.proxyModel.setFilterKeyColumn(self.filterColumnComboBox.currentIndex() + 1)

    def createABCModel(self):
        model = QStandardItemModel(0, 5)

        model.setHeaderData(0, Qt.Horizontal, "Index")
        model.setHeaderData(1, Qt.Horizontal, "Title")
        model.setHeaderData(2, Qt.Horizontal, "Rhythm")
        model.setHeaderData(3, Qt.Horizontal, "Meter")
        model.setHeaderData(4, Qt.Horizontal, "Key")

        x = 0
        for i in tuneBook.tunes:
            tune = Tune()
            tune.load(i)
            t = tune.getField('T:')
            r = tune.getField('R:')
            m = tune.getField('M:')
            k = tune.getField('K:')

            model.insertRow(0)
            model.setData(model.index(0, 0), x)
            model.setData(model.index(0, 1), t)
            model.setData(model.index(0, 2), r)
            model.setData(model.index(0, 3), m)
            model.setData(model.index(0, 4), k)
            x += 1
        return model

    def getTableViewValue(self,row, column, widget):
        choords = widget.model().index(row, column)
        return(widget.model().data(choords))

    def itemSelected(self):
        row = self.proxyView.currentIndex().row()
        column = 0
        index = self.getTableViewValue(row, column, self.proxyView)
        if index >= 0:  # Prevent None selected
            tuneBook.index = int(index)
            mainWindow.showTune()

    def reloadTable(self):
        app.setOverrideCursor(Qt.WaitCursor)
        self.setSourceModel(self.createABCModel())
        self.proxyView.resizeColumnsToContents()
        app.restoreOverrideCursor()


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.createActions()

        self.uuid = str(uuid.uuid4())
        self.tmpdir = os.path.abspath(os.path.join(os.sep, 'tmp'))
        self.midi = QFile(os.path.join(self.tmpdir, PROGRAM_NAME + self.uuid) + '.mid')

        self.statusT = QLabel()
        self.statusR = QLabel()
        self.statusK = QLabel()

        self.comboTempo = QComboBox()
        self.comboTempo.setEditable(False)
        self.comboTempo.currentIndexChanged[str].connect(self.updateMIDI)
        self.comboTempo.addItem(_("Default"))
        for i in range(60, 360, 60):
            self.comboTempo.addItem(str(i))

        self.transposeSpinBox = QSpinBox()
        self.transposeSpinBox.setRange(-100, 100)
        self.transposeSpinBox.setSingleStep(1)
        self.transposeSpinBox.setValue(0)
        self.transposeSpinBox.valueChanged.connect(self.transpose)

        self.svgWidget = QSvgWidget()
        self.svgPalette = self.svgWidget.palette()
        self.svgPalette.setColor(self.svgWidget.backgroundRole(), Qt.white)


        self.svgScroll = QScrollArea()
        self.svgScroll.setWidget(self.svgWidget)

        self.textEdit = QTextEdit()
        self.textEdit.textChanged.connect(self.autoUpdateInterface)

        self.logView = QTextEdit()

        self.mediaPlayer = QMediaPlayer()
        self.playList = QMediaPlaylist()
        self.tuneTable = TuneTable()

        self.createMenus()
        self.createToolBars()
        self.createDockWindows()
        self.createStatusBar()
        self.readSettings()

        try:
            f = sys.argv[1]
        except:
            f = None

        if f:
            self.openFile(f)

    def closeEvent(self, event):
        self.midi.remove()
        app.quit()

    def openFile(self, f=None):
        if f:
            select = f
        else:
            select = QFileDialog.getOpenFileName(self, _("Open file"))[0]

        if select:
            tuneBook.loadFile(select)
            self.showTune()
            for i in tuneBook.tunes:
                tuneBook.tunesSaved.append(i)
            self.tuneTable.reloadTable()
            if not self.toggleShowIndexAct.isChecked():
                self.tuneTable.proxyView.setColumnHidden(0,True)

    def showTune(self):
        if tuneBook.tunes:
            self.textEdit.setText(tuneBook.tunes[tuneBook.index])
            self.comboTempo.setCurrentIndex(0)
            self.transposeSpinBox.setValue(0)
            if not self.toggleAutorefreshAct.isChecked():
                self.updateInterface()

    def autoUpdateInterface(self):
        if self.toggleAutorefreshAct.isChecked():
            self.updateInterface()

    def updateInterface(self):
        tune = Tune()
        tune.load(self.textEdit.toPlainText())
        t = tune.getField('T:')
        self.logView.append(_("SHOWING: ") +  t)
        self.updateStatus()
        self.updateTitle()
        self.updateSvg()
        self.updateMIDI()

    def updateStatus(self):
        tune = Tune()
        tune.load(self.textEdit.toPlainText())
        t = tune.getField('T:')
        r = tune.getField('R:')
        k = tune.getField('K:')
        self.statusT.setText(t)
        self.statusK.setText(k)
        self.statusR.setText(r.title())

    def updateTitle(self):
        if self.textEdit.toPlainText() == tuneBook.tunes[tuneBook.index]:
            self.setWindowTitle(PROGRAM_NAME)
        else:
            self.setWindowTitle(PROGRAM_NAME + '*')

    def updateSvg(self):
        #if not self.toggleShowSheetAct.isChecked():
        #    return(0)
        buff = self.textEdit.toPlainText().encode()
        svg = subprocess.run(
            ('abcm2ps', '-q', '-g', '-', '-O', '-'),
            input=buff, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if svg.stderr:
            self.logView.append(svg.stderr.decode())
        else:
            self.logView.append(_("SVG OK"))
        self.svgWidget.load(svg.stdout)
        print(self.svgWidget.sizeHint())
        self.svgWidget.resize(self.svgWidget.sizeHint())
        self.svgWidget.setAutoFillBackground(True)
        self.svgWidget.setPalette(self.svgPalette)

    def exportMIDI(self):
        outfile = self.midi.fileName()
        print(outfile)
        buff = self.textEdit.toPlainText().encode()

        if not self.comboTempo.currentIndex():
            cmd = ('abc2midi', '-', '-silent', '-o', outfile)
        else:
            tempo = self.comboTempo.currentText()
            cmd = ('abc2midi', '-', '-silent', '-Q', tempo, '-o', outfile)

        midi = subprocess.run(cmd, input=buff, stderr=subprocess.PIPE)
        if midi.stderr:
            self.logView.append(midi.stderr.decode())
        else:
            self.logView.append(_("MIDI OK"))

    def exportMIDItoFile(self):
        tune = Tune()
        tune.load(self.textEdit.toPlainText())
        defname = tune.getField('T:') + '.mid'
        select = QFileDialog.getSaveFileName(self, _("Export to MIDI file"),
                                             defname)[0]
        print(select)
        if select:
            f = QFile(outfile)
            self.midi.copy(select)
            self.midi.close()

    def updateMIDI(self):
        if self.togglePlayAct.isChecked():
            self.exportMIDI()
            url = QUrl.fromLocalFile(self.midi.fileName())
            mediaContent = QMediaContent(url)
            self.playList.addMedia(mediaContent)
            self.playList.setPlaybackMode(QMediaPlaylist.Loop)
            self.mediaPlayer.setPlaylist(self.playList)
            self.mediaPlayer.play()

    def toggleShowSheet(self):
        if self.toggleShowSheetAct.isChecked():
            self.musicDock.show()
        else:
            self.musicDock.hide()

    def toggleShowCode(self):
        if self.toggleShowCodeAct.isChecked():
            self.editDock.show()
        else:
            self.editDock.hide()

    def toggleShowLog(self):
        if self.toggleShowLogAct.isChecked():
            self.logDock.show()
        else:
            self.logDock.hide()

    def toggleShowTable(self):
        if self.toggleShowTableAct.isChecked():
            self.tableDock.show()
        else:
            self.tableDock.hide()

    def toggleHideToolbar(self):
        if self.toggleHideToolbarAct.isChecked():
            self.playToolBar.hide()
        else:
            self.playToolBar.show()

    def toggleTearOff(self):
        if self.toggleTearOffAct.isChecked():
            self.tunebookMenu.setTearOffEnabled(True)
            self.tuneMenu.setTearOffEnabled(True)
            self.viewMenu.setTearOffEnabled(True)
            self.helpMenu.setTearOffEnabled(True)
        else:
            self.tunebookMenu.setTearOffEnabled(False)
            self.tuneMenu.setTearOffEnabled(False)
            self.viewMenu.setTearOffEnabled(False)
            self.helpMenu.setTearOffEnabled(False)

    def toggleShowIndex(self, coln):
        if self.toggleShowIndexAct.isChecked():
            self.tuneTable.proxyView.setColumnHidden(0, False)
        else:
            self.tuneTable.proxyView.setColumnHidden(0, True)


    def togglePlay(self):
        if self.togglePlayAct.isChecked():
            self.updateMIDI()
            self.mediaPlayer.stop()
            self.mediaPlayer.play()
        else:
            self.mediaPlayer.stop()

    def save(self):
        ''' Copy current text to tunebook tune and write tunebook to disk.
        If tunebook was reindexed or reordered, it will save such changes.'''
        tuneBook.save(self.textEdit.toPlainText())
        self.updateTitle()
        oldindex = self.tuneTable.proxyView.currentIndex().row()
        self.tuneTable.reloadTable()
        self.tuneTable.proxyView.setCurrentIndex(self.tuneTable.proxyView.model().index(max(oldindex, 0), 0))

    def restore(self):
        '''Loads backup to tunebook. But not save it.'''
        q = _("Are you sure you want to restore?\nAll changes will be lost.")
        buttonReply = QMessageBox.question(self, _("Restore"), q,
                                           QMessageBox.Yes | QMessageBox.No,
                                           QMessageBox.No)
        if buttonReply == QMessageBox.No:
            return(0)
        else:
            tuneBook.restore()
            self.tuneTable.reloadTable()
            self.showTune()

    def reindex(self):
        tuneBook.reindex()
        self.showTune()

    def sort(self):
        tuneBook.sort()
        self.tuneTable.reloadTable()
        self.showTune()

    def transpose(self):
        semitones = self.transposeSpinBox.value()
        tune = Tune()
        tune.load(self.textEdit.toPlainText())
        tune.transpose(semitones)
        self.textEdit.setText(tune.text)

    def isCopied(self):
        if QApplication.clipboard().text() == self.textEdit.toPlainText():
            return(True)
        return(False)

    def copyTune(self):
        self.textEdit.selectAll()
        self.textEdit.copy()
        self.textEdit.clearFocus()
        self.copyTuneAct.setEnabled(not self.isCopied())

    def addTune(self, tune):
        tuneBook.add(tune)
        self.tuneTable.reloadTable()
        #self.lastTune()

    def insertTune(self, tune):
        pos = self.tuneTable.proxyView.currentIndex().row()
        tuneBook.insert(pos, tune)
        self.tuneTable.reloadTable()
        self.tuneTable.proxyView.setCurrentIndex(self.tuneTable.proxyView.model().index(max(pos, 0), 0))

    def removeTune(self):
        if tuneBook.ntunes:
            row = self.tuneTable.proxyView.currentIndex().row()
            column = 0
            pos = self.tuneTable.getTableViewValue(row, column, self.tuneTable.proxyView)
            tuneBook.remove(pos)
            self.tuneTable.reloadTable()
            self.tuneTable.proxyView.setCurrentIndex(self.tuneTable.proxyView.model().index(max(row - 1, 0), 0))
            self.showTune()

    def showNewTuneForm(self):
        formWin.show()

    def showAbout(self):
        aboutDialog.show()

    def createActions(self):
        self.openFileAct = QAction(QIcon.fromTheme('document-open'),
                               _("&Open"),
                               self, shortcut=QKeySequence.Open,
                               statusTip=_("Open a tune file"),
                               triggered=self.openFile)

        self.exitAct = QAction(QIcon.fromTheme('window-close'), _("E&xit"),
                               self, shortcut=QKeySequence.Quit,
                               statusTip=_("Exit the application"),
                               triggered=self.closeEvent)

        self.copyTuneAct = QAction(QIcon.fromTheme('edit-copy'),
                               _("&Copy"),
                               self, shortcut=QKeySequence.Copy,
                               statusTip=_("Copy tune to the clipboard"),
                               triggered=self.copyTune)

        self.showAboutAct = QAction(QIcon.fromTheme(EXECUTABLE_NAME),
                                _("&About") + " " + PROGRAM_NAME, self,
                                statusTip=_("Information about"
                                            " this application"),
                                triggered=self.showAbout)

        self.aboutQtAct = QAction(QIcon.fromTheme('help-about'),
                                  _("About &Qt"), self,
                                  statusTip=_("Show information about"
                                              " the Qt library"),
                                  triggered=QApplication.instance().aboutQt)

        self.toggleShowSheetAct = QAction(QIcon.fromTheme('view-media-lyrics'),
                                          _("&Show sheet music"),
                                          self, shortcut='F4',
                                          statusTip=_("View sheet music"),
                                          triggered=self.toggleShowSheet)
        self.toggleShowSheetAct.setCheckable(True)
        self.toggleShowSheetAct.setChecked(True)

        self.toggleShowCodeAct = QAction(QIcon.fromTheme('code-context'),
                                          _("&Show abc code"),
                                          self, shortcut='F3',
                                          statusTip=_("View abc code"),
                                          triggered=self.toggleShowCode)
        self.toggleShowCodeAct.setCheckable(True)
        self.toggleShowCodeAct.setChecked(True)

        self.toggleShowTableAct = QAction(QIcon.fromTheme('table'),
                                          _("&Show table"),
                                          self, shortcut='F2',
                                          statusTip=_("View table"),
                                          triggered=self.toggleShowTable)
        self.toggleShowTableAct.setCheckable(True)
        self.toggleShowTableAct.setChecked(True)

        self.toggleShowLogAct = QAction(QIcon.fromTheme('text-x-log'),
                                          _("&Show log"),
                                          self, shortcut='F6',
                                          statusTip=_("View abc code"),
                                          triggered=self.toggleShowLog)
        self.toggleShowLogAct.setCheckable(True)

        self.toggleHideToolbarAct = QAction(QIcon.fromTheme('configure-toolbars'),
                                          _("&Hide toolbar"),
                                          self, shortcut='Ctrl+T',
                                          statusTip=_("Hide toolbar"),
                                          triggered=self.toggleHideToolbar)
        self.toggleHideToolbarAct.setCheckable(True)

        self.toggleAutorefreshAct = QAction(QIcon.fromTheme('view-refresh'),
                                          _("&Autorefresh"),
                                          self, shortcut='Ctrl+R',
                                          statusTip=_("Activate autorefreshing"),
                                          triggered=self.updateInterface)
        self.toggleAutorefreshAct.setCheckable(True)

        self.refreshAct = QAction(QIcon.fromTheme('view-refresh'),
                                          _("&Refresh"),
                                          self, shortcut='F5',
                                          statusTip=_("Refresh interface"),
                                          triggered=self.updateInterface)


        self.reindexAct = QAction(QIcon.fromTheme('format-list-ordered'),
                                  _("&Indexize"),
                                  self, shortcut='Ctrl+I',
                                  statusTip=_("Reformat indices"),
                                  triggered=self.reindex)

        self.sortAct = QAction(QIcon.fromTheme('sort-name'),
                               _("&Sort"),
                               self, shortcut='Ctrl+J',
                               statusTip=_("Sort by title"),
                               triggered=self.sort)

        self.restoreAct = QAction(QIcon.fromTheme('restoration'),
                                  _("&Restore"),
                                  self, shortcut='Ctrl+Alt+R',
                                  statusTip=_("Restore tunebook from backup"),
                                  triggered=self.restore)

        self.addTuneAct = QAction(QIcon.fromTheme('list-add'),
                                  _("&Add tune"),
                                  self, shortcut='Ctrl+Alt+A',
                                  statusTip=_("Add new tune"),
                                  triggered=self.showNewTuneForm)

        self.removeTuneAct = QAction(QIcon.fromTheme('list-remove'),
                                  _("&Remove"),
                                  self, shortcut='Ctrl+Alt+D',
                                  statusTip=_("Remove tune"),
                                  triggered=self.removeTune)

        self.toggleTearOffAct = QAction(QIcon.fromTheme('application-menu'),
                                        _("&Show Tear off menus"), self,
                                        shortcut=QKeySequence.InsertLineSeparator,
                                        statusTip=_("Show Tear off menus"),
                                        triggered=self.toggleTearOff)
        self.toggleTearOffAct.setCheckable(True)

        self.toggleShowIndexAct = QAction(QIcon.fromTheme('view-table-of-contents-rtl'),
                                        _("&Show index column"), self,
                                        shortcut='Ctrl+Alt+I',
                                        statusTip=_("Show index column"),
                                        triggered=self.toggleShowIndex)
        self.toggleShowIndexAct.setCheckable(True)

        self.saveAct = QAction(QIcon.fromTheme('document-save'),
                               _("&Save"),
                               self, shortcut=QKeySequence.Save,
                               statusTip=_("Save tunes"),
                               triggered=self.save)

        self.exportMIDIAct = QAction(QIcon.fromTheme('document-export'),
                               _("&Export MIDI"),
                               self, shortcut='Ctrl+M',
                               statusTip=_("Export tune as MIDI file"),
                               triggered=self.exportMIDItoFile)

        self.togglePlayAct = QAction(QIcon.fromTheme('media-playback-start'),
                                     _("&Play"),
                                     self, shortcut='Alt+Intro',
                                     statusTip=_("Play tune"),
                                     triggered=self.togglePlay)
        self.togglePlayAct.setCheckable(True)

    def createMenus(self):
        self.tunebookMenu = self.menuBar().addMenu(_("&Tunebook"))
        self.tunebookMenu.addAction(self.openFileAct)
        self.tunebookMenu.addAction(self.addTuneAct)
        self.tunebookMenu.addSeparator()
        self.tunebookMenu.addAction(self.reindexAct)
        self.tunebookMenu.addAction(self.sortAct)
        self.tunebookMenu.addSeparator()
        self.tunebookMenu.addAction(self.restoreAct)
        self.tunebookMenu.addAction(self.saveAct)
        self.tunebookMenu.addSeparator()
        self.tunebookMenu.addAction(self.exitAct)

        self.tuneMenu = self.menuBar().addMenu(_("&Tune"))
        self.tuneMenu.addAction(self.refreshAct)
        self.tuneMenu.addAction(self.toggleAutorefreshAct)
        self.tuneMenu.addSeparator()
        self.tuneMenu.addAction(self.copyTuneAct)
        self.tuneMenu.addAction(self.removeTuneAct)
        self.tuneMenu.addSeparator()
        self.tuneMenu.addAction(self.exportMIDIAct)

        self.viewMenu = self.menuBar().addMenu(_("View"))
        self.viewMenu.addAction(self.toggleShowTableAct)
        self.viewMenu.addAction(self.toggleShowCodeAct)
        self.viewMenu.addAction(self.toggleShowSheetAct)
        self.viewMenu.addAction(self.toggleShowLogAct)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.toggleShowIndexAct)
        self.viewMenu.addAction(self.toggleTearOffAct)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.toggleHideToolbarAct)

        self.helpMenu = self.menuBar().addMenu(_("&Help"))
        self.helpMenu.addAction(self.showAboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

    def createToolBars(self):
        self.playToolBar = self.addToolBar(_("Play"))
        self.playToolBar.addAction(self.toggleShowSheetAct)
        self.playToolBar.addSeparator()
        self.playToolBar.addAction(self.toggleShowCodeAct)
        self.playToolBar.addSeparator()
        self.playToolBar.addAction(self.togglePlayAct)
        self.playToolBar.addSeparator()
        self.playToolBar.addWidget(self.comboTempo)
        self.playToolBar.addSeparator()
        self.playToolBar.addWidget(self.transposeSpinBox)
        self.playToolBar.addSeparator()
        self.filterToolBar = self.addToolBar(_("Filter"))
        self.filterToolBar.addWidget(self.tuneTable.filterPatternLabel)
        self.filterToolBar.addWidget(self.tuneTable.filterPatternLineEdit)
        self.filterToolBar.addSeparator()
        self.filterToolBar.addWidget(self.tuneTable.filterColumnComboBox)
        self.filterToolBar.addSeparator()
        self.filterToolBar.addWidget(self.tuneTable.filterSyntaxComboBox)
        self.filterToolBar.addSeparator()
        self.filterToolBar.addWidget(self.tuneTable.filterCaseSensitivityCheckBox)

    def createStatusBar(self):
        self.statusBar().addWidget(self.statusT, Qt.AlignLeft)
        self.statusBar().addWidget(self.statusK, Qt.AlignRight)
        self.statusBar().addWidget(self.statusR, Qt.AlignRight)

    def createDockWindows(self):
        self.tableDock = QDockWidget(_("Tunes"), self)
        self.tableDock.setWidget(self.tuneTable)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.tableDock)

        self.logDock = QDockWidget(_("Log"), self)
        self.logDock.setWidget(self.logView)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.logDock)
        self.logDock.hide()

        self.musicDock = QDockWidget(_("Music score"), self)
        self.musicDock.setWidget(self.svgScroll)
        self.addDockWidget(Qt.RightDockWidgetArea, self.musicDock)

        self.editDock = QDockWidget(_("Edit tune"), self)
        self.editDock.setWidget(self.textEdit)
        self.addDockWidget(Qt.RightDockWidgetArea, self.editDock)

    def readSettings(self):
        settings = QSettings(PROGRAM_NAME, _("Settings"))
        size = settings.value("size", QSize(1280, 720))
        self.setWindowTitle(PROGRAM_NAME)
        self.setWindowIcon(QIcon.fromTheme(EXECUTABLE_NAME))
        self.resize(size)

if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    tuneBook = TuneBook()
    mainWindow = MainWindow()
    aboutDialog = AboutDialog()
    formWin = NewTuneForm()
    mainWindow.show()
    sys.exit(app.exec_())
