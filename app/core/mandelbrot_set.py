from PIL import Image
from app import BASE_PATH

import multiprocessing as mp


class MandelbrotSet:

	def __init__(self, w=1024, h=1024, max_iterations=256, handle_progress=None):
		self._w = w
		self._h = h
		self._max_iterations = max_iterations

		self._name = '{}/MandelbrotSetFractal.png'.format(BASE_PATH)

		self.progress_inc = 1.0 / h / w
		self.progress = self.progress_inc
		if handle_progress is None:
			raise ValueError('handle_progrees is not set')
		self._handle_progress = handle_progress

		self._pool = mp.Pool(mp.cpu_count())

	# Sequential
	def generate(self, zoom=1.0, x_off=0, y_off=0):
		# print('Generating {}, please wait...'.format(self._name))

		image = Image.new('RGB', (self._w, self._h))
		pixels = image.load()

		for x in range(self._w):
			for y in range(self._h):
				# calculate the initial real and imaginary part of z,
				# based on the pixel location and zoom and position values
				# We use (x-3*w/4) instead of (x-w/2) to fully visualize
				# the fractal along the x-axis

				zx = 1.5 * (x + x_off - 3 * self._w / 4) / (0.5 * zoom * self._w)
				zy = 1.0 * (y + y_off - self._h / 2) / (0.5 * zoom * self._h)

				z = complex(zx, zy)
				c = complex(0, 0)

				k = None
				for i in range(self._max_iterations):
					k = i
					if abs(c) > 4:
						break
					# Iterate till the point c is outside
					# the circle with radius 2.
					# Calculate new positions
					c = c ** 2 + z

				self.progress += self.progress_inc
				self._handle_progress(self.progress)

				if k is not None:
					color = (k << 21) + (k << 10) + k * 8
					# color = (k << 4) + (k << 12) + k * 2
					pixels[x, y] = color

		return image

	@staticmethod
	def _generate_row(row_num, w, h, max_iterations, zoom=1.0, x_off=0, y_off=0):
		pixels = []
		for x in range(w):
			zx = 1.5 * (x + x_off - 3 * w / 4) / (0.5 * zoom * w)
			zy = 1.0 * (row_num + y_off - h / 2) / (0.5 * zoom * h)

			z = complex(zx, zy)
			c = complex(0, 0)

			k = None
			for i in range(max_iterations):
				k = i
				if abs(c) > 4:
					break
				# Iterate till the point c is outside
				# the circle with radius 2.
				# Calculate new positions
				c = c ** 2 + z

			if k is not None:
				color = (k << 21) + (k << 10) + k * 8
				# color = (k << 4) + (k << 12) + k * 2
				pixels.append(color)
		return row_num, pixels

	# Parallel
	def generate_(self, zoom=1.0, x_off=0, y_off=0):
		print('Generating {}, please wait...'.format(self._name))

		image = Image.new('RGB', (self._w, self._h))
		pixels = image.load()

		results = [self._pool.apply(
			self._generate_row, args=(y, self._w, self._h, self._max_iterations, zoom, x_off, y_off)
		) for y in range(self._h)]

		self._pool.close()

		for x in range(self._w):
			for y in range(len(results)):
				pixels[x, y] = results[y][1][x]

		return image
