from PyQt5 import QtWidgets
import configparser
from PyQt5.QtCore import *
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
import settings
import pickle
import publishmenu
import videoscriptcore
import client
import cv2
import ast
from VideoTypes import standardredditformat

scriptsMenu = None

class VideoEditor(QMainWindow):
    def __init__(self, videoscript, scriptmenu = None):
        QWidget.__init__(self)
        global scriptsMenu
        if scriptsMenu is None:
            scriptsMenu = scriptmenu
            self.scriptmenu = scriptsMenu
        else:
            self.scriptmenu = scriptsMenu

        self.videoScript = videoscript
        uic.loadUi("UI/scripteditor.ui", self)
        self.progressBar.setValue(0)
        self.setWindowTitle("Video no. %s" % videoscript.vidNo)
        #self.treeWidget.currentItemChanged.connect(self.changeSelected)
        #self.addToTree()
        self.addCommentInformation()
        self.mainCommentIndex = 0
        self.childCommentIndex = 0
        self.maxMainComments = len(self.videoScript.commentInformation)
        self.scriptWrapper = self.videoScript.scriptWrapper
        #self.returnSelected()
        self.keep.clicked.connect(self.keepComment)
        self.skip.clicked.connect(self.skipComment)
        self.updateColors()
        self.treeWidget.currentItemChanged.connect(self.setSelection)
        self.treeWidget.clicked.connect(self.setSelection)
        self.publish.clicked.connect(self.publishVideo)
        self.editrendervalues.triggered.connect(self.openValueEditor)
        self.nightmode.triggered.connect(self.toggleNightMode)
        self.safeClose = False
        self.nightMode = True
        self.setConstants()
        self.musicTypes.clear()
        self.musicTypes.addItems(client.musicTypes)
        self.musicTypes.currentTextChanged.connect(self.updateMusicType)
        #self.videoScript.music_type
        #self.videoPublishWindow = publishmenu.PublishMenu(self.videoScript)
        #self.videoPublishWindow.show()

    def updateMusicType(self):
        self.videoScript.music_type = self.musicTypes.currentText()

    def openValueEditor(self):
        self.valueEditor = ValueEditor(self.videoScript)
        self.valueEditor.onFinish.connect(self.updateValues)
        self.valueEditor.show()


    def updateValues(self):
        self.videoScript.videosettings = self.valueEditor.videoScript.videosettings
        self.updateDisplay()

    def setConstants(self):
        self.videoquestion.setText("Video Title: %s"%self.videoScript.title)
        self.avgwordsmin.setText("Avg Words/Min: %s"%settings.wordsPerMinute)
        self.timebetweencommentthread.setText("Time Between Comment Thread: %s"%settings.timeBetweenCommentThread)
        self.subreddit.setText("r/%s"%self.videoScript.sub_reddit)

    def updateColors(self):
        for x, mainComment in enumerate(self.scriptWrapper.scriptMap):
            self.selectedMainComment = None
            for y, subComments in enumerate(mainComment):
                if y == 0:
                    self.selectedMainComment = self.getTopLevelByName("Main Comment %s" % str(x))
                    if subComments is True:
                        self.selectedMainComment.setForeground(0, QtGui.QBrush(QtGui.QColor("green")))
                    else:
                        self.selectedMainComment.setForeground(0, QtGui.QBrush(QtGui.QColor("red")))
                else:
                    if subComments is True:
                        self.selectedMainComment.child(y - 1).setForeground(0, QtGui.QBrush(QtGui.QColor("green")))
                    else:
                        self.selectedMainComment.child(y - 1).setForeground(0, QtGui.QBrush(QtGui.QColor("red")))

    def setSelection(self):
        self.currentTreeWidget = self.treeWidget.currentItem()
        if self.currentTreeWidget.parent() is None:
            self.mainCommentIndex = int(str(self.currentTreeWidget.text(0)).split(" ")[2])
            self.childCommentIndex = 0
        else:
            self.mainCommentIndex = int(str(self.currentTreeWidget.parent().text(0)).split(" ")[2])
            self.childCommentIndex = int(str(self.currentTreeWidget.text(0)).split(" ")[2])

        self.updateColors()
        self.updateDisplay()

    def updateDisplay(self, keep=None):
        self.scriptWrapper.saveScriptWrapper()
        self.getCurrentWidget(self.mainCommentIndex, self.childCommentIndex).setForeground(0, QtGui.QBrush(QtGui.QColor("blue")))
        comment_wrapper = self.scriptWrapper.getCommentData(self.mainCommentIndex, self.childCommentIndex)
        comment_text = comment_wrapper.text
        comment_author = comment_wrapper.author
        comment_upvotes = comment_wrapper.upvotes

        self.updateTextView(comment_wrapper)
        self.textView.setText("Text View: %s"%(self.getCurrentWidget(self.mainCommentIndex, self.childCommentIndex).text(0)))
        self.author.setText("Author: %s"%comment_author)
        self.upvotes.setText("Upvotes: %s"%comment_upvotes)
        self.wordscomment.setText("Words: %s"%len(comment_text.split(" ")))
        self.characterscomment.setText("Characters: %s"%len(comment_text))
        self.commentthreads.setText("Comment Threads: %s"%self.scriptWrapper.getEditedCommentThreadsAmount())
        self.commentamount.setText("Comments: %s"%self.scriptWrapper.getEditedCommentAmount())
        self.totalwords.setText("Total Words: %s"%self.scriptWrapper.getEditedWordCount())
        self.estvidtime.setText("Estimated Video Time: %s"%self.scriptWrapper.getEstimatedVideoTime())
        self.totalcharacters.setText("Total Characters: %s"%self.scriptWrapper.getEditedCharacterCount())
        self.progressBar.setValue((self.scriptWrapper.getEstimatedVideoTime() / settings.recommendedLength) * 100)

        animation_group_on_change = [self.commentamount, self.commentthreads, self.totalwords, self.estvidtime, self.totalaudiolines]
        if keep is True:
            self.animategroup(animation_group_on_change, QtGui.QColor(0, 128, 0))
        elif keep is False:
            self.animategroup(animation_group_on_change, QtGui.QColor(255, 0, 0))

        try:
            stillframe = standardredditformat.StandardReddit("standardredditformat", self.videoScript.videosettings).stillImage(self.scriptWrapper.getCommentInformation(self.mainCommentIndex, self.childCommentIndex))
            height, width, channel = stillframe.shape
            bytesPerLine = 3 * width
            qImg = QImage(stillframe.data, width, height, bytesPerLine, QImage.Format_RGB888).scaled(self.imageArea.frameGeometry().width(), self.imageArea.frameGeometry().height(), QtCore.Qt.KeepAspectRatio)
            self.imageArea.setPixmap(QPixmap(qImg))
        except Exception:
            self.imageArea.setText("Rendering Error for Post, skipping")
            print("Need to log this comment")
            self.skipComment()
        self.musicCat.setText("Music Category: %s" % self.videoScript.music_type)




    def getCurrentWidget(self, x, y):
        if y == 0:
            currentlySelected = self.getTopLevelByName("Main Comment %s" % x)
        else:
            currentMainComment = self.getTopLevelByName("Main Comment %s" % x)
            currentlySelected = currentMainComment.child(y - 1)

        return currentlySelected


    def skipComment(self):
        for i in range(self.childCommentIndex, self.scriptWrapper.getCommentAmount(self.mainCommentIndex), 1):
            self.scriptWrapper.skip(self.mainCommentIndex, i)
        self.updateColors()
        self.nextMainComment()
        self.updateDisplay(False)

    def keepComment(self):
        self.scriptWrapper.setCommentData(self.mainCommentIndex, self.childCommentIndex, self.commentDisplay.toPlainText())
        for i in range(self.childCommentIndex, -1, -1):
            self.scriptWrapper.keep(self.mainCommentIndex, i)
        self.updateColors()
        self.incrimentSelection()
        self.updateDisplay(True)

    def incrimentSelection(self):
        if self.childCommentIndex == self.scriptWrapper.getCommentAmount(self.mainCommentIndex) - 1:
            if not self.mainCommentIndex + 1 > self.scriptWrapper.getCommentThreadsAmount() - 1:
                self.mainCommentIndex += 1
                self.childCommentIndex = 0
        else:
            self.childCommentIndex += 1


    def nextMainComment(self):
        if not self.mainCommentIndex + 1 > self.scriptWrapper.getCommentThreadsAmount() - 1:
            self.childCommentIndex = 0
            self.mainCommentIndex += 1
            self.selectedMainComment = self.getTopLevelByName("Main Comment %s" % str(self.mainCommentIndex))

    def updateTextView(self, commentwrapper):
        text = commentwrapper.text
        self.commentDisplay.clear()
        self.commentDisplay.append(text)

    def addCommentInformation(self):
        self.treeWidget.clear()
        for i, commentTree in enumerate(self.videoScript.commentInformation):
            treeParentName = "Main Comment %s"%str(i)
            self.addTopLevel(treeParentName)
            if i == 0:
                self.selectedMainComment = self.getTopLevelByName(treeParentName)

            for i, comment in enumerate(commentTree):
                if not i == 0:
                    self.addChild(treeParentName, "Top Comment %s"%str(i))
        self.treeWidget.expandToDepth(0)

    def getAllTopLevel(self):
        items = []
        for index in range(self.treeWidget.topLevelItemCount()):
            items.append(self.treeWidget.topLevelItem(index))
        return items

    def addTopLevel(self, name):
        if self.getTopLevelByName(name) is None:
            QTreeWidgetItem(self.treeWidget, [name])

    def addChild(self, parent, child):
        self.addTopLevel(parent)
        QTreeWidgetItem(self.getTopLevelByName(parent), [child])

    def getTopLevelByName(self, name):
        for index in range(self.treeWidget.topLevelItemCount()):
            item = self.treeWidget.topLevelItem(index)
            if item.text(0) == name:
                return item
        return None

    def animategroup(self, widgets, color):
        self.changeanimationgroup = QParallelAnimationGroup()
        for widget in widgets:
            effect = QtWidgets.QGraphicsColorizeEffect(widget)
            widget.setGraphicsEffect(effect)
            anim = QtCore.QPropertyAnimation(effect, b"color")
            anim.setDuration(500)
            anim.setStartValue(QtGui.QColor(0, 0, 0))
            anim.setKeyValueAt(0.25, color)
            anim.setEndValue(QtGui.QColor(0, 0, 0))
            self.changeanimationgroup.addAnimation(anim)
        self.changeanimationgroup.start()


    def publishVideo(self):
        self.checkVideo()


    def checkVideo(self):
        if not self.scriptWrapper.isRecommendedLength():
            message = "Time: %s < %s" % (self.scriptWrapper.getEstimatedVideoTime(), settings.recommendedLength)
            self.createPopup("Warning", QMessageBox.Information, "Estimated Video Time Under 10 Minutes", message)
            if self.retMsg == QMessageBox.Ignore:
                self.videoScript.final_script = self.scriptWrapper.convertToFormat()
                self.safeClose = True
                self.close()
                self.videoPublishWindow = publishmenu.PublishMenu(self.videoScript)
                self.videoPublishWindow.show()
            else:
                pass
        else:
            self.videoScript.final_script = self.scriptWrapper.convertToFormat()
            self.safeClose = True
            self.close()
            self.videoPublishWindow = publishmenu.PublishMenu(self.videoScript)
            self.videoPublishWindow.show()

    def createPopup(self, messagetype, icon, text, message):
        self.msg = QMessageBox()
        self.msg.setIcon(icon)
        self.msg.setText(text)
        self.msg.setInformativeText(message)
        self.msg.setWindowTitle(messagetype)
        if messagetype == "Warning":
            self.msg.setStandardButtons(QMessageBox.Ignore | QMessageBox.Cancel)
        else:
            self.msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Close)

        self.retMsg = self.msg.exec_()

    def toggleNightMode(self):
        self.nightMode = not self.nightMode
        if self.nightMode:
            self.videoScript.videosettings['comment_text_color'] = [215, 218, 220]
            self.videoScript.videosettings['background_color'] = [25, 25, 25]
            self.videoScript.videosettings['author_details_color'] = [74, 175, 238]
        else:
            self.videoScript.videosettings['comment_text_color'] = [0, 0, 0]
            self.videoScript.videosettings['background_color'] = [255, 255, 255]
            self.videoScript.videosettings['author_details_color'] = [25, 25, 25]

        self.updateDisplay()

    def closeEvent(self, event):
        if not self.safeClose:
            client.quitEditing(self.videoScript.scriptno)
            scriptsMenu.isEditing = False




class ValueEditor(QMainWindow):
    onFinish = pyqtSignal()
    def __init__(self, videoscript):
        QWidget.__init__(self)
        uic.loadUi("UI/videotypeeditor.ui", self)
        self.videoScript = videoscript
        self.setWindowTitle("Video Settings")
        self.oldSettings = self.videoScript.videosettings
        nice_layout = ("\n\n".join("{}: {}".format("'%s'"%k, v) for k, v in videoscript.videosettings.items()))

        self.resetDefault.clicked.connect(self.setDefaultSettings)
        self.textEdit.setText(str(nice_layout))
        self.cancel.clicked.connect(self.cancelUpdate)
        self.ok.clicked.connect(self.completeChange)
        self.update.clicked.connect(self.setValues)

    def setDefaultSettings(self):
        self.videoScript.loadDefaultVideoSettings()
        self.onFinish.emit()
        nice_layout = ("\n\n".join("{}: {}".format("'%s'"%k, v) for k, v in self.videoScript.videosettings.items()))
        self.textEdit.setText(str(nice_layout))

    def cancelUpdate(self):
        self.videoScript.videosettings = self.oldSettings
        self.onFinish.emit()
        self.close()

    def completeChange(self):
        self.setValues()
        self.close()

    def setValues(self):
        try:
            text = self.textEdit.toPlainText()
            #for line in text.split("\n", ""):
            line_by_line = text.split("\n\n")
            dict_string = "{"
            for i, line in enumerate(line_by_line):
                split = line.split(": ")
                keyword = split[0]
                value = split[1]
                value_evaluated = ast.literal_eval(value)
                if i == len(line_by_line) - 1:
                    dict_string += "%s : %s}" % (keyword, value_evaluated)
                else:
                    dict_string += "%s : %s, " % (keyword, value_evaluated)
            new_settings = (ast.literal_eval(dict_string))
        except Exception as e:
            base_text = "Formatting of the inputs is broken!. \n"

            self.createPopup("Error", QMessageBox.Critical, "Couldn't convert to settings dict.", "%s%s"%(base_text, e))
            return
        self.videoScript.videosettings = new_settings
        self.onFinish.emit()


    def createPopup(self, messagetype, icon, text, message):
        self.msg = QMessageBox()
        self.msg.setIcon(icon)
        self.msg.setText(text)
        self.msg.setInformativeText(message)
        self.msg.setWindowTitle(messagetype)
        if messagetype == "Error":
            self.msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Close)
        self.retMsg = self.msg.exec_()




