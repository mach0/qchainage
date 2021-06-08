# -*- coding: utf-8 -*-
'''
File: qchainagedialog.py
Project: qchainage
Created Date: February 20th 2013
Author: Werner Macho
-----
Last Modified: Tue Jun 08 2021
Modified By: Werner Macho
-----
Copyright (c) 2013 - 2021 Werner Macho
-----
GNU General Public License v3.0 only
http://www.gnu.org/licenses/gpl-3.0-standalone.html
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
'''


from .ui_qchainage import Ui_QChainageDialog
from .chainagetool import points_along_line
from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox
from qgis.core import (
    QgsMapLayer,
    QgsWkbTypes,
    QgsUnitTypes,
    QgsDistanceArea,
    QgsProject
    )


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
        self.okButton = self.buttonBox.button(QDialogButtonBox.Ok)
        self.helpButton = self.buttonBox.button(QDialogButtonBox.Help)
        self.okButton.setEnabled(True)
        self.distanceArea = QgsDistanceArea()
        self.UnitsComboBox.clear()

        # Add Unit Items to Main Combobox TODO To be changed with Area distance
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
                self.load_layer(layer)
                counter += 1

            if layer == self.iface.mapCanvas().currentLayer():
                selected_layer_index = counter
            if selected_layer_index >= 0:
                self.selectLayerComboBox.setCurrentIndex(selected_layer_index)

    def set_current_layer(self):
        index = self.selectLayerComboBox.findData(self)
        self.selectLayerComboBox.setCurrentIndex(index)

    def load_layer(self, layer):
        self.selectLayerComboBox.addItem(layer.name(), layer)

    def get_current_layer(self):
        index = self.selectLayerComboBox.currentIndex()
        return self.selectLayerComboBox.itemData(index)

    def on_select_layer_combo_box_current_index_changed(self):
        layer = self.get_current_layer()

        if not layer:
            return

        units = layer.crs().mapUnits()

        self.distanceArea.setSourceCrs(
            layer.crs(), QgsProject.instance().transformContext()
            )
        self.distanceArea.setEllipsoid(
            QgsProject.instance().ellipsoid()
            )

        self.currentUnits = self.UnitsComboBox.findData(units)
        self.UnitsComboBox.setCurrentIndex(self.currentUnits)
        self.layerNameLine.setText("chain_" + layer.name())

        if layer.selectedFeatureCount() == 0:
            self.selectAllRadioBtn.setChecked(True)
            self.selectOnlyRadioBtn.setEnabled(False)
        else:
            self.selectOnlyRadioBtn.setChecked(True)
            self.selectOnlyRadioBtn.setEnabled(True)

        self.okButton.setEnabled(True)

    def on_units_combo_box_current_index_changed(self):
        if self.currentUnits is None:
            return
        calc2 = self.distanceArea.convertLengthMeasurement(
            1.0, 
            self.UnitsComboBox.currentData()
            )
        calc = self.distanceArea.convertLengthMeasurement(
            1.0, 
            self.currentUnits
            )
        self.distanceSpinBox.setValue(
            self.distanceSpinBox.value() / calc * calc2
            )
        self.currentUnits = self.UnitsComboBox.currentData()

    def accept(self):
        layer = self.get_current_layer()
        layerout = self.layerNameLine.text()
        self.UnitsComboBox.setCurrentIndex(
            self.UnitsComboBox.findData(
                layer.crs().mapUnits()
                )
            )
        distance = self.distanceSpinBox.value()
        startpoint = self.startSpinBox.value()
        endpoint = self.endSpinBox.value()
        selected_only = self.selectOnlyRadioBtn.isChecked()
        force_last = self.forceLastCheckBox.isChecked()
        force_first_last = self.force_fl_CB.isChecked()
        divide = self.divideSpinBox.value()

        projection_setting_key = "Projections/defaultBehaviour"
        old_projection_setting = self.qgisSettings.value(
            projection_setting_key
            )

        self.qgisSettings.setValue(
            projection_setting_key, "useGlobal"
            )
        
        self.qgisSettings.sync()

        points_along_line(
            layerout,
            startpoint,
            endpoint,
            distance,
            layer,
            selected_only,
            force_last,
            force_first_last,
            divide
            )

        self.qgisSettings.setValue(
            projection_setting_key,
            old_projection_setting
            )

        QDialog.accept(self)
