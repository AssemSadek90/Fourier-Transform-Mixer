import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as qtc
import PyQt5.QtGui as qtg
import cv2
import matplotlib.pyplot as plt
import numpy as np
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    '%(levelname)s:%(name)s:%(asctime)s - %(message)s')

file_handler = logging.FileHandler('log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


class Image:
    def __init__(self):
        self.path = qtw.QFileDialog.getOpenFileName(
            None, 'Load Image', './Test Input Images', "Image File(*.png *.jpg *.jpeg)")[0]
        if self.path:
            self.raw_data = plt.imread(self.path)
            self.format = self.path.split('.')[-1]
            if (self.format in ['jpg', 'jpeg',]):
                self.raw_data = self.raw_data.astype('float32')
                self.raw_data /= 255
            self.shape = self.raw_data.shape
            self.WIDTH = self.shape[0]
            self.HEIGHT = self.shape[1]
            self.fftpre = np.fft.fft2(self.raw_data)
            self.fft = np.fft.fftshift(self.fftpre)
            self.magnitude = np.abs(self.fft)
            self.phase = np.angle(self.fft)
            self.real = np.real(self.fft)
            self.imaginary = np.imag(self.fft)
            self.pixmap = qtg.QPixmap(self.path)
            self.components = {
                '': '',
                'Magnitude': self.magnitude,
                'Phase': self.phase,
                'Real': self.real,
                'Imaginary': self.imaginary,
            }

    def increase_brightness(self, factor):
        if len(self.raw_data.shape) == 3:  # Colored image
            self.raw_data *= factor
            # self.raw_data = np.clip(self.raw_data, 0, 1)
        else:  # Grayscale image
            self.raw_data *= factor
            # self.raw_data = np.clip(self.raw_data, 0, 1)

        self.update_components()

        if len(self.raw_data.shape) == 3:  # Colored image
            image_data = np.clip(self.raw_data * 255, 0, 255).astype(np.uint8)
            qimage = qtg.QImage(image_data.data, self.WIDTH,
                                self.HEIGHT, self.WIDTH * 3, qtg.QImage.Format_RGB888)
        else:  # Grayscale image
            image_data = np.clip(self.raw_data * 255, 0, 255).astype(np.uint8)
            qimage = qtg.QImage(image_data.data, self.WIDTH,
                                self.HEIGHT, self.WIDTH, qtg.QImage.Format_Grayscale8)

        self.pixmap = qtg.QPixmap.fromImage(qimage)

    def resize(self):
        new_width = 225
        new_height = 225

        # Resize the raw_data to the new dimensions
        self.raw_data = cv2.resize(self.raw_data, (new_width, new_height))

        # Update image properties
        self.shape = self.raw_data.shape
        self.WIDTH = self.shape[0]
        self.HEIGHT = self.shape[1]

        # Recalculate FFT components
        self.update_components()

        # Update the pixmap
        if len(self.raw_data.shape) == 3:  # Colored image
            image_data = np.clip(self.raw_data * 255, 0, 255).astype(np.uint8)
            qimage = qtg.QImage(image_data.data, self.WIDTH,
                                self.HEIGHT, self.WIDTH * 3, qtg.QImage.Format_RGB888)
        else:  # Grayscale image
            image_data = np.clip(self.raw_data * 255, 0, 255).astype(np.uint8)
            qimage = qtg.QImage(image_data.data, self.WIDTH,
                                self.HEIGHT, self.WIDTH, qtg.QImage.Format_Grayscale8)

        self.pixmap = qtg.QPixmap.fromImage(qimage)

    def increase_contrast(self, factor):
        mean_value = np.mean(self.raw_data)
        self.raw_data = mean_value + factor * (self.raw_data - mean_value)

        if (self.format in ['jpg', 'jpeg']):
            self.raw_data = np.clip(self.raw_data, 0, 1)

        self.update_components()

        image_data = np.clip(self.raw_data * 255, 0, 255).astype(np.uint8)
        qimage = qtg.QImage(image_data.data, self.WIDTH,
                            self.HEIGHT, self.WIDTH * 3, qtg.QImage.Format_RGB888)

        self.pixmap = qtg.QPixmap.fromImage(qimage)

    def to_grayscale(self):
        if len(self.raw_data.shape) == 3:
            # r, g, b = self.raw_data[:, :, 0], self.raw_data[:,
            #                                                 :, 1], self.raw_data[:, :, 2]
            # gray = (0.2989 * r + 0.5870 * g + 0.1140 * b)
            # self.raw_data = gray
            self.raw_data = cv2.cvtColor(self.raw_data, cv2.COLOR_BGR2GRAY)

            self.update_components()
            image_data = np.clip(self.raw_data * 255, 0, 255).astype(np.uint8)
            qimage = qtg.QImage(image_data.data, self.WIDTH,
                                self.HEIGHT, self.WIDTH, qtg.QImage.Format_Grayscale8)

            self.pixmap = qtg.QPixmap.fromImage(qimage)

    def filter(self, inner, percentage, component_type):
        if percentage >= 98 or percentage <= 2:
            self.update_components()
            return

        self.update_components()
        rows, cols = self.magnitude.shape

        region_size = int(min(rows, cols) * percentage / 100)

        if inner:
            mask = np.zeros((rows, cols), dtype=bool)
        else:
            mask = np.ones((rows, cols), dtype=bool)

        center_row, center_col = rows // 2, cols // 2
        if inner:
            mask[center_row - region_size // 2: center_row + region_size // 2,
                 center_col - region_size // 2: center_col + region_size // 2] = True
        else:
            mask[center_row - region_size // 2: center_row + region_size // 2,
                 center_col - region_size // 2: center_col + region_size // 2] = False

        filtered_component = self.components[component_type].copy()

        filtered_component[~mask] = 0

        self.components[component_type] = filtered_component

    def get_pixmap(self):
        return self.pixmap

    def compare(self, image2: 'Image') -> bool:
        return self.WIDTH == image2.WIDTH and self.HEIGHT == image2.HEIGHT

    def mix(self, image_2: 'Image', image_3: 'Image', image_4: 'Image', type_1: str, type_2: str, type_3: str, type_4: str,
            component_1_ratio: float, component_2_ratio: float, component_3_ratio: float, component_4_ratio: float,
            mode: str) -> qtg.QPixmap:
        first = self.get_component(type_1, component_1_ratio)
        second = image_2.get_component(type_2, component_2_ratio)
        third = image_3.get_component(type_3, component_3_ratio)
        fourth = image_4.get_component(type_4, component_4_ratio)

        first = np.where(first == 0, 1, first)
        second = np.where(second == 0, 1, second)
        third = np.where(third == 0, 1, third)
        fourth = np.where(fourth == 0, 1, fourth)
        if mode == 'mag-phase':
            construct = np.real(np.fft.ifft2(np.fft.ifftshift(np.multiply(
                np.multiply(np.multiply(first, second), third), fourth))))
        elif mode == 'real-imag':
            construct = np.real(np.fft.ifft2(
                np.fft.ifftshift(first + second + third + fourth)))
        else:
            raise ValueError(f"Invalid mode: {mode}")

        if np.max(construct) > 1.0:
            construct /= np.max(construct)

        plt.imsave('test.png', np.abs(construct), cmap='gray')
        return qtg.QPixmap('test.png')

    def get_component(self, type: str, ratio: float) -> np.ndarray:
        if type == "Magnitude":
            return self.components[type] * ratio
        elif type == "Phase":
            return np.exp(1j * self.components[type] * ratio)
        elif type == "Real":
            return self.components[type] * ratio
        elif type == "Imaginary":
            return 1j * self.components[type] * ratio

    def get_component_pixmap(self, component: str) -> qtg.QPixmap:
        # component_val = np.dot(self.components[component][...,:3], [0.2989, 0.5870, 0.1140])
        if component != '':
            # component_val = np.dot(self.components[component][..., :3], [
            #                        0.2125, 0.7154, 0.0721])
            component_val = self.components[component]

        if component in ['Magnitude', 'Real']:
            plt.imsave('test.png', np.log(
                np.abs(component_val) + 1e-10), cmap='gray')
        elif component == 'Phase':
            plt.imsave('test.png', (np.abs(component_val)), cmap='gray')
        elif component == 'Imaginary':
            component_tmp = np.where(
                component_val > 1.0e-10, component_val, 1.0e-10)
            result = np.where(component_val > 1.0e-10,
                              np.log10(component_tmp), -10)
            plt.imsave('test.png', (np.abs(result)), cmap='gray')
        else:
            return qtg.QPixmap("./assets/placeholder.png")
        return qtg.QPixmap('test.png')

    def update_components(self):
        self.fftpre = np.fft.fft2(self.raw_data)
        self.fft = np.fft.fftshift(self.fftpre)
        self.magnitude = np.abs(self.fft)
        self.phase = np.angle(self.fft)
        self.real = np.real(self.fft)
        self.imaginary = np.imag(self.fft)

        self.components = {
            '': '',
            'Magnitude': self.magnitude,
            'Phase': self.phase,
            'Real': self.real,
            'Imaginary': self.imaginary
        }
