from PIL import Image
from app import BASE_PATH


class JuliaSet:
	""" A julia set of geometry (width x height) and iterations 'niter' """

	def __init__(self, w=1024, h=1024, max_iterations=256):
		self._w = w
		self._h = h

		self._name = '{}/JuliaSetFractal.png'.format(BASE_PATH)

		self._max_iterations = max_iterations

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

		image.save(self._name, 'PNG')
		return self._name
