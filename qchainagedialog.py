# -*- coding: utf-8 -*-
"""
/***************************************************************************
 qchainageDialog
                                 A QGIS plugin
 chainage features
                             -------------------
        begin                : 2013-02-20
        copyright            : (C) 2013 by Werner Macho
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
from qgis.core import *
from qgis.utils import *
from PyQt4 import QtCore, QtGui
from ui_qchainage import Ui_QChainageDialog
from chainagetool import *

# create the dialog for zoom to point

class qchainageDialog(QtGui.QDialog, Ui_QChainageDialog):
    def __init__(self):
      
        QtGui.QDialog.__init__( self )
        # Set up the user interface from Designer.
        self.setupUi(self)
        
        self.distanceSpinBox.setValue(1)
        self.qgisSettings = QtCore.QSettings()  

    def setCurrentLayer(self, layer):
      index = self.selectLayerComboBox.findData(self)
      self.selectLayerComboBox.setCurrentIndex(index)

    def loadLayer(self, layer):
      self.selectLayerComboBox.addItem(layer.name(), layer)        

    def _getCurrentLayer(self):
      index = self.selectLayerComboBox.currentIndex()
      return self.selectLayerComboBox.itemData(index).toPyObject()

    def onComboBoxChanged(self, newIndex):
      layer = self._getCurrentLayer()
      if not layer:
        return 

      self.layerNameLine.setText("chain_" + layer.name())

      if layer.selectedFeatureCount() == 0:
        self.selectAllRadioButton.setChecked(True)
        self.selectOnlyRadioButton.setEnabled(False)
      else:
          self.selectOnlyRadioButton.setChecked(True)
    
    def accept(self):
      layer = self._getCurrentLayer()
      label = self.autoLabelCheckBox.isChecked()
      layerout = self.layerNameLine.text()
      distance = self.distanceSpinBox.value()
      startpoint = self.startpointSpinBox.value()
      endpoint = self.endpointSpinBox.value()
      selectedOnly = self.selectOnlyRadioButton.isChecked()
  
      projectionSettingKey = "Projections/defaultBehaviour"
      oldProjectionSetting = self.qgisSettings.value(projectionSettingKey)
      self.qgisSettings.setValue(projectionSettingKey, "useGlobal")
      self.qgisSettings.sync()
      pointsAlongLine(layerout, startpoint, endpoint, distance, label, layer, selectedOnly)
      self.qgisSettings.setValue(projectionSettingKey, oldProjectionSetting) 
