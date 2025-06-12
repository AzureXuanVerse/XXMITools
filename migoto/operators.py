import bpy
from bpy.props import BoolProperty, IntProperty, StringProperty
from bpy.types import Operator, AddonPreferences
from bpy_extras.io_utils import ImportHelper, orientation_helper

from .. import __name__ as package_name
from .. import addon_updater_ops
from .datahandling import (
    Fatal,
    apply_vgmap,
    import_pose,
    merge_armatures,
    update_vgmap,
)

from .datastructures import IOOBJOrientationHelper


class ApplyVGMap(Operator, ImportHelper):
    """应用顶点组映射到选定对象"""

    bl_idname = "mesh.migoto_vertex_group_map"
    bl_label = "应用3DMigoto顶点组映射"
    bl_options = {"UNDO"}

    filename_ext = ".vgmap"
    filter_glob: StringProperty(
        default="*.vgmap",
        options={"HIDDEN"},
    )

    # commit: BoolProperty(
    #        name="提交到当前网格",
    #        description="直接修改当前网格的顶点组，而不是在导出时执行映射",
    #        default=False,
    #        )

    rename: BoolProperty(
        name="重命名现有顶点组",
        description="重命名现有顶点组以匹配vgmap文件",
        default=True,
    )

    cleanup: BoolProperty(
        name="移除未列出的顶点组",
        description="移除任何未在vgmap文件中列出的现有顶点组",
        default=False,
    )

    reverse: BoolProperty(
        name="交换来源和目标",
        description="交换顶点组映射的顺序 - 如果此网格是'目标'且您想使用'来源'中的骨骼",
        default=False,
    )

    suffix: StringProperty(
        name="后缀",
        description="导出时添加到顶点缓冲区文件名的后缀，用于单个网格多个不同顶点组映射的批量导出",
        default="",
    )

    def invoke(self, context, event):
        self.suffix = ""
        return ImportHelper.invoke(self, context, event)

    def execute(self, context):
        try:
            keywords = self.as_keywords(ignore=("filter_glob",))
            apply_vgmap(self, context, **keywords)
        except Fatal as e:
            self.report({"ERROR"}, str(e))
        return {"FINISHED"}


class UpdateVGMap(Operator):
    """分配新的3DMigoto顶点组"""

    bl_idname = "mesh.update_migoto_vertex_group_map"
    bl_label = "分配新的3DMigoto顶点组"
    bl_options = {"UNDO"}

    vg_step: bpy.props.IntProperty(
        name="顶点组步长",
        description="如果使用的顶点组是0,1,2,3,等等，请指定1。如果是0,3,6,9,12,等等，请指定3",
        default=1,
        min=1,
    )

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        try:
            keywords = self.as_keywords()
            update_vgmap(self, context, **keywords)
        except Fatal as e:
            self.report({"ERROR"}, str(e))
        return {"FINISHED"}


@orientation_helper(axis_forward="-Z", axis_up="Y")
class Import3DMigotoPose(Operator, ImportHelper, IOOBJOrientationHelper):
    """从3DMigoto常量缓冲区转储导入姿态"""

    bl_idname = "armature.migoto_pose"
    bl_label = "导入3DMigoto姿态"
    bl_options = {"UNDO"}

    filename_ext = ".txt"
    filter_glob: StringProperty(
        default="*.txt",
        options={"HIDDEN"},
    )

    limit_bones_to_vertex_groups: BoolProperty(
        name="限制骨骼到顶点组",
        description="将导入的最大骨骼数限制为活动对象的顶点组数",
        default=True,
    )

    pose_cb_off: bpy.props.IntVectorProperty(
        name="骨骼CB范围",
        description="指示在骨骼CB中查找矩阵的开始和结束偏移量（以4个分量值的倍数）",
        default=[0, 0],
        size=2,
        min=0,
    )

    pose_cb_step: bpy.props.IntProperty(
        name="顶点组步长",
        description="如果使用的顶点组是0,1,2,3,等等，请指定1。如果是0,3,6,9,12,等等，请指定3",
        default=1,
        min=1,
    )

    def execute(self, context):
        try:
            keywords = self.as_keywords(ignore=("filter_glob",))
            import_pose(self, context, **keywords)
        except Fatal as e:
            self.report({"ERROR"}, str(e))
        return {"FINISHED"}


class Merge3DMigotoPose(Operator):
    """将相关骨架的相同姿态骨骼合并为一个"""

    bl_idname = "armature.merge_pose"
    bl_label = "合并3DMigoto姿态"
    bl_options = {"UNDO"}

    def execute(self, context):
        try:
            merge_armatures(self, context)
        except Fatal as e:
            self.report({"ERROR"}, str(e))
        return {"FINISHED"}


class DeleteNonNumericVertexGroups(Operator):
    """移除非数字名称的顶点组"""

    bl_idname = "vertex_groups.delete_non_numeric"
    bl_label = "移除非数字顶点组"
    bl_options = {"UNDO"}

    def execute(self, context):
        try:
            for obj in context.selected_objects:
                for vg in reversed(obj.vertex_groups):
                    if vg.name.isdecimal():
                        continue
                    print("Removing vertex group", vg.name)
                    obj.vertex_groups.remove(vg)
        except Fatal as e:
            self.report({"ERROR"}, str(e))
        return {"FINISHED"}


class Preferences(AddonPreferences):
    """首选项更新器"""

    bl_idname = package_name
    # Addon updater preferences.

    auto_check_update: BoolProperty(
        name="自动检查更新",
        description="如果启用，使用间隔自动检查更新",
        default=False,
    )

    updater_interval_months: IntProperty(
        name="月",
        description="检查更新之间的月数",
        default=0,
        min=0,
    )

    updater_interval_days: IntProperty(
        name="天",
        description="检查更新之间的天数",
        default=7,
        min=0,
        max=31,
    )

    updater_interval_hours: IntProperty(
        name="小时",
        description="检查更新之间的小时数",
        default=0,
        min=0,
        max=23,
    )

    updater_interval_minutes: IntProperty(
        name="分钟",
        description="检查更新之间的分钟数",
        default=0,
        min=0,
        max=59,
    )

    def draw(self, context):
        layout = self.layout
        print(addon_updater_ops.get_user_preferences(context))
        # Works best if a column, or even just self.layout.
        mainrow = layout.row()
        _ = mainrow.column()
        # Updater draw function, could also pass in col as third arg.
        addon_updater_ops.update_settings_ui(self, context)

        # Alternate draw function, which is more condensed and can be
        # placed within an existing draw function. Only contains:
        #   1) check for update/update now buttons
        #   2) toggle for auto-check (interval will be equal to what is set above)
        # addon_updater_ops.update_settings_ui_condensed(self, context, col)

        # Adding another column to help show the above condensed ui as one column
        # col = mainrow.column()
        # col.scale_y = 2
        # ops = col.operator("wm.url_open","Open webpage ")
        # ops.url=addon_updater_ops.updater.website
