# -*- coding: utf-8 -*-
'''
File: qchainage.py
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
