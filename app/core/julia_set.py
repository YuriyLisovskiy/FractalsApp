from PIL import Image
from app import BASE_PATH

import multiprocessing as mp


class JuliaSet:
	""" A julia set of geometry (width x height) and iterations 'niter' """

	def __init__(self, w=1024, h=1024, max_iterations=256, handle_progress=None):
		self._w = w
		self._h = h
		self._max_iterations = max_iterations

		self._name = '{}/JuliaSetFractal.png'.format(BASE_PATH)

		self.progress_inc = 1.0 / h / w
		self.progress = self.progress_inc
		self._handle_progress = handle_progress

		self._pool = mp.Pool(mp.cpu_count())

	# Sequential
	def generate(self, zoom=1.0, x_off=0, y_off=0):
		print('Generating {}, please wait...'.format(self._name))

		image = Image.new('RGB', (self._w, self._h))
		pixels = image.load()

		# Pick some defaults for the real and imaginary constants
		# This determines the shape of the Julia set.
		c_real, c_imag = -0.7, 0.27

		for x in range(self._w):
			for y in range(self._h):
				# calculate the initial real and imaginary part of z,
				# based on the pixel location and zoom and position values
				zx = 1.5 * (x + x_off - self._w / 2) / (0.5 * zoom * self._w)
				zy = 1.0 * (y + y_off - self._h / 2) / (0.5 * zoom * self._h)

				k = None
				for i in range(self._max_iterations):
					k = i
					radius_sqr = zx * zx + zy * zy
					# Iterate till the point is outside
					# the circle with radius 2.
					if radius_sqr > 4:
						break
					# Calculate new positions
					zy, zx = 2.0 * zx * zy + c_imag, zx * zx - zy * zy + c_real

				if k is not None:
					color = (k >> 21) + (k >> 10) + k * 8
					pixels[x, y] = color

				self.progress += self.progress_inc
				self._handle_progress(self.progress)

		return image

	@staticmethod
	def _generate_row(row_num, w, h, max_iterations, zoom=1.0, x_off=0, y_off=0):
		c_real, c_imag = -0.7, 0.27
		pixels = []
		for x in range(w):
			# calculate the initial real and imaginary part of z,
			# based on the pixel location and zoom and position values
			zx = 1.5 * (x + x_off - w / 2) / (0.5 * zoom * w)
			zy = 1.0 * (row_num + y_off - h / 2) / (0.5 * zoom * h)

			k = None
			for i in range(max_iterations):
				k = i
				radius_sqr = zx * zx + zy * zy
				# Iterate till the point is outside
				# the circle with radius 2.
				if radius_sqr > 4:
					break
				# Calculate new positions
				zy, zx = 2.0 * zx * zy + c_imag, zx * zx - zy * zy + c_real

			if k is not None:
				color = (k >> 21) + (k >> 10) + k * 8
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
