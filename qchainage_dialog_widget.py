# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qchainage_dialog_widget.ui'
#
# Created: Fri Oct 12 09:16:51 2012
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(380, 322)
        Dialog.setMinimumSize(QtCore.QSize(380, 200))
        self.gridLayout_2 = QtGui.QGridLayout(Dialog)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.labelSelectLayer = QtGui.QLabel(Dialog)
        self.labelSelectLayer.setObjectName(_fromUtf8("labelSelectLayer"))
        self.gridLayout_2.addWidget(self.labelSelectLayer, 0, 0, 1, 1)
        self.labelDistance = QtGui.QLabel(Dialog)
        self.labelDistance.setObjectName(_fromUtf8("labelDistance"))
        self.gridLayout_2.addWidget(self.labelDistance, 1, 0, 1, 1)
        self.distanceSpinBox = QtGui.QDoubleSpinBox(Dialog)
        self.distanceSpinBox.setObjectName(_fromUtf8("distanceSpinBox"))
        self.gridLayout_2.addWidget(self.distanceSpinBox, 1, 1, 1, 1)
        self.labelLayerName = QtGui.QLabel(Dialog)
        self.labelLayerName.setObjectName(_fromUtf8("labelLayerName"))
        self.gridLayout_2.addWidget(self.labelLayerName, 2, 0, 1, 1)
        self.layerNameLine = QtGui.QLineEdit(Dialog)
        self.layerNameLine.setObjectName(_fromUtf8("layerNameLine"))
        self.gridLayout_2.addWidget(self.layerNameLine, 2, 1, 1, 1)
        self.chainageGroupBox = QtGui.QGroupBox(Dialog)
        self.chainageGroupBox.setObjectName(_fromUtf8("chainageGroupBox"))
        self.gridLayout = QtGui.QGridLayout(self.chainageGroupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.selectAllRadioButton = QtGui.QRadioButton(self.chainageGroupBox)
        self.selectAllRadioButton.setCheckable(True)
        self.selectAllRadioButton.setObjectName(_fromUtf8("selectAllRadioButton"))
        self.gridLayout.addWidget(self.selectAllRadioButton, 1, 0, 1, 1)
        self.selectonlyRadioButton = QtGui.QRadioButton(self.chainageGroupBox)
        self.selectonlyRadioButton.setCheckable(True)
        self.selectonlyRadioButton.setChecked(True)
        self.selectonlyRadioButton.setObjectName(_fromUtf8("selectonlyRadioButton"))
        self.gridLayout.addWidget(self.selectonlyRadioButton, 0, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 2, 0, 1, 1)
        self.gridLayout_2.addWidget(self.chainageGroupBox, 4, 0, 1, 2)
        self.autoLabelcheckBox = QtGui.QCheckBox(Dialog)
        self.autoLabelcheckBox.setChecked(True)
        self.autoLabelcheckBox.setObjectName(_fromUtf8("autoLabelcheckBox"))
        self.gridLayout_2.addWidget(self.autoLabelcheckBox, 5, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Help|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_2.addWidget(self.buttonBox, 6, 0, 1, 2)
        self.selectLayerComboBox = QtGui.QComboBox(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.selectLayerComboBox.sizePolicy().hasHeightForWidth())
        self.selectLayerComboBox.setSizePolicy(sizePolicy)
        self.selectLayerComboBox.setObjectName(_fromUtf8("selectLayerComboBox"))
        self.gridLayout_2.addWidget(self.selectLayerComboBox, 0, 1, 1, 1)
        self.startpointSpinBox = QtGui.QDoubleSpinBox(Dialog)
        self.startpointSpinBox.setMaximum(9999.99)
        self.startpointSpinBox.setObjectName(_fromUtf8("startpointSpinBox"))
        self.gridLayout_2.addWidget(self.startpointSpinBox, 3, 1, 1, 1)
        self.labelStart = QtGui.QLabel(Dialog)
        self.labelStart.setObjectName(_fromUtf8("labelStart"))
        self.gridLayout_2.addWidget(self.labelStart, 3, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QObject.connect(self.selectLayerComboBox, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), Dialog.onComboBoxChanged)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.labelSelectLayer.setText(QtGui.QApplication.translate("Dialog", "Select Layer to chainage", None, QtGui.QApplication.UnicodeUTF8))
        self.labelDistance.setText(QtGui.QApplication.translate("Dialog", "Distance to chainage", None, QtGui.QApplication.UnicodeUTF8))
        self.labelLayerName.setText(QtGui.QApplication.translate("Dialog", "Name of output Layer", None, QtGui.QApplication.UnicodeUTF8))
        self.chainageGroupBox.setTitle(QtGui.QApplication.translate("Dialog", "Chainage", None, QtGui.QApplication.UnicodeUTF8))
        self.selectAllRadioButton.setText(QtGui.QApplication.translate("Dialog", "every Feature in Layer", None, QtGui.QApplication.UnicodeUTF8))
        self.selectonlyRadioButton.setText(QtGui.QApplication.translate("Dialog", "only selected Features", None, QtGui.QApplication.UnicodeUTF8))
        self.autoLabelcheckBox.setText(QtGui.QApplication.translate("Dialog", "Automatically Label the Layer", None, QtGui.QApplication.UnicodeUTF8))
        self.labelStart.setText(QtGui.QApplication.translate("Dialog", "Start from ", None, QtGui.QApplication.UnicodeUTF8))

