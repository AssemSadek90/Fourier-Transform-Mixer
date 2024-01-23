import sys
import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as qtc
import PyQt5.QtGui as qtg
from matplotlib.widgets import RectangleSelector
from Image import Image
from main_layout import Ui_MainWindow
from ClickableLabel import ClickableLabel
import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    '%(levelname)s:%(name)s:%(asctime)s - %(message)s')

file_handler = logging.FileHandler('log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.show()

        self.images = {
            '1': {
                'original': self.ui.image_1_original,
                'filtered': self.ui.image_1_after_filter,
                'picker': self.ui.image_1_pick
            },
            '2': {
                'original': self.ui.image_2_original,
                'filtered': self.ui.image_2_after_filter,
                'picker': self.ui.image_2_pick
            },
            '3': {
                'original': self.ui.image_3_original,
                'filtered': self.ui.image_3_after_filter,
                'picker': self.ui.image_3_pick
            },
            '4': {
                'original': self.ui.image_4_original,
                'filtered': self.ui.image_4_after_filter,
                'picker': self.ui.image_4_pick
            }
        }

        self.img = {}

        self.modes = {'Output 1': '', 'Output 2': ''}

        self.output_channels = {
            'Output 1': self.ui.output_1,
            'Output 2': self.ui.output_2
        }

        self.output_channels_controlers = {
            '': {
                'select1': '',
                'select2': '',
                'select3': '',
                'select4': '',
                'slider1': 0,
                'slider2': 0,
                'slider3': 0,
                'slider4': 0,
                'type1': '',
                'type2': '',
                'type3': '',
                'type4': '',
                'percentage1': 0,
                'percentage2': 0,
                'percentage3': 0,
                'percentage4': 0,
            },
            'Output 1': {
                'select1': '',
                'select2': '',
                'select3': '',
                'select4': '',
                'slider1': 0,
                'slider2': 0,
                'slider3': 0,
                'slider4': 0,
                'type1': '',
                'type2': '',
                'type3': '',
                'type4': '',
                'percentage1': 0,
                'percentage2': 0,
                'percentage3': 0,
                'percentage4': 0,
            },
            'Output 2': {
                'select1': '',
                'select2': '',
                'select3': '',
                'select4': '',
                'slider1': 0,
                'slider2': 0,
                'slider3': 0,
                'slider4': 0,
                'type1': '',
                'type2': '',
                'type3': '',
                'type4': '',
                'percentage1': 0,
                'percentage2': 0,
                'percentage3': 0,
                'percentage4': 0,
            },
        }

        self.output_complementary = {
            '': ['', 'Magnitude', 'Phase', 'Real', 'Imaginary'],
            'Magnitude': ['Phase', 'Magnitude'],
            'Phase': ['Magnitude', 'Phase'],
            'Real': ['Imaginary', 'Real'],
            'Imaginary': ['Real', 'Imaginary'],
            'Uniform Magnitude': ['Phase', 'Uniform Phase'],
            'Uniform Phase': ['Magnitude', 'Uniform Magnitude'],
        }

        self.available_images = {
            '': ''
        }

        self.enables = {
            '': [self.ui.component_1_select, self.ui.component_2_select, self.ui.component_3_select, self.ui.component_4_select,
                 self.ui.component_1_percentage, self.ui.component_1_slider, self.ui.component_1_type,
                 self.ui.component_2_percentage, self.ui.component_2_slider, self.ui.component_2_type,
                 self.ui.component_3_percentage, self.ui.component_3_slider, self.ui.component_3_type,
                 self.ui.component_4_percentage, self.ui.component_4_slider, self.ui.component_4_type],
            'output-select': [self.ui.component_1_select, self.ui.component_2_select, self.ui.component_3_select, self.ui.component_4_select],
            'select1': [self.ui.component_1_percentage, self.ui.component_1_type],
            'select2': [self.ui.component_2_percentage, self.ui.component_2_type],
            'select3': [self.ui.component_3_percentage, self.ui.component_3_type],
            'select4': [self.ui.component_4_percentage, self.ui.component_4_type],
            'type1': [self.ui.component_1_slider],
            'type2': [self.ui.component_2_slider],
            'type3': [self.ui.component_3_slider],
            'type4': [self.ui.component_4_slider]
        }

        self.current_output_channel = None

        self.ui.action_exit.triggered.connect(self.close)

        self.ui.action_open_image_1.triggered.connect(
            lambda: self.open_image(self.images['1'], 1))
        self.ui.action_open_image_2.triggered.connect(
            lambda: self.open_image(self.images['2'], 2))
        self.ui.action_open_image_3.triggered.connect(
            lambda: self.open_image(self.images['3'], 3))
        self.ui.action_open_image_4.triggered.connect(
            lambda: self.open_image(self.images['4'], 4))

        self.ui.image_1_pick.currentIndexChanged.connect(
            lambda: self.display_component(self.img['Image 1'], 1))
        self.ui.image_2_pick.currentIndexChanged.connect(
            lambda: self.display_component(self.img['Image 2'], 2))
        self.ui.image_3_pick.currentIndexChanged.connect(
            lambda: self.display_component(self.img['Image 3'], 3))
        self.ui.image_4_pick.currentIndexChanged.connect(
            lambda: self.display_component(self.img['Image 4'], 4))

        self.ui.output_select.currentIndexChanged.connect(
            lambda: self.pick_mixer_output())

        self.ui.component_1_select.currentIndexChanged.connect(
            lambda: self.select_enable('select1', self.ui.component_1_select.currentText()))
        self.ui.component_2_select.currentIndexChanged.connect(
            lambda: self.select_enable('select2', self.ui.component_2_select.currentText()))
        self.ui.component_3_select.currentIndexChanged.connect(
            lambda: self.select_enable('select3', self.ui.component_3_select.currentText()))
        self.ui.component_4_select.currentIndexChanged.connect(
            lambda: self.select_enable('select4', self.ui.component_4_select.currentText()))

        self.ui.component_1_slider.sliderReleased.connect(
            lambda: self.mixer('slider1', str(self.ui.component_1_slider.value())))
        self.ui.component_2_slider.sliderReleased.connect(
            lambda: self.mixer('slider2', str(self.ui.component_2_slider.value())))
        self.ui.component_3_slider.sliderReleased.connect(
            lambda: self.mixer('slider3', str(self.ui.component_3_slider.value())))
        self.ui.component_4_slider.sliderReleased.connect(
            lambda: self.mixer('slider4', str(self.ui.component_4_slider.value())))

        self.ui.component_1_percentage.valueChanged.connect(lambda: self.change_image(
            'percentage1', str(self.ui.component_1_percentage.value())))
        self.ui.component_2_percentage.valueChanged.connect(lambda: self.change_image(
            'percentage2', str(self.ui.component_2_percentage.value())))
        self.ui.component_3_percentage.valueChanged.connect(lambda: self.change_image(
            'percentage3', str(self.ui.component_3_percentage.value())))
        self.ui.component_4_percentage.valueChanged.connect(lambda: self.change_image(
            'percentage4', str(self.ui.component_4_percentage.value())))

        self.ui.component_1_type.currentIndexChanged.connect(
            lambda: self.component_1_conplementary())
        self.ui.component_1_type.currentIndexChanged.connect(
            lambda: self.select_enable('type1', str(self.ui.component_1_type.currentText())))
        self.ui.component_2_type.currentIndexChanged.connect(
            lambda: self.select_enable('type2', str(self.ui.component_2_type.currentText())))
        self.ui.component_3_type.currentIndexChanged.connect(
            lambda: self.select_enable('type3', str(self.ui.component_3_type.currentText())))
        self.ui.component_4_type.currentIndexChanged.connect(
            lambda: self.select_enable('type4', str(self.ui.component_4_type.currentText())))

        self.ui.image_1_original.clicked.connect(
            lambda: self.open_image(self.images['1'], 1))
        self.ui.image_2_original.clicked.connect(
            lambda: self.open_image(self.images['2'], 2))
        self.ui.image_3_original.clicked.connect(
            lambda: self.open_image(self.images['3'], 3))
        self.ui.image_4_original.clicked.connect(
            lambda: self.open_image(self.images['4'], 4))

        self.ui.image_1_original.dragged.connect(
            lambda: self.modify_brightness('Image 1', 1.02))
        self.ui.image_2_original.dragged.connect(
            lambda: self.modify_brightness('Image 2', 1.02))
        self.ui.image_3_original.dragged.connect(
            lambda: self.modify_brightness('Image 3', 1.02))
        self.ui.image_4_original.dragged.connect(
            lambda: self.modify_brightness('Image 4', 1.02))

        self.ui.image_1_original.dragged_downwards.connect(
            lambda: self.modify_brightness('Image 1', 0.98))
        self.ui.image_2_original.dragged_downwards.connect(
            lambda: self.modify_brightness('Image 2', 0.98))
        self.ui.image_3_original.dragged_downwards.connect(
            lambda: self.modify_brightness('Image 3', 0.98))
        self.ui.image_4_original.dragged_downwards.connect(
            lambda: self.modify_brightness('Image 4', 0.98))

        self.ui.region_slider.valueChanged[int].connect(
            lambda: self.region_apply())

    def new_instance(self) -> None:
        self.child_window = MainWindow()
        self.child_window.show()

    def display_images(self):
        for key, image_data in self.img.items():
            image_widget = image_data['widgets']
            image = image_data['image']
            component = image_widget['picker'].currentText()

            image_widget['original'].setPixmap(image.get_pixmap().scaled(
                225, 225, aspectRatioMode=qtc.Qt.KeepAspectRatio, transformMode=qtc.Qt.SmoothTransformation))

            image_widget['filtered'].setPixmap(image.get_component_pixmap(component).scaled(
                225, 225, aspectRatioMode=qtc.Qt.KeepAspectRatio, transformMode=qtc.Qt.SmoothTransformation))

    def modify_brightness(self, image_key, factor):
        if image_key in self.img:
            self.img[image_key]["image"].increase_brightness(factor)

            self.display_images()

    def modify_contrast(self, image_key, factor):
        if image_key in self.img:
            self.img[image_key]["image"].increase_contrast(factor)

            self.display_images()

    def open_image(self, imageWidget: dict, channel: int) -> None:
        image = Image()
        image.to_grayscale()
        image.resize()
        if not image.path:
            return

        image_key = f'Image {channel}'

        if image_key not in self.img:
            self.img[image_key] = {'image': image, 'widgets': imageWidget}

            if image_key not in self.available_images:
                self.available_images[image_key] = image_key
                self.append_outputs(channel=channel)
        else:
            self.img[image_key]["image"] = image
            self.img[image_key]["widgets"] = imageWidget

        imageWidget['original'].setPixmap(image.get_pixmap().scaled(
            225, 225, aspectRatioMode=qtc.Qt.KeepAspectRatio, transformMode=qtc.Qt.SmoothTransformation))
        imageWidget['picker'].setDisabled(False)
        self.ui.output_select.setDisabled(False)
        self.ui.output_select.setCurrentText("Output 1")
        if channel == 1:
            self.ui.component_1_select.setCurrentText(image_key)
            self.ui.component_2_select.setCurrentText(image_key)
            self.ui.component_3_select.setCurrentText(image_key)
            self.ui.component_4_select.setCurrentText(image_key)

            pass
        elif channel == 2:
            self.ui.component_2_select.setCurrentText(image_key)
            self.ui.component_3_select.setCurrentText(image_key)
            self.ui.component_4_select.setCurrentText(image_key)

            pass
        elif channel == 3:
            self.ui.component_3_select.setCurrentText(image_key)
            self.ui.component_4_select.setCurrentText(image_key)
            pass
        elif channel == 4:
            self.ui.component_4_select.setCurrentText(image_key)

            pass

    def append_outputs(self, channel: str = '') -> None:
        self.ui.component_1_select.addItem(f'Image {channel}')
        self.ui.component_2_select.addItem(f'Image {channel}')
        self.ui.component_3_select.addItem(f'Image {channel}')
        self.ui.component_4_select.addItem(f'Image {channel}')

    def display_component(self, imageWidget: dict, key: int) -> None:
        component = imageWidget['widgets']['picker'].currentText()
        imageWidget['widgets']['filtered'].setPixmap(imageWidget['image'].get_component_pixmap(component).scaled(
            225, 225, aspectRatioMode=qtc.Qt.KeepAspectRatio, transformMode=qtc.Qt.SmoothTransformation))
        try:
            os.remove('test.png')
        except:
            pass
        self.ui.inner_select.setDisabled(False)
        self.ui.outer_select.setDisabled(False)
        self.ui.region_slider.setDisabled(False)

    def region_apply(self):
        percentage = self.ui.region_slider.value()
        inner = self.ui.inner_select.isChecked()

        for key, image_data in self.img.items():
            image = image_data['image']
            component = image_data['widgets']['picker'].currentText()
            image.filter(inner, percentage, component)

        self.display_images()

    def pick_mixer_output(self) -> None:
        self.current_output_channel = self.ui.output_select.currentText()
        self.ui.component_1_slider.setValue(int(
            self.output_channels_controlers[self.ui.output_select.currentText()]['slider1']))
        self.ui.component_1_percentage.setValue(int(
            self.output_channels_controlers[self.ui.output_select.currentText()]['percentage1']))
        self.ui.component_1_select.setCurrentText(
            self.output_channels_controlers[self.ui.output_select.currentText()]['select1'])
        self.ui.component_1_type.setCurrentText(
            self.output_channels_controlers[self.ui.output_select.currentText()]['type1'])

        self.ui.component_2_slider.setValue(int(
            self.output_channels_controlers[self.ui.output_select.currentText()]['slider2']))
        self.ui.component_2_percentage.setValue(int(
            self.output_channels_controlers[self.ui.output_select.currentText()]['percentage2']))
        self.ui.component_2_select.setCurrentText(
            self.output_channels_controlers[self.ui.output_select.currentText()]['select2'])
        self.ui.component_2_type.setCurrentText(
            self.output_channels_controlers[self.ui.output_select.currentText()]['type2'])

        self.ui.component_3_slider.setValue(int(
            self.output_channels_controlers[self.ui.output_select.currentText()]['slider3']))
        self.ui.component_3_percentage.setValue(int(
            self.output_channels_controlers[self.ui.output_select.currentText()]['percentage3']))
        self.ui.component_3_select.setCurrentText(
            self.output_channels_controlers[self.ui.output_select.currentText()]['select3'])
        self.ui.component_3_type.setCurrentText(
            self.output_channels_controlers[self.ui.output_select.currentText()]['type3'])

        self.ui.component_4_slider.setValue(int(
            self.output_channels_controlers[self.ui.output_select.currentText()]['slider4']))
        self.ui.component_4_percentage.setValue(int(
            self.output_channels_controlers[self.ui.output_select.currentText()]['percentage4']))
        self.ui.component_4_select.setCurrentText(
            self.output_channels_controlers[self.ui.output_select.currentText()]['select4'])
        self.ui.component_4_type.setCurrentText(
            self.output_channels_controlers[self.ui.output_select.currentText()]['type4'])

        if self.ui.output_select.currentText() != '':
            self.set_mixer_components_disabled(
                self.enables['output-select'], False)
        else:
            self.set_mixer_components_disabled(
                self.enables['output-select'], False)

    def set_mixer_components_disabled(self, components: list, logic: bool) -> None:
        for component in components:
            component.setDisabled(logic)

    def select_enable(self, component: str, value: str):
        self.change_image(component, value)
        if value != '':
            self.set_mixer_components_disabled(self.enables[component], False)
        else:
            self.set_mixer_components_disabled(self.enables[component], True)

    def change_image(self, component: str, value: str) -> None:
        self.output_channels_controlers[self.current_output_channel][component] = value

    def component_1_conplementary(self):
        self.ui.component_2_type.clear()
        self.ui.component_2_type.addItems(
            self.output_complementary[self.ui.component_1_type.currentText()])
        self.ui.component_2_type.update()

        self.ui.component_3_type.clear()
        self.ui.component_3_type.addItems(
            self.output_complementary[self.ui.component_1_type.currentText()])
        self.ui.component_3_type.update()

        self.ui.component_4_type.clear()
        self.ui.component_4_type.addItems(
            self.output_complementary[self.ui.component_1_type.currentText()])
        self.ui.component_4_type.update()

        self.change_image('type1', self.ui.component_1_type.currentText())

    def mixer(self, slider: str, sliderValue: str) -> None:
        self.change_image(slider, sliderValue)

        channel_1_ratio = float(
            self.output_channels_controlers[self.current_output_channel]['slider1']) / 100
        channel_2_ratio = float(
            self.output_channels_controlers[self.current_output_channel]['slider2']) / 100
        channel_3_ratio = float(
            self.output_channels_controlers[self.current_output_channel]['slider3']) / 100
        channel_4_ratio = float(
            self.output_channels_controlers[self.current_output_channel]['slider4']) / 100

        image_1 = self.output_channels_controlers[self.current_output_channel]['select1']
        image_2 = self.output_channels_controlers[self.current_output_channel]['select2']
        image_3 = self.output_channels_controlers[self.current_output_channel]['select3']
        image_4 = self.output_channels_controlers[self.current_output_channel]['select4']

        type1 = self.output_channels_controlers[self.current_output_channel]['type1']
        type2 = self.output_channels_controlers[self.current_output_channel]['type2']
        type3 = self.output_channels_controlers[self.current_output_channel]['type3']
        type4 = self.output_channels_controlers[self.current_output_channel]['type4']

        if image_1 == "" or image_2 == "" or image_3 == "" or image_4 == "" or type1 == "" or type2 == "" or type3 == "" or type4 == "":
            return

        try:
            if (type1 in ['Magnitude', 'Phase', 'Uniform Magnitude', 'Uniform Phase']
                    and type2 in ['Magnitude', 'Phase', 'Uniform Magnitude', 'Uniform Phase']):
                self.modes[self.current_output_channel] = 'mag-phase'
            elif (type1 in ['Real', 'Imaginary'] and type2 in ['Real', 'Imaginary']):
                self.modes[self.current_output_channel] = 'real-imag'

            else:
                print('Error')
                return
            self.outImage = self.img[image_1]['image'].mix(
                self.img[image_2]['image'],
                self.img[image_3]['image'],
                self.img[image_4]['image'],
                self.output_channels_controlers[self.current_output_channel]['type1'],
                self.output_channels_controlers[self.current_output_channel]['type2'],
                self.output_channels_controlers[self.current_output_channel]['type3'],
                self.output_channels_controlers[self.current_output_channel]['type4'],
                channel_1_ratio,
                channel_2_ratio,
                channel_3_ratio,
                channel_4_ratio,
                self.modes[self.current_output_channel]
            )

            self.output_channels[self.current_output_channel].setPixmap(self.outImage.scaled(
                350, 350, aspectRatioMode=qtc.Qt.KeepAspectRatio, transformMode=qtc.Qt.SmoothTransformation))

        except:
            pass

        try:
            os.remove('test.png')
        except:
            pass


def main_window():
    app = qtw.QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main_window()
