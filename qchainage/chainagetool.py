# -*- coding: utf-8 -*-
"""
QChainage Plugin - Chainage Tool
Creates points at specified intervals along line geometries.

Copyright (c) 2012-2026 Werner Macho
Licensed under GNU GPL v3.0
"""

import bisect
import math
from typing import Any, List, Optional, Tuple

from qgis.PyQt.QtCore import QVariant
from qgis.core import (
    QgsDistanceArea,
    QgsFeature,
    QgsFeatureRequest,
    QgsField,
    QgsFields,
    QgsGeometry,
    QgsPointXY,
    QgsProject,
    QgsUnitTypes,
    QgsVectorLayer,
    QgsWkbTypes,
)


def _extract_coordinates(geometry: QgsGeometry) -> List[Any]:
    """Extract coordinates from geometry.

    Provided for backward compatibility.
    """
    if not geometry or geometry.isEmpty():
        return []

    coords = list(geometry.vertices())
    if len(coords) >= 2:
        return coords

    if geometry.isMultipart():
        parts = geometry.asMultiPolyline()
        return parts[0] if parts else []

    return geometry.asPolyline()


def reverse_geometry(geom: QgsGeometry) -> QgsGeometry:
    """Reverse a geometry preserving multipart structures and 3D/Z/M coords.

    Args:
        geom: Input line geometry.

    Returns:
        Reversed line geometry.
    """
    if not geom or geom.isEmpty():
        return geom
    try:
        abstract_geom = geom.constGet()
        if geom.isMultipart():
            # For multipart geometries, reverse part order & reverse each part
            parts = []
            for i in range(abstract_geom.numGeometries() - 1, -1, -1):
                sub_geom = abstract_geom.geometryN(i)
                parts.append(sub_geom.reversed())
            multi = abstract_geom.createEmptyWithSameType()
            for p in parts:
                multi.addGeometry(p)
            return QgsGeometry(multi)
        return QgsGeometry(abstract_geom.reversed())
    except (AttributeError, TypeError, RuntimeError):
        # Fallback to coordinate reversal if native reversal fails
        coords = _extract_coordinates(geom)
        if coords:
            coords = list(reversed(coords))
            coords_xy = [
                QgsPointXY(pt.x(), pt.y()) if hasattr(pt, 'x') else pt
                for pt in coords
            ]
            return QgsGeometry.fromPolylineXY(coords_xy)
        return geom


def calculate_cartesian_distance(geometry: QgsGeometry) -> float:
    """Calculate cartesian planar distance of a geometry."""
    if not geometry or geometry.isEmpty():
        return 0.0
    return geometry.length()


def setup_distance_calculator(
    layer_crs, use_ellipsoidal: bool
) -> Optional[QgsDistanceArea]:
    """Set up distance calculator based on calculation mode."""
    if not use_ellipsoidal:
        return None

    distance_area = QgsDistanceArea()

    if layer_crs:
        distance_area.setSourceCrs(
            layer_crs, QgsProject.instance().transformContext()
        )

    ellipsoid = QgsProject.instance().ellipsoid()
    distance_area.setEllipsoid(ellipsoid if ellipsoid != "NONE" else "WGS84")

    return distance_area


def get_line_length(
    geometry: QgsGeometry,
    distance_area: Optional[QgsDistanceArea],
    use_ellipsoidal: bool
) -> float:
    """Calculate line length using ellipsoidal or cartesian method."""
    if use_ellipsoidal and distance_area:
        return distance_area.measureLength(geometry)
    return calculate_cartesian_distance(geometry)


def interpolate_from_map(
    distance_map: List[Tuple[float, float]],
    target_meters: float,
    meter_keys: Optional[List[float]] = None
) -> Optional[float]:
    """Interpolate degree distance from meter distance using binary search.

    Args:
        distance_map: List of (accumulated_meters, degree_distance) tuples.
        target_meters: Distance in meters to interpolate at.
        meter_keys: Optional pre-extracted list of accumulated meters.

    Returns:
        Interpolated degree distance along geometry.
    """
    if not distance_map:
        return None

    if meter_keys is None:
        meter_keys = [item[0] for item in distance_map]

    if target_meters <= meter_keys[0]:
        return distance_map[0][1]
    if target_meters >= meter_keys[-1]:
        return distance_map[-1][1]

    idx = bisect.bisect_right(meter_keys, target_meters)
    m1, d1 = distance_map[idx - 1]
    m2, d2 = distance_map[idx]

    if m2 > m1:
        ratio = (target_meters - m1) / (m2 - m1)
        return d1 + ratio * (d2 - d1)
    return d1


def calculate_bearing_degrees(
    geom: QgsGeometry, distance_along_geom: float
) -> float:
    """Calculate tangent bearing (azimuth) along line geometry in [0, 360).

    North = 0°, East = 90°, South = 180°, West = 270°.
    """
    try:
        rad = geom.interpolateAngle(distance_along_geom)
        return round(math.degrees(rad) % 360.0, 3)
    except (AttributeError, TypeError, ValueError):
        return 0.0


def create_feature_with_point(
    fields: QgsFields,
    point_geometry: QgsGeometry,
    distance_value: float,
    source_feature: Optional[QgsFeature] = None,
    copy_attributes: Optional[List[str]] = None,
    angle_value: Optional[float] = None
) -> Optional[QgsFeature]:
    """Create a feature with point geometry and attributes.

    Preserves 3D (Z) and M coordinates from point_geometry.

    Args:
        fields: QgsFields for the output feature
        point_geometry: Point geometry for the feature
        distance_value: Distance value for the distance field
        source_feature: Source feature to copy attributes from (optional)
        copy_attributes: List of attribute names to copy (optional)
        angle_value: Tangent bearing angle in degrees (optional)
    """
    if (
        not point_geometry
        or point_geometry.isNull()
        or point_geometry.isEmpty()
    ):
        return None

    feature = QgsFeature(fields)
    # Directly set point_geometry to preserve 3D (Z) and M dimensions
    feature.setGeometry(point_geometry)

    # Set distance attribute
    if "dist" in fields.names():
        feature["dist"] = distance_value
    elif fields.count() > 0:
        feature[0] = distance_value

    # Set angle attribute if requested and present in fields
    if angle_value is not None and "angle" in fields.names():
        feature["angle"] = angle_value

    # Copy selected attributes from source feature
    if source_feature and copy_attributes:
        source_fields = source_feature.fields()
        for attr_name in copy_attributes:
            if (
                attr_name in source_fields.names()
                and attr_name in fields.names()
            ):
                feature[attr_name] = source_feature[attr_name]

    return feature


def create_points_by_distance(
    startpoint: float,
    endpoint: float,
    distance: float,
    geom: QgsGeometry,
    force_last: bool,
    force_first_last: bool,
    divide: int,
    distance_area: QgsDistanceArea,
    distance_units: Optional[Any] = None,
    source_feature: Optional[QgsFeature] = None,
    copy_attributes: Optional[List[str]] = None,
    reverse: bool = False,
    include_angle: bool = False,
    dist_field_name: str = "dist"
) -> List[QgsFeature]:
    """Create points at real-world distance intervals along a line.

    Used for geographic CRS with linear distance units (e.g. meters/feet).
    """
    if not geom or geom.isNull() or geom.isEmpty():
        return []

    # Reverse geometry if requested
    if reverse:
        geom = reverse_geometry(geom)

    # Convert input distances to meters for measurement
    if distance_units is None:
        distance_units = QgsUnitTypes.DistanceMeters

    to_meters = QgsUnitTypes.fromUnitToUnitFactor(
        distance_units, QgsUnitTypes.DistanceMeters
    )
    if to_meters <= 0:
        to_meters = 1.0

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
        distance_in_meters = (
            endpoint_in_meters - startpoint_in_meters
        ) / divide
    elif force_first_last:
        distance_in_meters = endpoint_in_meters - startpoint_in_meters

    # Safety check
    if distance_in_meters <= 0:
        return []

    # Prepare feature fields
    fields = QgsFields()
    fields.append(QgsField(dist_field_name, QVariant.Double))

    if include_angle:
        fields.append(QgsField("angle", QVariant.Double))

    # Add selected attributes from source feature
    if source_feature and copy_attributes:
        source_fields = source_feature.fields()
        for attr_name in copy_attributes:
            field_index = source_fields.indexFromName(attr_name)
            if field_index >= 0:
                field = source_fields.field(attr_name)
                fields.append(QgsField(field.name(), field.type()))

    features = []

    # Sample the line to create an efficient distance-to-position mapping
    cartesian_length = geom.length()
    geom_length = cartesian_length

    # High performance sample count: bounded between 50 and 1000
    num_samples = min(1000, max(50, int(cartesian_length / 0.001)))

    distance_map = [(0.0, 0.0)]  # (meters, degrees)
    meter_keys = [0.0]
    accumulated_meters = 0.0
    last_point = geom.interpolate(0)
    last_pxy = last_point.asPoint()

    for i in range(1, num_samples + 1):
        degree_dist = (cartesian_length * i) / num_samples
        if degree_dist > geom_length:
            break
        current_point = geom.interpolate(degree_dist)
        curr_pxy = current_point.asPoint()

        # Measure segment directly with measureLine for speed
        segment_meters = distance_area.measureLine(last_pxy, curr_pxy)
        accumulated_meters += segment_meters

        distance_map.append((accumulated_meters, degree_dist))
        meter_keys.append(accumulated_meters)
        last_pxy = curr_pxy

    def _create_pt(meter_dist: float) -> Optional[QgsFeature]:
        deg_dist = interpolate_from_map(distance_map, meter_dist, meter_keys)
        if deg_dist is None:
            return None
        pt = geom.interpolate(deg_dist)
        dist_orig = meter_dist / to_meters
        ang = (
            calculate_bearing_degrees(geom, deg_dist)
            if include_angle else None
        )
        return create_feature_with_point(
            fields, pt, dist_orig, source_feature, copy_attributes, ang
        )

    # For divide mode or force_first_last, use exact calculation
    if divide > 0 or force_first_last:
        num_divisions = divide if divide > 0 else 1

        # Create start point
        feat = _create_pt(startpoint_in_meters)
        if feat:
            features.append(feat)

        # Create intermediate and end points
        for i in range(1, num_divisions + 1):
            if i == num_divisions:
                pt_meter_dist = endpoint_in_meters
            else:
                pt_meter_dist = startpoint_in_meters + (
                    distance_in_meters * i
                )
            feat = _create_pt(pt_meter_dist)
            if feat:
                features.append(feat)
    else:
        # Standard distance-based point creation
        current_meter_distance = startpoint_in_meters
        while current_meter_distance <= endpoint_in_meters:
            feat = _create_pt(current_meter_distance)
            if feat:
                features.append(feat)
            current_meter_distance += distance_in_meters
            if distance_in_meters <= 0:
                break

        # Add last point if requested
        if force_last or force_first_last:
            should_add_endpoint = True
            if features:
                last_feat = features[-1]
                if dist_field_name in last_feat.fields().names():
                    last_dist_val = last_feat[dist_field_name]
                else:
                    last_dist_val = last_feat[0]
                if abs(last_dist_val * to_meters - endpoint_in_meters) < 0.01:
                    should_add_endpoint = False

            if should_add_endpoint:
                feat = _create_pt(endpoint_in_meters)
                if feat:
                    features.append(feat)

    return features


def create_points(
    startpoint: float,
    endpoint: float,
    distance: float,
    geom: QgsGeometry,
    force_last: bool,
    force_first_last: bool,
    divide: int,
    layer_crs: Any = None,
    use_ellipsoidal: bool = True,
    distance_units: Any = None,
    source_feature: Optional[QgsFeature] = None,
    copy_attributes: Optional[List[str]] = None,
    reverse: bool = False,
    include_angle: bool = False,
    dist_field_name: str = "dist"
) -> List[QgsFeature]:
    """Create points at specified intervals along a line geometry.

    Preserves 3D (Z) and M dimensions.
    """
    # Validate geometry
    if (
        not geom
        or geom.isNull()
        or geom.isEmpty()
        or geom.type() != QgsWkbTypes.LineGeometry
    ):
        return []

    # Set up distance calculation
    distance_area = setup_distance_calculator(layer_crs, use_ellipsoidal)

    # Get layer units
    layer_units = (
        layer_crs.mapUnits()
        if layer_crs else QgsUnitTypes.DistanceMeters
    )

    # If no distance units provided, use layer units
    if distance_units is None:
        distance_units = layer_units

    # For geographic CRS with linear unit input, use geographic placement
    is_geographic = layer_units == QgsUnitTypes.DistanceDegrees
    is_linear_unit = distance_units != QgsUnitTypes.DistanceDegrees
    use_meter_based_placement = is_geographic and is_linear_unit

    if use_meter_based_placement:
        if distance_area is None:
            distance_area = setup_distance_calculator(layer_crs, True)

        return create_points_by_distance(
            startpoint=startpoint,
            endpoint=endpoint,
            distance=distance,
            geom=geom,
            force_last=force_last,
            force_first_last=force_first_last,
            divide=divide,
            distance_area=distance_area,
            distance_units=distance_units,
            source_feature=source_feature,
            copy_attributes=copy_attributes,
            reverse=reverse,
            include_angle=include_angle,
            dist_field_name=dist_field_name
        )

    # Standard approach: work in layer units
    if reverse:
        geom = reverse_geometry(geom)

    geom_length = geom.length()

    # Get total line length
    if is_geographic:
        length = geom_length
    else:
        if use_ellipsoidal and distance_area:
            length = distance_area.measureLength(geom)
        else:
            length = geom_length

    # Convert distance from user units to layer units if needed
    conversion_factor = 1.0
    if distance_units != layer_units and distance > 0:
        conversion_factor = QgsUnitTypes.fromUnitToUnitFactor(
            distance_units, layer_units
        )
        if conversion_factor > 0:
            distance *= conversion_factor
            startpoint *= conversion_factor
            if endpoint > 0:
                endpoint *= conversion_factor

    # Calculate distance if needed (for force_first_last mode)
    if force_first_last or distance <= 0:
        distance = length

    # Validate and adjust parameters
    startpoint = max(0.0, min(startpoint, length))
    endpoint = min(endpoint if endpoint > 0 else length, length)

    if startpoint > length:
        return []

    # Scale endpoint to geometry length for interpolation
    endpoint_geom = (
        (endpoint / length * geom_length)
        if length > 0 else geom_length
    )

    # Recalculate distance for force_first_last after endpoint is set
    if force_first_last:
        distance = endpoint - startpoint
        if distance <= 0:
            distance = 1.0

    # Calculate distance for division mode
    if divide > 0:
        distance = (endpoint - startpoint) / divide

    # Prepare feature fields
    fields = QgsFields()
    fields.append(QgsField(dist_field_name, QVariant.Double))

    if include_angle:
        fields.append(QgsField("angle", QVariant.Double))

    # Add selected attributes from source feature
    if source_feature and copy_attributes:
        source_fields = source_feature.fields()
        for attr_name in copy_attributes:
            field_index = source_fields.indexFromName(attr_name)
            if field_index >= 0:
                field = source_fields.field(attr_name)
                fields.append(QgsField(field.name(), field.type()))

    features = []

    def _create_feature_at(
        dist_val: float, dist_geom_val: float
    ) -> Optional[QgsFeature]:
        pt = geom.interpolate(dist_geom_val)
        ang = (
            calculate_bearing_degrees(geom, dist_geom_val)
            if include_angle else None
        )
        # Store attribute in user-requested distance units
        attr_dist = (
            dist_val / conversion_factor
            if conversion_factor > 0 else dist_val
        )
        return create_feature_with_point(
            fields, pt, attr_dist, source_feature, copy_attributes, ang
        )

    # For divide mode or force_first_last, use exact calculation
    if divide > 0 or force_first_last:
        num_divisions = divide if divide > 0 else 1

        # Start point
        start_geom = (
            (startpoint / length * geom_length)
            if length > 0 else startpoint
        )
        feat = _create_feature_at(startpoint, start_geom)
        if feat:
            features.append(feat)

        # Intermediate and end points
        for i in range(1, num_divisions + 1):
            if i == num_divisions:
                pt_dist = endpoint
                pt_geom = endpoint_geom
            else:
                pt_dist = startpoint + (distance * i)
                pt_geom = (
                    (pt_dist / length * geom_length)
                    if length > 0 else pt_dist
                )

            feat = _create_feature_at(pt_dist, pt_geom)
            if feat:
                features.append(feat)
    else:
        # Create points along the line using distance intervals
        current_distance = startpoint
        while current_distance <= endpoint:
            cur_geom = (
                (current_distance / length * geom_length)
                if length > 0 else current_distance
            )
            feat = _create_feature_at(current_distance, cur_geom)
            if feat:
                features.append(feat)
            current_distance += distance
            if distance <= 0:
                break

        # Add last point if requested
        if force_last or force_first_last:
            should_add_endpoint = True
            if features:
                last_f = features[-1]
                if dist_field_name in last_f.fields().names():
                    last_dist = last_f[dist_field_name] * conversion_factor
                else:
                    last_dist = last_f[0] * conversion_factor
                tolerance = max(0.001, abs(endpoint) * 0.001)
                if abs(last_dist - endpoint) < tolerance:
                    should_add_endpoint = False

            if should_add_endpoint:
                feat = _create_feature_at(endpoint, endpoint_geom)
                if feat:
                    features.append(feat)

    return features


def points_along_line(
    layerout: str,
    startpoint: float,
    endpoint: float,
    distance: float,
    layer: QgsVectorLayer,
    selected_only: bool = True,
    force_last: bool = False,
    force_first_last: bool = False,
    divide: int = 0,
    use_ellipsoidal: bool = True,
    distance_units: Any = None,
    copy_attributes: Optional[List[str]] = None,
    reverse: bool = False,
    include_angle: bool = False
) -> Optional[QgsVectorLayer]:
    """Create a memory layer with points at intervals along line features.

    Preserves 3D (Z) and M geometry dimensions from the source layer.
    """
    if not layer or not layer.isValid():
        return None

    # Detect geometry dimensions (Point, PointZ, PointM, PointZM)
    point_type = "Point"
    if QgsWkbTypes.hasZ(layer.wkbType()):
        point_type += "Z"
    if QgsWkbTypes.hasM(layer.wkbType()):
        point_type += "M"

    # Create output layer
    virt_layer = QgsVectorLayer(
        f"{point_type}?crs={layer.crs().authid()}",
        layerout,
        "memory"
    )
    provider = virt_layer.dataProvider()

    # If no distance units provided, use layer units
    if distance_units is None:
        distance_units = layer.crs().mapUnits()

    # Set up layer attributes - use the selected distance units for field name
    unitname = QgsUnitTypes.toString(distance_units)
    dist_field_name = f"cng_{unitname}"

    # Start with standard chainage attribute
    attributes = [
        QgsField(dist_field_name, QVariant.Double)
    ]

    if include_angle:
        attributes.append(QgsField("angle", QVariant.Double))

    # Add selected attributes from source layer
    if copy_attributes:
        source_fields = layer.fields()
        for attr_name in copy_attributes:
            field = source_fields.field(attr_name)
            if field:
                attributes.append(QgsField(field.name(), field.type()))

    provider.addAttributes(attributes)
    virt_layer.updateFields()

    # Build feature request - optimize by only fetching required attributes
    request = QgsFeatureRequest()
    if copy_attributes:
        request.setSubsetOfAttributes(copy_attributes, layer.fields())
    else:
        request.setFlags(QgsFeatureRequest.NoAttributes)

    # Process features
    if selected_only:
        features_to_process = layer.getSelectedFeatures(request)
    else:
        features_to_process = layer.getFeatures(request)

    all_point_features = []
    for feature in features_to_process:
        geom = feature.geometry()
        if geom and not geom.isEmpty():
            point_features = create_points(
                startpoint=startpoint,
                endpoint=endpoint,
                distance=distance,
                geom=geom,
                force_last=force_last,
                force_first_last=force_first_last,
                divide=divide,
                layer_crs=layer.crs(),
                use_ellipsoidal=use_ellipsoidal,
                distance_units=distance_units,
                source_feature=feature,
                copy_attributes=copy_attributes,
                reverse=reverse,
                include_angle=include_angle,
                dist_field_name=dist_field_name
            )
            all_point_features.extend(point_features)

    # Add all features in a single batch
    if all_point_features:
        provider.addFeatures(all_point_features)

    virt_layer.updateExtents()
    QgsProject.instance().addMapLayers([virt_layer])
    virt_layer.triggerRepaint()

    return virt_layer
