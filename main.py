
import sys
import os
# Импортируем наш интерфейс из файла
import MainWindow
import OpenSaveWindow
import SettingsWindow
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import qApp, QFileDialog, QStyleFactory
from PyQt5.QtGui import QTextCursor, QImage, QPixmap, QStandardItemModel
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QThread, Qt
from settings import Settings
from ThreadVideo import Thread
import matplotlib.ticker as ticker


class STGWindow(QtWidgets.QMainWindow):

    def __init__(self, parent_settings, parent=None, callback=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = SettingsWindow.Ui_MainWindow()
        self.ui.setupUi(self)

        self.parent_settings = parent_settings
        self.settings = Settings('settings.json')
        self.settings.load_json()

        self.ui.pushButton_2.clicked.connect(self.close)
        self.ui.pushButton.clicked.connect(self.apply)
        self.ui.pushButton_3.clicked.connect(self.ok)
        self.ui.pushButton_4.clicked.connect(self.rollback)

        self.ui.checkBox.stateChanged.connect(self.change_enabled)
        self.ui.spinBox.valueChanged.connect(self.change_border_size)
        self.ui.spinBox_2.valueChanged.connect(self.change_text_size)
        self.ui.doubleSpinBox.valueChanged.connect(self.change_confidence)

        self.ui.listWidget.itemClicked.connect(self.list_select)
        for dct in self.settings.CLASSES:
            self.ui.listWidget.insertItem(0, dct['name'])

        self.ui.listWidget.setCurrentRow(0)
        self.list_select(self.ui.listWidget.currentItem())

    def change_confidence(self, value):
        name = self.ui.listWidget.currentItem().text()
        info = self.settings.getClassFromName(name)
        info['confidence'] = value

    def change_border_size(self, value):
        name = self.ui.listWidget.currentItem().text()
        info = self.settings.getClassFromName(name)
        info['border_size'] = value

    def change_text_size(self, value):
        name = self.ui.listWidget.currentItem().text()
        info = self.settings.getClassFromName(name)
        info['text_size'] = value

    def change_enabled(self):
        name = self.ui.listWidget.currentItem().text()
        info = self.settings.getClassFromName(name)
        info['enabled'] = self.ui.checkBox.isChecked()

    def rollback(self):
        self.settings.default()
        self.list_select(self.ui.listWidget.currentItem())

    def ok(self):
        self.apply()
        self.close()

    def apply(self):
        self.settings.save_json()
        self.parent_settings.load_json()

    def list_select(self, item):
        info = self.settings.getClassFromName(item.text())
        self.ui.checkBox.setChecked(info['enabled'])
        self.ui.spinBox.setValue(info['border_size'])
        self.ui.spinBox_2.setValue(info['text_size'])
        self.ui.doubleSpinBox.setValue(info['confidence'])


class OSWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None, callback=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.vebcam = True
        self.ui = OpenSaveWindow.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton_3.setEnabled(False)
        self.ui.lineEdit_2.setEnabled(False)
        self.ui.pushButton_2.setEnabled(False)
        self.ui.lineEdit.setEnabled(False)
        self.ui.pushButton_2.clicked.connect(self.loadfile)
        self.ui.pushButton_3.clicked.connect(self.savefile)
        self.ui.radioButton.clicked.connect(self.radiobutton1)
        self.ui.radioButton_2.clicked.connect(self.radiobutton2)
        self.ui.checkBox.stateChanged.connect(self.checkbutton)
        self.pathOpen = 0
        self.pathSave = None
        self.ui.pushButton.clicked.connect(self.accept)
        self.callback = callback

    def radiobutton1(self):
        self.ui.pushButton_2.setEnabled(False)
        self.ui.lineEdit.setEnabled(False)
        self.vebcam = True

    def radiobutton2(self):
        self.ui.pushButton_2.setEnabled(True)
        self.ui.lineEdit.setEnabled(True)
        self.vebcam = False

    def loadfile(self):
        self.pathOpen = QFileDialog.getOpenFileName(self, 'Open file', 'C:\\Users\\Александр\\PycharmProjects\\diplom', "Viseo files (*.mp4 *.avi)")[0]
        self.ui.lineEdit.setText(self.pathOpen)

    def savefile(self):
        self.pathSave = QFileDialog.getSaveFileName(self, 'Open file', 'c:\\', "Viseo file (*.mp4);; Viseo file (*.avi)")[0]
        self.ui.lineEdit_2.setText(self.pathSave)

    def accept(self):
        self.callback(pathOpen=self.pathOpen, pathSave=self.pathSave, vebcam=self.vebcam, save=self.ui.checkBox.isChecked())
        self.close()

    def checkbutton(self, int):
        if self.ui.checkBox.isChecked():
            self.ui.pushButton_3.setEnabled(True)
            self.ui.lineEdit_2.setEnabled(True)
        else:
            self.ui.pushButton_3.setEnabled(False)
            self.ui.lineEdit_2.setEnabled(False)


class MyWin(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = MainWindow.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.action.triggered.connect(self.action_trigger)
        self.ui.action_5.triggered.connect(self.show_settings)
        self.ui.action_3.triggered.connect(self.action_3_trigger)
        self.ui.action_2.triggered.connect(qApp.quit)

        self.ui.toolButton_2.clicked.connect(self.button_pause)
        self.ui.toolButton.clicked.connect(self.button_play)
        self.ui.toolButton_3.clicked.connect(self.button_stop)

        self.model = QStandardItemModel(0, 2, parent)
        self.model.setHeaderData(0, Qt.Horizontal, "Объект")
        self.model.setHeaderData(1, Qt.Horizontal, "Кол-во совпадений")
        self.ui.treeView.setModel(self.model)
        for i in range(22):
            self.model.insertRow(i)

        self.ui.MplWidget.canvas.axes.clear()
        self.ui.MplWidget.canvas.axes.set_title('Суммарное количество')
        self.ui.MplWidget.canvas.axes.set_facecolor('0.93')
        self.ui.MplWidget.canvas.axes.grid(True, color='1.0', linestyle='-')
        self.ui.MplWidget.canvas.axes.spines['top'].set_color('white')
        self.ui.MplWidget.canvas.axes.spines['bottom'].set_color('white')
        self.ui.MplWidget.canvas.axes.spines['right'].set_color('white')
        self.ui.MplWidget.canvas.axes.spines['left'].set_color('white')
        self.ui.MplWidget.canvas.axes.ticklabel_format(style='plain', axis='x', useOffset=False)

        for axis in [self.ui.MplWidget.canvas.axes.xaxis, self.ui.MplWidget.canvas.axes.yaxis]:
            axis.set_major_locator(ticker.MaxNLocator(integer=True))

        self.ui.MplWidget.canvas.draw()

        self.settings = Settings('settings.json')
        self.settings.load_json()
        self.accessLabelVideo = True
        self.pathOpen = None
        self.pathSave = None
        self.vebcam = None
        self.isSave = None
        self.stateVideo = 0
        self.prototx = 'MobileNetSSD_deploy.prototxt.txt'
        self.caffemodel = 'MobileNetSSD_deploy.caffemodel'

    def button_pause(self):
        self.stateVideo = 2

    def button_play(self):
        self.stateVideo = 1

    def button_stop(self):
        self.stateVideo = 0

    @pyqtSlot()
    def clear_image(self):
        self.ui.label.clear()

    def show_settings(self):
        self.myapp = STGWindow(self.settings, self)
        self.myapp.show()

    def action_3_trigger(self):
        if self.stateVideo == 0:
            if not self.pathOpen and not self.vebcam:
                QtWidgets.QMessageBox.about(self, "Ошибка", "Не указан источник")
                return
            self.stateVideo = 1

            self.th = Thread(self.prototx, self.caffemodel, self.pathOpen, self.pathSave, self.settings, self)
            self.th.changePixmap.connect(self.set_image)
            self.th.printLog.connect(self.print_log)
            self.th.changeStatic.connect(self.set_statistic)
            self.th.clearPixmap.connect(self.clear_image)

            self.th.start()
            self.moveToThread(self.th)

        else:
            QtWidgets.QMessageBox.about(self, "Ошибка", "Сначала завершите текущий сеанс")

    @pyqtSlot(dict, int)
    def set_statistic(self, total_visits: dict, count_frames: int):
        self.ui.MplWidget.canvas.axes.clear()
        self.ui.MplWidget.canvas.axes.grid(True)

        for dct in total_visits.values():
            if any(item != 0 for item in dct['counts'][-100:]):
                color = tuple([(1/255)*i for i in dct['color']])
                self.ui.MplWidget.canvas.axes.plot(dct['counts'][-100:], color=color)
        for axis in [self.ui.MplWidget.canvas.axes.xaxis, self.ui.MplWidget.canvas.axes.yaxis]:
            axis.set_major_locator(ticker.MaxNLocator(integer=True))
        self.ui.MplWidget.canvas.draw()

        i = 0
        for k, v in total_visits.items():
            self.model.setData(self.model.index(i, 0), k)
            self.model.setData(self.model.index(i, 1), v['counts'][-1])
            i += 1

    @pyqtSlot(QImage)
    def set_image(self, image):
        self.ui.label.setPixmap(QPixmap.fromImage(image))
        self.accessLabelVideo = True

    @pyqtSlot(str)
    def print_log(self, value):
        self.ui.plainTextEdit.moveCursor(QTextCursor.End)
        if type(value) is dict:
            for key, value in value.items():
                self.ui.plainTextEdit.insertPlainText('\n[%s]: %s' % (key, value))
        else:
            self.ui.plainTextEdit.insertPlainText('\n'+str(value))

    def action_trigger(self):
        self.myapp = OSWindow(self, self.getvar)
        self.myapp.show()

    def getvar(self, **kwargs):
        self.vebcam = kwargs.get('vebcam', None)
        self.isSave = kwargs.get('save', None)
        self.pathSave = kwargs.get('pathSave', None)
        self.pathOpen = kwargs.get('pathOpen', None)


if __name__ == "__main__":
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = "C:\\Users\\Александр\\PycharmProjects\\diplom\\venv\\Lib\\site-packages\\PyQt5\\Qt\\plugins\\platforms"
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion'))
    myapp = MyWin()
    myapp.show()
    sys.exit(app.exec_())










