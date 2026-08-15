import bpy
from . import utils

class DRAW2KEYS_PT_Main(bpy.types.Panel):
    bl_label = "Draw to Keys"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Animation"
    bl_options = {'HEADER_LAYOUT_EXPAND'}

    def draw(self, context):
        layout = self.layout
        props = context.scene.draw2keys_props

        col = layout.box().column()
        header = col.box().row()
        header.alignment = 'CENTER'
        header.label(text="Keyframes", icon="DECORATE_KEYFRAME")
        grid = col.grid_flow(row_major=True, columns=2, align=True)
        grid.prop(props, 'ipo_type', expand=True)
        col.prop(props, 'frame_step')
        row = col.row(align=True)
        row.prop(props, 'use_curr', toggle=True)
        start_col = row.column(align=True)
        start_col.enabled = not props.use_curr
        start_col.prop(props, 'start_frame')

        col = layout.box().column()
        header = col.box().row()
        header.alignment = 'CENTER'
        header.label(text="Path Keyframing", icon="TRACKING")
        row = col.row(align=True)
        row.prop(props, 'use_x', toggle=True)
        row.prop(props, 'use_y', toggle=True)
        row.prop(props, 'use_z', toggle=True)
        col.prop(props, 'use_val', toggle=True, icon=('RADIOBUT_ON' if props.use_val else 'RADIOBUT_OFF'))
        col.operator("draw2keys.create_keyframes", icon="DECORATE_KEYFRAME")

class DRAW2KEYS_PT_Advanced(bpy.types.Panel):
    bl_label = "Draw to Keys Advanced"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Animation"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        props = context.scene.draw2keys_props

        col = layout.box().column()
        header = col.box().row()
        header.alignment = 'CENTER'
        header.label(text="Intersection", icon="VIEWZOOM")

        row = col.row(align=True)
        row.prop(props, "auto_threshold", toggle=True)
        sub = col.column(align=True)
        sub.enabled = not props.auto_threshold
        sub.prop(props, "intersect_threshold")

        if props.auto_threshold:
            current = utils.auto_calc_threshold(context)
            sub.label(text=f"Current: {current:.4f}")

        col = layout.box().column()
        col.prop(props, 'debug')
