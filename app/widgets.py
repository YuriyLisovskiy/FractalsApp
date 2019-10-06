from PyQt5.QtWidgets import QPushButton as qPushButton


class QPushButton(qPushButton):

	def __init__(self, title, width, height, function, *__args):
		super().__init__(*__args)
		self.setText(title)
		self.setFixedWidth(width)
		self.setFixedHeight(height)

		# noinspection PyUnresolvedReferences
		self.clicked.connect(function)
