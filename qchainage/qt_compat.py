# -*- coding: utf-8 -*-
"""
Qt Compatibility Module for QChainage
Handles Qt5/Qt6 compatibility for QGIS plugin development.

Copyright (c) 2025 Werner Macho
Licensed under GNU General Public License v3.0
"""

# Detect Qt version and set up compatibility layer
def get_qt_version():
    """Detect which Qt version is available and return version info."""
    try:
        from qgis.PyQt import QtCore
        return QtCore.QT_VERSION_STR, "qgis.PyQt"
    except ImportError:
        pass
    
    try:
        from PyQt6 import QtCore
        return QtCore.QT_VERSION_STR, "PyQt6"
    except ImportError:
        pass
    
    try:
        from PyQt5 import QtCore
        return QtCore.QT_VERSION_STR, "PyQt5"
    except ImportError:
        pass
    
    return None, None

def is_qt6():
    """Check if Qt6 is being used."""
    version, _ = get_qt_version()
    return version and int(version.split('.')[0]) >= 6

# Compatibility imports
def get_qt_imports():
    """Get the appropriate Qt imports for the current environment."""
    try:
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
    
    try:
        from PyQt5 import QtCore, QtGui, QtWidgets, uic
        return QtCore, QtGui, QtWidgets, uic, "PyQt5"
    except ImportError:
        raise ImportError("No compatible Qt version found (PyQt5/PyQt6)")

# Initialize compatibility layer
try:
    QtCore, QtGui, QtWidgets, uic, QT_BINDING = get_qt_imports()
    QT_VERSION, _ = get_qt_version()
    
    # Export commonly used classes
    QSettings = QtCore.QSettings
    QTranslator = QtCore.QTranslator
    QCoreApplication = QtCore.QCoreApplication
    QFileInfo = QtCore.QFileInfo
    QVariant = QtCore.QVariant
    
    # Handle QAction location difference between Qt5 and Qt6
    QAction = getattr(QtWidgets, 'QAction', None) or QtGui.QAction
    
    QIcon = QtGui.QIcon
    QDialog = QtWidgets.QDialog
    QDialogButtonBox = QtWidgets.QDialogButtonBox
    
    # Create a compatible dialog base class
    class CompatDialog(QtWidgets.QDialog):
        """Qt5/Qt6 compatible dialog class."""
        
        def exec_(self):
            """Qt5/Qt6 compatible exec method."""
            return super().exec() if hasattr(super(), 'exec') else super().exec_()
        
        def exec(self):
            """Qt6 exec method that also works in Qt5."""
            return self.exec_()
    
    QDialog = CompatDialog
    
    # Handle QDialogButtonBox button enum differences
    if is_qt6():
        try:
            DialogButtonBox_Ok = QDialogButtonBox.StandardButton.Ok
            DialogButtonBox_Cancel = QDialogButtonBox.StandardButton.Cancel
            DialogButtonBox_Help = QDialogButtonBox.StandardButton.Help
        except AttributeError:
            DialogButtonBox_Ok = getattr(QDialogButtonBox, 'Ok', 1024)
            DialogButtonBox_Cancel = getattr(QDialogButtonBox, 'Cancel', 4194304)
            DialogButtonBox_Help = getattr(QDialogButtonBox, 'Help', 16777216)
    else:
        DialogButtonBox_Ok = getattr(QDialogButtonBox, 'Ok', 1024)
        DialogButtonBox_Cancel = getattr(QDialogButtonBox, 'Cancel', 4194304)
        DialogButtonBox_Help = getattr(QDialogButtonBox, 'Help', 16777216)
    
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
    'QT_VERSION', 'QT_BINDING', 'is_qt6', 'get_qt_version'
]
