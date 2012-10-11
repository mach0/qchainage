# -*- coding: utf-8 -*-
# ***************************************************************************
# __init__.py  -  A Chainage Tool for QGIS
# ---------------------
#     begin                : 2012-10-06
#     copyright            : (C) 2012 by Werner Macho
#     email                : werner.macho at gmail dot com
# ***************************************************************************
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 2 of the License, or     *
# *   (at your option) any later version.                                   *
# *                                                                         *
# ***************************************************************************

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from qchainage_dialog import QChainageDialog

class QChainagePlugin():
  def __init__(self, iface):
    self.iface = iface


  def initGui(self):
    self.actionRun = QAction(QIcon(":/plugins/plugin_reloader/reload.png"), u"Create Chainage", self.iface.mainWindow())
    self.actionRun.setWhatsThis(u"Create Chainage along selected line")
    self.iface.addPluginToMenu("&QChainage", self.actionRun)
    QObject.connect(self.actionRun, SIGNAL("triggered()"), self.run)


  def unload(self):
    self.iface.removePluginMenu("&QChainage",self.actionRun)
    self.iface.unregisterMainWindowAction(self.actionRun)


  def run(self):
  #  import pydevd; pydevd.settrace()
    d = QChainageDialog(self.iface)
    d.show()
    d.exec_()
    
    return