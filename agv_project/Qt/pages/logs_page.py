from PySide6.QtWidgets import QWidget, QTabWidget
from page_ui.pages.ui_logs import Ui_LogsForm

# Optional: advanced table logs (from v8)
try:
    from pages.logs_page_v8 import LogsPageV8
except Exception:
    LogsPageV8 = None


class LogsPage(QWidget):
    """Logs page.

    Keeps the original text log view (QTextEdit) and *adds* an optional
    advanced table view (filters/search/export) on a second tab.

    This is intentionally non-destructive: existing code that calls
    `append(msg)` continues to work.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_LogsForm()
        self.ui.setupUi(self)

        self._tabs = None
        self._adv = None

        # Convert the single text widget into a tabbed view (Text / Table)
        self._init_tabs()

        self.ui.btn_clear.clicked.connect(self.clear)

    def _init_tabs(self):
        # Create tabs and move the existing QTextEdit into the first tab
        tabs = QTabWidget(self)
        tabs.setObjectName("logsTabs")

        # remove existing text widget from layout and reparent into tab
        try:
            self.ui.vl_root.removeWidget(self.ui.text)
        except Exception:
            pass
        self.ui.text.setParent(None)
        tabs.addTab(self.ui.text, "Text")

        # second tab: advanced logs
        if LogsPageV8 is not None:
            try:
                self._adv = LogsPageV8()
                tabs.addTab(self._adv, "Table")
            except Exception:
                self._adv = None

        # Add tabs back into root layout (after top bar)
        self.ui.vl_root.addWidget(tabs)

        self._tabs = tabs

    def append(self, msg: str):
        # Always keep the raw text log for debugging
        self.ui.text.append(msg)
        # Advanced view (if available)
        if self._adv is not None:
            try:
                self._adv.append(msg)
            except Exception:
                pass

    def clear(self):
        # Clear both, but keep behavior intuitive for the current tab
        try:
            self.ui.text.clear()
        except Exception:
            pass
        if self._adv is not None:
            try:
                self._adv.clear()
            except Exception:
                pass
