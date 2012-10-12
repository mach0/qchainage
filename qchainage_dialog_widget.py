# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qchainage_dialog_widget.ui'
#
# Created: Fri Oct 12 23:58:06 2012
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
        Dialog.resize(380, 327)
        Dialog.setMinimumSize(QtCore.QSize(380, 200))
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.startpointSpinBox_2 = QtGui.QDoubleSpinBox(Dialog)
        self.startpointSpinBox_2.setMaximum(9999.99)
        self.startpointSpinBox_2.setObjectName(_fromUtf8("startpointSpinBox_2"))
        self.gridLayout.addWidget(self.startpointSpinBox_2, 3, 3, 1, 1)
        self.chainageGroupBox = QtGui.QGroupBox(Dialog)
        self.chainageGroupBox.setObjectName(_fromUtf8("chainageGroupBox"))
        self.selectAllRadioButton = QtGui.QRadioButton(self.chainageGroupBox)
        self.selectAllRadioButton.setEnabled(False)
        self.selectAllRadioButton.setGeometry(QtCore.QRect(17, 57, 173, 26))
        self.selectAllRadioButton.setCheckable(True)
        self.selectAllRadioButton.setObjectName(_fromUtf8("selectAllRadioButton"))
        self.selectonlyRadioButton = QtGui.QRadioButton(self.chainageGroupBox)
        self.selectonlyRadioButton.setEnabled(False)
        self.selectonlyRadioButton.setGeometry(QtCore.QRect(17, 25, 178, 26))
        self.selectonlyRadioButton.setCheckable(True)
        self.selectonlyRadioButton.setChecked(True)
        self.selectonlyRadioButton.setObjectName(_fromUtf8("selectonlyRadioButton"))
        self.gridLayout.addWidget(self.chainageGroupBox, 4, 0, 1, 4)
        self.autoLabelcheckBox = QtGui.QCheckBox(Dialog)
        self.autoLabelcheckBox.setChecked(True)
        self.autoLabelcheckBox.setObjectName(_fromUtf8("autoLabelcheckBox"))
        self.gridLayout.addWidget(self.autoLabelcheckBox, 6, 0, 1, 3)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Help|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 7, 0, 1, 4)
        self.selectLayerComboBox = QtGui.QComboBox(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.selectLayerComboBox.sizePolicy().hasHeightForWidth())
        self.selectLayerComboBox.setSizePolicy(sizePolicy)
        self.selectLayerComboBox.setObjectName(_fromUtf8("selectLayerComboBox"))
        self.gridLayout.addWidget(self.selectLayerComboBox, 0, 2, 1, 2)
        self.labelDistance = QtGui.QLabel(Dialog)
        self.labelDistance.setObjectName(_fromUtf8("labelDistance"))
        self.gridLayout.addWidget(self.labelDistance, 1, 0, 1, 2)
        self.distanceSpinBox = QtGui.QDoubleSpinBox(Dialog)
        self.distanceSpinBox.setDecimals(3)
        self.distanceSpinBox.setMaximum(9999.99)
        self.distanceSpinBox.setProperty("value", 1.0)
        self.distanceSpinBox.setObjectName(_fromUtf8("distanceSpinBox"))
        self.gridLayout.addWidget(self.distanceSpinBox, 1, 2, 1, 1)
        self.labelLayerName = QtGui.QLabel(Dialog)
        self.labelLayerName.setObjectName(_fromUtf8("labelLayerName"))
        self.gridLayout.addWidget(self.labelLayerName, 2, 0, 1, 2)
        self.layerNameLine = QtGui.QLineEdit(Dialog)
        self.layerNameLine.setObjectName(_fromUtf8("layerNameLine"))
        self.gridLayout.addWidget(self.layerNameLine, 2, 2, 1, 2)
        self.labelStart = QtGui.QLabel(Dialog)
        self.labelStart.setObjectName(_fromUtf8("labelStart"))
        self.gridLayout.addWidget(self.labelStart, 3, 0, 1, 1)
        self.startpointSpinBox = QtGui.QDoubleSpinBox(Dialog)
        self.startpointSpinBox.setMaximum(9999.99)
        self.startpointSpinBox.setObjectName(_fromUtf8("startpointSpinBox"))
        self.gridLayout.addWidget(self.startpointSpinBox, 3, 1, 1, 1)
        self.labelStart_2 = QtGui.QLabel(Dialog)
        self.labelStart_2.setObjectName(_fromUtf8("labelStart_2"))
        self.gridLayout.addWidget(self.labelStart_2, 3, 2, 1, 1)
        self.labelSelectLayer = QtGui.QLabel(Dialog)
        self.labelSelectLayer.setObjectName(_fromUtf8("labelSelectLayer"))
        self.gridLayout.addWidget(self.labelSelectLayer, 0, 0, 1, 2)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QObject.connect(self.selectLayerComboBox, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), Dialog.onComboBoxChanged)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.chainageGroupBox.setTitle(QtGui.QApplication.translate("Dialog", "Chainage", None, QtGui.QApplication.UnicodeUTF8))
        self.selectAllRadioButton.setText(QtGui.QApplication.translate("Dialog", "every Feature in Layer", None, QtGui.QApplication.UnicodeUTF8))
        self.selectonlyRadioButton.setText(QtGui.QApplication.translate("Dialog", "only selected Features", None, QtGui.QApplication.UnicodeUTF8))
        self.autoLabelcheckBox.setText(QtGui.QApplication.translate("Dialog", "Automatically Label the Layer", None, QtGui.QApplication.UnicodeUTF8))
        self.labelDistance.setText(QtGui.QApplication.translate("Dialog", "Distance to chainage", None, QtGui.QApplication.UnicodeUTF8))
        self.labelLayerName.setText(QtGui.QApplication.translate("Dialog", "Name of output Layer", None, QtGui.QApplication.UnicodeUTF8))
        self.labelStart.setText(QtGui.QApplication.translate("Dialog", "Start from ", None, QtGui.QApplication.UnicodeUTF8))
        self.labelStart_2.setText(QtGui.QApplication.translate("Dialog", "End at", None, QtGui.QApplication.UnicodeUTF8))
        self.labelSelectLayer.setText(QtGui.QApplication.translate("Dialog", "Select Layer to chainage", None, QtGui.QApplication.UnicodeUTF8))

