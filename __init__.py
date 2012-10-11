# -*- coding: utf-8 -*-
# ***************************************************************************
# __init__.py  -  A Chainage Tool for QGIS
# ---------------------
#     begin                : 2012-10-06
#     copyright            : (C) 2012 by Werner Macho
#     email                : werner.macho at gmail dot com
# ***************************************************************************
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 2 of the License, or     *
# *   (at your option) any later version.                                   *
# *                                                                         *
# ***************************************************************************

def name():
  return "Qchainage"

def version():
  return "Version 0.0.1"

def description():
  return "Gives chainage along a selected line"

def qgisMinimumVersion():
  return "1.5"

def experimental():
  return True

def authorName():
  return "Werner Macho"

def classFactory(iface):
  from qchainage_plugin import QChainagePlugin
  return QChainagePlugin(iface)
