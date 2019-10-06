from datetime import datetime

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
	QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox, QComboBox, QLineEdit, QProgressBar
)
from PyQt5.QtCore import Qt, QThreadPool

from app import BASE_PATH
from app.settings import APP_MIN_WIDTH, APP_MIN_HEIGHT, APP_NAME, APP_FONT
from app.canvas import Canvas
from app.widgets import QPushButton
from app.utility import Worker

from app.core.mandelbrot_set import MandelbrotSet
from app.core.julia_set import JuliaSet


class MainWindow(QMainWindow):

	IMAGE_SIZES = ['200x150', '400x300', '640x480', '800x600', '1024x768', '1200x900', '1600x900']
	MAX_ITERATIONS_VALUES = [25, 50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000]
	FRACTALS_NAMES = ['Mandelbrot Set', 'Julia Set']

	def __init__(self):
		super().__init__(None, Qt.WindowFlags())

		self.window().setWindowTitle(APP_NAME)
		self.setMinimumWidth(APP_MIN_WIDTH)
		self.setMinimumHeight(APP_MIN_HEIGHT)

		self.thread_pool = QThreadPool()

		self._canvas = Canvas()

		self._btn_draw = QPushButton(self.tr('Draw'), 90, 30, self._draw_set)

		self._btn_save = QPushButton(self.tr('Save'), 90, 30, self._save_canvas)
		self._btn_save.setEnabled(False)

		self._progress = QProgressBar(self)
		self._progress.setGeometry(200, 80, 250, 20)

		self._fractals = [
			(MandelbrotSet, '{}/MandelbrotSetFractal.png'.format(BASE_PATH)),
			(JuliaSet, '{}/JuliaSetFractal.png'.format(BASE_PATH))
		]

		self._start_calculation_time = None

		self._current_fractal = 0
		self._image_size = (800, 600)
		self._max_iterations = 1000
		self._x_offset = 0
		self._y_offset = 0
		self._zoom = 1

		self._fractal_cb = None
		self._image_size_cb = None
		self._max_iterations_cb = None
		self._x_offset_le = None
		self._y_offset_le = None
		self._zoom_le = None

		self._current_image = None

		main_widget = self.init_main_widget()
		self.setCentralWidget(main_widget)

		self.setFont(QFont('SansSerif', APP_FONT))

	def _save_canvas(self):
		if self._current_image is not None:
			self._current_image[1].save(self._current_image[0], 'PNG')
			self._popup_success('Image \'{}\' is saved.'.format(self._current_image[0]))

	def _handle_progress(self, progress):
		self._progress.setValue(progress * 100)

	def _draw_set(self):
		self._btn_save.setEnabled(False)
		worker = Worker(self._draw_set_fn, self._fractals[self._current_fractal])
		worker.signals.error.connect(self._popup_err)
		worker.signals.param_success.connect(self._draw_set_finished)
		self.thread_pool.start(worker)

	def _draw_set_finished(self, result):
		later = datetime.now()
		self._current_image = result
		self._canvas.draw(result[1])
		self._btn_save.setEnabled(True)
		self._popup_success('Time: {} sec'.format((later - self._start_calculation_time).total_seconds()))

	def _draw_set_fn(self, fractal):
		self._start_calculation_time = datetime.now()
		cls = fractal[0]
		ms = cls(self._image_size[0], self._image_size[1], self._max_iterations, self._handle_progress)
		return fractal[1], ms.generate(self._zoom, self._x_offset, self._y_offset)

	def _add_input(self, parent, title, values, changed):
		widget = QWidget(self, flags=self.windowFlags())
		layout = QVBoxLayout(widget)
		layout.addWidget(QLabel(title), 0, Qt.AlignLeft)

		cb = QComboBox()
		cb.addItems([str(x) for x in values])
		cb.currentIndexChanged.connect(changed)

		layout.addWidget(cb, 0, Qt.AlignLeft)
		parent.addWidget(widget, 0, Qt.AlignHCenter)

		return cb

	def _add_input_line(self, parent, title, value, changed):
		widget = QWidget(self, flags=self.windowFlags())
		layout = QVBoxLayout(widget)
		layout.addWidget(QLabel(title), 0, Qt.AlignLeft)

		le = QLineEdit()
		le.setText(str(value))
		le.textChanged.connect(changed)

		layout.addWidget(le, 0, Qt.AlignLeft)
		parent.addWidget(widget, 0, Qt.AlignHCenter)

		return le

	def init_main_widget(self):
		layout = QVBoxLayout()

		# noinspection PyArgumentList
		layout.addWidget(self._canvas)

		container = QWidget(self, flags=self.windowFlags())
		container.setStyleSheet('background-color: lightgray;')
		container.setFixedHeight(100)

		tools = QHBoxLayout(container)

		self._fractal_cb = self._add_input(tools, 'Fractal:', self.FRACTALS_NAMES, self._fractal_changed)
		self._fractal_cb.setCurrentIndex(self._current_fractal)

		self._image_size_cb = self._add_input(tools, 'Image size:', self.IMAGE_SIZES, self._image_size_changed)
		self._image_size_cb.setCurrentIndex(self.IMAGE_SIZES.index('x'.join([str(x) for x in self._image_size])))

		self._max_iterations_cb = self._add_input(
			tools, 'Max iterations:', self.MAX_ITERATIONS_VALUES, self._max_iterations_changed
		)
		self._max_iterations_cb.setCurrentIndex(self.MAX_ITERATIONS_VALUES.index(self._max_iterations))

		self._x_offset_le = self._add_input_line(tools, 'X-offset', self._x_offset, self._x_offset_changed)
		self._y_offset_le = self._add_input_line(tools, 'Y-offset', self._y_offset, self._y_offset_changed)
		self._zoom_le = self._add_input_line(tools, 'Zoom', self._zoom, self._zoom_changed)

		tools.addWidget(self._btn_draw, 0, Qt.AlignHCenter)
		tools.addWidget(self._btn_save, 0, Qt.AlignHCenter)

		# noinspection PyArgumentList
		layout.addWidget(container)

		# noinspection PyArgumentList
		layout.addWidget(self._progress)

		widget = QWidget(flags=self.windowFlags())
		widget.setLayout(layout)
		return widget

	def _image_size_changed(self, i):
		size = self._image_size_cb.itemText(i).split('x')
		self._image_size = tuple([int(x) for x in size])

	def _max_iterations_changed(self, i):
		self._max_iterations = int(self._max_iterations_cb.itemText(i))

	def _x_offset_changed(self, text):
		if len(text) > 0 and text != '-':
			self._x_offset = float(text)

	def _y_offset_changed(self, text):
		if len(text) > 0 and text != '-':
			self._y_offset = float(text)

	def _zoom_changed(self, text):
		if len(text) > 0 and text != '-':
			self._zoom = float(text)

	def _fractal_changed(self, i):
		self._current_fractal = i

	def _popup_err(self, err):
		err_msg = 'Input data error\nCheck inputs'
		if err is not None:
			if isinstance(err, str):
				err_msg = err
			else:
				err_msg = err[1]
		msg_box = QMessageBox()
		msg_box.warning(self, 'Input data error', err_msg, QMessageBox.Ok)
		self._btn_draw.setEnabled(True)

	def _popup_success(self, msg):
		msg_box = QMessageBox()
		msg_box.information(self, 'Success', msg, QMessageBox.Ok)
