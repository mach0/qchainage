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
from __future__ import print_function
"""
 Main Chainage definitions"""


from qgis.PyQt.QtCore import (
    QVariant,
    QCoreApplication
)
from qgis.core import (
    QgsVectorLayer,
    QgsMarkerSymbol,
    QgsGeometry,
    QgsProject,
    QgsField,
    QgsFields,
    QgsFeature,
    QgsMessageLog,
    QgsPoint,
    Qgis,
    QgsSingleSymbolRenderer,
    QgsVectorFileWriter,
    QgsUnitTypes
)


def create_points_at(startpoint,
                     endpoint,
                     distance,
                     geom,
                     fid,
                     force,
                     fo_fila,
                     divide):
    """Creating Points at coordinates along the line
    """
    # don't allow distance to be zero and loop endlessly
    if fo_fila:
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
                      fo_fila=False,
                      divide=0,
                      decimal=2):
    """Adding Points along the line
    """

    crs = layer.crs().authid()

    # TODO check for virtual or shapelayer and set virt_layer according to it
    shape = False
    if shape:
        # define fields for feature attributes. A list of QgsField objects is needed
        fields = [QgsField("first", QVariant.Int),
                  QgsField("second", QVariant.String)]
        # create an instance of vector file writer, which will create the vector file.
        # Arguments:
        # 1. path to new file (will fail if exists already)
        # 2. encoding of the attributes
        # 3. field map
        # 4. geometry type - from WKBTYPE enum
        # 5. layer's spatial reference (instance of
        #    QgsCoordinateReferenceSystem) - optional
        # 6. driver name for the output file
        writer = QgsVectorFileWriter("my_shapes.shp",
                                     "CP1250",
                                     fields,
                                     Qgis.WKBPoint,
                                     crs,
                                     "ESRI Shapefile")
        if writer.hasError() != QgsVectorFileWriter.NoError:
            # fix_print_with_import
            print("Error when creating shapefile: ", writer.hasError())
        # add a feature
        fet = QgsFeature()
        fet.setGeometry(QgsGeometry.fromPoint(QgsPoint(10, 10)))
        fet.setAttributes([1, "text"])
        writer.addFeature(fet)
        # delete the writer to flush features to disk (optional)
        del writer

        layer_type = "Shapefile"  # TODO Add Shapefile functionality here
    else:
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

        features = create_points_at(startpoint,
                                    endpoint,
                                    distance,
                                    geom,
                                    fid,
                                    force,
                                    fo_fila,
                                    divide)
        provider.addFeatures(features)
        virt_layer.updateExtents()

    proj = QgsProject.instance()
    proj.addMapLayers([virt_layer])
    virt_layer.commitChanges()
    virt_layer.reload()

    # generic labeling properties
    if label:
        virt_layer.setCustomProperty("labeling", "pal")
        virt_layer.setCustomProperty("labeling/enabled", "true")
        virt_layer.setCustomProperty("labeling/fieldName", "cng")
        virt_layer.setCustomProperty("labeling/fontSize", "10")
        virt_layer.setCustomProperty("labeling/multiLineLabels", "true")
        virt_layer.setCustomProperty("labeling/formatNumbers", "true")
        virt_layer.setCustomProperty("labeling/decimals", decimal)
        virt_layer.setCustomProperty("labeling/Size", "5")
    # symbol = QgsMarkerSymbol.createSimple({"name": "capital"})
    # virt_layer.setRenderer(QgsSingleSymbolRenderer(symbol))
    virt_layer.triggerRepaint()
    return
