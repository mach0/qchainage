# -*- coding: utf-8 -*-
"""
/***************************************************************************
 qchainage
                                 A QGIS plugin
 chainage features
                             -------------------
        begin                : 2013-02-20
        copyright            : (C) 2013 by Werner Macho
        email                : werner.macho@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


def classFactory(iface):
    """
    load qchainage class from file qchainage and init plugin
    """
    from qchainage import Qchainage
    return Qchainage(iface)
