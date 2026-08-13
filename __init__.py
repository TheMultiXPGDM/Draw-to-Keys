import bpy
from . import properties, operators, panels

classes = (
    properties.Draw2KeysProperties,
    operators.CreateKeyframesOperator,
    panels.DRAW2KEYS_PT_Main,
    panels.DRAW2KEYS_PT_Advanced,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.draw2keys_props = bpy.props.PointerProperty(type=properties.Draw2KeysProperties)

def unregister():
    del bpy.types.Scene.draw2keys_props
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()