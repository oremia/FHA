# fha_model.py
# 职责：作为FHA功能的核心后端，处理所有数据逻辑，与界面完全分离。

import pandas as pd


class FHA_Model:
    """
    FHA功能的数据模型。
    负责加载、保存、编辑和查询FHA数据。
    """
    # 将ARP4761标准作为类属性，方便外部调用
    ARP4761_CATEGORIES = [
        "灾难的 (Catastrophic)", "危险的 (Hazardous)", "大的 (Major)",
        "小的 (Minor)", "无安全影响 (No Safety Effect)"
    ]

    TABLE_COLUMNS = [
        '编号', '一级功能', '二级功能', '三级功能', '飞行阶段',
        '失效状态', '对飞行器的影响', '对地面/空域的影响',
        '危害性分类', '理由/备注'
    ]

    def __init__(self):
        """初始化时，创建一个空的DataFrame。"""
        self.dataframe = pd.DataFrame(columns=self.TABLE_COLUMNS)

    def get_dataframe(self):
        """返回当前的完整数据，供视图展示。"""
        return self.dataframe

    def new_blank_table(self):
        """清空当前数据，重置为一个新的空白表格。"""
        self.dataframe = pd.DataFrame(columns=self.TABLE_COLUMNS)
        return True

    def load_from_excel(self, filepath):
        """从Excel文件加载数据。"""
        try:
            df = pd.read_excel(filepath, engine='openpyxl')
            df = df.fillna('')
            self.dataframe = df.astype(str)
            return True, "加载成功！"
        except Exception as e:
            return False, f"加载失败: {e}"

    def export_to_excel(self, filepath):
        """将当前数据导出到Excel文件。"""
        if self.dataframe.empty:
            return False, "没有可导出的数据。"
        try:
            self.dataframe.to_excel(filepath, index=False, engine='openpyxl')
            return True, f"报告已成功导出至\n{filepath}"
        except Exception as e:
            return False, f"导出失败: {e}"

    def add_new_row(self):
        """在数据末尾添加一个空行。"""
        new_row = pd.DataFrame([{col: '' for col in self.TABLE_COLUMNS}])
        self.dataframe = pd.concat([self.dataframe, new_row], ignore_index=True)
        # 返回新行的索引，方便视图定位
        return self.dataframe.index[-1]

    def delete_row(self, index):
        """根据索引删除一行。"""
        if 0 <= index < len(self.dataframe):
            self.dataframe.drop(index, inplace=True)
            self.dataframe.reset_index(drop=True, inplace=True)
            return True
        return False

    def update_cell(self, index, column_name, value):
        """更新指定单元格的内容。"""
        if 0 <= index < len(self.dataframe) and column_name in self.dataframe.columns:
            self.dataframe.loc[index, column_name] = value
            return True
        return False

    def get_unique_level_functions(self, level, parent_functions=None):
        """根据父级功能，获取指定级别的唯一功能项（用于下拉框）。"""
        filtered_df = self.dataframe.copy()
        if parent_functions:
            for parent_level, function_name in parent_functions.items():
                if function_name:
                    filtered_df = filtered_df[filtered_df[parent_level] == function_name]

        unique_functions = filtered_df[level].unique()
        return [func for func in unique_functions if str(func).strip()]

    def get_filtered_data(self, functions):
        """根据选择的层级进行智能查询。"""
        query_df = self.dataframe.copy()
        active_filters = {level: name for level, name in functions.items() if name}
        if not active_filters:
            return pd.DataFrame(columns=self.TABLE_COLUMNS)

        for level, name in active_filters.items():
            query_df = query_df[query_df[level] == name]

        if functions.get('二级功能') and not functions.get('三级功能'):
            query_df = query_df[query_df['三级功能'] == '']
        if functions.get('一级功能') and not functions.get('二级功能'):
            query_df = query_df[query_df['二级功能'] == '']

        return query_df