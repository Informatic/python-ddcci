#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
PyQt4 DDC/CI GUI, python-ddcci example
"""

import sys
import ddcci
import os
from PyQt4 import QtGui, QtCore
from PyKDE4.kdeui import KStatusNotifierItem

script_path = os.path.dirname(os.path.realpath(os.path.abspath(__file__)))
assets_path = os.path.join(script_path, 'assets')


def asset(name):
    return os.path.join(assets_path, name)


class QDDCCIGui(QtGui.QWidget):
    controls = [{
        'tag': 'brightness',
        'name': 'Brightness',
        'id': 0x10,
        }, {
        'tag': 'contrast',
        'name': 'Constrast',
        'id': 0x12,
        }]

    scroll_control = controls[1]

    def __init__(self, busid):
        super(QDDCCIGui, self).__init__()

        self.device = ddcci.DDCCIDevice(busid)
        self.init_ui()

    def init_ui(self):
        grid = QtGui.QGridLayout()
        grid.setSpacing(2)

        for i, control in enumerate(self.controls):
            icon = QtGui.QLabel(self)
            icon.setPixmap(QtGui.QPixmap(asset('%s.png' % control['tag'])))
            icon.setToolTip(control['name'])
            grid.addWidget(icon, i+1, 0)

            label = QtGui.QLabel(self)
            label.setMinimumWidth(32)
            label.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
            grid.addWidget(label, i+1, 1)

            sld = QtGui.QSlider(QtCore.Qt.Horizontal, self)

            sld.label = label
            sld.control = control

            value, max_value = self.device.read(control['id'], True)

            sld.setMinimum(0)
            sld.setMaximum(max_value)
            sld.setValue(value)
            self.update_label(sld)

            sld.setMinimumWidth(150)
            sld.setFocusPolicy(QtCore.Qt.NoFocus)
            sld.valueChanged[int].connect(self.change_value)

            control['slider'] = sld  # FIXME circular reference

            grid.addWidget(sld, i+1, 2)

        self.setLayout(grid)
        self.setGeometry(300, 300, 280, 70)
        self.setWindowTitle('Qt DDC/CI Gui')
        self.show()

        if self.scroll_control:
            self.tray_icon = KStatusNotifierItem("qddccigui", self)
            self.tray_icon.setIconByPixmap(QtGui.QIcon(QtGui.QPixmap(
                asset('%s.png' % self.scroll_control['tag']))))
            self.tray_icon.scrollRequested[int, QtCore.Qt.Orientation].\
                connect(self.scroll_requested)

    def change_value(self, value, update=True):
        self.update_label(self.sender())

        if update:
            self.device.write(self.sender().control['id'], value)

    def scroll_requested(self, delta, orientation):
        new_value = self.scroll_control['slider'].value() + delta/24
        self.scroll_control['slider'].setValue(new_value)

    def update_label(self, sld):
        sld.label.setText('%d%%' % sld.value())


def main():
    app = QtGui.QApplication(sys.argv)
    argv = app.arguments()
    ex = QDDCCIGui(int(argv[1]) if len(argv) > 1 else 8)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
