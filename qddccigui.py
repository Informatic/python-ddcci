#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
PyQt4 DDC/CI GUI, python-ddcci example
"""

import sys
import ddcci
from PyQt4 import QtGui, QtCore
from PyKDE4.kdeui import KStatusNotifierItem

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

    scrollControl = controls[1]

    def __init__(self, busid):
        super(QDDCCIGui, self).__init__()

        self.device = ddcci.DDCCIDevice(busid)
        self.initUI()

    def initUI(self):
        grid = QtGui.QGridLayout()
        grid.setSpacing(2)

        for i, control in enumerate(self.controls):
            icon = QtGui.QLabel(self)
            icon.setPixmap(QtGui.QPixmap('assets/%s.png' % control['tag']))
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
            self.updateLabel(sld)

            sld.setMinimumWidth(150)
            sld.setFocusPolicy(QtCore.Qt.NoFocus)
            sld.valueChanged[int].connect(self.changeValue)

            control['slider'] = sld # FIXME circular reference

            grid.addWidget(sld, i+1, 2)

        self.setLayout(grid)
        self.setGeometry(300, 300, 280, 70)
        self.setWindowTitle('Qt DDC/CI Gui')
        self.show()
        
        if self.scrollControl:
            self.trayIcon = KStatusNotifierItem("qddccigui", self)
            self.trayIcon.setIconByPixmap(QtGui.QIcon(QtGui.QPixmap('assets/%s.png' % self.scrollControl['tag'])))
            self.trayIcon.scrollRequested[int,QtCore.Qt.Orientation].connect(self.scrollRequested)

    def changeValue(self, value, update=True):
        self.updateLabel(self.sender())
        if update: self.device.write(self.sender().control['id'], value)

    def scrollRequested(self, delta, orientation):
        new_value = self.scrollControl['slider'].value() + delta/24
        self.scrollControl['slider'].setValue(new_value)

    def updateLabel(self, sld):
        sld.label.setText('%d%%' % sld.value())

def main():
    app = QtGui.QApplication(sys.argv)
    argv = app.arguments()
    ex = QDDCCIGui(int(argv[1]) if len(argv) > 1 else 8)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
