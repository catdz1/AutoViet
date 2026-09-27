"""style.py — Light theme cho toàn bộ ứng dụng AutoViet"""
DARK = """
/* ── BASE ── */
QMainWindow, QWidget {
    background: #f0f4f8;
    color: #1e293b;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}
QDialog {
    background: #ffffff;
    color: #1e293b;
}
QWidget#sidebar {
    background: #0f1f35;
    border-right: none;
    min-width: 210px;
    max-width: 210px;
}
QWidget#sidebar * {
    background: #0f1f35;
}
QFrame#line_logo {
    background: rgba(255,255,255,0.08);
    max-height: 1px;
    border: none;
}
QWidget#logo_widget { background: #0a1628; }
QLabel#lbl_logo {
    font-size: 16px;
    font-weight: 700;
    color: #ffffff;
    background: transparent;
    padding: 14px 0 2px 0;
}
QLabel#lbl_logo_sub {
    font-size: 10px;
    color: rgba(255,255,255,0.4);
    background: transparent;
    letter-spacing: 0.5px;
    padding-bottom: 10px;
}
QTreeWidget {
    background: #0f1f35;
    border: none;
    color: rgba(255,255,255,0.75);
    font-size: 13px;
    outline: 0;
    padding: 4px 0;
}
QTreeWidget::item {
    height: 38px;
    padding-left: 8px;
    border-radius: 8px;
    margin: 2px 8px;
    background: transparent;
}
QTreeWidget::item:hover { background: #1e3a5f; color: #ffffff; }
QTreeWidget::item:selected { background: #2563eb; color: #ffffff; font-weight: 700; }
QTreeWidget::branch {
    background: #0f1f35;
    border: none;
}
QTreeWidget::branch:has-siblings:!adjoins-item { background: #0f1f35; }
QTreeWidget::branch:has-siblings:adjoins-item { background: #0f1f35; }
QTreeWidget::branch:!has-children:!has-siblings:adjoins-item { background: #0f1f35; }
QTreeWidget::branch:closed:has-children:has-siblings { background: #0f1f35; }
QTreeWidget::branch:open:has-children:has-siblings { background: #0f1f35; }
QTreeWidget::branch:open:has-children:!has-siblings { background: #0f1f35; }
/* ── STACKED / CONTENT ── */
QStackedWidget { background: #f1f5f9; }
QWidget#page_dashboard,
QWidget#page_xe,
QWidget#page_khach_hang,
QWidget#page_don_hang,
QWidget#page_nhan_vien,
QWidget#page_dich_vu,
QWidget#page_bao_cao { background: #f1f5f9; }

/* ── TOOLBAR ── */
QWidget#toolbar_widget {
    background: #ffffff;
    border-bottom: 1px solid #e2e8f0;
}

/* ── BUTTONS ── */
QPushButton {
    background: #ffffff;
    color: #334155;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 7px 14px;
    font-size: 13px;
}
QPushButton:hover   { background: #f8fafc; border-color: #94a3b8; }
QPushButton:pressed { background: #f1f5f9; }

QPushButton#btn_add {
    background: #7c3aed;
    color: #ffffff;
    border: none;
    font-weight: 700;
    min-width: 95px;
}
QPushButton#btn_add:hover   { background: #6d28d9; }
QPushButton#btn_add:pressed { background: #5b21b6; }

QPushButton#btn_del {
    color: #ef4444;
    border-color: rgba(239,68,68,0.3);
    background: #fff;
}
QPushButton#btn_del:hover { background: rgba(239,68,68,0.08); }

QPushButton#btn_excel {
    background: #dcfce7;
    color: #16a34a;
    border-color: #86efac;
}
QPushButton#btn_excel:hover { background: #bbf7d0; }

QPushButton#btn_print {
    color: #2563eb;
    border-color: rgba(37,99,235,0.3);
    background: #eff6ff;
}
QPushButton#btn_print:hover { background: #dbeafe; }

/* ── INPUTS ── */
QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox {
    background: #ffffff;
    color: #1e293b;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 7px 12px;
    font-size: 13px;
    selection-background-color: #ddd6fe;
}
QLineEdit:focus, QTextEdit:focus,
QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #7c3aed;
    background: #faf5ff;
}
QLineEdit#search_box {
    background: #f8fafc;
    border-radius: 20px;
    padding: 7px 16px 7px 14px;
    min-width: 200px;
    border: 1px solid #e2e8f0;
}
QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
    background: #f1f5f9;
    border: none;
    width: 20px;
    border-radius: 4px;
}

/* ── COMBOBOX ── */
QComboBox {
    background: #ffffff;
    color: #1e293b;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 7px 12px;
    font-size: 13px;
}
QComboBox:focus { border-color: #7c3aed; background: #faf5ff; }
QComboBox::drop-down { border: none; width: 28px; }
QComboBox QAbstractItemView {
    background: #ffffff;
    color: #1e293b;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    selection-background-color: #ede9fe;
    outline: 0;
}

/* ── TABLE ── */
QTableWidget {
    background: #ffffff;
    alternate-background-color: #f8fafc;
    color: #1e293b;
    gridline-color: #f1f5f9;
    border: none;
    selection-background-color: #ede9fe;
    selection-color: #7c3aed;
    font-size: 13px;
    outline: 0;
}
QTableWidget::item { padding: 4px 10px; border: none; }
QTableWidget::item:selected { background: #ede9fe; color: #7c3aed; }
QHeaderView { background: #f8fafc; border: none; }
QHeaderView::section {
    background: #f8fafc;
    color: #94a3b8;
    border: none;
    border-bottom: 1px solid #e2e8f0;
    border-right: 1px solid #e2e8f0;
    padding: 10px 10px;
    font-weight: 700;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}
QHeaderView::section:last { border-right: none; }

/* ── SCROLLBAR ── */
QScrollBar:vertical {
    background: #f1f5f9; width: 6px; border-radius: 3px;
}
QScrollBar::handle:vertical {
    background: #cbd5e1; border-radius: 3px; min-height: 30px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal {
    background: #f1f5f9; height: 6px; border-radius: 3px;
}
QScrollBar::handle:horizontal { background: #cbd5e1; border-radius: 3px; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* ── MENU ── */
QMenuBar {
    background: #0f1f35;
    color: rgba(255,255,255,0.75);
    border-bottom: none;
    padding: 4px 12px;
    font-size: 13px;
    font-weight: 600;
}
QMenuBar::item { padding: 6px 14px; border-radius: 6px; }
QMenuBar::item:selected { background: #2563eb; color: #ffffff; }
QMenuBar::item:pressed  { background: #1d4ed8; color: #ffffff; }
QMenu {
    background: #ffffff;
    color: #1e293b;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 4px;
}
QMenu::item { padding: 8px 24px; border-radius: 4px; font-size: 13px; }
QMenu::item:selected { background: #eff6ff; color: #2563eb; }
QMenu::separator { height: 1px; background: #e2e8f0; margin: 4px 8px; }

/* ── STATUS BAR ── */
QStatusBar {
    background: #ffffff;
    color: #94a3b8;
    border-top: 1px solid #e2e8f0;
    font-size: 12px;
    padding: 2px 12px;
}
QStatusBar::item { border: none; }

/* ── LABEL ── */
QLabel { background: transparent; color: #1e293b; }
QLabel#section_label {
    font-size: 10px;
    font-weight: 700;
    color: rgba(255,255,255,0.6);
    text-transform: uppercase;
    letter-spacing: 1.5px;
    padding: 12px 16px 4px;
    background: transparent;
}
QLabel#detail_title  { font-size: 15px; font-weight: 700; color: #1e293b; background: transparent; }
QLabel#detail_key    { font-size: 10px; color: #94a3b8; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; background: transparent; margin-top: 6px; }
QLabel#detail_val    { font-size: 13px; color: #334155; background: transparent; }
QLabel#lbl_page_title{ font-size: 17px; font-weight: 700; color: #1e293b; background: transparent; }
QLabel#detail_key_form { font-size: 10px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.8px; background: transparent; }

/* ── FRAME ── */
QFrame[frameShape="4"] { background: #e2e8f0; max-height: 1px; border: none; }
QFrame[frameShape="5"] { background: #e2e8f0; max-width: 1px; border: none; }

/* ── GROUP BOX ── */
QGroupBox {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    margin-top: 20px;
    padding: 12px 8px 8px;
    font-size: 11px;
    color: #94a3b8;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px; top: -10px;
    font-weight: 700; letter-spacing: 1px; text-transform: uppercase;
}

/* ── TAB ── */
QTabWidget::pane { border: none; background: #ffffff; }
QTabBar::tab {
    background: #f8fafc; color: #94a3b8;
    border: none; border-bottom: 2px solid transparent;
    padding: 10px 20px; font-size: 13px;
}
QTabBar::tab:selected { color: #7c3aed; border-bottom-color: #7c3aed; background: #ffffff; }
QTabBar::tab:hover    { color: #334155; background: #f1f5f9; }

/* ── SPLITTER ── */
QSplitter::handle { background: #e2e8f0; }

/* ── DATE EDIT ── */
QDateEdit, QDateTimeEdit {
    background: #ffffff;
    color: #1e293b;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 7px 12px;
}
QDateEdit:focus { border-color: #7c3aed; }
QCalendarWidget {
    background: #ffffff;
    color: #1e293b;
}
QCalendarWidget QAbstractItemView {
    background: #ffffff;
    selection-background-color: #7c3aed;
    selection-color: white;
}

/* ── PROGRESS BAR ── */
QProgressBar {
    background: #e2e8f0;
    border-radius: 6px;
    height: 8px;
    text-align: center;
    color: #1e293b;
    font-size: 10px;
    font-weight: 700;
    border: none;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #7c3aed, stop:1 #a78bfa);
    border-radius: 6px;
}

/* ── CHECKBOX ── */
QCheckBox { color: #334155; background: transparent; }
QCheckBox::indicator {
    width: 16px; height: 16px;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    background: #ffffff;
}
QCheckBox::indicator:checked {
    background: #7c3aed;
    border-color: #7c3aed;
}

/* ── RADIO ── */
QRadioButton { color: #334155; background: transparent; }
QRadioButton::indicator {
    width: 16px; height: 16px;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    background: #ffffff;
}
QRadioButton::indicator:checked {
    background: #7c3aed;
    border-color: #7c3aed;
}
"""