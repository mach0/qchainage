# -*- coding: utf-8 -*-
"""
QChainage Plugin Initialization
Copyright (c) 2013-2024 Werner Macho
Licensed under GNU GPL v3.0
"""


def classFactory(iface):
    """Load and initialize the QChainage plugin."""
    from .qchainage import Qchainage
    return Qchainage(iface)
