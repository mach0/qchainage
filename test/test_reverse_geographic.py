#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Reverse Chainage on Geographic CRS (EPSG:4326)

Verifies that reverse chainage works correctly for WGS84.
"""

import sys
import os
from pathlib import Path

# Add plugin path to Python path
plugin_path = Path(__file__).parent.parent / 'qchainage'
sys.path.insert(0, str(plugin_path))

from qgis.core import (
    QgsApplication,
    QgsGeometry,
    QgsPointXY,
    QgsCoordinateReferenceSystem,
    QgsUnitTypes,
)

from chainagetool import create_points

# Initialize QGIS
QgsApplication.setPrefixPath('/usr', True)
qgs = QgsApplication([], False)
qgs.initQgis()

print("\n" + "="*70)
print("REVERSE CHAINAGE TEST - GEOGRAPHIC CRS (EPSG:4326)")
print("="*70)

# Test 1: EPSG:31287 (Projected - UTM)
print("\n" + "="*70)
print("TEST 1: EPSG:31287 (Projected CRS)")
print("="*70)

crs_projected = QgsCoordinateReferenceSystem("EPSG:31287")
line_projected = QgsGeometry.fromPolylineXY([
    QgsPointXY(0, 0),
    QgsPointXY(100, 0)
])

print(f"CRS: {crs_projected.authid()} - {crs_projected.description()}")
print(f"Line: 100m horizontal from (0,0) to (100,0)")
print(f"Distance: 25m intervals\n")

# Forward
points_proj_fwd = create_points(
    startpoint=0, endpoint=100, distance=25,
    geom=line_projected, force_last=True, force_first_last=False, divide=0,
    layer_crs=crs_projected, use_ellipsoidal=False,
    distance_units=QgsUnitTypes.DistanceMeters, reverse=False
)

print(f"Forward: {len(points_proj_fwd)} points")
for p in points_proj_fwd:
    pt = p.geometry().asPoint()
    print(f"  ({pt.x():.1f}, {pt.y():.1f}) @ {p['dist']:.1f}m")

# Reverse
points_proj_rev = create_points(
    startpoint=0, endpoint=100, distance=25,
    geom=line_projected, force_last=True, force_first_last=False, divide=0,
    layer_crs=crs_projected, use_ellipsoidal=False,
    distance_units=QgsUnitTypes.DistanceMeters, reverse=True
)

print(f"\nReverse: {len(points_proj_rev)} points")
for p in points_proj_rev:
    pt = p.geometry().asPoint()
    print(f"  ({pt.x():.1f}, {pt.y():.1f}) @ {p['dist']:.1f}m")

if len(points_proj_fwd) == len(points_proj_rev):
    print("\n EPSG:31287 - Same point count")
else:
    print(f"\n EPSG:31287 - Point count mismatch: {len(points_proj_fwd)} vs {len(points_proj_rev)}")

# Test 2: EPSG:4326 (Geographic - WGS84)
print("\n" + "="*70)
print("TEST 2: EPSG:4326 (Geographic CRS)")
print("="*70)

crs_geographic = QgsCoordinateReferenceSystem("EPSG:4326")
line_geographic = QgsGeometry.fromPolylineXY([
    QgsPointXY(0, 0),
    QgsPointXY(1, 0)  # 1 degree along equator ≈ 111 km
])

print(f"CRS: {crs_geographic.authid()} - {crs_geographic.description()}")
print(f"Line: 1° along equator from (0°,0°) to (1°,0°)")
print(f"Distance: 25000m (25km) intervals\n")

# Forward
points_geo_fwd = create_points(
    startpoint=0, endpoint=0, distance=25000,
    geom=line_geographic, force_last=True, force_first_last=False, divide=0,
    layer_crs=crs_geographic, use_ellipsoidal=True,
    distance_units=QgsUnitTypes.DistanceMeters, reverse=False
)

print(f"Forward: {len(points_geo_fwd)} points")
for p in points_geo_fwd:
    pt = p.geometry().asPoint()
    print(f"  ({pt.x():.4f}°, {pt.y():.4f}°) @ {p['dist']:.0f}m")

# Reverse
points_geo_rev = create_points(
    startpoint=0, endpoint=0, distance=25000,
    geom=line_geographic, force_last=True, force_first_last=False, divide=0,
    layer_crs=crs_geographic, use_ellipsoidal=True,
    distance_units=QgsUnitTypes.DistanceMeters, reverse=True
)

print(f"\nReverse: {len(points_geo_rev)} points")
for p in points_geo_rev:
    pt = p.geometry().asPoint()
    print(f"  ({pt.x():.4f}°, {pt.y():.4f}°) @ {p['dist']:.0f}m")

if len(points_geo_fwd) == len(points_geo_rev):
    print("\n EPSG:4326 - Same point count")
else:
    print(f"\n EPSG:4326 - Point count mismatch: {len(points_geo_fwd)} vs {len(points_geo_rev)}")

# Summary
print("\n" + "="*70)
print("TEST SUMMARY")
print("="*70)
if len(points_proj_fwd) == len(points_proj_rev):
    print(" EPSG:31287 (Projected): Reverse works correctly")
else:
    print(" EPSG:31287 (Projected): Reverse NOT working")

if len(points_geo_fwd) == len(points_geo_rev):
    print(" EPSG:4326 (Geographic): Reverse works correctly")
else:
    print(" EPSG:4326 (Geographic): Reverse NOT working")
print("="*70)

# Cleanup
qgs.exitQgis()
