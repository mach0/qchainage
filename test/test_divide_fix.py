#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick test script to verify divide mode fix
Run this to test both projected and geographic CRS
"""

import sys
from pathlib import Path

# Add plugin path
plugin_path = Path(__file__).parent.parent / 'qchainage'
sys.path.insert(0, str(plugin_path))

from qgis.core import (
    QgsApplication,
    QgsVectorLayer,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsProject,
    QgsCoordinateReferenceSystem,
    QgsUnitTypes,
)

from chainagetool import points_along_line


def test_divide_projected():
    """Test divide mode on projected CRS (UTM)."""
    print("\n" + "="*70)
    print("TEST 1: Divide mode on PROJECTED CRS (EPSG:32633 - UTM)")
    print("="*70)
    
    crs = QgsCoordinateReferenceSystem("EPSG:32633")
    layer = QgsVectorLayer(f"LineString?crs={crs.authid()}", "test_utm", "memory")
    
    # Create 100m line
    feat = QgsFeature()
    feat.setGeometry(QgsGeometry.fromPolylineXY([
        QgsPointXY(500000, 6000000),
        QgsPointXY(500100, 6000000)
    ]))
    layer.dataProvider().addFeature(feat)
    layer.updateExtents()
    
    # Test: Divide into 3 parts
    print("Line: 100m horizontal")
    print("Divide into: 3 parts")
    print("Expected: 4 points at 0, 33.33, 66.67, 100m")
    
    points_along_line(
        layerout="test_utm_divide3",
        startpoint=0,
        endpoint=0,
        distance=0,
        layer=layer,
        selected_only=False,
        force_last=False,
        force_first_last=False,
        divide=3,
        use_ellipsoidal=True,
        distance_units=QgsUnitTypes.DistanceMeters
    )
    
    # Check results
    result_layers = QgsProject.instance().mapLayersByName("test_utm_divide3")
    if result_layers:
        result_layer = result_layers[0]
        count = result_layer.featureCount()
        print(f"\n✓ Result: {count} points created")
        
        # Show actual distances
        print("  Distances:")
        for feat in result_layer.getFeatures():
            dist = feat.attribute('cng_meters')
            print(f"    - {dist:.2f}m")
        
        if count == 4:
            print("\n✅ TEST PASSED: Correct number of points (4)")
        else:
            print(f"\n❌ TEST FAILED: Expected 4 points, got {count}")
            return False
    else:
        print("❌ TEST FAILED: Output layer not created")
        return False
    
    QgsProject.instance().removeAllMapLayers()
    return True


def test_divide_geographic():
    """Test divide mode on geographic CRS (WGS84)."""
    print("\n" + "="*70)
    print("TEST 2: Divide mode on GEOGRAPHIC CRS (EPSG:4326 - WGS84)")
    print("="*70)
    
    crs = QgsCoordinateReferenceSystem("EPSG:4326")
    layer = QgsVectorLayer(f"LineString?crs={crs.authid()}", "test_geo", "memory")
    
    # Create 1 degree line along equator (≈111.3 km)
    feat = QgsFeature()
    feat.setGeometry(QgsGeometry.fromPolylineXY([
        QgsPointXY(0, 0),
        QgsPointXY(1, 0)
    ]))
    layer.dataProvider().addFeature(feat)
    layer.updateExtents()
    
    # Test: Divide into 4 parts
    print("Line: 1° along equator (≈111.3 km)")
    print("Divide into: 4 parts")
    print("Expected: 5 points")
    
    points_along_line(
        layerout="test_geo_divide4",
        startpoint=0,
        endpoint=0,
        distance=0,
        layer=layer,
        selected_only=False,
        force_last=False,
        force_first_last=False,
        divide=4,
        use_ellipsoidal=True,
        distance_units=QgsUnitTypes.DistanceMeters
    )
    
    # Check results
    result_layers = QgsProject.instance().mapLayersByName("test_geo_divide4")
    if result_layers:
        result_layer = result_layers[0]
        count = result_layer.featureCount()
        print(f"\n✓ Result: {count} points created")
        
        # Show actual distances
        print("  Distances:")
        for feat in result_layer.getFeatures():
            dist = feat.attribute('cng_meters')
            print(f"    - {dist:.0f}m")
        
        if count == 5:
            print("\n✅ TEST PASSED: Correct number of points (5)")
        else:
            print(f"\n❌ TEST FAILED: Expected 5 points, got {count}")
            return False
    else:
        print("❌ TEST FAILED: Output layer not created")
        return False
    
    QgsProject.instance().removeAllMapLayers()
    return True


def main():
    """Run all tests."""
    # Initialize QGIS
    qgs = QgsApplication([], False)
    qgs.initQgis()
    
    print("\n" + "="*70)
    print("DIVIDE MODE FIX VERIFICATION")
    print("="*70)
    print("Testing that divide mode includes endpoint for both CRS types")
    
    # Run tests
    test1_passed = test_divide_projected()
    test2_passed = test_divide_geographic()
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Projected CRS (UTM):     {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Geographic CRS (WGS84):  {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print("="*70)
    
    if test1_passed and test2_passed:
        print("\n🎉 ALL TESTS PASSED! Divide mode fix is working correctly.")
        exit_code = 0
    else:
        print("\n⚠️  SOME TESTS FAILED! Please review the fix.")
        exit_code = 1
    
    # Cleanup
    qgs.exitQgis()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
