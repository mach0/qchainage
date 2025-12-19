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
        self.startUnitsComboBox.currentIndexChanged.connect(self._on_start_units_changed)
        self.endUnitsComboBox.currentIndexChanged.connect(self._on_end_units_changed)
        self.selectLayerComboBox.currentIndexChanged.connect(self._on_layer_changed)
        self.rBEllipsoidal.toggled.connect(self._on_projection_changed)
        self.rBCartesian.toggled.connect(self._on_projection_changed)
        
        # Connect checkboxes to enable/disable start/end controls
        self.checkBoxStartFrom.toggled.connect(self._on_start_checkbox_toggled)
        self.checkBoxEndAt.toggled.connect(self._on_end_checkbox_toggled)
        
        # Connect attribute selection controls
        self.selectAllAttributesBtn.clicked.connect(self._select_all_attributes)
        self.deselectAllAttributesBtn.clicked.connect(self._deselect_all_attributes)

        # Ensure layer units and OK button are initialized on startup
        self._on_layer_changed()

    def _setup_units_combo(self):
        """Initialize all units combo boxes with available distance units."""
        # Common distance units
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
        
        # Setup all three combo boxes
        for combo in [self.UnitsComboBox, self.startUnitsComboBox, self.endUnitsComboBox]:
            combo.clear()
            for unit in units:
                combo.addItem(QgsUnitTypes.toString(unit), unit)

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
        
        # Update all units combos to match layer units
        self.current_units = self.UnitsComboBox.findData(units)
        if self.current_units >= 0:
            self.UnitsComboBox.setCurrentIndex(self.current_units)
            self.startUnitsComboBox.setCurrentIndex(self.current_units)
            self.endUnitsComboBox.setCurrentIndex(self.current_units)
        
        # Set default output layer name
        self.layerNameLine.setText(f"chain_{layer.name()}")
        
        # Populate attributes list
        self._populate_attributes_list(layer)
        
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

    def _on_start_units_changed(self):
        """Handle start units change - sync with main units."""
        # No conversion needed, start units just set the interpretation
        pass

    def _on_end_units_changed(self):
        """Handle end units change - sync with main units."""
        # No conversion needed, end units just set the interpretation
        pass

    def _on_start_checkbox_toggled(self, checked):
        """Enable/disable start spinbox and units when checkbox is toggled."""
        self.startSpinBox.setEnabled(checked)
        self.startUnitsComboBox.setEnabled(checked)

    def _on_end_checkbox_toggled(self, checked):
        """Enable/disable end spinbox and units when checkbox is toggled."""
        self.endSpinBox.setEnabled(checked)
        self.endUnitsComboBox.setEnabled(checked)

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

    def _populate_attributes_list(self, layer):
        """Populate the attributes list widget with layer fields."""
        self.attributesListWidget.clear()
        
        if not layer:
            return
        
        # Get all fields from the layer, excluding FID-type fields
        fields = layer.fields()
        for field in fields:
            field_name = field.name()
            # Skip FID and ID fields (case-insensitive)
            if field_name.lower() in ['fid', 'id', 'objectid', 'ogc_fid']:
                continue
            self.attributesListWidget.addItem(field_name)

    def _select_all_attributes(self):
        """Select all attributes in the list."""
        for i in range(self.attributesListWidget.count()):
            self.attributesListWidget.item(i).setSelected(True)

    def _deselect_all_attributes(self):
        """Deselect all attributes in the list."""
        self.attributesListWidget.clearSelection()

    def _get_selected_attributes(self):
        """Get list of selected attribute names."""
        if not self.copyAttributesCheckBox.isChecked():
            return []
        
        selected_items = self.attributesListWidget.selectedItems()
        return [item.text() for item in selected_items]

    def accept(self):
        """Process the chainage creation when OK is clicked."""
        layer = self._get_current_layer()
        if not layer:
            return
            
        # Get parameters from UI
        layer_name = self.layerNameLine.text()
        distance = self.distanceSpinBox.value()
        
        # Get start/end with their units and convert to layer units
        startpoint = self.startSpinBox.value()
        endpoint = self.endSpinBox.value()
        
        # Get selected units for each parameter
        distance_units = self.UnitsComboBox.currentData()
        start_units = self.startUnitsComboBox.currentData()
        end_units = self.endUnitsComboBox.currentData()
        
        # Convert start/end to distance_units if they differ
        layer_units = layer.crs().mapUnits()
        
        if start_units != distance_units and startpoint > 0:
            conversion_factor = QgsUnitTypes.fromUnitToUnitFactor(start_units, distance_units)
            startpoint *= conversion_factor
        
        if end_units != distance_units and endpoint > 0:
            conversion_factor = QgsUnitTypes.fromUnitToUnitFactor(end_units, distance_units)
            endpoint *= conversion_factor
        
        selected_only = self.selectOnlyRadioBtn.isChecked()
        force_last = self.forceLastCheckBox.isChecked()
        force_first_last = self.force_fl_CB.isChecked()
        divide = self.divideSpinBox.value()
        use_ellipsoidal = self.rBEllipsoidal.isChecked()
        reverse = self.checkBoxReverse.isChecked()
        
        # Get selected attributes to copy
        copy_attributes = self._get_selected_attributes()
        
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
                use_ellipsoidal, distance_units, copy_attributes, reverse
            )
        finally:
            # Restore original projection setting
            self.qgis_settings.setValue(projection_key, old_setting)
        
        super().accept()
