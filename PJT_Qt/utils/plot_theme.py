# utils/plot_theme.py
# QSS(qproperty-*)로 정의된 plot 토큰을 읽어서 PyQtGraph PlotWidget에 적용

import pyqtgraph as pg


def _get_prop(w, name: str, default):
    v = w.property(name)
    if v is None:
        return default

    # QColor가 들어올 수도 있어서 문자열로 통일
    try:
        v = v.name()  # QColor
    except Exception:
        pass

    # ✅ 핵심: 빈 문자열/공백이면 default로
    if isinstance(v, str) and v.strip() == "":
        return default

    return v



def apply_plot_theme(plot_widget: pg.PlotWidget):
    """Apply a dark theme to a PlotWidget based on QSS properties.

    Expected QSS properties (qproperty-*):
      - plotBg, gridColor, axisColor, labelColor
      - gridAlpha, axisWidth
    """

    bg = _get_prop(plot_widget, "plotBg", "#0b0e14")
    axis_color = _get_prop(plot_widget, "axisColor", "#3a4356")
    label_color = _get_prop(plot_widget, "labelColor", "#d7dbe0")
    grid_alpha = float(_get_prop(plot_widget, "gridAlpha", 0.25))
    axis_w = int(_get_prop(plot_widget, "axisWidth", 1))

    p = plot_widget.getPlotItem()

    # background
    plot_widget.setBackground(bg)

    # grid (alpha)
    p.showGrid(x=True, y=True, alpha=grid_alpha)

    # axes
    axis_pen = pg.mkPen(axis_color, width=axis_w)
    text_pen = pg.mkPen(label_color)
    for ax in ("left", "bottom"):
        a = p.getAxis(ax)
        a.setPen(axis_pen)
        a.setTextPen(text_pen)

    # legend label color (if exists)
    if p.legend is not None:
        for sample, label in p.legend.items:
            if label is not None:
                label.setText(label.text, color=label_color)


def mk_pen_from_qss(plot_widget: pg.PlotWidget,
                    color_key: str,
                    width_key: str,
                    fallback_color: str = "#e7eaf0",
                    fallback_width: int = 2):
    """Convenience: make a pen using color/width tokens from QSS."""
    c = _get_prop(plot_widget, color_key, fallback_color)
    w = int(_get_prop(plot_widget, width_key, fallback_width))
    return pg.mkPen(c, width=w)
