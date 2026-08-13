import bpy

class Draw2KeysProperties(bpy.types.PropertyGroup):
    ipo_type: bpy.props.EnumProperty(
        name="Interpolation Type",
        items=(
            ("DEFAULT", "Default", "Set default interpolation", "BLANK1", 0),
            ("CONSTANT", "Constant", "Set interpolation to constant", "IPO_CONSTANT", 1),
            ("LINEAR", "Linear", "Set interpolation to linear", "IPO_LINEAR", 2),
            ("BEZIER", "Bezier", "Set interpolation to bezier", "IPO_BEZIER", 3),
        ),
        default="DEFAULT",
    )

    frame_step: bpy.props.IntProperty(
        name="Frame Step",
        description="Number of frames per keyframe",
        min=1,
        default=1,
    )

    start_frame: bpy.props.IntProperty(
        name="Start",
        description="Frame of the first keyframe",
        default=0,
    )

    use_curr: bpy.props.BoolProperty(
        name="Use Current Frame",
        default=True,
    )

    use_x: bpy.props.BoolProperty(
        name="X",
        description="Enable X axis",
        default=True,
    )

    use_y: bpy.props.BoolProperty(
        name="Y",
        description="Enable Y axis",
        default=True,
    )

    use_z: bpy.props.BoolProperty(
        name="Z",
        description="Enable Z axis",
        default=True,
    )

    use_val: bpy.props.BoolProperty(
        name="Include Value",
        description="Include an extra value of the percentage of the path",
        default=False,
    )

    intersect_threshold: bpy.props.FloatProperty(
        name="Intersection Threshold",
        description="Maximum distance between a dash and the main path to be considered intersecting",
        default=1e-3,
        min=0.0,
        max=1.0,
        step=1e-3,
        precision=4,
    )

    auto_threshold: bpy.props.BoolProperty(
        name="Auto Threshold",
        description="Automatically calculate threshold based on scene scale",
        default=True,
    )

    debug: bpy.props.BoolProperty(
        name="Debug",
        description="Print debug info to console",
        default=False,
    )