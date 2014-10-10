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
from qgis.core import QGis, QgsSingleSymbolRendererV2

from PyQt4.QtCore import QVariant


def create_points_at(startpoint, endpoint, distance, geom, fid, force, divide):
    """Creating Points at coordinates along the line
    """
    length = geom.length()

    if divide > 0:
        length2 = length
        if startpoint > 0:
            length2 = length - startpoint
        if endpoint > 0:
            length2 = endpoint
        if startpoint > 0 and endpoint > 0:
            length2 = endpoint - startpoint
        distance = length2 / divide
        current_distance = distance
    else:
        current_distance = distance

    feats = []

    if endpoint > 0:
        length = endpoint

    # set the first point at startpoint
    point = geom.interpolate(startpoint)

    field_id = QgsField(name="id", type=QVariant.Int)
    field = QgsField(name="dist", type=QVariant.Double)
    fields = QgsFields()

    fields.append(field_id)
    fields.append(field)

    feature = QgsFeature(fields)
    feature['dist'] = startpoint
    feature['id'] = fid

    feature.setGeometry(point)
    feats.append(feature)

    while startpoint + current_distance <= length:
        # Get a point along the line at the current distance
        point = geom.interpolate(startpoint + current_distance)
        # Create a new QgsFeature and assign it the new geometry
        feature = QgsFeature(fields)
        feature['dist'] = (startpoint + current_distance)
        feature['id'] = fid
        feature.setGeometry(point)
        feats.append(feature)
        # Increase the distance
        current_distance = current_distance + distance

    # set the last point at endpoint if wanted
    if force is True:
        end = geom.length()
        point = geom.interpolate(end)
        feature = QgsFeature(fields)
        feature['dist'] = end
        feature['id'] = fid
        feature.setGeometry(point)
        feats.append(feature)

    return feats


def points_along_line(layerout,
                      startpoint,
                      endpoint,
                      distance,
                      label,
                      layer,
                      selected_only=True,
                      force=False,
                      divide=0):
    """Adding Points along the line
    """
    # Create a new memory layer and add a distance attribute self.layerNameLine
    #layer_crs = virt_layer.setCrs(layer.crs())
    virt_layer = QgsVectorLayer("Point?crs=%s" % layer.crs().authid(),
                                layerout,
                                "memory")
    provider = virt_layer.dataProvider()
    virt_layer.startEditing()   # actually writes attributes
    units = layer.crs().mapUnits()
    unit_dic = {
        QGis.Degrees: 'Degrees',
        QGis.Meters: 'Meters',
        QGis.Feet: 'Feet',
        QGis.UnknownUnit: 'Unknown'}
    unit = unit_dic.get(units, 'Unknown')
    provider.addAttributes([QgsField("fid", QVariant.Int)])
    provider.addAttributes([QgsField("cng_("+unit+")", QVariant.Int)])

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
        # Add feature ID of selected feature
        fid = feature.id()
        if not geom:
            QgsMessageLog.logMessage("No geometry", "QChainage")
            continue

        features = create_points_at(startpoint, endpoint, distance, geom,
                                    fid, force, divide)
        provider.addFeatures(features)
        virt_layer.updateExtents()

    QgsMapLayerRegistry.instance().addMapLayers([virt_layer])
    virt_layer.commitChanges()
    virt_layer.reload()

    #from here Add labeling
    #generic labeling properties
    if label:
        virt_layer.setCustomProperty("labeling", "pal")
        virt_layer.setCustomProperty("labeling/enabled", "true")
        virt_layer.setCustomProperty("labeling/fieldName", "cng_("+unit+")")
        virt_layer.setCustomProperty("labeling/fontSize", "10")
        virt_layer.setCustomProperty("labeling/multiLineLabels", "true")

        #virt_layer.setCustomProperty("labeling/Size", "5")
    # symbol = QgsMarkerSymbolV2.createSimple({"name": "capital"})
    # virt_layer.setRendererV2(QgsSingleSymbolRendererV2(symbol))
    virt_layer.triggerRepaint()
    return
