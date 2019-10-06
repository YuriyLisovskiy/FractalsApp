from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

from PIL.ImageQt import ImageQt


class Canvas(QWidget):

	def __init__(self, *args, **kwargs):
		super().__init__(None, flags=Qt.WindowFlags())
		self._label = QLabel(self)
		layout = QVBoxLayout()
		layout.addWidget(self._label, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
		self.setLayout(layout)

	def draw(self, image):
		if image is not None:
			# pix_map = QPixmap().fromImage(ImageQt(image))
			im = image.convert("RGB")
			data = im.tobytes("raw", "RGB")
			qim = QImage(data, im.size[0], im.size[1], QImage.Format_RGB888)
			# pix_map = QPixmap(image)
			pix_map = QPixmap(qim)
			self._label.setPixmap(
				pix_map.scaled(self.width(), self.height(), Qt.KeepAspectRatio)
			)
		self.update()

	def clean(self):
		self.draw(None)
