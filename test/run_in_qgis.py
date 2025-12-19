#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test runner for QGIS Python Console
Load this file and call run_all_tests() or run_specific_test()

Usage in QGIS Python Console:
    exec(open('/home/macho/projects/qgis/plugins/qchainage/test/run_in_qgis.py').read())
    run_all_tests()
"""

import sys
import os
import unittest

# Add plugin path - handle both exec() and normal execution
try:
    # When run normally
    script_dir = os.path.dirname(__file__)
except NameError:
    # When run via exec(open(...).read()) - __file__ not defined
    # Use hardcoded path
    script_dir = '/home/macho/projects/qgis/plugins/qchainage/test'

plugin_dir = os.path.dirname(script_dir)
sys.path.insert(0, os.path.join(plugin_dir, 'qchainage'))
sys.path.insert(0, script_dir)

from test_qchainage import (
    TestBasicChainage,
    TestDivideMode,
    TestDistanceUnits,
    TestProjectionModes,
    TestStartEndPoints,
    TestMultipleFeatures,
    run_tests
)


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
    
    print("\n" + "="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
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
    
    print("\n" + "="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
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
    
    print("\n" + "="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
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
    
    print("\n" + "="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
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
    
    # Map class names to classes
    test_classes = {
        'TestBasicChainage': TestBasicChainage,
        'TestDivideMode': TestDivideMode,
        'TestDistanceUnits': TestDistanceUnits,
        'TestProjectionModes': TestProjectionModes,
        'TestStartEndPoints': TestStartEndPoints,
        'TestMultipleFeatures': TestMultipleFeatures,
    }
    
    if test_class_name not in test_classes:
        print(f"❌ Error: Test class '{test_class_name}' not found!")
        print(f"Available: {', '.join(test_classes.keys())}")
        return None
    
    test_class = test_classes[test_class_name]
    suite = unittest.TestSuite()
    suite.addTest(test_class(test_method_name))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print(f"\n{'='*70}")
    if result.wasSuccessful():
        print("✅ TEST PASSED")
    else:
        print("❌ TEST FAILED")
    print(f"{'='*70}")
    
    return result


def cleanup_test_layers():
    """Remove all test output layers from QGIS project."""
    from qgis.core import QgsProject
    
    removed = 0
    for layer in QgsProject.instance().mapLayers().values():
        if layer.name().startswith('test_') or layer.name().startswith('chain_'):
            QgsProject.instance().removeMapLayer(layer.id())
            removed += 1
    
    print(f"✓ Removed {removed} test layers")


def list_available_tests():
    """List all available test cases."""
    print("\n" + "="*70)
    print("AVAILABLE TEST FUNCTIONS")
    print("="*70)
    
    print("\n📦 Test Suites:")
    print("  run_all_tests()         - Run all tests (15+ tests)")
    print("  run_basic_tests()       - Basic chainage tests (4 tests)")
    print("  run_divide_tests()      - Divide mode tests (3 tests)")
    print("  run_units_tests()       - Distance units tests (2 tests)")
    print("  run_projection_tests()  - Projection mode tests (3 tests)")
    
    print("\n🔬 Individual Tests:")
    print("  run_single_test('TestBasicChainage', 'test_simple_line_all_features')")
    print("  run_single_test('TestDivideMode', 'test_divide_into_3_parts')")
    print("  run_single_test('TestProjectionModes', 'test_geographic_crs_ellipsoidal')")
    
    print("\n🧹 Utilities:")
    print("  cleanup_test_layers()   - Remove all test layers from project")
    print("  list_available_tests()  - Show this help")
    
    print("\n📋 Test Classes Available:")
    print("  1. TestBasicChainage      - All features, selected, force last/first")
    print("  2. TestDivideMode         - Divide into N parts")
    print("  3. TestDistanceUnits      - Kilometers, feet, unit conversion")
    print("  4. TestProjectionModes    - Ellipsoidal vs Cartesian")
    print("  5. TestStartEndPoints     - Custom start/end positions")
    print("  6. TestMultipleFeatures   - Multiple line features")
    
    print("\n💡 Examples:")
    print("  >>> run_all_tests()")
    print("  >>> run_basic_tests()")
    print("  >>> run_single_test('TestDivideMode', 'test_divide_into_3_parts')")
    print("  >>> cleanup_test_layers()")
    
    print("\n" + "="*70 + "\n")


# Auto-print help when loaded
if __name__ == '__console__':
    # Running in QGIS Python Console
    print("\n" + "="*70)
    print("✅ QCHAINAGE TEST RUNNER LOADED!")
    print("="*70)
    list_available_tests()
else:
    # Running from exec(open(...))
    print("\n" + "="*70)
    print("✅ QCHAINAGE TEST RUNNER LOADED!")
    print("="*70)
    list_available_tests()
