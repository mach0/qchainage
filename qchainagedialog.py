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
from __future__ import absolute_import
from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox

from qgis.core import (
    QgsMapLayer,
    QgsWkbTypes,
    QgsUnitTypes,
    QgsDistanceArea,
    QgsProject
)

from .ui_qchainage import Ui_QChainageDialog
from .chainagetool import points_along_line


class QChainageDialog(QDialog, Ui_QChainageDialog):
    """ Setting up User Interface
    """
    def __init__(self, iface):
        self.iface = iface
        QDialog.__init__(self)

        self.setupUi(self)
        self.setWindowTitle('QChainage')
        self.currentUnits = None
        self.qgisSettings = QSettings()
        self.okbutton = self.buttonBox.button(QDialogButtonBox.Ok)
        self.okbutton.setEnabled(False)
        self.da = QgsDistanceArea()
        self.UnitsComboBox.clear()
        for u in [
            QgsUnitTypes.DistanceMeters,
            QgsUnitTypes.DistanceKilometers,
            QgsUnitTypes.DistanceFeet,
            QgsUnitTypes.DistanceNauticalMiles,
            QgsUnitTypes.DistanceYards,
            QgsUnitTypes.DistanceMiles,
            QgsUnitTypes.DistanceDegrees,
            QgsUnitTypes.DistanceCentimeters,
            QgsUnitTypes.DistanceMillimeters,
            QgsUnitTypes.DistanceUnknownUnit,
        ]:
            self.UnitsComboBox.addItem(QgsUnitTypes.toString(u), u)
        
        selected_layer_index = -1
        counter = -1

        for layer in self.iface.mapCanvas().layers():
            if layer.type() == QgsMapLayer.VectorLayer and \
                 layer.geometryType() == QgsWkbTypes.LineGeometry:
                self.loadLayer(layer)
                counter += 1

            if layer == self.iface.mapCanvas().currentLayer():
                selected_layer_index = counter
            if selected_layer_index >= 0:
                self.selectLayerComboBox.setCurrentIndex(selected_layer_index)

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

        self.da.setSourceCrs(layer.crs(), QgsProject.instance().transformContext())
        self.da.setEllipsoid( QgsProject.instance().ellipsoid())
        self.currentUnits = self.UnitsComboBox.findData(units)
        self.UnitsComboBox.setCurrentIndex(self.currentUnits)
        self.layerNameLine.setText("chain_" + layer.name())

        if layer.selectedFeatureCount() == 0:
            self.selectAllRadioBtn.setChecked(True)
            self.selectOnlyRadioBtn.setEnabled(False)
        else:
            self.selectOnlyRadioBtn.setChecked(True)
            self.selectOnlyRadioBtn.setEnabled(True)
  
        self.okbutton.setEnabled(True)

    def on_UnitsComboBox_currentIndexChanged(self):
        if self.currentUnits is None:
            return
        calc2 = self.da.convertLengthMeasurement(1.0, self.UnitsComboBox.currentData())
        calc = self.da.convertLengthMeasurement(1.0, self.currentUnits)
        self.distanceSpinBox.setValue(self.distanceSpinBox.value() / calc * calc2)
        self.currentUnits = self.UnitsComboBox.currentData()
            
    def accept(self):
        layer = self.get_current_layer()
        label = self.autoLabelCheckBox.isChecked()
        layerout = self.layerNameLine.text()
        self.UnitsComboBox.setCurrentIndex(self.UnitsComboBox.findData(layer.crs().mapUnits()))
        distance = self.distanceSpinBox.value()
        startpoint = self.startSpinBox.value()
        endpoint = self.endSpinBox.value()
        selected_only = self.selectOnlyRadioBtn.isChecked()
        force = self.forceLastCheckBox.isChecked()
        fo_fila = self.force_fl_CB.isChecked()
        divide = self.divideSpinBox.value()
        decimal = self.decimalSpinBox.value()

        projection_setting_key = "Projections/defaultBehaviour"
        old_projection_setting = self.qgisSettings.value(projection_setting_key)
        self.qgisSettings.setValue(projection_setting_key, "useGlobal")
        self.qgisSettings.sync()

        points_along_line(
            layerout,
            startpoint,
            endpoint,
            distance,
            label,
            layer,
            selected_only,
            force,
            fo_fila,
            divide,
            decimal)
        self.qgisSettings.setValue(projection_setting_key, old_projection_setting)
        QDialog.accept(self)
