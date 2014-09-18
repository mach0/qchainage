# -*- coding: utf-8 -*-
"""
/***************************************************************************
 qchainageDialog
                                 A QGIS plugin
 chainage features
                             -------------------
        begin                : 2013-02-20
        copyright            : (C) 2014 by Werner Macho
        email                : werner.macho@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4 import QtCore, QtGui

from qgis.core import QgsMapLayer, QGis 
from qgis.gui import QgsMessageBar

from ui_qchainage import Ui_QChainageDialog
from chainagetool import points_along_line

# create the dialog for zoom to point


class QChainageDialog(QtGui.QDialog, Ui_QChainageDialog):
    """ Setting up User Interface
    """
    def __init__(self, iface):
        self.iface = iface
        QtGui.QDialog.__init__(self)

        self.setupUi(self)
        self.setWindowTitle('QChainage')
        self.distanceSpinBox.setValue(1)
        self.qgisSettings = QtCore.QSettings()
        self.okbutton = self.buttonBox.button(QtGui.QDialogButtonBox.Ok)
        self.okbutton.setEnabled(False)
        
        leave = -1
        for layer in self.iface.mapCanvas().layers():
            if layer.type() == QgsMapLayer.VectorLayer and \
               layer.geometryType() == QGis.Line:
                leave += 1
                
        if leave < 0:
            message = "No Line Vector Layers, Chainage not useful!"
            mb = iface.messageBar()
            mb.pushWidget(mb.createMessage(message), QgsMessageBar.WARNING, 5)
        
        selectedLayerIndex = -1
        counter = -1

        for layer in self.iface.mapCanvas().layers():
            if layer.type() == QgsMapLayer.VectorLayer and \
                    layer.geometryType() == QGis.Line:
                self.loadLayer(layer)
                counter += 1

            if layer == self.iface.mapCanvas().currentLayer():
                selectedLayerIndex = counter
            if selectedLayerIndex >= 0:
                self.selectLayerComboBox.setCurrentIndex(selectedLayerIndex)

    def setCurrentLayer(self):
        index = self.selectLayerComboBox.findData(self)
        self.selectLayerComboBox.setCurrentIndex(index)

    def loadLayer(self, layer):
        self.selectLayerComboBox.addItem(layer.name(), layer)

    def get_current_layer(self):
        index = self.selectLayerComboBox.currentIndex()
        return self.selectLayerComboBox.itemData(index)
         
    def on_selectLayerComboBox_currentIndexChanged(self):
        layer = self.get_current_layer()
        
        if not layer:
            return
            
        units = layer.crs().mapUnits()
        unitdic = {
            QGis.Degrees: 'Degrees',
            QGis.Meters: 'Meters',
            QGis.Feet: 'Feet',
            QGis.UnknownUnit: 'Unknown'}
        self.labelUnit.setText(unitdic.get(units, 'Unknown'))
        self.labelUnit_2.setText(unitdic.get(units, 'Unknown'))
        self.labelUnit_3.setText(unitdic.get(units, 'Unknown'))
        self.layerNameLine.setText("chain_" + layer.name())

        if layer.selectedFeatureCount() == 0:
            self.selectAllRadioBtn.setChecked(True)
            self.selectOnlyRadioBtn.setEnabled(False)
        else:
            self.selectOnlyRadioBtn.setChecked(True)
            self.selectOnlyRadioBtn.setEnabled(True)
  
        self.okbutton.setEnabled(True)
            
    def accept(self):
        layer = self.get_current_layer()
        label = self.autoLabelCheckBox.isChecked()
        layerout = self.layerNameLine.text()
        distance = self.distanceSpinBox.value()
        startpoint = self.startSpinBox.value()
        endpoint = self.endSpinBox.value()
        selectedOnly = self.selectOnlyRadioBtn.isChecked()
        force = self.forceLastCheckBox.isChecked()
        divide = self.divideSpinBox.value()

        projectionSettingKey = "Projections/defaultBehaviour"
        oldProjectionSetting = self.qgisSettings.value(projectionSettingKey)
        self.qgisSettings.setValue(projectionSettingKey, "useGlobal")
        self.qgisSettings.sync()

        points_along_line(
            layerout,
            startpoint,
            endpoint,
            distance,
            label,
            layer,
            selectedOnly,
            force,
            divide)
        self.qgisSettings.setValue(projectionSettingKey, oldProjectionSetting)
