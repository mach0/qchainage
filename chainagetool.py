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


def createPointsAt(distance, geom):
    length = geom.length()
    currentdistance = distance
    feats = []
    
    # set the first point at 0.0
    fet = QgsFeature()
    fet.setAttributeMap( { 0 : 0.0 } )
    fet.setGeometry( QgsGeometry().fromPoint( geom.asPolyline()[0] ) )
    feats.append(fet)

    while currentdistance < length:
        # Get a point along the line at the current distance
        point = geom.interpolate(currentdistance)
        # Create a new QgsFeature and assign it the new geometry
        fet = QgsFeature()
        fet.setAttributeMap( { 0 : currentdistance } )
        fet.setGeometry(point)
        feats.append(fet)
        # Increase the distance
        currentdistance = currentdistance + distance

    return feats

def pointsAlongLine(distance, iface):
    sdd = "nameofselectedlayer" #self.layerNameLine.text()
    chainlayername = "chain_"+ sdd
    # Create a new memory layer and add a distance attributeself.layerNameLine
    vl = QgsVectorLayer("Point", chainlayername, "memory")
    pr = vl.dataProvider()
    pr.addAttributes( [ QgsField("distance", QVariant.Int) ] )
    layer = iface.mapCanvas().currentLayer()
    # Loop though all the selected features
    for feature in layer.selectedFeatures():
        geom = feature.geometry()
        features = createPointsAt(distance, geom)
        pr.addFeatures(features)
        vl.updateExtents()

    QgsMapLayerRegistry.instance().addMapLayer(vl)

