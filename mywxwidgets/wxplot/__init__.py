# -*- coding: utf-8 -*-
"""
A simple plotting library for the wxPython Phoenix project.

"""

from .plotcanvas import PlotCanvas
from .polyobjects import (PlotGraphics, PlotPrintout, PolyBoxPlot,
                          PolyHistogram, PolyLine, PolyMarker, PolySpline)

__all__ = [
    'PolyLine', 'PolySpline', 'PolyMarker', 'PolyBoxPlot', 'PolyHistogram',
    'PlotGraphics', 'PlotCanvas', 'PlotPrintout'
]
__updated__ = '2025-2-7'
