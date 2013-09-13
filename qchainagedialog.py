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
    def __init__(self, iface):
        self.iface = iface
        QtGui.QDialog.__init__( self )
        # Set up the user interface from Designer.
        self.setupUi(self)
        self.setWindowTitle('QChainage') 
        self.distanceSpinBox.setValue(1)
        self.qgisSettings = QtCore.QSettings() 
        #self.selectLayerComboBox.currentIndexChanged.connect(self.onComboBoxChanged) 
        
        selectedLayerIndex = -1
        counter = -1        
        
        for layer in self.iface.mapCanvas().layers():
          #  print l.geometryType()
          if layer.type() == QgsMapLayer.VectorLayer and \
              layer.geometryType() == QGis.Line:
                  print "Loading layer"
                  self.loadLayer(layer)
                  counter += 1
                  if layer == self.iface.mapCanvas().currentLayer():
                      selectedLayerIndex = counter
          #   else:
          #    print "no Vectorlayer found"
          #   return 
        if selectedLayerIndex >= 0:
            self.selectLayerComboBox.setCurrentIndex(selectedLayerIndex)
                         
    def setCurrentLayer(self, layer):
        index = self.selectLayerComboBox.findData(self)
        self.selectLayerComboBox.setCurrentIndex(index)

    def loadLayer(self, layer):
        self.selectLayerComboBox.addItem(layer.name(), layer)        

    def _getCurrentLayer(self):
        index = self.selectLayerComboBox.currentIndex()
        return self.selectLayerComboBox.itemData(index)

    def on_selectLayerComboBox_currentIndexChanged(self, newIndex):
        layer = self._getCurrentLayer()
        if not layer:
            return 
            
        units = layer.crs().mapUnits() 
        unitdic = {QGis.Degrees : 'Degrees', QGis.Meters : 'Meters', QGis.Feet : 'Feet', QGis.UnknownUnit :'Unknown' }
        self.labelUnit.setText(unitdic.get(units, 'Unknown' ))

        print self.layerNameLine.text()
        print layer.name()
        
        self.layerNameLine.setText("chain_" + layer.name())

        if layer.selectedFeatureCount() == 0:
            self.selectAllRadioButton.setChecked(True)
            self.selectOnlyRadioButton.setEnabled(False)
        else:
            self.selectOnlyRadioButton.setChecked(True)
            self.selectOnlyRadioButton.setEnabled(True)
    
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
      
        points_along_line(layerout, startpoint, endpoint, distance, label, layer, selectedOnly)
        self.qgisSettings.setValue(projectionSettingKey, oldProjectionSetting) 
