# utils/themed_plot_widget.py
# A small pyqtgraph PlotWidget subclass that exposes QSS-settable qproperty-* tokens.

from PySide6.QtCore import Property
import pyqtgraph as pg


class ThemedPlotWidget(pg.PlotWidget):
    """PlotWidget with Qt properties so QSS `qproperty-*` works without warnings.

    Properties (all strings/numbers):
      - plotBg, gridColor, axisColor, labelColor
      - lineColor, markerColor, thresholdColor
      - gridAlpha, axisWidth, lineWidth
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # color tokens (usually '#RRGGBB')
        self._plotBg = ""
        self._gridColor = ""
        self._axisColor = ""
        self._labelColor = ""
        self._lineColor = ""
        self._markerColor = ""
        self._thresholdColor = ""

        # numeric tokens
        self._gridAlpha = 0.25
        self._axisWidth = 1
        self._lineWidth = 2

    # --- getters/setters ---
    def _get_plotBg(self):
        return self._plotBg

    def _set_plotBg(self, v):
        self._plotBg = str(v)

    plotBg = Property(str, _get_plotBg, _set_plotBg)

    def _get_gridColor(self):
        return self._gridColor

    def _set_gridColor(self, v):
        self._gridColor = str(v)

    gridColor = Property(str, _get_gridColor, _set_gridColor)

    def _get_axisColor(self):
        return self._axisColor

    def _set_axisColor(self, v):
        self._axisColor = str(v)

    axisColor = Property(str, _get_axisColor, _set_axisColor)

    def _get_labelColor(self):
        return self._labelColor

    def _set_labelColor(self, v):
        self._labelColor = str(v)

    labelColor = Property(str, _get_labelColor, _set_labelColor)

    def _get_lineColor(self):
        return self._lineColor

    def _set_lineColor(self, v):
        self._lineColor = str(v)

    lineColor = Property(str, _get_lineColor, _set_lineColor)

    def _get_markerColor(self):
        return self._markerColor

    def _set_markerColor(self, v):
        self._markerColor = str(v)

    markerColor = Property(str, _get_markerColor, _set_markerColor)

    def _get_thresholdColor(self):
        return self._thresholdColor

    def _set_thresholdColor(self, v):
        self._thresholdColor = str(v)

    thresholdColor = Property(str, _get_thresholdColor, _set_thresholdColor)

    def _get_gridAlpha(self):
        return float(self._gridAlpha)

    def _set_gridAlpha(self, v):
        try:
            self._gridAlpha = float(v)
        except Exception:
            pass

    gridAlpha = Property(float, _get_gridAlpha, _set_gridAlpha)

    def _get_axisWidth(self):
        return int(self._axisWidth)

    def _set_axisWidth(self, v):
        try:
            self._axisWidth = int(v)
        except Exception:
            pass

    axisWidth = Property(int, _get_axisWidth, _set_axisWidth)

    def _get_lineWidth(self):
        return int(self._lineWidth)

    def _set_lineWidth(self, v):
        try:
            self._lineWidth = int(v)
        except Exception:
            pass

    lineWidth = Property(int, _get_lineWidth, _set_lineWidth)
