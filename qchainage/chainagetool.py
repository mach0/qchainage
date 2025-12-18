# -*- coding: utf-8 -*-
"""
QChainage Plugin - Chainage Tool
Creates points at specified intervals along line geometries.

Copyright (c) 2012-2024 Werner Macho
Licensed under GNU GPL v3.0
"""

import math
from qgis.PyQt.QtCore import QVariant
from qgis.core import (
    QgsVectorLayer,
    QgsGeometry,
    QgsProject,
    QgsField,
    QgsFields,
    QgsFeature,
    QgsUnitTypes,
    QgsDistanceArea,
    QgsMessageLog,
    QgsWkbTypes,
    QgsPointXY,
)


def _extract_coordinates(geometry):
    """Extract coordinates from geometry using the most reliable method."""
    # Try vertices() iterator first (most direct access)
    try:
        coords = list(geometry.vertices())
        if len(coords) >= 2:
            return coords
    except:
        pass
    
    # Fallback to asPolyline()
    try:
        if geometry.isMultipart():
            parts = geometry.asMultiPolyline()
            return parts[0] if parts else []
        return geometry.asPolyline()
    except:
        return []


def calculate_cartesian_distance(geometry):
    """Calculate cartesian distance using raw coordinates (Euclidean distance)."""
    coords = _extract_coordinates(geometry)
    
    if len(coords) < 2:
        return 0.0
    
    total_distance = 0.0
    for i in range(len(coords) - 1):
        dx = coords[i + 1].x() - coords[i].x()
        dy = coords[i + 1].y() - coords[i].y()
        total_distance += math.sqrt(dx * dx + dy * dy)
    
    return total_distance


def setup_distance_calculator(layer_crs, use_ellipsoidal):
    """Set up distance calculator based on calculation mode."""
    if not use_ellipsoidal:
        return None
    
    distance_area = QgsDistanceArea()
    
    if layer_crs:
        distance_area.setSourceCrs(layer_crs, QgsProject.instance().transformContext())
    
    ellipsoid = QgsProject.instance().ellipsoid()
    distance_area.setEllipsoid(ellipsoid if ellipsoid != "NONE" else "WGS84")
    
    return distance_area


def get_line_length(geometry, distance_area, use_ellipsoidal):
    """Calculate line length using ellipsoidal or cartesian method."""
    return (distance_area.measureLength(geometry) if use_ellipsoidal 
            else calculate_cartesian_distance(geometry))


def create_feature_with_point(fields, point_geometry, distance_value, feature_id):
    """Create a feature with point geometry and attributes."""
    if point_geometry.isNull() or point_geometry.isEmpty():
        return None
    
    feature = QgsFeature(fields)
    feature.setGeometry(QgsGeometry.fromPointXY(point_geometry.asPoint()))
    feature['dist'] = distance_value
    feature['id'] = feature_id
    
    return feature


def create_points_by_distance(startpoint, endpoint, distance, geom, fid, force_last,
                              force_first_last, divide, distance_area, distance_units=None):
    """Create points at real-world distance intervals along a line (for geographic CRS)."""
    # Convert input distances to meters for measurement
    if distance_units is None:
        distance_units = QgsUnitTypes.DistanceMeters
    
    to_meters = QgsUnitTypes.fromUnitToUnitFactor(distance_units, QgsUnitTypes.DistanceMeters)
    distance_in_meters = distance * to_meters
    startpoint_in_meters = startpoint * to_meters
    endpoint_in_meters = endpoint * to_meters if endpoint > 0 else 0
    
    # Measure total line length in meters
    total_length_meters = distance_area.measureLength(geom)
    
    # Adjust endpoint
    if endpoint_in_meters <= 0 or endpoint_in_meters > total_length_meters:
        endpoint_in_meters = total_length_meters
    
    # Calculate distance for division mode
    if divide > 0:
        distance_in_meters = (endpoint_in_meters - startpoint_in_meters) / divide
    elif force_first_last:
        distance_in_meters = endpoint_in_meters - startpoint_in_meters
    
    # Safety check
    if distance_in_meters <= 0:
        return []
    
    # Prepare feature fields
    fields = QgsFields()
    fields.append(QgsField("id", QVariant.Int))
    fields.append(QgsField("dist", QVariant.Double))
    
    features = []
    
    # We need to walk along the line in degrees and measure distance in meters
    # Sample the line to create a distance-to-position mapping
    cartesian_length = calculate_cartesian_distance(geom)
    num_samples = max(100, int(cartesian_length / 0.0001))  # Sample every ~0.0001 degrees
    
    # Build distance map: accumulated meter distance -> degree distance
    distance_map = [(0.0, 0.0)]  # (meters, degrees)
    accumulated_meters = 0.0
    last_point = geom.interpolate(0)
    
    for i in range(1, num_samples + 1):
        degree_dist = (cartesian_length * i) / num_samples
        current_point = geom.interpolate(degree_dist)
        
        # Measure segment in meters
        segment_geom = QgsGeometry.fromPolylineXY([
            last_point.asPoint(),
            current_point.asPoint()
        ])
        segment_meters = distance_area.measureLength(segment_geom)
        accumulated_meters += segment_meters
        
        distance_map.append((accumulated_meters, degree_dist))
        last_point = current_point
    
    # Now create points at the requested meter intervals
    current_meter_distance = startpoint_in_meters
    
    while current_meter_distance <= endpoint_in_meters:
        # Find the corresponding degree distance
        degree_dist = interpolate_from_map(distance_map, current_meter_distance)
        
        if degree_dist is not None:
            point = geom.interpolate(degree_dist)
            # Store distance in original units
            distance_in_original_units = current_meter_distance / to_meters
            feature = create_feature_with_point(fields, point, distance_in_original_units, fid)
            if feature:
                features.append(feature)
        
        current_meter_distance += distance_in_meters
        
        if distance_in_meters <= 0:
            break
    
    # Add last point if requested
    if force_last and (not features or abs(features[-1]['dist'] * to_meters - endpoint_in_meters) > 0.01):
        degree_dist = interpolate_from_map(distance_map, endpoint_in_meters)
        if degree_dist is not None:
            point = geom.interpolate(degree_dist)
            distance_in_original_units = endpoint_in_meters / to_meters
            feature = create_feature_with_point(fields, point, distance_in_original_units, fid)
            if feature:
                features.append(feature)
    
    return features


def interpolate_from_map(distance_map, target_meters):
    """Interpolate degree distance from meter distance using the distance map."""
    if not distance_map:
        return None
    
    # Find the two points to interpolate between
    for i in range(len(distance_map) - 1):
        meters1, degrees1 = distance_map[i]
        meters2, degrees2 = distance_map[i + 1]
        
        if meters1 <= target_meters <= meters2:
            if meters2 - meters1 > 0:
                ratio = (target_meters - meters1) / (meters2 - meters1)
                return degrees1 + ratio * (degrees2 - degrees1)
            else:
                return degrees1
    
    # If beyond the end, return the last value
    return distance_map[-1][1]


def create_feature_with_point(fields, point_geometry, distance_value, feature_id):
    """Create a feature with point geometry and attributes."""
    if point_geometry.isNull() or point_geometry.isEmpty():
        return None
    
    feature = QgsFeature(fields)
    feature.setGeometry(QgsGeometry.fromPointXY(point_geometry.asPoint()))
    feature['dist'] = distance_value
    feature['id'] = feature_id
    
    return feature


def create_points(startpoint, endpoint, distance, geom, fid, force_last, 
                  force_first_last, divide, layer_crs=None, use_ellipsoidal=True,
                  distance_units=None):
    """Create points at specified intervals along a line geometry."""
    # Validate geometry
    if not geom or geom.isNull() or geom.isEmpty() or geom.type() != QgsWkbTypes.LineGeometry:
        return []
    
    # Set up distance calculation
    distance_area = setup_distance_calculator(layer_crs, use_ellipsoidal)
    
    # Get layer units
    layer_units = layer_crs.mapUnits() if layer_crs else QgsUnitTypes.DistanceMeters
    
    # If no distance units provided, use layer units
    if distance_units is None:
        distance_units = layer_units
    
    # For geographic CRS with any linear unit input (meters, centimeters, feet, etc.),
    # we need to use a different approach because geom.interpolate() works in degrees
    is_geographic = layer_units == QgsUnitTypes.DistanceDegrees
    is_linear_unit = distance_units != QgsUnitTypes.DistanceDegrees
    use_meter_based_placement = is_geographic and is_linear_unit
    
    if use_meter_based_placement:
        # For linear unit placement on geographic CRS, we MUST use ellipsoidal measurements
        # even if user selected cartesian mode, because we need real-world distances
        if distance_area is None:
            distance_area = setup_distance_calculator(layer_crs, True)
        
        # Use distance mapping for real-world distance placement
        return create_points_by_distance(
            startpoint, endpoint, distance, geom, fid, force_last,
            force_first_last, divide, distance_area, distance_units
        )
    
    # Standard approach: work in layer units
    # Get total line length in layer units
    length = calculate_cartesian_distance(geom) if is_geographic else distance_area.measureLength(geom)
    
    # Convert distance from user units to layer units if needed
    if distance_units != layer_units and distance > 0:
        conversion_factor = QgsUnitTypes.fromUnitToUnitFactor(distance_units, layer_units)
        if conversion_factor > 0:
            distance *= conversion_factor
            startpoint *= conversion_factor
            if endpoint > 0:
                endpoint *= conversion_factor
    
    # Calculate distance if needed (for force_first_last mode)
    if force_first_last or distance <= 0:
        distance = length
    
    # Validate and adjust parameters
    startpoint = max(0, min(startpoint, length))
    endpoint = min(endpoint if endpoint > 0 else length, length)
    
    if startpoint > length:
        return []
    
    # Calculate distance for division mode
    if divide > 0:
        distance = (endpoint - startpoint) / divide
    
    # Prepare feature fields
    fields = QgsFields()
    fields.append(QgsField("id", QVariant.Int))
    fields.append(QgsField("dist", QVariant.Double))
    
    features = []
    current_distance = startpoint
    
    # Create points along the line
    while current_distance <= endpoint:
        point = geom.interpolate(current_distance)
        feature = create_feature_with_point(fields, point, current_distance, fid)
        if feature:
            features.append(feature)
        
        # Move to next distance
        current_distance += distance
        
        # Safety check to prevent infinite loop
        if distance <= 0:
            break
    
    # Add last point if requested and not already added
    if force_last and (not features or features[-1]['dist'] < length):
        point = geom.interpolate(length)
        feature = create_feature_with_point(fields, point, length, fid)
        if feature:
            features.append(feature)
    
    return features


def points_along_line(layerout, startpoint, endpoint, distance, layer,
                      selected_only=True, force_last=False, force_first_last=False,
                      divide=0, use_ellipsoidal=True, distance_units=None):
    """Create a memory layer with points at specified intervals along line features."""
    # Create output layer
    virt_layer = QgsVectorLayer(
        f"Point?crs={layer.crs().authid()}", 
        layerout, 
        "memory"
    )
    provider = virt_layer.dataProvider()
    
    # Set up layer attributes
    unitname = QgsUnitTypes.toString(layer.crs().mapUnits())
    provider.addAttributes([
        QgsField("source_fid", QVariant.Int),
        QgsField(f"cng_{unitname}", QVariant.Double)
    ])
    virt_layer.updateFields()
    
    # If no distance units provided, use layer units
    if distance_units is None:
        distance_units = layer.crs().mapUnits()
    
    # Process features
    features_to_process = (layer.selectedFeatures() if selected_only 
                          else layer.getFeatures())
    
    all_point_features = []
    for feature in features_to_process:
        geom = feature.geometry()
        if geom:
            point_features = create_points(
                startpoint, endpoint, distance, geom, feature.id(), 
                force_last, force_first_last, divide, layer.crs(), use_ellipsoidal,
                distance_units
            )
            all_point_features.extend(point_features)
    
    # Add all features at once (more efficient)
    if all_point_features:
        provider.addFeatures(all_point_features)
    
    virt_layer.updateExtents()
    QgsProject.instance().addMapLayers([virt_layer])
    virt_layer.triggerRepaint()
