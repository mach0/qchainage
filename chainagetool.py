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
from qgis.core import *
from PyQt4.QtCore import QVariant
from qgis.utils import *


def createPointsAt(startpoint, endpoint, distance, geom):
    length = geom.length()
    currentdistance = distance
    feats = []
    
    if endpoint > 0:
      length = endpoint
      
    # set the first point at startpoint
    point = geom.interpolate(startpoint)
    fet = QgsFeature()
    fet[0] = startpoint
    fet.setGeometry(point)
    #fet.setGeometry( QgsGeometry().fromPoint( geom.asPolyline()[0] ) )
    feats.append(fet)

    while startpoint + currentdistance <= length:
        # Get a point along the line at the current distance
        point = geom.interpolate(startpoint + currentdistance)
        # Create a new QgsFeature and assign it the new geometry
        fet = QgsFeature()
        fet[0] = (startpoint + currentdistance)
        fet.setGeometry(point)
        feats.append(fet)
        # Increase the distance
        currentdistance = currentdistance + distance

    return feats

def pointsAlongLine(layerout, startpoint, endpoint, distance, label, layer, selectedOnly=True):
    # Create a new memory layer and add a distance attributeself.layerNameLine
    vl = QgsVectorLayer("Point", layerout, "memory")
    vl.setCrs(layer.crs())
    pr = vl.dataProvider()
    vl.startEditing()   #actually writes attributes
    pr.addAttributes( [ QgsField("chainage", QVariant.Int) ] )
    
    def getFeatures():
        if selectedOnly:
            return layer.selectedFeatures()
        else:
            return layer.getFeatures()

    # Loop through all selected features
    for feature in getFeatures():
        geom = feature.geometry()
        if not geom:
            QgsMessageLog.logMessage("No geom", "QChainage")
            continue

        features = createPointsAt(startpoint, endpoint, distance, geom)
        pr.addFeatures(features)
        vl.updateExtents()

    QgsMapLayerRegistry.instance().addMapLayers([vl])
    vl.commitChanges()
    vl.reload()

    #Add labeling from here
    vl.setUsingRendererV2( true )
    #generic labeling properties
    if label:
      vl.setCustomProperty("labeling/fieldName", "chainage" )  # default value provider.fieldNameIndex(layer.displayField())
      vl.setCustomProperty("labeling","pal" ) # new gen labeling activated 
      vl.setCustomProperty("labeling/fontSize","10" ) # default value 
      vl.setCustomProperty("labeling/multiLineLabels","true" ) # default value 
      vl.setCustomProperty("labeling/enabled","true" ) # default value 
    #style_path = os.path.join( os.path.dirname(__file__), "style.qml" )
    #(errorMsg, result) = vl.loadNamedStyle( style_path )
    vl.triggerRepaint()
    symbol = QgsMarkerSymbolV2.createSimple({"name":"arrow"})
    #layer = qgis.utils.iface.activeLayer()
    vl.rendererV2().setSymbol(symbol)
    return
