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
    fet.setAttributeMap( { 0 : startpoint } )
    fet.setGeometry(point)
    #fet.setGeometry( QgsGeometry().fromPoint( geom.asPolyline()[0] ) )
    feats.append(fet)

    while startpoint + currentdistance <= length:
        # Get a point along the line at the current distance
        point = geom.interpolate(startpoint + currentdistance)
        # Create a new QgsFeature and assign it the new geometry
        fet = QgsFeature()
        fet.setAttributeMap( { 0 : startpoint + currentdistance } )
        fet.setGeometry(point)
        feats.append(fet)
        # Increase the distance
        currentdistance = currentdistance + distance

    return feats

def pointsAlongLine(layerout, startpoint, endpoint, distance, crs, iface):
    # Create a new memory layer and add a distance attributeself.layerNameLine
    vl = QgsVectorLayer("Point", layerout, "memory")
    vl.setCrs(crs)
    pr = vl.dataProvider()
    vl.startEditing()   #actually writes attributes
    pr.addAttributes( [ QgsField("chainage", QVariant.Int) ] )
    layer = iface.mapCanvas().currentLayer()
    # Loop though all the selected features
    for feature in layer.selectedFeatures():
        geom = feature.geometry()
        features = createPointsAt(startpoint, endpoint, distance, geom)
        pr.addFeatures(features)
        vl.updateExtents()
    vl.setCrs(crs)
    vl.commitChanges()
    vl.reload()
    
    QgsMapLayerRegistry.instance().addMapLayer(vl)

