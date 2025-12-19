#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Test Suite for QChainage Plugin

Tests all interface functions:
- All features vs. selected features
- Force first/last point
- Divide mode
- Different distance units
- Cartesian vs. Ellipsoidal calculations
- Different CRS types (geographic, projected)

Copyright (c) 2025 Werner Macho
Licensed under GNU GPL v3.0
"""

import sys
import os
import unittest
from pathlib import Path

# Add plugin path to Python path
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

from chainagetool import points_along_line, create_points


class TestQChainageSetup(unittest.TestCase):
    """Base class with setup and helper methods."""
    
    @classmethod
    def setUpClass(cls):
        """Initialize QGIS application (only if not already running)."""
        # Check if QgsApplication is already running (e.g., in QGIS Python Console)
        try:
            from qgis.utils import iface
            # If iface exists, we're running inside QGIS
            cls.qgs = None
            cls.running_in_qgis = True
            print("✓ Running inside QGIS - using existing application")
        except ImportError:
            # We're running standalone, need to initialize QGIS
            cls.qgs = QgsApplication([], False)
            cls.qgs.initQgis()
            cls.running_in_qgis = False
            print("✓ Running standalone - initialized QGIS application")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up QGIS application (only if we initialized it)."""
        if cls.qgs is not None:
            cls.qgs.exitQgis()
            print("✓ Cleaned up QGIS application")
    
    def create_line_layer(self, crs_code, name="test_layer"):
        """Create a simple line layer with given CRS."""
        crs = QgsCoordinateReferenceSystem(f"EPSG:{crs_code}")
        layer = QgsVectorLayer(f"LineString?crs={crs.authid()}", name, "memory")
        return layer
    
    def add_line_feature(self, layer, points):
        """Add a line feature to a layer."""
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPolylineXY([QgsPointXY(x, y) for x, y in points]))
        layer.dataProvider().addFeature(feature)
        layer.updateExtents()
        return feature
    
    def count_points_in_layer(self, layer_name):
        """Count points in a layer by name."""
        layers = QgsProject.instance().mapLayersByName(layer_name)
        if layers:
            return layers[0].featureCount()
        return 0


class TestBasicChainage(TestQChainageSetup):
    """Test basic chainage functionality."""
    
    def test_simple_line_all_features(self):
        """Test chainage on all features in a layer."""
        # Create a 100m line in UTM (meters)
        layer = self.create_line_layer(32633, "utm_test")
        self.add_line_feature(layer, [(500000, 6000000), (500100, 6000000)])
        
        # Create points every 10 meters
        points_along_line(
            layerout="test_output",
            startpoint=0,
            endpoint=0,
            distance=10,
            layer=layer,
            selected_only=False,
            force_last=True,
            force_first_last=False,
            divide=0,
            use_ellipsoidal=True,
            distance_units=QgsUnitTypes.DistanceMeters
        )
        
        # Should have 11 points (0, 10, 20, ..., 90, 100)
        count = self.count_points_in_layer("test_output")
        self.assertEqual(count, 11, f"Expected 11 points, got {count}")
        
        # Clean up
        QgsProject.instance().removeAllMapLayers()
    
    def test_selected_features_only(self):
        """Test chainage on selected features only."""
        layer = self.create_line_layer(32633, "utm_test")
        
        # Add two features
        feat1 = self.add_line_feature(layer, [(500000, 6000000), (500100, 6000000)])
        feat2 = self.add_line_feature(layer, [(500200, 6000000), (500300, 6000000)])
        
        # Select only the first feature
        layer.selectByIds([feat1.id()])
        
        # Create points every 25 meters on selected features only
        points_along_line(
            layerout="test_selected",
            startpoint=0,
            endpoint=0,
            distance=25,
            layer=layer,
            selected_only=True,
            force_last=True,
            force_first_last=False,
            divide=0,
            use_ellipsoidal=True,
            distance_units=QgsUnitTypes.DistanceMeters
        )
        
        # Should have 5 points from first feature only (0, 25, 50, 75, 100)
        count = self.count_points_in_layer("test_selected")
        self.assertEqual(count, 5, f"Expected 5 points from selected feature, got {count}")
        
        # Clean up
        QgsProject.instance().removeAllMapLayers()
    
    def test_force_last_point(self):
        """Test force_last option ensures endpoint is included."""
        layer = self.create_line_layer(32633, "utm_test")
        self.add_line_feature(layer, [(500000, 6000000), (500095, 6000000)])  # 95m line
        
        # Create points every 30 meters with force_last
        points_along_line(
            layerout="test_force_last",
            startpoint=0,
            endpoint=0,
            distance=30,
            layer=layer,
            selected_only=False,
            force_last=True,  # Force endpoint
            force_first_last=False,
            divide=0,
            use_ellipsoidal=True,
            distance_units=QgsUnitTypes.DistanceMeters
        )
        
        # Should have points at 0, 30, 60, 90, and 95 (forced) = 5 points
        count = self.count_points_in_layer("test_force_last")
        self.assertEqual(count, 5, f"Expected 5 points with forced last, got {count}")
        
        # Clean up
        QgsProject.instance().removeAllMapLayers()
    
    def test_force_first_last_only(self):
        """Test force_first_last creates only start and end points."""
        layer = self.create_line_layer(32633, "utm_test")
        self.add_line_feature(layer, [(500000, 6000000), (500100, 6000000)])
        
        # Create only first and last points
        points_along_line(
            layerout="test_first_last",
            startpoint=0,
            endpoint=0,
            distance=0,  # Ignored when force_first_last=True
            layer=layer,
            selected_only=False,
            force_last=False,
            force_first_last=True,  # Only endpoints
            divide=0,
            use_ellipsoidal=True,
            distance_units=QgsUnitTypes.DistanceMeters
        )
        
        # Should have exactly 2 points
        count = self.count_points_in_layer("test_first_last")
        self.assertEqual(count, 2, f"Expected 2 points (first and last), got {count}")
        
        # Clean up
        QgsProject.instance().removeAllMapLayers()


class TestDivideMode(TestQChainageSetup):
    """Test divide mode functionality."""
    
    def test_divide_into_segments(self):
        """Test dividing line into equal segments."""
        layer = self.create_line_layer(32633, "utm_test")
        self.add_line_feature(layer, [(500000, 6000000), (500100, 6000000)])  # 100m
        
        # Divide into 5 equal segments (will create 6 points: 0, 20, 40, 60, 80, 100)
        points_along_line(
            layerout="test_divide",
            startpoint=0,
            endpoint=0,
            distance=0,  # Ignored when divide > 0
            layer=layer,
            selected_only=False,
            force_last=False,  # Not needed - divide mode always includes endpoint
            force_first_last=False,
            divide=5,  # 5 segments = 6 points
            use_ellipsoidal=True,
            distance_units=QgsUnitTypes.DistanceMeters
        )
        
        # Should have 6 points (100m / 5 = 20m spacing)
        count = self.count_points_in_layer("test_divide")
        self.assertEqual(count, 6, f"Expected 6 points from 5 divisions, got {count}")
        
        # Clean up
        QgsProject.instance().removeAllMapLayers()
    
    def test_divide_into_3_parts(self):
        """Test dividing line into 3 parts (should create 4 points)."""
        layer = self.create_line_layer(32633, "utm_test")
        self.add_line_feature(layer, [(500000, 6000000), (500100, 6000000)])  # 100m
        
        # Divide into 3 equal parts
        points_along_line(
            layerout="test_divide_3",
            startpoint=0,
            endpoint=0,
            distance=0,
            layer=layer,
            selected_only=False,
            force_last=False,  # Not needed for divide mode
            force_first_last=False,
            divide=3,  # 3 parts = 4 points (0, 33.33, 66.67, 100)
            use_ellipsoidal=True,
            distance_units=QgsUnitTypes.DistanceMeters
        )
        
        # Should have 4 points
        count = self.count_points_in_layer("test_divide_3")
        self.assertEqual(count, 4, f"Expected 4 points from 3 divisions, got {count}")
        
        # Clean up
        QgsProject.instance().removeAllMapLayers()
    
    def test_divide_with_start_end_points(self):
        """Test divide mode with custom start and end points."""
        layer = self.create_line_layer(32633, "utm_test")
        self.add_line_feature(layer, [(500000, 6000000), (500100, 6000000)])  # 100m
        
        # Divide segment from 20m to 80m into 3 parts
        points_along_line(
            layerout="test_divide_range",
            startpoint=20,
            endpoint=80,
            distance=0,
            layer=layer,
            selected_only=False,
            force_last=False,
            force_first_last=False,
            divide=3,  # Divide 60m into 3 = 20m each = 4 points
            use_ellipsoidal=True,
            distance_units=QgsUnitTypes.DistanceMeters
        )
        
        # Should have 4 points (20, 40, 60, 80)
        count = self.count_points_in_layer("test_divide_range")
        self.assertEqual(count, 4, f"Expected 4 points, got {count}")
        
        # Clean up
        QgsProject.instance().removeAllMapLayers()


class TestDistanceUnits(TestQChainageSetup):
    """Test different distance units."""
    
    def test_kilometers_on_meter_layer(self):
        """Test using kilometers on a meter-based layer."""
        layer = self.create_line_layer(32633, "utm_test")
        self.add_line_feature(layer, [(500000, 6000000), (505000, 6000000)])  # 5000m = 5km
        
        # Create points every 1 kilometer
        points_along_line(
            layerout="test_km",
            startpoint=0,
            endpoint=0,
            distance=1,
            layer=layer,
            selected_only=False,
            force_last=True,
            force_first_last=False,
            divide=0,
            use_ellipsoidal=True,
            distance_units=QgsUnitTypes.DistanceKilometers
        )
        
        # Should have 6 points (0, 1, 2, 3, 4, 5 km)
        count = self.count_points_in_layer("test_km")
        self.assertEqual(count, 6, f"Expected 6 points at 1km intervals, got {count}")
        
        # Clean up
        QgsProject.instance().removeAllMapLayers()
    
    def test_feet_on_meter_layer(self):
        """Test using feet on a meter-based layer."""
        layer = self.create_line_layer(32633, "utm_test")
        # 1000 feet ≈ 304.8 meters, create 609.6m line
        self.add_line_feature(layer, [(500000, 6000000), (500609.6, 6000000)])
        
        # Create points every 500 feet
        points_along_line(
            layerout="test_feet",
            startpoint=0,
            endpoint=0,
            distance=500,
            layer=layer,
            selected_only=False,
            force_last=True,
            force_first_last=False,
            divide=0,
            use_ellipsoidal=True,
            distance_units=QgsUnitTypes.DistanceFeet
        )
        
        # Should have at least 4 points
        count = self.count_points_in_layer("test_feet")
        self.assertGreaterEqual(count, 4, f"Expected at least 4 points, got {count}")
        
        # Clean up
        QgsProject.instance().removeAllMapLayers()


class TestProjectionModes(TestQChainageSetup):
    """Test Cartesian vs Ellipsoidal calculations."""
    
    def test_ellipsoidal_on_projected_crs(self):
        """Test ellipsoidal calculation on projected CRS."""
        layer = self.create_line_layer(32633, "utm_test")
        self.add_line_feature(layer, [(500000, 6000000), (500100, 6000000)])
        
        points_along_line(
            layerout="test_ellipsoidal",
            startpoint=0,
            endpoint=0,
            distance=10,
            layer=layer,
            selected_only=False,
            force_last=True,
            force_first_last=False,
            divide=0,
            use_ellipsoidal=True,  # Ellipsoidal
            distance_units=QgsUnitTypes.DistanceMeters
        )
        
        count_ellipsoidal = self.count_points_in_layer("test_ellipsoidal")
        self.assertEqual(count_ellipsoidal, 11, f"Expected 11 points, got {count_ellipsoidal}")
        
        # Clean up
        QgsProject.instance().removeAllMapLayers()
    
    def test_cartesian_on_projected_crs(self):
        """Test cartesian calculation on projected CRS."""
        layer = self.create_line_layer(32633, "utm_test")
        self.add_line_feature(layer, [(500000, 6000000), (500100, 6000000)])
        
        points_along_line(
            layerout="test_cartesian",
            startpoint=0,
            endpoint=0,
            distance=10,
            layer=layer,
            selected_only=False,
            force_last=True,
            force_first_last=False,
            divide=0,
            use_ellipsoidal=False,  # Cartesian
            distance_units=QgsUnitTypes.DistanceMeters
        )
        
        count_cartesian = self.count_points_in_layer("test_cartesian")
        # On short projected lines, should be nearly identical
        self.assertEqual(count_cartesian, 11, f"Expected 11 points, got {count_cartesian}")
        
        # Clean up
        QgsProject.instance().removeAllMapLayers()
    
    def test_geographic_crs_ellipsoidal(self):
        """Test ellipsoidal on geographic CRS (lat/lon)."""
        layer = self.create_line_layer(4326, "geographic_test")
        # Line along equator from 0° to 1° longitude ≈ 111.3 km
        self.add_line_feature(layer, [(0, 0), (1, 0)])
        
        # Create points every 20 km
        points_along_line(
            layerout="test_geo_ellipsoidal",
            startpoint=0,
            endpoint=0,
            distance=20000,  # 20 km in meters
            layer=layer,
            selected_only=False,
            force_last=True,
            force_first_last=False,
            divide=0,
            use_ellipsoidal=True,
            distance_units=QgsUnitTypes.DistanceMeters
        )
        
        count = self.count_points_in_layer("test_geo_ellipsoidal")
        # 111.3 km / 20 km ≈ 6 points
        self.assertGreaterEqual(count, 5, f"Expected at least 5 points, got {count}")
        self.assertLessEqual(count, 7, f"Expected at most 7 points, got {count}")
        
        # Clean up
        QgsProject.instance().removeAllMapLayers()


class TestStartEndPoints(TestQChainageSetup):
    """Test custom start and end points."""
    
    def test_custom_start_point(self):
        """Test chainage starting from a custom point."""
        layer = self.create_line_layer(32633, "utm_test")
        self.add_line_feature(layer, [(500000, 6000000), (500100, 6000000)])
        
        # Start at 30m, points every 20m
        points_along_line(
            layerout="test_start",
            startpoint=30,
            endpoint=0,
            distance=20,
            layer=layer,
            selected_only=False,
            force_last=True,
            force_first_last=False,
            divide=0,
            use_ellipsoidal=True,
            distance_units=QgsUnitTypes.DistanceMeters
        )
        
        # Should have points at 30, 50, 70, 90, 100 = 5 points
        count = self.count_points_in_layer("test_start")
        self.assertEqual(count, 5, f"Expected 5 points, got {count}")
        
        # Clean up
        QgsProject.instance().removeAllMapLayers()
    
    def test_custom_start_and_end(self):
        """Test chainage with custom start and end points."""
        layer = self.create_line_layer(32633, "utm_test")
        self.add_line_feature(layer, [(500000, 6000000), (500100, 6000000)])
        
        # From 20m to 80m, points every 15m
        points_along_line(
            layerout="test_start_end",
            startpoint=20,
            endpoint=80,
            distance=15,
            layer=layer,
            selected_only=False,
            force_last=True,
            force_first_last=False,
            divide=0,
            use_ellipsoidal=True,
            distance_units=QgsUnitTypes.DistanceMeters
        )
        
        # Should have points at 20, 35, 50, 65, 80 = 5 points
        count = self.count_points_in_layer("test_start_end")
        self.assertEqual(count, 5, f"Expected 5 points, got {count}")
        
        # Clean up
        QgsProject.instance().removeAllMapLayers()


class TestMultipleFeatures(TestQChainageSetup):
    """Test handling multiple features."""
    
    def test_all_features_multiple_lines(self):
        """Test chainage on all features when layer has multiple lines."""
        layer = self.create_line_layer(32633, "utm_test")
        
        # Add three 50m lines
        self.add_line_feature(layer, [(500000, 6000000), (500050, 6000000)])
        self.add_line_feature(layer, [(500100, 6000000), (500150, 6000000)])
        self.add_line_feature(layer, [(500200, 6000000), (500250, 6000000)])
        
        # Points every 25m on all features
        points_along_line(
            layerout="test_multiple",
            startpoint=0,
            endpoint=0,
            distance=25,
            layer=layer,
            selected_only=False,
            force_last=True,
            force_first_last=False,
            divide=0,
            use_ellipsoidal=True,
            distance_units=QgsUnitTypes.DistanceMeters
        )
        
        # Each line: 0, 25, 50 = 3 points × 3 lines = 9 points
        count = self.count_points_in_layer("test_multiple")
        self.assertEqual(count, 9, f"Expected 9 points from 3 lines, got {count}")
        
        # Clean up
        QgsProject.instance().removeAllMapLayers()


def run_tests():
    """Run all tests and print results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestBasicChainage))
    suite.addTests(loader.loadTestsFromTestCase(TestDivideMode))
    suite.addTests(loader.loadTestsFromTestCase(TestDistanceUnits))
    suite.addTests(loader.loadTestsFromTestCase(TestProjectionModes))
    suite.addTests(loader.loadTestsFromTestCase(TestStartEndPoints))
    suite.addTests(loader.loadTestsFromTestCase(TestMultipleFeatures))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
