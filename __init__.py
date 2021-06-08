# -*- coding: utf-8 -*-
'''
File: __init__.py
Project: qchainage
Created Date: February 20th 2013
Author: Werner Macho
-----
Last Modified: Tue Jun 08 2021
Modified By: Werner Macho
-----
Copyright (c) 2013 - 2021 Werner Macho
-----
GNU General Public License v3.0 only
http://www.gnu.org/licenses/gpl-3.0-standalone.html
-----
HISTORY:
Date      	By	Comments
----------	---	---------------------------------------------------------
'''


from __future__ import absolute_import


def classFactory(iface):
    """
    load qchainage class from file qchainage and init plugin
    """
    from .qchainage import Qchainage
    return Qchainage(iface)
