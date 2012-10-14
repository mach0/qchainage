# -*- coding: utf-8 -*-
# ***************************************************************************
# qchainage_dialog.py.py  -  A Chainage Tool for QGIS
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

from qgis.core import *
from qgis.utils import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from chainagetool import *
from qchainage_dialog_widget import Ui_Dialog

class QChainageDialog (QDialog, Ui_Dialog):
  
  def __init__(self, parent):
    QDialog.__init__(self)
    self.iface = parent
    self.setupUi(self)
    
    selfeatures = 0
    
    for l in self.iface.mapCanvas().layers():
      if l.type() == QgsMapLayer.VectorLayer and l.geometryType() == QGis.Line:
        self.selectLayerComboBox.addItem( l.name() )
        selfeatures += l.selectedFeatureCount()
      
    
    self.distanceSpinBox.setValue(1)
    
    """
     Here we do anything to do with UI init
    """
  def onComboBoxChanged(self, newIndex):
    tx = self.selectLayerComboBox.currentText()
    for l in self.iface.mapCanvas().layers():
      if l.name() == tx:
        self.iface.mapCanvas().setCurrentLayer(l)
        self.layerNameLine.setText("chain_" + tx)
      
 
  def accept(self):
    countfeatures = 0
    for l in self.iface.mapCanvas().layers():
      if l.type() == QgsMapLayer.VectorLayer and l.geometryType() == QGis.Line:
        countfeatures += l.selectedFeatureCount()
    if countfeatures  < 1:
      QMessageBox.critical(self.iface.mainWindow(), "ERROR", "I autoselect all features because you have not selected a single one" )
      layer = self.iface.mapCanvas().currentLayer() # set layer
      layer.select([]) # we don't actually need the attributes
      layer.setSelectedFeatures([feat.id() for feat in layer]) # select all the feature ids
      
    layerout = self.layerNameLine.text()
    distance = self.distanceSpinBox.value()
    startpoint = self.startpointSpinBox.value()
    endpoint = self.endpointSpinBox.value()
    pointsAlongLine(layerout, startpoint, endpoint, distance, self.iface)
    
    return
    
  """
  do stuff
  cl = self.iface.mapCanvas().currentLayer()
  """