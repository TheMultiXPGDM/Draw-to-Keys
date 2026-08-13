import bpy
from mathutils import Vector
from . import utils

class CreateKeyframesOperator(bpy.types.Operator):
    """Keyframe the selected object along the drawn path"""
    bl_idname = "draw2keys.create_keyframes"
    bl_label = "Create Keyframes"
    bl_options = {'REGISTER', 'UNDO'}

    def get_object(self, context):
        obj = context.active_object
        if obj is None or not obj.select_get():
            return None
        if obj.mode == 'POSE':
            if context.active_pose_bone and context.active_pose_bone.select:
                return context.active_pose_bone
        return obj

    def keyframe_object(self, context, intersections, obj):
        props = context.scene.draw2keys_props
        start = context.scene.frame_current if props.use_curr else props.start_frame
        frame_step = props.frame_step
        ipo_type = props.ipo_type

        intersections.sort(key=lambda x: x["value"])

        is_bone = isinstance(obj, bpy.types.PoseBone)
        modified_curves = set()

        if is_bone:
            armature = obj.id_data
            rest_head = obj.bone.matrix_local.to_translation()
            armature_world_inv = armature.matrix_world.inverted()
        else:
            parent = obj.parent
            parent_world_inv = parent.matrix_world.inverted() if parent else None

        for i, inter in enumerate(intersections):
            frame = start + i * frame_step
            context.scene.frame_set(frame)

            global_point = Vector(inter["point"])

            if is_bone:
                arm_space = armature_world_inv @ global_point
                new_mat = obj.matrix.copy()
                new_mat.translation = arm_space
                obj.matrix = new_mat
            else:
                local_pos = parent_world_inv @ global_point if parent_world_inv else global_point
                obj.location = local_pos

            for axis, use_flag in enumerate([props.use_x, props.use_y, props.use_z]):
                if use_flag:
                    obj.keyframe_insert(data_path="location", frame=frame, index=axis)
                    modified_curves.add(("location", axis))

            if props.use_val:
                obj["stroke_value"] = inter["value"]
                obj.keyframe_insert(data_path='["stroke_value"]', frame=frame)
                modified_curves.add(('["stroke_value"]', -1))

        if ipo_type != "DEFAULT":
            if is_bone:
                anim_data = armature.animation_data
            else:
                anim_data = obj.animation_data

            if anim_data and anim_data.action:
                fcurves = utils.get_action_fcurves(anim_data.action)
                if fcurves:
                    for fcurve in fcurves:
                        key = (fcurve.data_path, fcurve.array_index)
                        if key in modified_curves and fcurve.keyframe_points:
                            fcurve.keyframe_points[0].interpolation = ipo_type

    def execute(self, context):
        props = context.scene.draw2keys_props
        obj = self.get_object(context)
        if obj is None:
            self.report({'WARNING'}, "Select an object or bone.")
            return {'FINISHED'}

        strokes = utils.get_strokes(context)
        if not strokes:
            self.report({'WARNING'}, "No strokes found.")
            return {'FINISHED'}

        mainpath = utils.get_main_path(strokes)
        candidates = utils.get_candidates(strokes, mainpath)
        if props.debug:
            print(candidates)
        intersections = utils.get_intersections(context, candidates, strokes, mainpath)
        if props.debug:
            print(intersections)

        self.keyframe_object(context, intersections, obj)
        self.report({'INFO'}, f"{len(intersections)} keyframes generated.")
        return {'FINISHED'}