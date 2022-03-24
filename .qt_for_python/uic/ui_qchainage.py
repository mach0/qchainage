# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/wmacho/dev/python/qchainage/ui_qchainage.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_QChainageDialog(object):
    def setupUi(self, QChainageDialog):
        QChainageDialog.setObjectName("QChainageDialog")
        QChainageDialog.setEnabled(True)
        QChainageDialog.resize(528, 325)
        QChainageDialog.setMinimumSize(QtCore.QSize(380, 200))
        self.verticalLayout = QtWidgets.QVBoxLayout(QChainageDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtWidgets.QTabWidget(QChainageDialog)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.tab)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.selectLayerComboBox = QtWidgets.QComboBox(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.selectLayerComboBox.sizePolicy().hasHeightForWidth())
        self.selectLayerComboBox.setSizePolicy(sizePolicy)
        self.selectLayerComboBox.setObjectName("selectLayerComboBox")
        self.gridLayout_2.addWidget(self.selectLayerComboBox, 1, 0, 1, 5)
        self.layerNameLine = QtWidgets.QLineEdit(self.tab)
        self.layerNameLine.setFrame(True)
        self.layerNameLine.setEchoMode(QtWidgets.QLineEdit.Normal)
        self.layerNameLine.setCursorPosition(15)
        self.layerNameLine.setObjectName("layerNameLine")
        self.gridLayout_2.addWidget(self.layerNameLine, 6, 2, 1, 3)
        self.labelLayerName = QtWidgets.QLabel(self.tab)
        self.labelLayerName.setObjectName("labelLayerName")
        self.gridLayout_2.addWidget(self.labelLayerName, 6, 0, 1, 2)
        self.labelDistance = QtWidgets.QLabel(self.tab)
        self.labelDistance.setObjectName("labelDistance")
        self.gridLayout_2.addWidget(self.labelDistance, 2, 0, 1, 2)
        self.labelSelectLayer = QtWidgets.QLabel(self.tab)
        self.labelSelectLayer.setObjectName("labelSelectLayer")
        self.gridLayout_2.addWidget(self.labelSelectLayer, 0, 0, 1, 3)
        self.distanceSpinBox = QtWidgets.QDoubleSpinBox(self.tab)
        self.distanceSpinBox.setDecimals(9)
        self.distanceSpinBox.setMaximum(999999999.999999)
        self.distanceSpinBox.setProperty("value", 1.0)
        self.distanceSpinBox.setObjectName("distanceSpinBox")
        self.gridLayout_2.addWidget(self.distanceSpinBox, 2, 2, 1, 1)
        self.UnitsComboBox = QtWidgets.QComboBox(self.tab)
        self.UnitsComboBox.setObjectName("UnitsComboBox")
        self.gridLayout_2.addWidget(self.UnitsComboBox, 2, 3, 1, 2)
        self.rBCartesian = QtWidgets.QRadioButton(self.tab)
        self.rBCartesian.setObjectName("rBCartesian")
        self.buttonGroup = QtWidgets.QButtonGroup(QChainageDialog)
        self.buttonGroup.setObjectName("buttonGroup")
        self.buttonGroup.addButton(self.rBCartesian)
        self.gridLayout_2.addWidget(self.rBCartesian, 3, 0, 1, 2)
        self.rBEllipsoidal = QtWidgets.QRadioButton(self.tab)
        self.rBEllipsoidal.setChecked(True)
        self.rBEllipsoidal.setObjectName("rBEllipsoidal")
        self.buttonGroup.addButton(self.rBEllipsoidal)
        self.gridLayout_2.addWidget(self.rBEllipsoidal, 3, 2, 1, 3)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 5, 2, 1, 1)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.gridLayout = QtWidgets.QGridLayout(self.tab_2)
        self.gridLayout.setObjectName("gridLayout")
        self.label_2 = QtWidgets.QLabel(self.tab_2)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 6, 1, 1, 1)
        self.checkBoxReverse = QtWidgets.QCheckBox(self.tab_2)
        self.checkBoxReverse.setEnabled(False)
        self.checkBoxReverse.setObjectName("checkBoxReverse")
        self.gridLayout.addWidget(self.checkBoxReverse, 2, 1, 1, 4)
        self.label_3 = QtWidgets.QLabel(self.tab_2)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 6, 3, 1, 1)
        self.label = QtWidgets.QLabel(self.tab_2)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 1, 1, 1)
        self.checkBoxStartFrom = QtWidgets.QCheckBox(self.tab_2)
        self.checkBoxStartFrom.setObjectName("checkBoxStartFrom")
        self.gridLayout.addWidget(self.checkBoxStartFrom, 4, 1, 1, 1)
        self.divideSpinBox = QtWidgets.QSpinBox(self.tab_2)
        self.divideSpinBox.setMaximum(999999999)
        self.divideSpinBox.setObjectName("divideSpinBox")
        self.gridLayout.addWidget(self.divideSpinBox, 6, 2, 1, 1)
        self.selectOnlyRadioBtn = QtWidgets.QRadioButton(self.tab_2)
        self.selectOnlyRadioBtn.setEnabled(True)
        self.selectOnlyRadioBtn.setCheckable(True)
        self.selectOnlyRadioBtn.setChecked(False)
        self.selectOnlyRadioBtn.setObjectName("selectOnlyRadioBtn")
        self.gridLayout.addWidget(self.selectOnlyRadioBtn, 1, 2, 1, 2)
        self.UnitsComboStart = QtWidgets.QComboBox(self.tab_2)
        self.UnitsComboStart.setObjectName("UnitsComboStart")
        self.gridLayout.addWidget(self.UnitsComboStart, 4, 3, 1, 3)
        self.selectAllRadioBtn = QtWidgets.QRadioButton(self.tab_2)
        self.selectAllRadioBtn.setEnabled(True)
        self.selectAllRadioBtn.setCheckable(True)
        self.selectAllRadioBtn.setObjectName("selectAllRadioBtn")
        self.gridLayout.addWidget(self.selectAllRadioBtn, 0, 2, 1, 2)
        self.endSpinBox = QtWidgets.QDoubleSpinBox(self.tab_2)
        self.endSpinBox.setEnabled(False)
        self.endSpinBox.setDecimals(9)
        self.endSpinBox.setMaximum(999999999.999999)
        self.endSpinBox.setObjectName("endSpinBox")
        self.gridLayout.addWidget(self.endSpinBox, 5, 2, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 7, 2, 1, 1)
        self.checkBoxEndAt = QtWidgets.QCheckBox(self.tab_2)
        self.checkBoxEndAt.setObjectName("checkBoxEndAt")
        self.gridLayout.addWidget(self.checkBoxEndAt, 5, 1, 1, 1)
        self.startSpinBox = QtWidgets.QDoubleSpinBox(self.tab_2)
        self.startSpinBox.setEnabled(False)
        self.startSpinBox.setDecimals(9)
        self.startSpinBox.setMaximum(999999999.999999)
        self.startSpinBox.setObjectName("startSpinBox")
        self.gridLayout.addWidget(self.startSpinBox, 4, 2, 1, 1)
        self.UnitsComboEnd = QtWidgets.QComboBox(self.tab_2)
        self.UnitsComboEnd.setObjectName("UnitsComboEnd")
        self.gridLayout.addWidget(self.UnitsComboEnd, 5, 3, 1, 3)
        self.force_fl_CB = QtWidgets.QCheckBox(self.tab_2)
        self.force_fl_CB.setObjectName("force_fl_CB")
        self.gridLayout.addWidget(self.force_fl_CB, 3, 1, 1, 1)
        self.forceLastCheckBox = QtWidgets.QCheckBox(self.tab_2)
        self.forceLastCheckBox.setObjectName("forceLastCheckBox")
        self.gridLayout.addWidget(self.forceLastCheckBox, 3, 2, 1, 1)
        self.tabWidget.addTab(self.tab_2, "")
        self.verticalLayout.addWidget(self.tabWidget)
        self.buttonBox = QtWidgets.QDialogButtonBox(QChainageDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Help|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(QChainageDialog)
        self.tabWidget.setCurrentIndex(0)
        self.buttonBox.accepted.connect(QChainageDialog.accept)
        self.buttonBox.rejected.connect(QChainageDialog.reject)
        self.checkBoxStartFrom.toggled['bool'].connect(self.startSpinBox.setEnabled)
        self.checkBoxEndAt.toggled['bool'].connect(self.endSpinBox.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(QChainageDialog)

    def retranslateUi(self, QChainageDialog):
        _translate = QtCore.QCoreApplication.translate
        QChainageDialog.setWindowTitle(_translate("QChainageDialog", "QChainage"))
        self.layerNameLine.setText(_translate("QChainageDialog", "defaultChainage"))
        self.layerNameLine.setPlaceholderText(_translate("QChainageDialog", "Layername"))
        self.labelLayerName.setText(_translate("QChainageDialog", "Output Layername"))
        self.labelDistance.setText(_translate("QChainageDialog", "Chainage every"))
        self.labelSelectLayer.setText(_translate("QChainageDialog", "Select Layer to chainage"))
        self.rBCartesian.setText(_translate("QChainageDialog", "Cartesian"))
        self.rBEllipsoidal.setText(_translate("QChainageDialog", "Ellipsoidal"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("QChainageDialog", "Basic"))
        self.label_2.setText(_translate("QChainageDialog", "Divide Feature into"))
        self.checkBoxReverse.setText(_translate("QChainageDialog", "Reverse chainage"))
        self.label_3.setText(_translate("QChainageDialog", "Parts"))
        self.label.setText(_translate("QChainageDialog", "Chainage"))
        self.checkBoxStartFrom.setText(_translate("QChainageDialog", "Start from"))
        self.selectOnlyRadioBtn.setText(_translate("QChainageDialog", "only selected Features"))
        self.selectAllRadioBtn.setText(_translate("QChainageDialog", "all Features in Layer"))
        self.checkBoxEndAt.setText(_translate("QChainageDialog", "End at"))
        self.force_fl_CB.setText(_translate("QChainageDialog", "Only first and last point"))
        self.forceLastCheckBox.setText(_translate("QChainageDialog", "Force last point"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("QChainageDialog", "Advanced"))
