# -*- coding: utf-8 -*-
"""
QChainage Plugin - Creates points at specified intervals along line geometries.
Compatible with QGIS 3.x and Qt5/Qt6.

Copyright (c) 2013-2024 Werner Macho
Licensed under GNU GPL v3.0
"""

import os
from qgis.PyQt.QtCore import QFileInfo, QSettings, QTranslator, QCoreApplication, qVersion
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import Qgis, QgsMapLayer, QgsWkbTypes
from .qchainagedialog import QChainageDialog


class Qchainage:
    """Main QChainage plugin class."""

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.action = None
        self._setup_translation()

    def _setup_translation(self):
        """Set up plugin translation."""
        locale = QSettings().value("locale/userLocale", "en")[0:2]
        locale_path = os.path.join(self.plugin_dir, f"i18n/qchainage_{locale}.qm")
        
        if QFileInfo(locale_path).exists():
            self.translator = QTranslator()
            self.translator.load(locale_path)
            
            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

    def initGui(self):
        """Initialize the plugin GUI."""
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

    def unload(self):
        """Unload the plugin."""
        if self.action:
            self.iface.removePluginVectorMenu("&QChainage", self.action)
            self.iface.removeToolBarIcon(self.action)

    def _has_line_layers(self):
        """Check if any line layers are available."""
        return any(
            layer.type() == QgsMapLayer.VectorLayer and 
            layer.geometryType() == QgsWkbTypes.LineGeometry
            for layer in self.iface.mapCanvas().layers()
        )

    def _show_warning(self, message):
        """Display a warning message to the user."""
        text = QCoreApplication.translate('Qchainage', message)
        self.iface.messageBar().pushMessage(
            "QChainage", text, Qgis.Warning, duration=5
        )

    def run(self):
        """Run the plugin."""
        if not self._has_line_layers():
            self._show_warning("No layers with line features - no layer chainable")
            return

        # Show dialog
        dialog = QChainageDialog(self.iface)
        dialog.exec_()
