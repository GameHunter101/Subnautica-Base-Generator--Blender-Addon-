import bpy
from easybpy import *
from bpy.types import Operator
import keyboard
import os
import sys

dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir )

import globals
"""
class Object_PT_Subscribe(Operator):
    bl_idname = "object.subscribe"
    bl_label = "bl ui widgets operator"
    bl_description = "Operator for bl ui widgets" 
    bl_options = {'REGISTER'}

    def execute(self, context):
        print("SUBSCRIBING")
        def go_to_local(ob):
                #gen_tool.editing_windows = False
                deselect_all_objects()
                orig_obj = ao()
                # on red object select, select all children and go to local view
                #bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
                for child in ao().children:
                    select_object(orig_obj)
                    select_object(ob)
                    select_object(child)
                for window in bpy.context.window_manager.windows:
                    screen = window.screen
                    for area in screen.areas:
                        if area.type == "VIEW_3D":
                            override = {"window": window, "screen": screen, "area": area}
                            bpy.ops.view3d.localview(override)
                            #gen_tool.editing_windows = True
                            bpy.msgbus.clear_by_owner(ob)
                            keyboard.press_and_release("f12")
                            break

        ob = get_object("skel")
        bpy.msgbus.clear_by_owner(ob)
        def subscribe_to_click_event(ob):
            subscribe_to = bpy.types.LayerObjects, "active"
            bpy.msgbus.subscribe_rna(
                key = subscribe_to,
                owner = ob,
                args = (ob,),
                notify = go_to_local,
            )
        subscribe_to_click_event(ob)
        return {"FINISHED"}

def register():
    bpy.utils.register_class(Object_PT_Subscribe)

def unregister():
    bpy.utils.unregister_class(Object_PT_Subscribe)

if __name__ == "__main__":
    register()

"""

def to_window_append(ob):
    print("appending")
    if "room" not in ao().name:
        globals.to_windows.append(ao())

def go_to_local(ob):
    #gen_tool.editing_windows = False
    deselect_all_objects()
    orig_obj = ao()
    # on red object select, select all children and go to local view
    #bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
    if "room_instance" in orig_obj.name:
        for child in ao().children:
            if "con" not in child.name:
                select_object(orig_obj)
                #select_object(ob)
                select_object(child)
        for window in bpy.context.window_manager.windows:
            screen = window.screen
            for area in screen.areas:
                if area.type == "VIEW_3D":
                    override = {"window": window, "screen": screen, "area": area}
                    bpy.ops.view3d.localview(override)
                    #gen_tool.editing_windows = True
                    bpy.msgbus.clear_by_owner(ob)
                    keyboard.press_and_release("f12")
                    break
    else:
        globals.to_windows.append(ao())
def prep_subscribe(ob, func):
    subscribe_to = bpy.types.LayerObjects, "active"
    bpy.msgbus.subscribe_rna(
        key = subscribe_to,
        owner = ob,
        args = (ob,),
        notify = func,
    )

def subscribe_obj(obj, function):
    print("subscribing")
    prep_subscribe(obj, function)

def alt_subscribe(obj):
    print("alt_subscribing")
    prep_subscribe(obj, to_window_append)