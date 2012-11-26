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
    """
     Here we do anything to do with UI init
    """
    QDialog.__init__(self)
    self.iface = parent
    self.setupUi(self)
    
    self.distanceSpinBox.setValue(1)
    self.qgisSettings = QSettings()

    for l in self.iface.mapCanvas().layers():
      if l.type() == QgsMapLayer.VectorLayer and l.geometryType() == QGis.Line:
        self.selectLayerComboBox.addItem(l.name(), l)
    
    currentLayer = self.iface.mapCanvas().currentLayer()
    index = self.selectLayerComboBox.findData(currentLayer)
    self.selectLayerComboBox.setCurrentIndex(index)

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