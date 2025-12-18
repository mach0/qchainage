# -*- coding: utf-8 -*-
"""
QChainage Dialog - User interface for configuring chainage parameters.
Compatible with both Qt5 (QGIS 3.x) and Qt6 (future QGIS versions).

Copyright (c) 2013 - 2025 Werner Macho
Licensed under GNU GPL v3.0
"""

import os
from .chainagetool import points_along_line
from .qt_compat import uic, QSettings, QDialog, DialogButtonBox_Ok
from qgis.core import (
    QgsMapLayer, QgsWkbTypes, QgsUnitTypes, QgsDistanceArea,
    QgsProject, QgsMessageLog
)

# Load UI file with error handling
try:
    FORM_CLASS, _ = uic.loadUiType(os.path.join(
        os.path.dirname(__file__), 'ui_qchainage.ui'))
except Exception as e:
    print(f"Warning: Could not load UI file: {e}")
    FORM_CLASS = QDialog


class QChainageDialog(QDialog, FORM_CLASS):
    """Dialog for configuring chainage parameters."""

    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.setupUi(self)
        self.setWindowTitle('QChainage')
        
        self.current_units = None
        self.qgis_settings = QSettings()
        self.distance_area = QgsDistanceArea()
        
        # Setup buttons using Qt5/Qt6 compatible enum values
        self.ok_button = self.buttonBox.button(DialogButtonBox_Ok)
        self.ok_button.setEnabled(False)
        
        # Initialize UI components
        self._setup_units_combo()
        self._setup_layer_combo()
        
        # Connect signals
        self.UnitsComboBox.currentIndexChanged.connect(self._on_units_changed)
        self.selectLayerComboBox.currentIndexChanged.connect(self._on_layer_changed)
        self.rBEllipsoidal.toggled.connect(self._on_projection_changed)
        self.rBCartesian.toggled.connect(self._on_projection_changed)

        # Ensure layer units and OK button are initialized on startup
        self._on_layer_changed()

    def _setup_units_combo(self):
        """Initialize the units combo box with available distance units."""
        self.UnitsComboBox.clear()
        
        # Add common distance units
        units = [
            QgsUnitTypes.DistanceMeters,
            QgsUnitTypes.DistanceKilometers,
            QgsUnitTypes.DistanceFeet,
            QgsUnitTypes.DistanceNauticalMiles,
            QgsUnitTypes.DistanceYards,
            QgsUnitTypes.DistanceMiles,
            QgsUnitTypes.DistanceDegrees,
            QgsUnitTypes.DistanceCentimeters,
            QgsUnitTypes.DistanceMillimeters,
        ]
        
        for unit in units:
            self.UnitsComboBox.addItem(QgsUnitTypes.toString(unit), unit)

    def _setup_layer_combo(self):
        """Populate layer combo box with line layers."""
        selected_index = -1
        current_layer = self.iface.mapCanvas().currentLayer()
        
        # Find line layers
        for i, layer in enumerate(self.iface.mapCanvas().layers()):
            if (layer.type() == QgsMapLayer.VectorLayer and 
                layer.geometryType() == QgsWkbTypes.LineGeometry):
                
                self.selectLayerComboBox.addItem(layer.name(), layer)
                
                # Set current layer as selected if it's a line layer
                if layer == current_layer:
                    selected_index = self.selectLayerComboBox.count() - 1
        
        if selected_index >= 0:
            self.selectLayerComboBox.setCurrentIndex(selected_index)

    def _get_current_layer(self):
        """Get the currently selected layer."""
        index = self.selectLayerComboBox.currentIndex()
        return self.selectLayerComboBox.itemData(index)

    def _on_layer_changed(self):
        """Handle layer selection change."""
        layer = self._get_current_layer()
        if not layer:
            return
            
        # Update UI based on selected layer
        units = layer.crs().mapUnits()
        self.layerUnits.setText(QgsUnitTypes.toString(units))
        
        # Setup distance calculations with proper ellipsoid handling
        self.distance_area.setSourceCrs(
            layer.crs(), QgsProject.instance().transformContext()
        )
        
        # Configure projection type based on radio button selection
        self._configure_distance_calculation(layer)
        
        # Update units combo to match layer units
        self.current_units = self.UnitsComboBox.findData(units)
        if self.current_units >= 0:
            self.UnitsComboBox.setCurrentIndex(self.current_units)
        
        # Set default output layer name
        self.layerNameLine.setText(f"chain_{layer.name()}")
        
        # Configure selection options based on selected features
        if layer.selectedFeatureCount() == 0:
            # No features selected: switch to 'all features' and enable OK
            self.selectAllRadioBtn.setChecked(True)
            self.selectOnlyRadioBtn.setEnabled(False)
            self.ok_button.setEnabled(True)
        else:
            # Some features selected: switch to 'selected only' and enable OK
            self.selectOnlyRadioBtn.setChecked(True)
            self.selectOnlyRadioBtn.setEnabled(True)
            self.ok_button.setEnabled(True)

    def _on_units_changed(self):
        """Handle units change and convert distance value."""
        if self.current_units is None:
            return
            
        # Convert current distance value to new units
        old_unit_factor = self.distance_area.convertLengthMeasurement(
            1.0, QgsUnitTypes.DistanceUnit(self.current_units)
        )
        new_unit_factor = self.distance_area.convertLengthMeasurement(
            1.0, self.UnitsComboBox.currentData()
        )
        
        # Update distance spin box value
        current_value = self.distanceSpinBox.value()
        new_value = current_value / old_unit_factor * new_unit_factor
        self.distanceSpinBox.setValue(new_value)
        
        self.current_units = self.UnitsComboBox.currentData()

    def _configure_distance_calculation(self, layer):
        """Configure distance calculation based on projection type selection."""
        if self.rBEllipsoidal.isChecked():
            self.distance_area.setEllipsoid(QgsProject.instance().ellipsoid())
        else:
            self.distance_area.setEllipsoid("NONE")
            
            # Warn if using cartesian with geographic coordinates
            if layer and layer.crs().isGeographic():
                QgsMessageLog.logMessage(
                    "Warning: Cartesian with geographic coordinates (lat/lon) produces "
                    "distances in degrees. Use Ellipsoidal for accurate distances.", 
                    "QChainage"
                )

    def _on_projection_changed(self):
        """Handle projection type change (ellipsoidal vs cartesian)."""
        layer = self._get_current_layer()
        if layer:
            self._configure_distance_calculation(layer)

    def accept(self):
        """Process the chainage creation when OK is clicked."""
        layer = self._get_current_layer()
        if not layer:
            return
            
        # Get parameters from UI
        layer_name = self.layerNameLine.text()
        distance = self.distanceSpinBox.value()
        startpoint = self.startSpinBox.value()
        endpoint = self.endSpinBox.value()
        selected_only = self.selectOnlyRadioBtn.isChecked()
        force_last = self.forceLastCheckBox.isChecked()
        force_first_last = self.force_fl_CB.isChecked()
        divide = self.divideSpinBox.value()
        use_ellipsoidal = self.rBEllipsoidal.isChecked()
        
        # Get selected distance units
        distance_units = self.UnitsComboBox.currentData()
        
        # Safety check: ensure distance is valid
        if distance <= 0 and not force_first_last and divide == 0:
            QgsMessageLog.logMessage(
                "Warning: Distance is zero or negative. Cannot create chainage points.",
                "QChainage"
            )
            return
        
        # Temporarily set projection behavior
        projection_key = "Projections/defaultBehaviour"
        old_setting = self.qgis_settings.value(projection_key)
        self.qgis_settings.setValue(projection_key, "useGlobal")
        
        try:
            # Create chainage points
            points_along_line(
                layer_name, startpoint, endpoint, distance, layer,
                selected_only, force_last, force_first_last, divide,
                use_ellipsoidal, distance_units
            )
        finally:
            # Restore original projection setting
            self.qgis_settings.setValue(projection_key, old_setting)
        
        super().accept()
