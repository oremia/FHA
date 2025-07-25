# fha_main_app.py (v12.0 - 最终稳定版)
# -*- coding: utf-8 -*-

import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTableView, QPushButton,
    QMessageBox, QFileDialog, QLabel, QHeaderView, QTabWidget, QGridLayout,
    QComboBox
)
from PySide6.QtCore import Qt

try:
    from fha_model import FHA_Model
    from pandas_model import PandasModel
except ImportError as e:
    # 打印到控制台，因为此时GUI可能还未启动
    print(f"依赖缺失: 无法导入 {e.name}。\n请确保 fha_model.py 和 pandas_model.py 文件与主程序在同一个文件夹下。")
    sys.exit(1)


class FHA_Widget(QWidget):
    """一个自包含的、功能完整的FHA分析Qt组件。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("FHA模块独立测试 (v12.0)")
        self.setGeometry(100, 100, 1400, 800)

        self.fha_model = FHA_Model()
        self.init_ui()
        self.update_main_table()
        self.update_all_query_ui()

    def init_ui(self):
        """创建所有界面元素。"""
        self.tabs = QTabWidget()
        self.fha_report_tab = QWidget()
        self.query_tab = QWidget()
        self.tabs.addTab(self.fha_report_tab, "FHA分析与报告")
        self.tabs.addTab(self.query_tab, "智能分级查询")

        self._create_report_tab_ui()
        self._create_query_tab_ui()

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.tabs)

    def _create_report_tab_ui(self):
        """创建“分析与报告”标签页的界面。"""
        self.table_view = QTableView()
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table_view.doubleClicked.connect(self.on_table_double_clicked)  # 绑定双击事件

        self.new_button = QPushButton("新建")
        self.load_button = QPushButton("加载")
        self.add_button = QPushButton("添加行")
        self.delete_button = QPushButton("删除行")
        self.export_button = QPushButton("导出")
        self.filepath_label = QLabel("新表格 - 未保存")

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.new_button)
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.export_button)
        button_layout.addSpacing(20)
        button_layout.addWidget(self.filepath_label)
        button_layout.addStretch()

        self.new_button.clicked.connect(self.new_file)
        self.load_button.clicked.connect(self.load_file)
        self.add_button.clicked.connect(self.add_row)
        self.delete_button.clicked.connect(self.delete_row)
        self.export_button.clicked.connect(self.export_file)

        layout = QVBoxLayout(self.fha_report_tab)
        layout.addLayout(button_layout)
        layout.addWidget(self.table_view)

    def _create_query_tab_ui(self):
        """创建“智能查询”标签页的界面。"""
        self.query_combos = {}
        levels = ['一级功能', '二级功能', '三级功能']
        grid_layout = QGridLayout()
        for i, level in enumerate(levels):
            label = QLabel(f"{level}:")
            combo = QComboBox()
            self.query_combos[level] = combo
            grid_layout.addWidget(label, i, 0)
            grid_layout.addWidget(combo, i, 1)
            # === 【核心修复点】: 所有下拉框的信号都连接到同一个总指挥函数 ===
            combo.currentTextChanged.connect(self.on_query_selection_changed)
        grid_layout.setColumnStretch(1, 1)

        self.details_table_view = QTableView()
        self.details_table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.details_table_view.setAlternatingRowColors(True)

        layout = QVBoxLayout(self.query_tab)
        layout.addLayout(grid_layout)
        layout.addWidget(QLabel("查询结果:"))
        layout.addWidget(self.details_table_view)

    # --- 功能函数（槽） ---

    def new_file(self):
        if self.fha_model.get_dataframe().empty or \
                QMessageBox.question(self, "确认",
                                     "当前有未保存的数据，确定要新建吗？") == QMessageBox.StandardButton.Yes:
            self.fha_model.new_blank_table()
            self.update_main_table()
            self.update_all_query_ui()
            self.filepath_label.setText("新表格 - 未保存")

    def load_file(self):
        if self.fha_model.get_dataframe().empty or \
                QMessageBox.question(self, "确认",
                                     "加载新文件将覆盖当前数据，确定吗？") == QMessageBox.StandardButton.Yes:
            filepath, _ = QFileDialog.getOpenFileName(self, "选择Excel文件", "", "Excel Files (*.xlsx *.xls)")
            if filepath:
                success, msg = self.fha_model.load_from_excel(filepath)
                if success:
                    self.update_main_table()
                    self.update_all_query_ui()
                    self.filepath_label.setText(f"当前文件: {filepath.split('/')[-1]}")
                else:
                    QMessageBox.critical(self, "错误", msg)

    def export_file(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "保存报告", "", "Excel Files (*.xlsx)")
        if filepath:
            success, msg = self.fha_model.export_to_excel(filepath)
            if success:
                QMessageBox.information(self, "成功", msg)
                self.filepath_label.setText(f"当前文件: {filepath.split('/')[-1]}")
            else:
                QMessageBox.warning(self, "警告", msg)

    def add_row(self):
        new_row_index = self.fha_model.add_new_row()
        self.update_main_table()
        self.table_view.scrollToBottom()
        self.table_view.selectRow(new_row_index)

    def delete_row(self):
        selected_rows = self.table_view.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请先选择要删除的行。")
            return

        row_index_to_delete = selected_rows[0].row()
        if QMessageBox.question(self, "确认",
                                f"确定要删除第 {row_index_to_delete + 1} 行吗？") == QMessageBox.StandardButton.Yes:
            self.fha_model.delete_row(row_index_to_delete)
            self.update_main_table()
            self.update_all_query_ui()

    def on_table_double_clicked(self, index):
        """处理主表格双击事件，以更新后端数据模型。"""
        # 这个槽函数目前为空，因为PandasModel已经实现了编辑后自动更新DataFrame。
        # 如果未来需要在此处添加额外逻辑（如记录日志），可以写在这里。
        pass

    def update_main_table(self):
        current_data = self.fha_model.get_dataframe()
        self.pandas_model = PandasModel(current_data)
        self.table_view.setModel(self.pandas_model)

    def update_all_query_ui(self):
        """刷新整个查询界面的下拉框和结果。"""
        self._update_query_combo_options(is_reset=True)
        self._display_query_results()

    # === 【核心修复点】: 这是新的“总指挥”函数 ===
    def on_query_selection_changed(self):
        """当任何一个查询下拉框变化时，这个函数被调用。"""
        self._update_query_combo_options()
        self._display_query_results()

    def _update_query_combo_options(self, is_reset=False):
        """只负责更新下拉框里的选项内容。"""
        for combo in self.query_combos.values():
            combo.blockSignals(True)

        current_selections = {level: combo.currentText() for level, combo in self.query_combos.items()}

        if is_reset:
            for combo in self.query_combos.values():
                combo.clear()

        # 更新一级
        l1_funcs = self.fha_model.get_unique_level_functions('一级功能')
        if self.query_combos['一级功能'].count() == 0 or is_reset:
            self.query_combos['一级功能'].addItems([""] + l1_funcs)

        # 更新二级
        parent = {'一级功能': current_selections.get('一级功能')}
        l2_funcs = self.fha_model.get_unique_level_functions('二级功能', parent)
        self.query_combos['二级功能'].clear()
        self.query_combos['二级功能'].addItems([""] + l2_funcs)
        # 恢复之前的选择（如果还在新选项里）
        if current_selections.get('二级功能') in l2_funcs:
            self.query_combos['二级功能'].setCurrentText(current_selections.get('二级功能'))

        # 更新三级
        parent['二级功能'] = self.query_combos['二级功能'].currentText()  # 使用更新后的二级选择
        l3_funcs = self.fha_model.get_unique_level_functions('三级功能', parent)
        self.query_combos['三级功能'].clear()
        self.query_combos['三级功能'].addItems([""] + l3_funcs)
        if current_selections.get('三级功能') in l3_funcs:
            self.query_combos['三级功能'].setCurrentText(current_selections.get('三级功能'))

        for combo in self.query_combos.values():
            combo.blockSignals(False)

    def _display_query_results(self):
        """只负责根据当前选择，显示查询结果。"""
        selections = {level: combo.currentText() for level, combo in self.query_combos.items()}
        filtered_data = self.fha_model.get_filtered_data(selections)
        details_model = PandasModel(filtered_data)
        self.details_table_view.setModel(details_model)


# =================================================================
# ==== 独立运行的入口 ====
# =================================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_widget = FHA_Widget()
    main_widget.show()
    sys.exit(app.exec())