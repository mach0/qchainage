# -*- coding: utf-8 -*-
"""
/***************************************************************************
 qchainage
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

import os
from builtins import object

from qgis.PyQt.QtCore import (
    QFileInfo,
    QSettings,
    QTranslator,
    QCoreApplication,
    qVersion,
)
from qgis.PyQt.QtGui import (
    QIcon
)
from qgis.PyQt.QtWidgets import QAction
from qgis.core import (
    Qgis,
    QgsMapLayer,
    QgsWkbTypes,
    QgsDistanceArea
)

# Import the code for the dialog
from .qchainagedialog import QChainageDialog


def show_warning(self, message):
    text = QCoreApplication.translate('Qchainage', message)
    mb = self.iface.messageBar()
    mb.pushWidget(mb.createMessage(text),
                  Qgis.Warning, 5)


class Qchainage(object):
    """Main class for Chainage
    """
    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale_path = ""
        locale = QSettings().value("locale/userLocale")[0:2]

        if QFileInfo(self.plugin_dir).exists():
            locale_path = self.plugin_dir + "/i18n/qchainage_" + locale + ".qm"

        if QFileInfo(locale_path).exists():
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

    def initGui(self):
        """Initiate GUI
        """
        # Create action that will start plugin configuration
        filePath = QFileInfo(__file__).absolutePath()
        chainIcon = QIcon(filePath + '/img/qchainage.svg')
        self.action = QAction(chainIcon,
                              u"QChainage",
                              self.iface.mainWindow())
        self.action.triggered.connect(self.run)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToVectorMenu(u"&QChainage", self.action)

    def unload(self):
        """ Unloading the plugin
        """
        # Remove the plugin menu item and icon
        self.iface.removePluginVectorMenu(u"&QChainage", self.action)
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        """ Running the plugin
        """
        leave = -1

        for layer in self.iface.mapCanvas().layers():
            if layer.type() == QgsMapLayer.VectorLayer and \
               layer.geometryType() == QgsWkbTypes.LineGeometry:
                leave += 1

        if leave < 0:
            message = "No layers with line features - no layer chainable"
            show_warning(self, message)
            return
        # show the dialog
        dialog = QChainageDialog(self.iface)
        # Run the dialog event loop
        result = dialog.exec_()
        # See if OK was pressed
        if result == 1:
            pass
