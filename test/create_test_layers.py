#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manual Test Script for QChainage Plugin
Run this in QGIS Python Console to create test layers and test all features

Copyright (c) 2025 Werner Macho
Licensed under GNU GPL v3.0
"""

from qgis.core import (
    QgsVectorLayer,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsProject,
    QgsCoordinateReferenceSystem,
)
from qgis.utils import iface


def create_test_layers():
    """
    Create test layers for manual testing of QChainage plugin.
    Run this function in QGIS Python console.
    """
    
    print("Creating test layers for QChainage...")
    
    # Test 1: UTM projected layer (meters)
    print("\n1. Creating UTM test layer (100m horizontal line)...")
    crs_utm = QgsCoordinateReferenceSystem("EPSG:32633")
    layer_utm = QgsVectorLayer(f"LineString?crs={crs_utm.authid()}", 
                                "Test_UTM_100m", "memory")
    
    feat1 = QgsFeature()
    feat1.setGeometry(QgsGeometry.fromPolylineXY([
        QgsPointXY(500000, 6000000),
        QgsPointXY(500100, 6000000)
    ]))
    layer_utm.dataProvider().addFeature(feat1)
    layer_utm.updateExtents()
    QgsProject.instance().addMapLayer(layer_utm)
    print("   ✓ Created 100m line for basic testing")
    
    # Test 2: Multiple features for selection testing
    print("\n2. Creating multi-feature layer (3 lines of 50m each)...")
    layer_multi = QgsVectorLayer(f"LineString?crs={crs_utm.authid()}", 
                                  "Test_Multiple_Features", "memory")
    
    lines = [
        [(500000, 6000000), (500050, 6000000)],  # Line 1: 50m
        [(500000, 6000100), (500050, 6000100)],  # Line 2: 50m
        [(500000, 6000200), (500050, 6000200)],  # Line 3: 50m
    ]
    
    for line_coords in lines:
        feat = QgsFeature()
        feat.setGeometry(QgsGeometry.fromPolylineXY([
            QgsPointXY(x, y) for x, y in line_coords
        ]))
        layer_multi.dataProvider().addFeature(feat)
    
    layer_multi.updateExtents()
    QgsProject.instance().addMapLayer(layer_multi)
    print("   ✓ Created 3 lines (50m each)")
    print("   → Test 'selected only' by selecting 1 or 2 lines")
    
    # Test 3: Longer line for divide and km testing
    print("\n3. Creating long line (5000m = 5km)...")
    layer_long = QgsVectorLayer(f"LineString?crs={crs_utm.authid()}", 
                                 "Test_Long_5km", "memory")
    
    feat_long = QgsFeature()
    feat_long.setGeometry(QgsGeometry.fromPolylineXY([
        QgsPointXY(500000, 6000000),
        QgsPointXY(505000, 6000000)
    ]))
    layer_long.dataProvider().addFeature(feat_long)
    layer_long.updateExtents()
    QgsProject.instance().addMapLayer(layer_long)
    print("   ✓ Created 5000m line")
    print("   → Test with km units (1 km = 6 points)")
    print("   → Test divide mode (e.g., divide=10 = 11 points)")
    
    # Test 4: Geographic CRS layer (lat/lon)
    print("\n4. Creating geographic layer (lat/lon along equator)...")
    crs_geo = QgsCoordinateReferenceSystem("EPSG:4326")
    layer_geo = QgsVectorLayer(f"LineString?crs={crs_geo.authid()}", 
                                "Test_Geographic_WGS84", "memory")
    
    feat_geo = QgsFeature()
    # 1 degree along equator ≈ 111.3 km
    feat_geo.setGeometry(QgsGeometry.fromPolylineXY([
        QgsPointXY(0, 0),
        QgsPointXY(1, 0)
    ]))
    layer_geo.dataProvider().addFeature(feat_geo)
    layer_geo.updateExtents()
    QgsProject.instance().addMapLayer(layer_geo)
    print("   ✓ Created 1° line along equator (≈111.3 km)")
    print("   → Test Ellipsoidal: 20000m spacing = 6 points")
    print("   → Test Cartesian: will give wrong results with meters!")
    
    # Test 5: Diagonal line for angle testing
    print("\n5. Creating diagonal line (100m at 45°)...")
    layer_diag = QgsVectorLayer(f"LineString?crs={crs_utm.authid()}", 
                                 "Test_Diagonal_45deg", "memory")
    
    # 45 degree diagonal, length ≈ 141.4m
    import math
    length = 100
    dx = length * math.cos(math.radians(45))
    dy = length * math.sin(math.radians(45))
    
    feat_diag = QgsFeature()
    feat_diag.setGeometry(QgsGeometry.fromPolylineXY([
        QgsPointXY(500000, 6000000),
        QgsPointXY(500000 + dx, 6000000 + dy)
    ]))
    layer_diag.dataProvider().addFeature(feat_diag)
    layer_diag.updateExtents()
    QgsProject.instance().addMapLayer(layer_diag)
    print(f"   ✓ Created {length}m diagonal line")
    
    # Test 6: Short line for precision testing
    print("\n6. Creating short line (10m)...")
    layer_short = QgsVectorLayer(f"LineString?crs={crs_utm.authid()}", 
                                  "Test_Short_10m", "memory")
    
    feat_short = QgsFeature()
    feat_short.setGeometry(QgsGeometry.fromPolylineXY([
        QgsPointXY(500000, 6000000),
        QgsPointXY(500010, 6000000)
    ]))
    layer_short.dataProvider().addFeature(feat_short)
    layer_short.updateExtents()
    QgsProject.instance().addMapLayer(layer_short)
    print("   ✓ Created 10m line")
    print("   → Test with small distances (e.g., 2m = 6 points)")
    
    # Zoom to extent of first layer
    iface.mapCanvas().setExtent(layer_utm.extent())
    iface.mapCanvas().refresh()
    
    print("\n" + "="*70)
    print("All test layers created successfully!")
    print("="*70)
    print("\nMANUAL TEST CHECKLIST:")
    print("\nTest Cases to Perform:")
    print("\n1. BASIC CHAINAGE (Test_UTM_100m):")
    print("   □ All features, 10m spacing → 11 points (0-100m)")
    print("   □ Force last point, 30m spacing → 5 points (0,30,60,90,100)")
    print("   □ Force first/last only → 2 points (0,100)")
    print("   □ Start=20, End=80, 15m spacing → 5 points (20,35,50,65,80)")
    
    print("\n2. SELECTED FEATURES (Test_Multiple_Features):")
    print("   □ Select line 1 only → points only on that line")
    print("   □ Select lines 1 & 2 → points on both")
    print("   □ All features (no selection) → points on all 3 lines")
    
    print("\n3. DIVIDE MODE (Test_Long_5km):")
    print("   □ Divide=5 → 6 points (1000m spacing)")
    print("   □ Divide=10 → 11 points (500m spacing)")
    print("   □ Start=1000, End=4000, Divide=6 → 7 points")
    
    print("\n4. DISTANCE UNITS (Test_Long_5km):")
    print("   □ 1 kilometer → 6 points (0,1,2,3,4,5 km)")
    print("   □ 500 meters → 11 points")
    print("   □ 1640 feet (≈500m) → ~11 points")
    
    print("\n5. PROJECTION MODES (Test_Geographic_WGS84):")
    print("   □ Ellipsoidal + 20km meters → 6 points (correct!)")
    print("   □ Cartesian + 20000 meters → wrong/error (degrees≠meters)")
    print("   □ Should see warning for Cartesian on geographic CRS")
    
    print("\n6. ELLIPSOIDAL vs CARTESIAN (Test_UTM_100m):")
    print("   □ Both should give same results on projected CRS")
    print("   □ Small difference on very long lines")
    
    print("\n7. EDGE CASES:")
    print("   □ Test_Short_10m: 2m spacing → 6 points")
    print("   □ Distance larger than line length → 2 points max")
    print("   □ Zero distance (should show error or use force_first_last)")
    
    print("\n" + "="*70)
    print(" Tips:")
    print("   - Use 'Select Features' tool to test selected-only mode")
    print("   - Check attribute table of output layers to verify distances")
    print("   - Compare Ellipsoidal vs Cartesian on geographic layer")
    print("   - Verify units field shows correct CRS units")
    print("="*70)


def print_test_instructions():
    """Print testing instructions."""
    print("\n" + "="*70)
    print("QCHAINAGE MANUAL TESTING INSTRUCTIONS")
    print("="*70)
    print("\nTO CREATE TEST LAYERS:")
    print("1. Open QGIS Python Console (Ctrl+Alt+P)")
    print("2. Copy and paste this entire script")
    print("3. Run: create_test_layers()")
    print("\nTO RUN AUTOMATED TESTS:")
    print("1. In terminal, navigate to test directory")
    print("2. Run: python3 test_qchainage.py")
    print("="*70 + "\n")


# Auto-run if executed directly in console
if __name__ == '__console__':
    create_test_layers()
else:
    print_test_instructions()
