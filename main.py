
import sys
import os
# Импортируем наш интерфейс из файла
from enum import Enum

from VideoState import VideoState
from view import MainWindow, OpenSaveWindow, SettingsWindow
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import qApp, QFileDialog, QStyleFactory, QColorDialog
from PyQt5.QtGui import QTextCursor, QImage, QPixmap, QStandardItemModel, QColor
from PyQt5.QtCore import pyqtSlot, Qt
from settings import Settings
from ThreadVideo import Thread
import matplotlib.ticker as ticker


#
# Класс настроек программы
#
class STGWindow(QtWidgets.QMainWindow):

    def __init__(self, parent_settings, parent=None, callback=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = SettingsWindow.Ui_MainWindow()
        self.ui.setupUi(self)

        self.color = QColor()

        self.parent_settings = parent_settings
        self.settings = Settings('config/settings.json')
        self.settings.load_json()

        self.ui.pushButton_2.clicked.connect(self.close)
        self.ui.pushButton.clicked.connect(self.apply)
        self.ui.pushButton_3.clicked.connect(self.ok)
        self.ui.pushButton_4.clicked.connect(self.rollback)
        self.ui.pushButton_5.clicked.connect(self.select_color)
        self.ui.pushButton_6.clicked.connect(self.apply_all)

        self.ui.checkBox.stateChanged.connect(self.change_enabled)
        self.ui.spinBox.valueChanged.connect(self.change_border_size)
        self.ui.spinBox_2.valueChanged.connect(self.change_text_size)
        self.ui.doubleSpinBox.valueChanged.connect(self.change_confidence)
        self.ui.lineEdit.textChanged.connect(self.change_color)

        self.ui.listWidget.itemClicked.connect(self.list_select)
        for dct in self.settings.CLASSES:
            self.ui.listWidget.insertItem(0, dct['name'])

        self.ui.listWidget.setCurrentRow(0)
        self.list_select(self.ui.listWidget.currentItem())

    def apply_all(self):
        rgb = self.color.getRgb()
        for info in self.settings.CLASSES:
            info['color'] = [rgb[0], rgb[1], rgb[2]]
            info['confidence'] = self.ui.doubleSpinBox.value()
            info['border_size'] = self.ui.spinBox.value()
            info['text_size'] = self.ui.spinBox_2.value()
            info['enabled'] = self.ui.checkBox.isChecked()

    def change_color(self, value):
        invert = QColor(255, 255, 255)
        invert.setRgb(invert.rgb()-self.color.rgb())
        self.ui.lineEdit.setStyleSheet("QWidget { background-color: %s; color: %s}" % (self.color.name(), invert.name()))

        name = self.ui.listWidget.currentItem().text()
        info = self.settings.getClassFromName(name)
        rgb = self.color.getRgb()
        info['color'] = [rgb[0], rgb[1], rgb[2]]

    def select_color(self):
        self.color = QColorDialog.getColor()
        self.ui.lineEdit.setText(self.color.name())

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


        self.color = QColor(info['color'][0], info['color'][1], info['color'][2])
        self.ui.lineEdit.setText(self.color.name())


#
# Класс начальных параметров программы
#
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
        self.ui.radioButton.toggled.connect(self.radiobutton1)
        self.ui.radioButton_2.toggled.connect(self.radiobutton2)
        self.ui.checkBox.stateChanged.connect(self.checkbutton)
        self.pathOpen = None
        self.pathSave = None
        self.ui.pushButton.clicked.connect(self.accept)
        self.callback = callback

        self.settings = Settings('config/settings.json')
        self.settings.load_json()
        self.load_settings()

    def load_settings(self):
        parameters = self.settings.PARAMETERS
        if parameters.get('is_vebcam'):
            self.ui.radioButton.setChecked(True)
        else:
            self.ui.radioButton_2.setChecked(True)
        self.ui.checkBox.setChecked(parameters.get('is_save'))
        self.ui.lineEdit.setText(parameters.get('path_open'))
        self.ui.lineEdit_2.setText(parameters.get('path_save'))

    def radiobutton1(self):
        self.ui.pushButton_2.setEnabled(False)
        self.ui.lineEdit.setEnabled(False)
        self.vebcam = True

    def radiobutton2(self):
        self.ui.pushButton_2.setEnabled(True)
        self.ui.lineEdit.setEnabled(True)
        self.vebcam = False

    def loadfile(self):
        self.pathOpen = QFileDialog.getOpenFileName(self, 'Open file', os.getcwd()+'/video', "Video files (*.mp4 *.avi)")[0]
        self.ui.lineEdit.setText(self.pathOpen)

    def savefile(self):
        self.pathSave = QFileDialog.getSaveFileName(self, 'Open file', os.getcwd()+'/video', "Video file (*.mp4);; Video file (*.avi)")[0]
        self.ui.lineEdit_2.setText(self.pathSave)

    def accept(self):
        self.settings.PARAMETERS['is_vebcam'] = self.ui.radioButton.isChecked()
        self.settings.PARAMETERS['is_save'] = self.ui.checkBox.isChecked()
        self.settings.PARAMETERS['path_open'] = self.ui.lineEdit.text()
        self.settings.PARAMETERS['path_save'] = self.ui.lineEdit_2.text()

        self.settings.save_json()

        self.callback(pathOpen=self.ui.lineEdit.text(), pathSave=self.ui.lineEdit_2.text(), vebcam=self.vebcam, save=self.ui.checkBox.isChecked())
        self.close()

    def checkbutton(self, state):
        #self.ui.checkBox.isChecked()
        if state:
            self.ui.pushButton_3.setEnabled(True)
            self.ui.lineEdit_2.setEnabled(True)
        else:
            self.ui.pushButton_3.setEnabled(False)
            self.ui.lineEdit_2.setEnabled(False)

#
# Класс основного окна программы
#
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
        self.model.setHeaderData(0, Qt.Horizontal, "Object")
        self.model.setHeaderData(1, Qt.Horizontal, "Count")
        self.ui.treeView.setModel(self.model)
        for i in range(22):
            self.model.insertRow(i)

        self.ui.MplWidget.canvas.axes.clear()
        self.ui.MplWidget.canvas.axes.set_title('Summary count')
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

        self.settings = Settings('config/settings.json')
        self.settings.load_json()
        self.accessLabelVideo = True
        self.pathOpen = None
        self.pathSave = None
        self.vebcam = None
        self.isSave = None
        self.stateVideo = VideoState.VIDEO_STOP
        self.prototx = 'config/MobileNetSSD_deploy.prototxt.txt'
        self.caffemodel = 'config/MobileNetSSD_deploy.caffemodel'
        self.action_trigger()

    def button_pause(self):
        self.stateVideo = VideoState.VIDEO_PAUSE

    def button_play(self):
        self.__start_playing_video()

    def button_stop(self):
        self.stateVideo = VideoState.VIDEO_STOP

    @pyqtSlot()
    def clear_image(self):
        self.ui.label.clear()

    def show_settings(self):
        self.myapp = STGWindow(self.settings, self)
        self.myapp.show()

    def __start_playing_video(self):
        if self.stateVideo == VideoState.VIDEO_STOP:
            if not self.pathOpen and not self.vebcam:
                QtWidgets.QMessageBox.about(self, "Error", "Source not specified")
                return
            self.stateVideo = VideoState.VIDEO_START

            self.th = Thread(self.prototx, self.caffemodel, self.pathOpen if not self.vebcam else 0, self.pathSave, self.settings, self)
            self.th.changePixmap.connect(self.set_image)
            self.th.printLog.connect(self.print_log)
            self.th.changeStatic.connect(self.set_statistic)
            self.th.clearPixmap.connect(self.clear_image)

            self.th.start()
            self.moveToThread(self.th)

        elif self.stateVideo == VideoState.VIDEO_PAUSE:
            self.stateVideo = VideoState.VIDEO_START
            # QtWidgets.QMessageBox.about(self, "Ошибка", "Сначала завершите текущий сеанс")

    def action_3_trigger(self):
        self.__start_playing_video()

    # Работа с графиком
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

    @pyqtSlot(str, bool)
    def print_log(self, value, is_clear: bool = False):
        self.ui.plainTextEdit.moveCursor(QTextCursor.End)
        if is_clear:
            self.ui.plainTextEdit.clear()
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
    # os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = "C:\\Users\\Александр\\PycharmProjects\\diplom\\venv\\Lib\\site-packages\\PyQt5\\Qt\\plugins\\platforms"
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.getcwd()+"\\venv\\Lib\\site-packages\\PyQt5\\Qt\\plugins\\platforms"
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('windowsvista'))
    myapp = MyWin()
    myapp.show()
    sys.exit(app.exec_())










