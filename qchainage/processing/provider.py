# -*- coding: utf-8 -*-
"""
QChainage Processing Provider
Integrates QChainage algorithms into the QGIS Processing Toolbox.

Copyright (c) 2025 Werner Macho
Licensed under GNU GPL v3.0
"""

import os
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsProcessingProvider

from .chainage_algorithm import QChainageAlgorithm


class QChainageProvider(QgsProcessingProvider):
    """Processing provider for QChainage algorithms."""

    def loadAlgorithms(self):
        """Load algorithms provided by this provider."""
        self.addAlgorithm(QChainageAlgorithm())

    def id(self) -> str:
        """Unique provider ID."""
        return 'qchainage'

    def name(self) -> str:
        """Provider name displayed in Processing toolbox."""
        return 'QChainage'

    def longName(self) -> str:
        """Long provider name."""
        return 'QChainage Tools'

    def icon(self) -> QIcon:
        """Provider icon."""
        icon_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'img',
            'qchainage.svg'
        )
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        return super().icon()
