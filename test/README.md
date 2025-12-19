# QChainage Plugin - Test Suite

This directory contains comprehensive tests for all QChainage plugin functionality.

## Test Files

### 1. `test_qchainage.py` - Automated Unit Tests

Automated test suite that tests all plugin features programmatically.

**Test Coverage:**
- ✅ Basic chainage (all features, selected features)
- ✅ Force first/last point options
- ✅ Divide mode (equal segments)
- ✅ Distance units (meters, kilometers, feet)
- ✅ Projection modes (Cartesian vs Ellipsoidal)
- ✅ Geographic vs Projected CRS
- ✅ Custom start/end points
- ✅ Multiple features handling

**Requirements:**
- QGIS Python environment with PyQt5/PyQt6
- Access to QGIS core libraries

**How to Run:**
```bash
# From the test directory
python3 test_qchainage.py

# Or using QGIS Python
/usr/bin/python3 test_qchainage.py
```

**Expected Output:**
```
test_all_features_multiple_lines ... ok
test_cartesian_on_projected_crs ... ok
test_custom_start_and_end ... ok
test_custom_start_point ... ok
test_divide_into_segments ... ok
test_divide_with_start_end_points ... ok
test_ellipsoidal_on_projected_crs ... ok
test_feet_on_meter_layer ... ok
test_force_first_last_only ... ok
test_force_last_point ... ok
test_geographic_crs_ellipsoidal ... ok
test_kilometers_on_meter_layer ... ok
test_selected_features_only ... ok
test_simple_line_all_features ... ok

----------------------------------------------------------------------
Ran 14 tests in X.XXXs

OK
```

---

### 2. `create_test_layers.py` - Manual Test Layer Generator

Script to create test layers in QGIS for manual testing through the plugin UI.

**Creates 6 Test Layers:**

1. **Test_UTM_100m** - Basic 100m horizontal line (EPSG:32633)
   - For basic chainage testing
   - Test distance intervals, start/end points

2. **Test_Multiple_Features** - 3 separate 50m lines (EPSG:32633)
   - Test "all features" vs "selected only"
   - Practice feature selection

3. **Test_Long_5km** - 5000m line (EPSG:32633)
   - Test kilometer units
   - Test divide mode with many segments

4. **Test_Geographic_WGS84** - 1° line along equator (EPSG:4326)
   - Test Ellipsoidal vs Cartesian difference
   - Demonstrate importance of correct mode for lat/lon

5. **Test_Diagonal_45deg** - 100m diagonal line (EPSG:32633)
   - Verify correct distance calculation on angled lines

6. **Test_Short_10m** - 10m line (EPSG:32633)
   - Test precision with small distances

**How to Use:**
1. Open QGIS
2. Open Python Console (Plugins → Python Console or Ctrl+Alt+P)
3. Load the script:
   ```python
   exec(open('/path/to/test/create_test_layers.py').read())
   ```
4. Create test layers:
   ```python
   create_test_layers()
   ```

---

### 3. `testproj.gpkg` - Test GeoPackage

Pre-created test project with sample data.

---

## Manual Test Checklist

Use this checklist when testing the plugin manually:

### ✅ Basic Chainage Tests
- [ ] All features with 10m spacing on 100m line → 11 points
- [ ] Force last point with 30m spacing → 5 points (0,30,60,90,100)
- [ ] Force first/last only → 2 points (start and end)
- [ ] Custom start=20, end=80, 15m spacing → 5 points

### ✅ Feature Selection Tests
- [ ] All features (no selection) → points on all lines
- [ ] Selected features only → points only on selected line(s)
- [ ] Empty selection switches to "all features" mode

### ✅ Divide Mode Tests
- [ ] Divide=5 on 5km line → 6 points (1000m spacing)
- [ ] Divide=10 on 5km line → 11 points (500m spacing)
- [ ] Divide with custom start/end range

### ✅ Distance Units Tests
- [ ] Meters on meter-based layer
- [ ] Kilometers on meter-based layer (1km on 5km line → 6 points)
- [ ] Feet on meter-based layer (conversion works correctly)
- [ ] Centimeters, millimeters for precision work

### ✅ Projection Mode Tests
- [ ] Ellipsoidal on projected CRS (UTM) → correct distances
- [ ] Cartesian on projected CRS (UTM) → nearly identical for short lines
- [ ] Ellipsoidal on geographic CRS (WGS84) → correct real-world distances
- [ ] Cartesian on geographic CRS → WARNING displayed, wrong results

### ✅ UI/UX Tests
- [ ] Layer units field is read-only (QLabel, not editable)
- [ ] Layer units field shows correct CRS units (meters, degrees, feet)
- [ ] OK button disabled when no suitable layers
- [ ] OK button enabled when layer selected
- [ ] Selected features count affects radio button state
- [ ] Output layer name auto-fills as "chain_[layername]"

### ✅ Edge Cases
- [ ] Very short line (10m) with small spacing (2m)
- [ ] Distance larger than line length
- [ ] Zero or negative distance (should error/prevent)
- [ ] Start point beyond line length
- [ ] End point before start point

### ✅ Stress Tests
- [ ] Many features (50+ lines)
- [ ] Very long line (100+ km)
- [ ] Very small spacing (centimeters)
- [ ] Very large spacing (kilometers)

---

## Test Results Template

When running manual tests, document results:

```
Test Date: YYYY-MM-DD
QGIS Version: X.XX
Qt Version: 5/6
Plugin Version: X.X.X

Test Case: [Name]
Input: [Layer, settings]
Expected: [What should happen]
Actual: [What happened]
Status: ✅ PASS / ❌ FAIL
Notes: [Any observations]
```

---

## Reporting Issues

If you find bugs while testing:

1. **Document the issue:**
   - QGIS version
   - Plugin version
   - Test layer used
   - Settings applied
   - Expected vs actual result
   - Screenshots if applicable

2. **Check if reproducible:**
   - Try on different layer
   - Try with different settings
   - Check console for errors

3. **Create detailed bug report**

---

## Test Coverage Summary

| Feature | Automated Test | Manual Test | Status |
|---------|---------------|-------------|---------|
| All features | ✅ | ✅ | Complete |
| Selected features | ✅ | ✅ | Complete |
| Force last point | ✅ | ✅ | Complete |
| Force first/last only | ✅ | ✅ | Complete |
| Divide mode | ✅ | ✅ | Complete |
| Distance units | ✅ | ✅ | Complete |
| Ellipsoidal calc | ✅ | ✅ | Complete |
| Cartesian calc | ✅ | ✅ | Complete |
| Geographic CRS | ✅ | ✅ | Complete |
| Projected CRS | ✅ | ✅ | Complete |
| Start/end points | ✅ | ✅ | Complete |
| Multiple features | ✅ | ✅ | Complete |
| UI elements | ❌ | ✅ | Manual only |

---

## Notes

- Automated tests use QGIS core libraries and may require proper QGIS Python environment
- Some features (UI elements) can only be tested manually
- Geographic CRS tests demonstrate the critical importance of using Ellipsoidal mode
- Always test with both small and large scale data

---

## Quick Start

**For developers:**
```bash
python3 test_qchainage.py
```

**For manual testers:**
1. Open QGIS
2. Run `create_test_layers.py` in Python Console
3. Follow the printed checklist
4. Test each scenario
5. Document results
