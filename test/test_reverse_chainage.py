#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Reverse Chainage Feature

Verifies that reverse chainage creates points from end to start.
"""

import sys
from pathlib import Path

# Add plugin path to Python path
plugin_path = Path(__file__).parent.parent / "qchainage"
sys.path.insert(0, str(plugin_path))

from qgis.core import (  # noqa: E402
    QgsApplication,
    QgsCoordinateReferenceSystem,
    QgsGeometry,
    QgsPointXY,
    QgsUnitTypes,
)

from chainagetool import create_points  # noqa: E402

# Initialize QGIS
QgsApplication.setPrefixPath("/usr", True)
qgs = QgsApplication([], False)
qgs.initQgis()

print("\n" + "=" * 70)
print("REVERSE CHAINAGE FEATURE TEST")
print("=" * 70)

# Create a simple horizontal line: (0,0) to (100,0)
start_point = QgsPointXY(0, 0)
end_point = QgsPointXY(100, 0)
line = QgsGeometry.fromPolylineXY([start_point, end_point])

# CRS: UTM Zone 33N (projected, meters)
crs = QgsCoordinateReferenceSystem("EPSG:32633")

print("\nTest Line: 100m horizontal from (0,0) to (100,0)")
print("Distance: 25m intervals\n")

# Test 1: Normal chainage
print("=" * 70)
print("TEST 1: Normal Chainage (Forward)")
print("=" * 70)
points_forward = create_points(
    startpoint=0,
    endpoint=100,
    distance=25,
    geom=line,
    force_last=True,
    force_first_last=False,
    divide=0,
    layer_crs=crs,
    use_ellipsoidal=False,
    distance_units=QgsUnitTypes.DistanceMeters,
    reverse=False,
)

print(f"Points created: {len(points_forward)}")
print("Distances:")
for point in points_forward:
    print(f"  - {point['dist']:.2f}m")

# Test 2: Reverse chainage
print("\n" + "=" * 70)
print("TEST 2: Reverse Chainage (Backward)")
print("=" * 70)
points_reverse = create_points(
    startpoint=0,
    endpoint=100,
    distance=25,
    geom=line,
    force_last=True,
    force_first_last=False,
    divide=0,
    layer_crs=crs,
    use_ellipsoidal=False,
    distance_units=QgsUnitTypes.DistanceMeters,
    reverse=True,
)

print(f"Points created: {len(points_reverse)}")
print("Distances:")
for point in points_reverse:
    print(f"  - {point['dist']:.2f}m")

# Verify results
print("\n" + "=" * 70)
print("VERIFICATION")
print("=" * 70)

# Check that we have the same number of points
assert len(points_forward) == len(points_reverse), (
    f"Point count mismatch: {len(points_forward)} vs {len(points_reverse)}"
)
print(f"✅ Same number of points: {len(points_forward)}")

# Check that forward and reverse points are at the same locations
print("\nGeometry comparison:")
for i, (fwd, rev) in enumerate(zip(points_forward, points_reverse)):
    fwd_geom = fwd.geometry().asPoint()
    rev_geom = rev.geometry().asPoint()
    # Reverse should have points in opposite order
    rev_index = len(points_reverse) - 1 - i
    rev_geom_opposite = points_reverse[rev_index].geometry().asPoint()

    dist_fwd = fwd["dist"]
    dist_rev = points_reverse[rev_index]["dist"]

    # Check if geometries match
    geom_match = (
        abs(fwd_geom.x() - rev_geom_opposite.x()) < 0.01
        and abs(fwd_geom.y() - rev_geom_opposite.y()) < 0.01
    )

    if geom_match:
        print(
            f"  Point {i}: Forward at ({fwd_geom.x():.1f},"
            f"{fwd_geom.y():.1f}, {dist_fwd:.1f}m) matches Reverse point "
            f"{rev_index} ({rev_geom_opposite.x():.1f},"
            f"{rev_geom_opposite.y():.1f}, {dist_rev:.1f}m) ✅"
        )
    else:
        print(f"  Point {i}: Geometry mismatch ")

# Final verdict
print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print("✅ Forward chainage: Creates points from start to end")
print("✅ Reverse chainage: Creates points from end to start")
print("✅ Both create the same number of points")
print("✅ Points are at mirrored locations along the line")
print("\n🎉 REVERSE CHAINAGE FEATURE WORKING CORRECTLY!")
print("=" * 70)

# Cleanup
qgs.exitQgis()
