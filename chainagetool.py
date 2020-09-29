# -*- coding: utf-8 -*-
"""
/***************************************************************************
 __init__.py  -  A Chainage Tool for QGIS
 
        begin                : 2012-10-06
        copyright            : (C) 2012 by Werner Macho
        email                : werner.macho at gmail dot com
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
from __future__ import print_function

from qgis.PyQt.QtCore import (
    QVariant
)
from qgis.core import (
    QgsVectorLayer,
    QgsGeometry,
    QgsProject,
    QgsField,
    QgsFields,
    QgsFeature,
    QgsMessageLog,
    QgsUnitTypes,
    QgsDistanceArea
)


def create_points(startpoint,
                  endpoint,
                  distance,
                  geom,
                  fid,
                  force_last,
                  force_first_last,
                  divide):
    """Creating Points at coordinates along the line
    """
    # don't allow distance to be zero or/and loop endlessly
    if force_first_last:
        distance = 0

    if distance <= 0:
        distance = geom.length()

    length = geom.length()

    if length < endpoint:
        endpoint = length

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
    # convert 3D geometry to 2D geometry as OGR seems to have problems with this
    point = QgsGeometry.fromPointXY(point.asPoint())

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
    if force_last is True:
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
                      layer,
                      selected_only=True,
                      force_last=False,
                      force_first_last=False,
                      divide=0):
    """Adding Points along the line
    """

    crs = layer.crs().authid()

    layer_type = "memory"

    virt_layer = QgsVectorLayer("Point?crs=%s" % crs,
                                layerout,
                                layer_type)
    provider = virt_layer.dataProvider()
    virt_layer.startEditing()   # actually writes attributes

    units = layer.crs().mapUnits()

    unitname = QgsUnitTypes.toString(units)
    provider.addAttributes([QgsField("fid", QVariant.Int),
                            QgsField("cng"+unitname, QVariant.Double)])

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

        features = create_points(startpoint,
                                 endpoint,
                                 distance,
                                 geom,
                                 fid,
                                 force_last,
                                 force_first_last,
                                 divide)
        provider.addFeatures(features)
        virt_layer.updateExtents()

    proj = QgsProject.instance()
    proj.addMapLayers([virt_layer])
    virt_layer.commitChanges()
    virt_layer.reload()
    virt_layer.triggerRepaint()
    return
