import os

from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import pyqtSignal, QThread, Qt
import cv2
import time
import numpy as np
from settings import Settings


class Thread(QThread):
    changePixmap = pyqtSignal(QImage)
    changeStatic = pyqtSignal(dict, int)
    printLog = pyqtSignal(str)
    clearPixmap = pyqtSignal()


    prototxt = None
    size_text = None

    def __init__(self, prototxt: str, model: str, pathopen: str, pathsave: str, settings: Settings, *args):
        super(Thread, self).__init__(*args)

        self.CLASSES = settings.CLASSES
        self.total_counts = {key['name']: {'color': key['color'], 'counts': []} for key in self.CLASSES}
        self.prototxt = prototxt
        self.model = model
        self.pathopen = pathopen
        self.pathsave = pathsave
        self.size_text = settings.size_text
        self.overlay_frequency = settings.overlay_frequency


    def run(self):
        self.printLog.emit("[INFO] Загрузка моделей...")
        net = cv2.dnn.readNetFromCaffe(self.prototxt, self.model)

        self.printLog.emit("[INFO] Инициализация видеопотока...")
        cap = cv2.VideoCapture(self.pathopen)

        count_frames = 0
        currient_overlay_frequency = 0
        time.sleep(2.0)
        if self.pathsave:
            frame_width = int(cap.get(3))
            frame_height = int(cap.get(4))
            filename, format = os.path.splitext(self.pathsave)
            if format == '.avi':
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
            elif format == '.mp4':
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(self.pathsave, fourcc, 5, (frame_width, frame_height))

        while cap.isOpened():

            if self.parent().stateVideo == 1 and self.parent().accessLabelVideo:
                ret, frame = cap.read()
                if ret:
                    self.parent().accessLabelVideo = False
                    (h, w) = frame.shape[:2]
                    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)

                    if currient_overlay_frequency == 0:
                        currient_overlay_frequency = self.overlay_frequency
                        net.setInput(blob)
                        detections = net.forward()

                    count_frames += 1
                    currient_overlay_frequency -= 1

                    for k in self.total_counts.keys():
                        self.total_counts[k]['counts'].append(0)

                    for i in np.arange(0, detections.shape[2]):
                        confidence = detections[0, 0, i, 2]
                        idx = int(detections[0, 0, i, 1])
                        try:
                            if self.CLASSES[idx].get('enabled') and self.CLASSES[idx].get('confidence') < confidence:
                                name = self.CLASSES[idx].get('name')
                                color = self.CLASSES[idx].get('color')
                                self.total_counts[name]['counts'][-1] += 1
                                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                                (startX, startY, endX, endY) = box.astype("int")

                                label = "{}: {:.1f}%".format(name, confidence * 100)
                                cv2.rectangle(frame, (startX, startY), (endX, endY), color, self.CLASSES[idx].get('border_size'))
                                y = startY - 15 if startY - 15 > 15 else startY + 15
                                cv2.putText(frame, label, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, self.size_text, color, self.CLASSES[idx].get('text_size'))
                        except IndexError:
                            pass

                    if self.pathsave:
                        out.write(frame)

                    rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    convertToQtFormat = QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0], QImage.Format_RGB888)
                    p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)

                    self.changeStatic.emit(self.total_counts, count_frames)
                    self.changePixmap.emit(p)

            elif self.parent().stateVideo == 0:
                self.clearPixmap.emit()
                break

        if self.pathsave:
            out.release()
        cap.release()
        cv2.destroyAllWindows()
