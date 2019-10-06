from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout


class Canvas(QWidget):

	def __init__(self, *args, **kwargs):
		super().__init__(None, flags=Qt.WindowFlags())
		self._label = QLabel(self)
		self._label.setGeometry(self.rect())
		layout = QVBoxLayout()
		layout.addWidget(self._label, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
		self.setLayout(layout)

	def draw(self, image):
		if image is not None:
			image = image.convert('RGB')
			data = image.tobytes('raw', 'RGB')
			qim = QImage(data, image.size[0], image.size[1], QImage.Format_RGB888)
			pix_map = QPixmap(qim)
			self._label.setPixmap(
				pix_map.scaled(self.width(), self.height(), Qt.KeepAspectRatio)
			)
		self.update()

	def clean(self):
		self.draw(None)
