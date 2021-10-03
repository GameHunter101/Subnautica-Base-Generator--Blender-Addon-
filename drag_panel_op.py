import bpy
import sys
import os
from easybpy import *

dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir )

from bpy.types import Operator

from bl_ui_button import *
from subscribe_func import *

import keyboard
import globals
wm = bpy.types.WindowManager
wm.DP_started = bpy.props.BoolProperty(default=False)

class DP_OT_draw_operator(Operator):
    bl_idname = "object.dp_ot_draw_operator"
    bl_label = "bl ui widgets operator"
    bl_description = "Operator for bl ui widgets" 
    bl_options = {'REGISTER'}
       
    @classmethod
    def poll(cls, context):
        return True
    
    def __init__(self):
        self.draw_handle = None
        self.draw_event  = None
        
        self.button1 = BL_UI_Button(20, 20, 120, 30)
        self.button1.set_bg_color((1.0, 0.2, 0.2, 0.8))
        self.button1.set_mouse_down(self.button1_press)
        self.button1.set_text("Back")
        
    
    # Button press handlers    
    def button1_press(self, widget):
        #print("Button '{0}' is pressed".format(widget.text))
        for window in bpy.context.window_manager.windows:
                screen = window.screen
                for area in screen.areas:
                     if area.type == "VIEW_3D":
                        override = {"window": window, "screen": screen, "area": area}
                        bpy.ops.view3d.localview(override)
                        ob = get_object("skel")
                        bpy.msgbus.clear_by_owner(ob)
                        def instance_helper(orig_obj, new_name, new_location = None):
                            new_obj = copy_object(orig_obj)
                            rename_object(new_obj, new_name)
                            parts.append(new_obj)
                            
                            if new_location != None:
                                location(new_obj, new_location)
                            return new_obj
                        keyboard.press_and_release("f12")
                        globals.to_windows = selected_objects()
                        print(globals.to_windows, "&&&&&&")
                        parts = []
                        set_window = selected_objects()
                        for wall in set_window:
                            new_window_wall = instance_helper(get_object("part10"), "window_instance", location(wall))
                            rotation(new_window_wall, rotation(wall))
                            if "tilt" in wall.name:
                                deselect_all_objects()
                                select_object(new_window_wall)
                                bpy.ops.transform.rotate(value=-0.785398, orient_axis='Z', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
                            #display_as_bounds(wall)
                            #hide_in_render(wall)
                            delete_object(wall)
                        subscribe_obj(ob, go_to_local)
                        break
        
    def invoke(self, context, event):
        args = (self, context)
        
        if(context.window_manager.DP_started is False):
            context.window_manager.DP_started = True
                
            # Register draw callback
            self.register_handlers(args, context)
                       
            context.window_manager.modal_handler_add(self)
            return {"RUNNING_MODAL"}
        else:
            context.window_manager.DP_started = False
            return {'CANCELLED'}
    
    def register_handlers(self, args, context):
        self.draw_handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_px, (self, context), "WINDOW", "POST_PIXEL")
        self.draw_event = context.window_manager.event_timer_add(0.1, window=context.window)
        
    def unregister_handlers(self, context):
        
        context.window_manager.event_timer_remove(self.draw_event)
        
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handle, "WINDOW")
        self.draw_handle = None
        self.draw_event  = None
          
    def modal(self, context, event):
        if context.area:
            context.area.tag_redraw()
        
        # TODO: Refactor this  
        if self.button1.handle_event(event):
            return {'RUNNING_MODAL'}   
        
        if event.type in {"ESC"}:
            context.window_manager.DP_started = False
        
        if not context.window_manager.DP_started:
            self.unregister_handlers(context)
            return {'CANCELLED'}
               
        return {"PASS_THROUGH"}
                            
        
    def cancel(self, context):
        if context.window_manager.DP_started:
            self.unregister_handlers(context)
        return {'CANCELLED'}        
        
    def finish(self):
        self.unregister_handlers(context)
        return {"FINISHED"}
        
    # Draw handler to paint onto the screen
    def draw_callback_px(self, context, args):
        self.button1.draw()


def register():
    bpy.utils.register_class(DP_OT_draw_operator)

def unregister():
    bpy.utils.unregister_class(DP_OT_draw_operator)

if __name__ == "__main__":
    register()