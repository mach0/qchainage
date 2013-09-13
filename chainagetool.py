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
""""
 Main Chainage definitions"""
from qgis.core import *
from PyQt4.QtCore import QVariant, QMetaType
from qgis.utils import *


def create_points_at(startpoint, endpoint, distance, geom):
    """Creating Points at coordinate onlong the line
    """
    length = geom.length()
    currentdistance = distance
    feats = []
    
    if endpoint > 0:
        length = endpoint
      
    # set the first point at startpoint
    point = geom.interpolate(startpoint)
    field = QgsField(name="foo" , type=QVariant.Double)
    fields = QgsFields()
    fields.append(field)
    
    fet = QgsFeature(fields)
    
    #print fet[0]
    
    fet['foo'] = startpoint
    
    #print fet[0]
    
    fet.setGeometry(point)
    #fet.setGeometry( QgsGeometry().fromPoint( geom.asPolyline()[0] ) )
    feats.append(fet)

    while startpoint + currentdistance <= length:
        # Get a point along the line at the current distance
        point = geom.interpolate(startpoint + currentdistance)
        # Create a new QgsFeature and assign it the new geometry
        fet = QgsFeature(fields)
        fet['foo'] = (startpoint + currentdistance)
        fet.setGeometry(point)
        feats.append(fet)
        # Increase the distance
        currentdistance = currentdistance + distance

    return feats

def points_along_line(layerout, startpoint, endpoint, distance, label, layer, 
                    selected_only=True):
    """Adding Points along the line
    """
    # Create a new memory layer and add a distance attributeself.layerNameLine
    virt_layer = QgsVectorLayer("Point", layerout, "memory")
    virt_layer.setCrs(layer.crs())
    provider = virt_layer.dataProvider()
    virt_layer.startEditing()   #actually writes attributes
    provider.addAttributes( [ QgsField("chainage", QVariant.Int) ] )
    
    def get_features():
        """Getting the features 
        """
        if selected_only:
            return layer.selectedFeatures()
        else:
            return layer.getFeatures()

    # Loop through all selected features
    for feature in get_features():
        geom = feature.geometry()
        if not geom:
            QgsMessageLog.logMessage("No geom", "QChainage")
            continue

        features = create_points_at(startpoint, endpoint, distance, geom)
        provider.addFeatures(features)
        virt_layer.updateExtents()

    QgsMapLayerRegistry.instance().addMapLayers([virt_layer])
    virt_layer.commitChanges()
    virt_layer.reload()

    #Add labeling from here
    #generic labeling properties
    if label:
        virt_layer.setCustomProperty("labeling/fieldName", "chainage" )  
        # default value provider.fieldNameIndex(layer.displayField())
        virt_layer.setCustomProperty("labeling","pal" ) # new gen labeling activated 
        virt_layer.setCustomProperty("labeling/fontSize","10" ) # default value 
        virt_layer.setCustomProperty("labeling/multiLineLabels","true" )
        virt_layer.setCustomProperty("labeling/enabled","true" ) # default value 
    #style_path = os.path.join( os.path.dirname(__file__), "style.qml" )
    #(errorMsg, result) = vl.loadNamedStyle( style_path )
    symbol = QgsMarkerSymbolV2.createSimple({"name":"square"})
    #layer = qgis.utils.iface.activeLayer()
    virt_layer.rendererV2().setSymbol(symbol)
    virt_layer.triggerRepaint()
    return
