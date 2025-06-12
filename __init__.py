#!/usr/bin/env python3
import sys
from pathlib import Path
from . import auto_load

sys.path.insert(0, str(Path(__file__).parent / "libs"))
# 原始插件作者：DarkStarSword (https://github.com/DarkStarSword/3d-fixes/blob/master/blender_3dmigoto.py)
# 由DOA修改Discord的MicroKnightmare更新以支持3.0

####### AGMG Discord 贡献者 #######
# 由SilentNightSound#7430修改，添加原神支持和更多原神特定功能
# 由HazrateGolabi#1364添加QOL功能（导出时忽略隐藏网格）
# HummyR#8131为原神网格创建了优化的轮廓算法
# 由LeoTorreZ将此插件的几个其他游戏迭代版本合并回单一版本
# 由SinsOfSeven测试和开发现代功能
# 由SpectrumQT添加WUWA支持并正式实现其类

bl_info = {
    "name": "XXMI_Tools",
    "blender": (2, 93, 0),
    "author": "LeoTorreZ",
    "location": "文件 > 导入导出",
    "description": "导入用3DMigoto帧分析转储的网格，并导出适合重新注入的网格。原始插件作者：DarkStarSword。贡献者：SilentNightSound#7430, HazrateGolabi#1364, HummyR#8131, SinsOfSeven, SpectrumQT",
    "category": "导入导出",
    "tracker_url": "https://github.com/leotorrez/XXMITools",
    "version": (1, 5, 3),
}
auto_load.init()


def register():
    auto_load.register()


def unregister():
    auto_load.unregister()
