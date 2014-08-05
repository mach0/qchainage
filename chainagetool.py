# -*- coding: utf-8 -*-
""""
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
"""
"""
 Main Chainage definitions"""
from qgis.core import QgsVectorLayer, QgsMapLayerRegistry, QgsMarkerSymbolV2
from qgis.core import QgsField, QgsFields, QgsFeature, QgsMessageLog
from qgis.core import QgsSingleSymbolRendererV2

from PyQt4.QtCore import QVariant


def create_points_at(startpoint, endpoint, distance, geom):
    """Creating Points at coordinates along the line
    """
    length = geom.length()
    currentdistance = distance
    feats = []

    if endpoint > 0:
        length = endpoint

    # set the first point at startpoint
    point = geom.interpolate(startpoint)
    field = QgsField(name="foo", type=QVariant.Double)
    fields = QgsFields()
    fields.append(field)

    feature = QgsFeature(fields)
    feature['foo'] = startpoint

    feature.setGeometry(point)
    feats.append(feature)

    while startpoint + currentdistance <= length:
        # Get a point along the line at the current distance
        point = geom.interpolate(startpoint + currentdistance)
        # Create a new QgsFeature and assign it the new geometry
        feature = QgsFeature(fields)
        feature['foo'] = (startpoint + currentdistance)
        feature.setGeometry(point)
        feats.append(feature)
        # Increase the distance
        currentdistance = currentdistance + distance

    return feats


def points_along_line(layerout,
                      startpoint,
                      endpoint,
                      distance,
                      label,
                      layer,
                      selected_only=True):
    """Adding Points along the line
    """
    # Create a new memory layer and add a distance attributeself.layerNameLine
    virt_layer = QgsVectorLayer("Point", layerout, "memory")
    virt_layer.setCrs(layer.crs())
    provider = virt_layer.dataProvider()
    virt_layer.startEditing()   # actually writes attributes
    units = "todo"
    provider.addAttributes([QgsField("cng_("+units+")", QVariant.Int)])
    provider.addAttributes([QgsField("id", QVariant.Int)])

    def get_features():
        """Getting the features
        """
        if selected_only:
            return layer.selectedFeatures()
        else:
            return layer.getFeatures()

    # Loop through all (selected) features
    for feature in get_features():
        geom = feature.geometry()
        if not geom:
            QgsMessageLog.logMessage("No geometry", "QChainage")
            continue

        features = create_points_at(startpoint, endpoint, distance, geom)
        provider.addFeatures(features)
        virt_layer.updateExtents()

    QgsMapLayerRegistry.instance().addMapLayers([virt_layer])
    virt_layer.commitChanges()
    virt_layer.reload()

    #from here Add labeling
    #generic labeling properties
    if label:
        virt_layer.setCustomProperty("labeling/fieldName", "cng_("+units+")")
        virt_layer.setCustomProperty("labeling", "pal")
        virt_layer.setCustomProperty("labeling/fontSize", "10")
        virt_layer.setCustomProperty("labeling/multiLineLabels", "true")
        virt_layer.setCustomProperty("labeling/enabled", "true")
    symbol = QgsMarkerSymbolV2.createSimple({"name": "square"})
    virt_layer.setRendererV2(QgsSingleSymbolRendererV2(symbol))
    virt_layer.triggerRepaint()
    return
