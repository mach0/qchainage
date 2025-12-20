#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Test Runner for QGIS Python Console
Just paste this entire script into QGIS Python Console!

No need for exec(open(...)) - just copy and paste this whole file.
"""

import sys
import os
import unittest

# Auto-detect plugin path from this script's location
# Works when pasted into QGIS console
PLUGIN_DIR = '/home/macho/projects/qgis/plugins/qchainage'
TEST_DIR = os.path.join(PLUGIN_DIR, 'test')
CODE_DIR = os.path.join(PLUGIN_DIR, 'qchainage')

# Add to path
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)
if TEST_DIR not in sys.path:
    sys.path.insert(0, TEST_DIR)

# Import test classes
try:
    from test_qchainage import (
        TestBasicChainage,
        TestDivideMode,
        TestDistanceUnits,
        TestProjectionModes,
        TestStartEndPoints,
        TestMultipleFeatures,
        run_tests
    )
    print("Test modules loaded successfully!")
except ImportError as e:
    print(f"Error loading tests: {e}")
    print(f"   CODE_DIR: {CODE_DIR}")
    print(f"   TEST_DIR: {TEST_DIR}")
    print(f"   sys.path: {sys.path[:3]}")
    raise


def run_all_tests():
    """Run all QChainage tests."""
    print("\n" + "="*70)
    print("RUNNING ALL QCHAINAGE TESTS")
    print("="*70 + "\n")
    return run_tests()


def run_basic_tests():
    """Run only basic chainage tests."""
    print("\n" + "="*70)
    print("RUNNING BASIC CHAINAGE TESTS")
    print("="*70 + "\n")
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestBasicChainage)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    _print_summary(result)
    return result


def run_divide_tests():
    """Run only divide mode tests."""
    print("\n" + "="*70)
    print("RUNNING DIVIDE MODE TESTS")
    print("="*70 + "\n")
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestDivideMode)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    _print_summary(result)
    return result


def run_units_tests():
    """Run distance units tests."""
    print("\n" + "="*70)
    print("RUNNING DISTANCE UNITS TESTS")
    print("="*70 + "\n")
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestDistanceUnits)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    _print_summary(result)
    return result


def run_projection_tests():
    """Run projection mode tests."""
    print("\n" + "="*70)
    print("RUNNING PROJECTION MODE TESTS")
    print("="*70 + "\n")
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestProjectionModes)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    _print_summary(result)
    return result


def run_single_test(test_class_name, test_method_name):
    """
    Run a single specific test.
    
    Example:
        run_single_test('TestBasicChainage', 'test_simple_line_all_features')
    """
    print(f"\n{'='*70}")
    print(f"RUNNING: {test_class_name}.{test_method_name}")
    print(f"{'='*70}\n")
    
    test_classes = {
        'TestBasicChainage': TestBasicChainage,
        'TestDivideMode': TestDivideMode,
        'TestDistanceUnits': TestDistanceUnits,
        'TestProjectionModes': TestProjectionModes,
        'TestStartEndPoints': TestStartEndPoints,
        'TestMultipleFeatures': TestMultipleFeatures,
    }
    
    if test_class_name not in test_classes:
        print(f"Error: Test class '{test_class_name}' not found!")
        print(f"Available: {', '.join(test_classes.keys())}")
        return None
    
    test_class = test_classes[test_class_name]
    suite = unittest.TestSuite()
    suite.addTest(test_class(test_method_name))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print(f"\n{'='*70}")
    if result.wasSuccessful():
        print("TEST PASSED")
    else:
        print("TEST FAILED")
    print(f"{'='*70}")
    
    return result


def cleanup_test_layers():
    """Remove all test output layers from QGIS project."""
    from qgis.core import QgsProject
    
    removed = 0
    for layer in list(QgsProject.instance().mapLayers().values()):
        if layer.name().startswith('test_') or layer.name().startswith('chain_'):
            QgsProject.instance().removeMapLayer(layer.id())
            removed += 1
    
    print(f"✓ Removed {removed} test layers")
    return removed


def _print_summary(result):
    """Print test result summary."""
    print("\n" + "="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)


def list_available_tests():
    """List all available test cases."""
    print("\n" + "="*70)
    print("AVAILABLE TEST FUNCTIONS")
    print("="*70)
    
    print("\nTest Suites:")
    print("  run_all_tests()         - Run all tests (15+ tests)")
    print("  run_basic_tests()       - Basic chainage tests (4 tests)")
    print("  run_divide_tests()      - Divide mode tests (3 tests)")
    print("  run_units_tests()       - Distance units tests (2 tests)")
    print("  run_projection_tests()  - Projection mode tests (3 tests)")
    
    print("\nIndividual Tests:")
    print("  run_single_test('TestBasicChainage', 'test_simple_line_all_features')")
    print("  run_single_test('TestDivideMode', 'test_divide_into_3_parts')")
    print("  run_single_test('TestProjectionModes', 'test_geographic_crs_ellipsoidal')")
    
    print("\nUtilities:")
    print("  cleanup_test_layers()   - Remove all test layers from project")
    print("  list_available_tests()  - Show this help")
    
    print("\nTest Classes Available:")
    print("  1. TestBasicChainage      - All features, selected, force last/first")
    print("  2. TestDivideMode         - Divide into N parts")
    print("  3. TestDistanceUnits      - Kilometers, feet, unit conversion")
    print("  4. TestProjectionModes    - Ellipsoidal vs Cartesian")
    print("  5. TestStartEndPoints     - Custom start/end positions")
    print("  6. TestMultipleFeatures   - Multiple line features")
    
    print("\nExamples:")
    print("  >>> run_all_tests()")
    print("  >>> run_basic_tests()")
    print("  >>> run_single_test('TestDivideMode', 'test_divide_into_3_parts')")
    print("  >>> cleanup_test_layers()")
    
    print("\n" + "="*70 + "\n")


# Auto-show help when loaded
print("\n" + "="*70)
print("QCHAINAGE TEST RUNNER LOADED!")
print("="*70)
list_available_tests()
