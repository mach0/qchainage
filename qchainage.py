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
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import QFileInfo, QSettings, QTranslator
from PyQt4.QtCore import QCoreApplication, qVersion
from PyQt4.QtGui import QAction, QIcon

from qgis.core import QgsApplication
# Import the code for the dialog
from qchainagedialog import QChainageDialog

# Initialize Qt resources from file resources.py, don't delete even if it
# shows not used
import resources_rc


def debug():
    import pydevd
    pydevd.settrace('localhost', port=53100, stdoutToServer=True,
                    stderrToServer=True, suspend=False)


class Qchainage:
    """Main class for Chainage
    """
    def __init__(self, iface):
        try:
            debug()
        except:
            print 'Debugger not enabled'
        # save reference to the QGIS interface
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = \
            QFileInfo(QgsApplication.qgisUserDbFilePath()).path() + \
            "/python/plugins/qchainage"
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

        # Create the dialog (after translation) and keep reference

    def initGui(self):
        """Initiate GUI
        """
        # Create action that will start plugin configuration
        self.action = QAction(
            QIcon(":/plugins/qchainage/img/qchainage.png"),
            u"QChainage", self.iface.mainWindow())
        # connect the action to the run method
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

    # run method that performs all the real work
    def run(self):
        """ Running the plugin
        """
        # show the dialog
        dialog = QChainageDialog(self.iface)
        # Run the dialog event loop
        result = dialog.exec_()
        # See if OK was pressed
        if result == 1:
            # do something useful (delete the line containing pass and
            # substitute with your code)
            pass
