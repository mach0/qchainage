# -*- coding: utf-8 -*-
"""
QChainage Dialog - User interface for configuring chainage parameters.
Compatible with both Qt5 (QGIS 3.x) and Qt6 (QGIS 4.x).

Copyright (c) 2013-2026 Werner Macho
Licensed under GNU GPL v3.0
"""

import os
from typing import List, Optional

from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtGui import QDesktopServices
from qgis.core import (
    Qgis,
    QgsDistanceArea,
    QgsMessageLog,
    QgsProject,
    QgsUnitTypes,
    QgsVectorLayer,
    QgsWkbTypes,
)

from .chainagetool import points_along_line
from .qt_compat import (
    DialogButtonBox_Help,
    DialogButtonBox_Ok,
    QDialog,
    QSettings,
    uic,
)

# Load UI file with error handling
try:
    FORM_CLASS, _ = uic.loadUiType(os.path.join(
        os.path.dirname(__file__), 'ui_qchainage.ui'
    ))
except Exception as e:
    QgsMessageLog.logMessage(
        f"Warning: Could not load UI file: {e}", "QChainage", Qgis.Warning
    )
    FORM_CLASS = QDialog


class QChainageDialog(QDialog, FORM_CLASS):
    """Dialog for configuring chainage parameters."""

    def __init__(self, iface, parent=None):
        super().__init__(parent)
        self.iface = iface
        self.setupUi(self)
        self.setWindowTitle('QChainage')

        self.current_units = None
        self.current_start_units = None
        self.current_end_units = None
        self.qgis_settings = QSettings()
        self.distance_area = QgsDistanceArea()

        # Setup buttons using Qt5/Qt6 compatible enum values
        self.ok_button = self.buttonBox.button(DialogButtonBox_Ok)
        if self.ok_button:
            self.ok_button.setEnabled(False)

        help_button = self.buttonBox.button(DialogButtonBox_Help)
        if help_button:
            help_button.clicked.connect(self._show_help)

        # Initialize UI components
        self._setup_units_combo()
        self._setup_layer_combo()

        # Connect signals
        self.UnitsComboBox.currentIndexChanged.connect(self._on_units_changed)
        self.startUnitsComboBox.currentIndexChanged.connect(
            self._on_start_units_changed
        )
        self.endUnitsComboBox.currentIndexChanged.connect(
            self._on_end_units_changed
        )
        self.selectLayerComboBox.currentIndexChanged.connect(
            self._on_layer_changed
        )
        self.rBEllipsoidal.toggled.connect(self._on_projection_changed)
        self.rBCartesian.toggled.connect(self._on_projection_changed)

        # Connect mode controls to enable/disable distance box
        self.force_fl_CB.toggled.connect(self._on_mode_changed)
        self.divideSpinBox.valueChanged.connect(self._on_mode_changed)

        # Connect checkboxes to enable/disable start/end controls
        self.checkBoxStartFrom.toggled.connect(self._on_start_checkbox_toggled)
        self.checkBoxEndAt.toggled.connect(self._on_end_checkbox_toggled)

        # Connect attribute selection controls
        self.selectAllAttributesBtn.clicked.connect(
            self._select_all_attributes
        )
        self.deselectAllAttributesBtn.clicked.connect(
            self._deselect_all_attributes
        )

        # Connect to project layer changes to keep combo in sync
        QgsProject.instance().layersAdded.connect(self._setup_layer_combo)
        QgsProject.instance().layersRemoved.connect(self._setup_layer_combo)

        # Ensure layer units and OK button are initialized on startup
        self._on_layer_changed()

    def _show_help(self):
        """Open plugin help documentation."""
        QDesktopServices.openUrl(QUrl("https://github.com/mach0/qchainage"))

    def _setup_units_combo(self):
        """Initialize all units combo boxes with available distance units."""
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

        combos = [
            self.UnitsComboBox,
            self.startUnitsComboBox,
            self.endUnitsComboBox
        ]
        for combo in combos:
            combo.blockSignals(True)
            combo.clear()
            for unit in units:
                combo.addItem(QgsUnitTypes.toString(unit), unit)
            combo.blockSignals(False)

    def _setup_layer_combo(self):
        """Populate layer combo box with line layers from the project."""
        current_layer = self.iface.activeLayer() if self.iface else None
        previously_selected = self._get_current_layer()
        target_layer = previously_selected or current_layer

        self.selectLayerComboBox.blockSignals(True)
        self.selectLayerComboBox.clear()

        selected_index = -1
        # Search all vector layers in the project with Line geometry
        for layer in QgsProject.instance().mapLayers().values():
            if (
                isinstance(layer, QgsVectorLayer)
                and layer.isValid()
                and layer.geometryType() == QgsWkbTypes.LineGeometry
            ):
                self.selectLayerComboBox.addItem(layer.name(), layer)
                if target_layer and layer.id() == target_layer.id():
                    selected_index = self.selectLayerComboBox.count() - 1

        if selected_index >= 0:
            self.selectLayerComboBox.setCurrentIndex(selected_index)
        elif self.selectLayerComboBox.count() > 0:
            self.selectLayerComboBox.setCurrentIndex(0)

        self.selectLayerComboBox.blockSignals(False)
        self._on_layer_changed()

    def _get_current_layer(self) -> Optional[QgsVectorLayer]:
        """Get the currently selected layer."""
        index = self.selectLayerComboBox.currentIndex()
        if index >= 0:
            return self.selectLayerComboBox.itemData(index)
        return None

    def _on_mode_changed(self):
        """Enable or disable distance spin box based on selected mode."""
        is_first_last = self.force_fl_CB.isChecked()
        is_divide = self.divideSpinBox.value() > 0
        self.distanceSpinBox.setEnabled(not (is_first_last or is_divide))

    def _on_layer_changed(self):
        """Handle layer selection change."""
        layer = self._get_current_layer()
        if not layer or not layer.isValid():
            if self.ok_button:
                self.ok_button.setEnabled(False)
            self.layerUnits.setText("")
            return

        if self.ok_button:
            self.ok_button.setEnabled(True)

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
        unit_idx = self.UnitsComboBox.findData(units)
        if unit_idx >= 0:
            combos = [
                self.UnitsComboBox,
                self.startUnitsComboBox,
                self.endUnitsComboBox
            ]
            for combo in combos:
                combo.blockSignals(True)
                combo.setCurrentIndex(unit_idx)
                combo.blockSignals(False)

        self.current_units = units
        self.current_start_units = units
        self.current_end_units = units

        # Set default output layer name
        self.layerNameLine.setText(f"chain_{layer.name()}")

        # Populate attributes list
        self._populate_attributes_list(layer)

        # Configure selection options based on selected features
        selected_count = layer.selectedFeatureCount()
        if selected_count == 0:
            self.selectAllRadioBtn.setChecked(True)
            self.selectOnlyRadioBtn.setEnabled(False)
        else:
            self.selectOnlyRadioBtn.setEnabled(True)
            self.selectOnlyRadioBtn.setChecked(True)

    def _on_units_changed(self):
        """Handle units change and convert distance value."""
        if self.current_units is None:
            return

        old_unit = self.current_units
        new_unit = self.UnitsComboBox.currentData()

        if old_unit == new_unit:
            return

        # Convert current distance value to new units
        factor = QgsUnitTypes.fromUnitToUnitFactor(old_unit, new_unit)
        if factor > 0:
            current_value = self.distanceSpinBox.value()
            self.distanceSpinBox.setValue(current_value * factor)

        self.current_units = new_unit

    def _on_start_units_changed(self):
        """Handle start units change and convert start value."""
        if self.current_start_units is None:
            return

        old_unit = self.current_start_units
        new_unit = self.startUnitsComboBox.currentData()

        if old_unit == new_unit:
            return

        factor = QgsUnitTypes.fromUnitToUnitFactor(old_unit, new_unit)
        if factor > 0:
            self.startSpinBox.setValue(self.startSpinBox.value() * factor)

        self.current_start_units = new_unit

    def _on_end_units_changed(self):
        """Handle end units change and convert end value."""
        if self.current_end_units is None:
            return

        old_unit = self.current_end_units
        new_unit = self.endUnitsComboBox.currentData()

        if old_unit == new_unit:
            return

        factor = QgsUnitTypes.fromUnitToUnitFactor(old_unit, new_unit)
        if factor > 0:
            self.endSpinBox.setValue(self.endSpinBox.value() * factor)

        self.current_end_units = new_unit

    def _on_start_checkbox_toggled(self, checked: bool):
        """Enable/disable start spinbox and units when checkbox is toggled."""
        self.startSpinBox.setEnabled(checked)
        self.startUnitsComboBox.setEnabled(checked)

    def _on_end_checkbox_toggled(self, checked: bool):
        """Enable/disable end spinbox and units when checkbox is toggled."""
        self.endSpinBox.setEnabled(checked)
        self.endUnitsComboBox.setEnabled(checked)

    def _configure_distance_calculation(self, layer: Optional[QgsVectorLayer]):
        """Configure distance calculation based on projection selection."""
        if self.rBEllipsoidal.isChecked():
            self.distance_area.setEllipsoid(QgsProject.instance().ellipsoid())
        else:
            self.distance_area.setEllipsoid("NONE")

            # Warn if using cartesian with geographic coordinates
            if layer and layer.crs().isGeographic():
                QgsMessageLog.logMessage(
                    "Warning: Cartesian with geographic coordinates produces "
                    "distances in degrees. Use Ellipsoidal for real-world "
                    "distances.",
                    "QChainage",
                    Qgis.Warning
                )

    def _on_projection_changed(self):
        """Handle projection type change (ellipsoidal vs cartesian)."""
        layer = self._get_current_layer()
        if layer:
            self._configure_distance_calculation(layer)

    def _populate_attributes_list(self, layer: Optional[QgsVectorLayer]):
        """Populate the attributes list widget with layer fields."""
        self.attributesListWidget.clear()

        if not layer:
            return

        # Get all fields from the layer, excluding internal FID-type fields
        fields = layer.fields()
        for field in fields:
            field_name = field.name()
            if field_name.lower() in ['fid', 'ogc_fid']:
                continue
            self.attributesListWidget.addItem(field_name)

    def _select_all_attributes(self):
        """Select all attributes in the list."""
        for i in range(self.attributesListWidget.count()):
            self.attributesListWidget.item(i).setSelected(True)

    def _deselect_all_attributes(self):
        """Deselect all attributes in the list."""
        self.attributesListWidget.clearSelection()

    def _get_selected_attributes(self) -> List[str]:
        """Get list of selected attribute names."""
        if not self.copyAttributesCheckBox.isChecked():
            return []

        selected_items = self.attributesListWidget.selectedItems()
        return [item.text() for item in selected_items]

    def accept(self):
        """Process the chainage creation when OK is clicked."""
        layer = self._get_current_layer()
        if not layer or not layer.isValid():
            return

        # Get parameters from UI
        layer_name = self.layerNameLine.text().strip()
        if not layer_name:
            layer_name = f"chain_{layer.name()}"

        distance = self.distanceSpinBox.value()

        # Only use start/end points if their checkboxes are checked
        if self.checkBoxStartFrom.isChecked():
            startpoint = self.startSpinBox.value()
        else:
            startpoint = 0.0

        if self.checkBoxEndAt.isChecked():
            endpoint = self.endSpinBox.value()
        else:
            endpoint = 0.0

        # Get selected units for each parameter
        distance_units = self.UnitsComboBox.currentData()
        start_units = self.startUnitsComboBox.currentData()
        end_units = self.endUnitsComboBox.currentData()

        # Convert start/end to distance_units if they differ
        if start_units != distance_units and startpoint > 0:
            conversion_factor = QgsUnitTypes.fromUnitToUnitFactor(
                start_units, distance_units
            )
            if conversion_factor > 0:
                startpoint *= conversion_factor

        if end_units != distance_units and endpoint > 0:
            conversion_factor = QgsUnitTypes.fromUnitToUnitFactor(
                end_units, distance_units
            )
            if conversion_factor > 0:
                endpoint *= conversion_factor

        selected_only = self.selectOnlyRadioBtn.isChecked()
        force_last = self.forceLastCheckBox.isChecked()
        force_first_last = self.force_fl_CB.isChecked()
        divide = self.divideSpinBox.value()
        use_ellipsoidal = self.rBEllipsoidal.isChecked()
        reverse = self.checkBoxReverse.isChecked()
        include_angle = (
            getattr(self, 'checkBoxAngle', None) is not None
            and self.checkBoxAngle.isChecked()
        )

        # Get selected attributes to copy
        copy_attributes = self._get_selected_attributes()

        # Safety check: ensure distance is valid when needed
        if distance <= 0 and not force_first_last and divide == 0:
            if self.iface:
                self.iface.messageBar().pushMessage(
                    "QChainage",
                    "Distance must be greater than zero.",
                    Qgis.Warning,
                    duration=5
                )
            return

        # Create chainage points
        virt_layer = points_along_line(
            layerout=layer_name,
            startpoint=startpoint,
            endpoint=endpoint,
            distance=distance,
            layer=layer,
            selected_only=selected_only,
            force_last=force_last,
            force_first_last=force_first_last,
            divide=divide,
            use_ellipsoidal=use_ellipsoidal,
            distance_units=distance_units,
            copy_attributes=copy_attributes,
            reverse=reverse,
            include_angle=include_angle
        )

        # Provide user feedback
        if virt_layer and self.iface:
            count = virt_layer.featureCount()
            if count > 0:
                self.iface.messageBar().pushMessage(
                    "QChainage",
                    f"Chainage complete: Created {count} points in layer "
                    f"'{layer_name}'.",
                    Qgis.Success,
                    duration=4
                )
            else:
                self.iface.messageBar().pushMessage(
                    "QChainage",
                    f"Chainage completed, but 0 points were created in "
                    f"'{layer_name}'. Please check parameters.",
                    Qgis.Warning,
                    duration=5
                )

        super().accept()
