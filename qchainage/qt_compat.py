# -*- coding: utf-8 -*-
"""
Qt Compatibility Module for QChainage
Handles Qt5/Qt6 compatibility for QGIS plugin development.

Copyright (c) 2025 Werner Macho
Licensed under GNU General Public License v3.0
"""

import sys

# Detect Qt version and set up compatibility layer
def get_qt_version():
    """Detect which Qt version is available and return version info."""
    qt_version = None
    qt_binding = None
    
    try:
        # First try QGIS PyQt (preferred)
        from qgis.PyQt import QtCore
        qt_version = QtCore.QT_VERSION_STR
        qt_binding = "qgis.PyQt"
        return qt_version, qt_binding
    except ImportError:
        pass
    
    try:
        # Try PyQt6
        from PyQt6 import QtCore
        qt_version = QtCore.QT_VERSION_STR
        qt_binding = "PyQt6"
        return qt_version, qt_binding
    except ImportError:
        pass
    
    try:
        # Fallback to PyQt5
        from PyQt5 import QtCore
        qt_version = QtCore.QT_VERSION_STR
        qt_binding = "PyQt5"
        return qt_version, qt_binding
    except ImportError:
        pass
    
    return None, None

def is_qt6():
    """Check if Qt6 is being used."""
    version, _ = get_qt_version()
    if version:
        major_version = int(version.split('.')[0])
        return major_version >= 6
    return False

def is_qt5():
    """Check if Qt5 is being used."""
    version, _ = get_qt_version()
    if version:
        major_version = int(version.split('.')[0])
        return major_version == 5
    return False

# Compatibility imports
def get_qt_imports():
    """Get the appropriate Qt imports for the current environment."""
    try:
        # Prefer QGIS PyQt
        from qgis.PyQt import QtCore, QtGui, QtWidgets, uic
        return QtCore, QtGui, QtWidgets, uic, "qgis.PyQt"
    except ImportError:
        pass
    
    if is_qt6():
        try:
            from PyQt6 import QtCore, QtGui, QtWidgets, uic
            return QtCore, QtGui, QtWidgets, uic, "PyQt6"
        except ImportError:
            pass
    
    # Fallback to Qt5
    try:
        from PyQt5 import QtCore, QtGui, QtWidgets, uic
        return QtCore, QtGui, QtWidgets, uic, "PyQt5"
    except ImportError:
        raise ImportError("No compatible Qt version found (PyQt5/PyQt6)")

# Initialize compatibility layer
try:
    QtCore, QtGui, QtWidgets, uic, QT_BINDING = get_qt_imports()
    QT_VERSION, _ = get_qt_version()
    
    # Export commonly used classes with Qt5/Qt6 compatibility
    QSettings = QtCore.QSettings
    QTranslator = QtCore.QTranslator
    QCoreApplication = QtCore.QCoreApplication
    QFileInfo = QtCore.QFileInfo
    QVariant = QtCore.QVariant
    
    # Handle QAction location difference between Qt5 and Qt6
    try:
        # Qt5: QAction is in QtWidgets
        QAction = QtWidgets.QAction
    except AttributeError:
        # Qt6: QAction moved to QtGui
        QAction = QtGui.QAction
    
    QIcon = QtGui.QIcon
    QDialog = QtWidgets.QDialog
    QDialogButtonBox = QtWidgets.QDialogButtonBox
    
    # Create a compatible dialog base class that handles exec_() vs exec() difference
    class CompatDialog(QtWidgets.QDialog):
        """Qt5/Qt6 compatible dialog class."""
        
        def exec_(self):
            """Qt5/Qt6 compatible exec method."""
            if hasattr(super(), 'exec'):
                # Qt6: use exec()
                return super().exec()
            else:
                # Qt5: use exec_()
                return super().exec_()
        
        def exec(self):
            """Qt6 exec method that also works in Qt5."""
            return self.exec_()
    
    # Export the compatible dialog class
    QDialog = CompatDialog
    
    # Handle QDialogButtonBox button enum differences between Qt5 and Qt6
    if is_qt6():
        # Qt6: Use StandardButton enum
        try:
            DialogButtonBox_Ok = QDialogButtonBox.StandardButton.Ok
            DialogButtonBox_Cancel = QDialogButtonBox.StandardButton.Cancel
            DialogButtonBox_Help = QDialogButtonBox.StandardButton.Help
        except AttributeError:
            # Fallback if enum structure is different
            try:
                DialogButtonBox_Ok = QDialogButtonBox.Ok
                DialogButtonBox_Cancel = QDialogButtonBox.Cancel
                DialogButtonBox_Help = QDialogButtonBox.Help
            except AttributeError:
                # Ultimate fallback with numeric values
                DialogButtonBox_Ok = 1024  # QDialogButtonBox::Ok
                DialogButtonBox_Cancel = 4194304  # QDialogButtonBox::Cancel
                DialogButtonBox_Help = 16777216  # QDialogButtonBox::Help
    else:
        # Qt5: Direct attribute access
        try:
            DialogButtonBox_Ok = QDialogButtonBox.Ok
            DialogButtonBox_Cancel = QDialogButtonBox.Cancel
            DialogButtonBox_Help = QDialogButtonBox.Help
        except AttributeError:
            # Fallback with numeric values for Qt5 too
            DialogButtonBox_Ok = 1024
            DialogButtonBox_Cancel = 4194304
            DialogButtonBox_Help = 16777216
    
    # Version info
    def qVersion():
        return QtCore.QT_VERSION_STR
        
except ImportError as e:
    raise ImportError(f"Failed to initialize Qt compatibility layer: {e}")

__all__ = [
    'QtCore', 'QtGui', 'QtWidgets', 'uic',
    'QSettings', 'QTranslator', 'QCoreApplication', 'QFileInfo', 'QVariant',
    'QAction', 'QIcon', 'QDialog', 'QDialogButtonBox', 'qVersion',
    'DialogButtonBox_Ok', 'DialogButtonBox_Cancel', 'DialogButtonBox_Help',
    'QT_VERSION', 'QT_BINDING', 'is_qt5', 'is_qt6', 'get_qt_version'
]
