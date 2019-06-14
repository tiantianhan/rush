from __future__ import print_function
from maya import OpenMayaUI
from maya.api import OpenMaya
from maya import cmds
from maya import mel
from rush.Qt import QtGui, QtWidgets, QtCore

try:
    import shiboken2 as shiboken
except ImportError:
    import shiboken

import sys
import os

import rush
reload(rush)


QSS = """
QListView
{
    background-color: rgb(42, 42, 42);
    border-style: solid;
    border-radius: 0px;
    border-width: 0px;
    border-color: rgb(60, 60, 60, 100);
    font-size: 14pt;
}

QLineEdit
{
    background-color: rgb(42, 42, 42);
    border-style: solid;
    border-radius: 10px;
    padding: 4px;
    border-width: 5px;
    border-color: rgb(95, 195, 206);
    font-size: 16pt;
}
"""

kPluginCmdName = "rush2"
kVerboseFlag = "-v"
kVerboseLongFlag = "-verbose"


MAYA_SCRIPT_DIR = cmds.internalVar(userScriptDir=True)


# Define mel procedure to call the previous function
mel.eval("""
global proc callLastCommand(string $function)
{
    repeatLast -ac $function -acl "blah-blah....";
}
""")


def getMayaWindow():
    ptr = OpenMayaUI.MQtUtil.mainWindow()
    return shiboken.wrapInstance(long(ptr), QtWidgets.QMainWindow)


class History(object):

    def __init__(self, parent=None):

        self.history = self.read()

    @classmethod
    def read(cls):
        """ Load history

        Return:
            history(list): list of commands

        """
        historyPath = os.path.join(MAYA_SCRIPT_DIR, "rushHistory.txt")
        if os.path.exists(historyPath):
            try:
                historyFile = open(historyPath, 'r')
                h = historyFile.read().splitlines()
                historyFile.close()
                return h
            except IOError:
                return []
        else:
            return []

    def append(self, command):
        """ append history

        Args:
            command (str): name of a command

        Return:
            None

        """
        # If command already exists in the history, move it to the front
        if command in self.history:
            self.history.insert(
                0, self.history.pop(self.history.index(command)))
        else:
            self.history.insert(0, command)

        # Set maximum number of histories
        self.history = self.history[:25]

    def save(self):
        """ Write history

        """

        historyPath = os.path.join(MAYA_SCRIPT_DIR, "rushHistory.txt")
        try:
            historyFile = open(historyPath, 'w')
            for line in self.history:
                historyFile.write(line + "\n")
            historyFile.close()
        except IOError:
            pass

    def clear(self):
        """ Clear history

        Return:
            None

        """
        pass


class CustomQLineEdit(QtWidgets.QLineEdit):
    """ Custom QLineEdit with custom events and signals
    Reference:
    https://ilmvfx.wordpress.com/2016/11/02/how-to-add-a-search-icon-and-clear-button-to-qlineedit/
    """

    escPressed = QtCore.Signal(str)
    tabPressed = QtCore.Signal(str)
    downPressed = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(CustomQLineEdit, self).__init__(parent)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        b64_data = (
            'PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iaXNvLTg4NTktMSI/Pgo8IS0tI'
            'EdlbmVyYXRvcjogQWRvYmUgSWxsdXN0cmF0b3IgMTYuMC4wLCBTVkcgRXhwb3J0IF'
            'BsdWctSW4gLiBTVkcgVmVyc2lvbjogNi4wMCBCdWlsZCAwKSAgLS0+CjwhRE9DVFl'
            'QRSBzdmcgUFVCTElDICItLy9XM0MvL0RURCBTVkcgMS4xLy9FTiIgImh0dHA6Ly93'
            'd3cudzMub3JnL0dyYXBoaWNzL1NWRy8xLjEvRFREL3N2ZzExLmR0ZCI+Cjxzdmcge'
            'G1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB4bWxuczp4bGluaz0iaH'
            'R0cDovL3d3dy53My5vcmcvMTk5OS94bGluayIgdmVyc2lvbj0iMS4xIiBpZD0iQ2F'
            'wYV8xIiB4PSIwcHgiIHk9IjBweCIgd2lkdGg9IjMycHgiIGhlaWdodD0iMzJweCIg'
            'dmlld0JveD0iMCAwIDQ4NS4yMTMgNDg1LjIxMyIgc3R5bGU9ImVuYWJsZS1iYWNrZ'
            '3JvdW5kOm5ldyAwIDAgNDg1LjIxMyA0ODUuMjEzOyIgeG1sOnNwYWNlPSJwcmVzZX'
            'J2ZSI+CjxnPgoJPGc+CgkJPHBhdGggZD0iTTQ3MS44ODIsNDA3LjU2N0wzNjAuNTY'
            '3LDI5Ni4yNDNjLTE2LjU4NiwyNS43OTUtMzguNTM2LDQ3LjczNC02NC4zMzEsNjQu'
            'MzIxbDExMS4zMjQsMTExLjMyNCAgICBjMTcuNzcyLDE3Ljc2OCw0Ni41ODcsMTcuN'
            'zY4LDY0LjMyMSwwQzQ4OS42NTQsNDU0LjE0OSw0ODkuNjU0LDQyNS4zMzQsNDcxLj'
            'g4Miw0MDcuNTY3eiIgZmlsbD0iI0ZGRkZGRiIvPgoJCTxwYXRoIGQ9Ik0zNjMuOTA'
            '5LDE4MS45NTVDMzYzLjkwOSw4MS40NzMsMjgyLjQ0LDAsMTgxLjk1NiwwQzgxLjQ3'
            'NCwwLDAuMDAxLDgxLjQ3MywwLjAwMSwxODEuOTU1czgxLjQ3MywxODEuOTUxLDE4M'
            'S45NTUsMTgxLjk1MSAgICBDMjgyLjQ0LDM2My45MDYsMzYzLjkwOSwyODIuNDM3LD'
            'M2My45MDksMTgxLjk1NXogTTE4MS45NTYsMzE4LjQxNmMtNzUuMjUyLDAtMTM2LjQ'
            '2NS02MS4yMDgtMTM2LjQ2NS0xMzYuNDYgICAgYzAtNzUuMjUyLDYxLjIxMy0xMzYu'
            'NDY1LDEzNi40NjUtMTM2LjQ2NWM3NS4yNSwwLDEzNi40NjgsNjEuMjEzLDEzNi40N'
            'jgsMTM2LjQ2NSAgICBDMzE4LjQyNCwyNTcuMjA4LDI1Ny4yMDYsMzE4LjQxNiwxOD'
            'EuOTU2LDMxOC40MTZ6IiBmaWxsPSIjRkZGRkZGIi8+CgkJPHBhdGggZD0iTTc1Ljg'
            'xNywxODEuOTU1aDMwLjMyMmMwLTQxLjgwMywzNC4wMTQtNzUuODE0LDc1LjgxNi03'
            'NS44MTRWNzUuODE2QzEyMy40MzgsNzUuODE2LDc1LjgxNywxMjMuNDM3LDc1LjgxN'
            'ywxODEuOTU1eiIgZmlsbD0iI0ZGRkZGRiIvPgoJPC9nPgo8L2c+CjxnPgo8L2c+Cj'
            'xnPgo8L2c+CjxnPgo8L2c+CjxnPgo8L2c+CjxnPgo8L2c+CjxnPgo8L2c+CjxnPgo'
            '8L2c+CjxnPgo8L2c+CjxnPgo8L2c+CjxnPgo8L2c+CjxnPgo8L2c+CjxnPgo8L2c+'
            'CjxnPgo8L2c+CjxnPgo8L2c+CjxnPgo8L2c+Cjwvc3ZnPgo=')

        data = QtCore.QByteArray.fromBase64(b64_data)
        tempPixmap = QtGui.QPixmap()
        tempPixmap.loadFromData(data)
        self.iconPixmap = tempPixmap.scaled(
            20,
            20,
            QtCore.Qt.IgnoreAspectRatio,
            QtCore.Qt.SmoothTransformation)

        self.setTextMargins(26, 0, 0, 0)

    def focusOutEvent(self, event):
        # Emit signal to close the window when it gets out of focus
        self.escPressed.emit('esc')

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.escPressed.emit('esc')
        elif event.key() == QtCore.Qt.Key_Tab:
            self.tabPressed.emit('tab')
        elif event.key() == QtCore.Qt.Key_Down:
            self.downPressed.emit('down')
        else:
            super(CustomQLineEdit, self).keyPressEvent(event)

    def paintEvent(self, event):
        super(CustomQLineEdit, self).paintEvent(event)

        painter = QtGui.QPainter(self)
        painter.setOpacity(0.75)
        height = self.iconPixmap.height()
        right_border = 8
        painter.drawPixmap(
            right_border+2, (self.height() - height) / 2, self.iconPixmap)


class Gui(rush.TempClass, QtWidgets.QFrame):

    def __init__(self, parent=None):
        """

        Args:
            cmdDict (dict): Dict of all commands

        """
        super(Gui, self).__init__(parent)

        self.cmdDict = self.commandDict
        self.history = History()

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("Rush")
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowFlags(
            QtCore.Qt.Popup | QtCore.Qt.FramelessWindowHint)
        try:
            self.setWindowFlags(
                self.windowFlags() | QtCore.Qt.NoDropShadowWindowHint)
        except AttributeError:
            pass
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # Dpi value to set the width for window and lineedit.
        self.dpi = self.physicalDpiX()

        self.setStyleSheet(QSS)

        # Create Data then UI
        self.createData()
        self.createUI()

        self.setFixedWidth(self.dpi * 3.5)

    def createUI(self):
        self.LE = CustomQLineEdit(self)
        self.LE.setFixedWidth(self.dpi * 3.5)
        self.LE.setPlaceholderText("Search")

        # Layout
        self.layout = QtWidgets.QBoxLayout(
            QtWidgets.QBoxLayout.TopToBottom)
        self.layout.addWidget(self.LE)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # Set up QCompleter
        self.completer = QtWidgets.QCompleter(self)
        self.completer.setCompletionMode(
            QtWidgets.QCompleter.UnfilteredPopupCompletion)
        self.completer.setModel(self.filteredModel)
        self.completer.setObjectName("commandCompleter")
        self.completer.popup().setStyleSheet(QSS)

        # Setup QCompleter for history
        self.histCompleter = QtWidgets.QCompleter(self)
        self.histCompleter.setCompletionMode(
            QtWidgets.QCompleter.UnfilteredPopupCompletion)
        self.histCompleter.setModel(self.historyModel)
        self.histCompleter.popup().setStyleSheet(QSS)

        # Edit line Edit behavior
        self.LE.setCompleter(self.completer)
        self.LE.textEdited.connect(self.updateData)
        self.LE.returnPressed.connect(self.execute)
        self.LE.escPressed.connect(self.close)
        self.LE.tabPressed.connect(self.tabCompletion)
        self.LE.downPressed.connect(self.showHistory)
        self.LE.setFocus()

    def createData(self):
        """

        Return:
            QSortFilterProxyModel: data

        """

        model = QtGui.QStandardItemModel()

        # Add all command names and icon paths to the the model(model)
        for num, command in enumerate(self.cmdDict):
            item = QtGui.QStandardItem(command)
            if os.path.isabs(self.cmdDict[command]['icon']) is True:
                iconPath = os.path.normpath(self.cmdDict[command]['icon'])
                item.setIcon(QtGui.QIcon(iconPath))
            else:
                item.setIcon(
                    QtGui.QIcon(":%s" % self.cmdDict[command]['icon']))
            model.setItem(num, 0, item)

        # Store the model(model) into the sortFilterProxy model
        self.filteredModel = QtCore.QSortFilterProxyModel(self)
        self.filteredModel.setFilterCaseSensitivity(
            QtCore.Qt.CaseInsensitive)
        self.filteredModel.setSourceModel(model)

        # History model
        self.historyList = self.history.read()
        self.historyModel = QtGui.QStandardItemModel()

        for num, command in enumerate(self.historyList):

            # Capitalize the first letter of the command
            displayName = command[:1].capitalize() + command[1:]

            # If a command dosen't exist in the history list,
            # for some reason(eg. command renamed), do nothing.
            if displayName not in self.cmdDict:
                continue

            item = QtGui.QStandardItem(displayName)
            if os.path.isabs(self.cmdDict[displayName]['icon']) is True:
                iconPath = os.path.normpath(self.cmdDict[displayName]['icon'])
                item.setIcon(QtGui.QIcon(iconPath))
            else:
                item.setIcon(
                    QtGui.QIcon(":%s" % self.cmdDict[displayName]['icon']))
            self.historyModel.setItem(num, 0, item)

    def updateData(self):
        """ Update current completion data

        """

        # command completer
        currentText = self.LE.text()
        if currentText == "":
            self.LE.setCompleter(self.completer)

        # Set commands to case insensitive
        regExp = QtCore.QRegExp(
            self.LE.text(),
            QtCore.Qt.CaseInsensitive,
            QtCore.QRegExp.RegExp)
        self.filteredModel.setFilterRegExp(regExp)

    def tabCompletion(self):
        """ Complete commands by tab key

        """
        selections = self.completer.popup().selectedIndexes()
        currentModelIndex = self.completer.popup().currentIndex()
        if len(selections) == 0:
            # When no completion item is selected
            if currentModelIndex.row() == -1:
                modelIndex = self.filteredModel.index(0, 0)
                self.completer.popup().setCurrentIndex(modelIndex)
            else:
                self.completer.popup().setCurrentIndex(currentModelIndex)
        else:
            # When any of completions are selected
            modelIndex = selections[0]
            nextIndex = modelIndex.row() + 1
            newModelIndex = self.filteredModel.index(nextIndex, 0)
            self.completer.popup().setCurrentIndex(newModelIndex)

    def showHistory(self, *args):
        """ Show previously executed commands

        """

        self.LE.setCompleter(self.histCompleter)
        self.histCompleter.complete()

    def execute(self):
        # cmd = self.LE.text()
        if not self.LE.text():
            return

        try:
            cmd = self.cmdDict[self.LE.text()]['command']
        except KeyError:
            print("No such command.")
            return

        # Close gui first otherwise maya clashes(2017)
        self.close()

        try:
            f = getattr(self, "%s" % cmd)
            f()
            print("Rush command executed : %s" % cmd)

            # Add to repeatLast command so the comamnd can be repeatable
            # by G key
            cmdString = """python(\\"from rush import TempClass; TempClass.%s()\\")""" % cmd
            mel.eval("""callLastCommand("%s")""" % cmdString)

            # Add command to history data
            self.history.append(cmd)
            self.history.save()

        except AttributeError:
            pass


class Rush(OpenMaya.MPxCommand):

    def __init__(self):
        super(Rush, self).__init__()

        self.verbose = False

    def doIt(self, args):

        # Parse the arguments.
        argData = OpenMaya.MArgDatabase(self.syntax(), args)

        if argData.isFlagSet(kVerboseFlag):
            self.verbose = argData.flagArgumentBool(kVerboseFlag, 0)

        self.mw = Gui(getMayaWindow())
        self.mw.show()

        pos = QtGui.QCursor.pos()
        self.mw.move(
            pos.x() - (self.mw.width() / 2),
            pos.y() - (self.mw.height() / 2))

        self.mw.raise_()
        self.mw.activateWindow()

    def undoIt(self):
        pass

    def redoIt(self):
        pass

    @classmethod
    def isUndoable(cls):
        return False

    @staticmethod
    def cmdCreator():
        return Rush()


def syntaxCreator():
    """ Syntax creator

    Return:
        syntax (OpenMaya.MSyntax): return value

    """
    syntax = OpenMaya.MSyntax()
    syntax.addArg(OpenMaya.MSyntax.kString)
    syntax.addFlag(kVerboseFlag, kVerboseLongFlag, OpenMaya.MSyntax.kBoolean)
    return syntax


def maya_useNewAPI():
    """
    The presence of this function tells Maya that the plugin produces, and
    expects to be passed, objects created using the Maya Python API 2.0.
    """
    pass


def initializePlugin(mobject):
    """ Initialize the script plug-in

    Args:
        mobject (OpenMaya.MObject):

    """
    mplugin = OpenMaya.MFnPlugin(mobject, "Michitaka Inoue", "2.4.1", "Any")
    try:
        mplugin.registerCommand(kPluginCmdName, Rush.cmdCreator, syntaxCreator)
    except Exception:
        sys.stderr.write("Failed to register command: %s\n" % kPluginCmdName)
        raise


def uninitializePlugin(mobject):
    """ Uninitialize the script plug-in

    Args:
        mobject (OpenMaya.MObject):

    """
    mplugin = OpenMaya.MFnPlugin(mobject)
    try:
        mplugin.deregisterCommand(kPluginCmdName)
    except Exception:
        sys.stderr.write("Failed to unregister command: %s\n" % kPluginCmdName)
        raise
