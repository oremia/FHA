# install_qt_requirements.py
# -*- coding: utf-8 -*-

import subprocess
import sys

# 运行Qt版应用所需的软件包列表
packages = [
    "pandas",
    "openpyxl",
    "PySide6"  # Qt for Python (官方推荐)
]


def install():
    print("开始检查并安装Qt版应用所需的软件包...")
    for package in packages:
        try:
            print(f"正在安装 {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "-q", package])
            print(f"✅ {package} 已成功安装。")
        except subprocess.CalledProcessError:
            print(f"❌ 安装 {package} 失败。")
            print("请尝试手动打开命令行（CMD或PowerShell），然后运行以下命令：")
            print(f"pip install {package}")
            sys.exit(1)

    print("\n🎉 所有必需的软件包均已安装完毕！现在您可以运行 fha_main_app.py 了。")


if __name__ == "__main__":
    install()
    if sys.platform == "win32":
        input("按 Enter键 退出...")