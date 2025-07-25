# pandas_model.py (v3.0 - 支持悬停提示)
# 职责：作为Pandas DataFrame和Qt表格视图之间的标准适配器。

from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from PySide6.QtGui import QColor


class PandasModel(QAbstractTableModel):
    """一个将Pandas DataFrame作为数据源的、支持编辑和悬停提示的Qt表格模型。"""

    def __init__(self, data):
        super().__init__()
        self._data = data

    def rowCount(self, parent=QModelIndex()):
        return len(self._data.index)

    def columnCount(self, parent=QModelIndex()):
        return len(self._data.columns)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        # 用于显示和编辑的文本
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            return str(self._data.iloc[index.row(), index.column()])

        # === 【核心新增功能】: 添加工具提示角色 ===
        if role == Qt.ItemDataRole.ToolTipRole:
            # 当视图请求“工具提示”时，返回该单元格的完整文本
            return str(self._data.iloc[index.row(), index.column()])

        # 交替行背景色
        if role == Qt.ItemDataRole.BackgroundRole:
            return QColor("#FFFFFF") if index.row() % 2 == 0 else QColor("#F0F0F0")

        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self._data.columns[section]
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Vertical:
            return str(self._data.index[section] + 1)
        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if role == Qt.ItemDataRole.EditRole:
            self._data.iloc[index.row(), index.column()] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        return super().flags(index) | Qt.ItemFlag.ItemIsEditable