# -*- coding: utf-8 -*-
"""
QChainage Plugin - Creates points at specified intervals along line geometries.
Compatible with QGIS 3.x and QGIS 4.x (Qt5/Qt6).

Copyright (c) 2013-2026 Werner Macho
Licensed under GNU GPL v3.0
"""

import os
from qgis.PyQt.QtCore import (
    QCoreApplication,
    QFileInfo,
    QSettings,
    QTranslator,
)
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import (
    Qgis,
    QgsApplication,
    QgsMessageLog,
    QgsProject,
    QgsVectorLayer,
    QgsWkbTypes,
)
from .qchainagedialog import QChainageDialog


class Qchainage:
    """Main QChainage plugin class."""

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.action = None
        self.provider = None
        self.translator = None
        self._setup_translation()

    def _setup_translation(self):
        """Set up plugin translation."""
        locale = QSettings().value("locale/userLocale", "en")[0:2]
        locale_path = os.path.join(
            self.plugin_dir, f"i18n/qchainage_{locale}.qm"
        )

        if QFileInfo(locale_path).exists():
            self.translator = QTranslator()
            if self.translator.load(locale_path):
                QCoreApplication.installTranslator(self.translator)

    def initProcessing(self):
        """Initialize and register Processing toolbox algorithms."""
        try:
            from .processing.provider import QChainageProvider
            self.provider = QChainageProvider()
            QgsApplication.processingRegistry().addProvider(self.provider)
        except (ImportError, AttributeError, RuntimeError) as e:
            QgsMessageLog.logMessage(
                f"Failed to register QChainage processing provider: {e}",
                "QChainage",
                Qgis.Warning
            )

    def initGui(self):
        """Initialize the plugin GUI and processing provider."""
        # Create action with icon
        icon_path = os.path.join(self.plugin_dir, 'img/qchainage.svg')
        self.action = QAction(
            QIcon(icon_path),
            "QChainage",
            self.iface.mainWindow()
        )
        self.action.triggered.connect(self.run)

        # Add to toolbar and menu
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToVectorMenu("&QChainage", self.action)

        # Register processing algorithm provider
        self.initProcessing()

    def unload(self):
        """Unload the plugin."""
        if self.action:
            self.iface.removePluginVectorMenu("&QChainage", self.action)
            self.iface.removeToolBarIcon(self.action)
            self.action = None

        if self.provider:
            QgsApplication.processingRegistry().removeProvider(self.provider)
            self.provider = None

        if self.translator:
            QCoreApplication.removeTranslator(self.translator)
            self.translator = None

    def _has_line_layers(self) -> bool:
        """Check if any line layers are available in the project."""
        return any(
            isinstance(layer, QgsVectorLayer)
            and layer.isValid()
            and layer.geometryType() == QgsWkbTypes.LineGeometry
            for layer in QgsProject.instance().mapLayers().values()
        )

    def _show_warning(self, message: str):
        """Display a warning message to the user."""
        text = QCoreApplication.translate('Qchainage', message)
        if self.iface:
            self.iface.messageBar().pushMessage(
                "QChainage", text, Qgis.Warning, duration=5
            )

    def run(self):
        """Run the plugin dialog."""
        if not self._has_line_layers():
            self._show_warning("No line layers found in the project.")
            return

        parent = self.iface.mainWindow() if self.iface else None
        dialog = QChainageDialog(self.iface, parent=parent)
        if hasattr(dialog, 'exec'):
            dialog.exec()
        else:
            dialog.exec_()
