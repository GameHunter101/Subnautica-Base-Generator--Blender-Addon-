bl_info = {
    "name": "Subnautica Base Generator",
    "author": "Lior Carmeli",
    "version": (3,1),
    "blender": (2,93,0),
    "location": "View3D > Object",
    "description": "Generates a Subnautica base from a base mesh",
    "warning": "",
    "wiki_url": "",
    "catergory": "Object",
}




import bpy
from bpy.types import (
    AddonPreferences,
    Operator,
    Panel,
    PropertyGroup,
)
from bpy.props import(
    StringProperty,
    PointerProperty,
    IntProperty,
    BoolProperty,
    EnumProperty,
)
from bpy.props import *
from bpy_extras.io_utils import ImportHelper
import bmesh
from easybpy import *
import mathutils
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import math
import os
import re
import random
from bpy.types import Operator
from bpy.utils import register_class, unregister_class
import gc
import sys
import tracemalloc
import numpy
import subprocess
from collections import namedtuple
import subprocess
import importlib.util

dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir )



wm = bpy.types.WindowManager
wm.DP_started = bpy.props.BoolProperty(default=False)

name = "keyboard"

if name in sys.modules:
    import keyboard
    from .drag_panel_op import DP_OT_draw_operator
#elif (spec := importlib.util.find_spec(name)) is not None:
else:
    # If you choose to perform the actual import ...
    """module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)"""
    # path to python.exe
    python_exe = os.path.join(sys.prefix, 'bin', 'python.exe')
    # install required packages
    subprocess.call([python_exe, "-m", "pip", "install", name])

    import keyboard
    from .drag_panel_op import DP_OT_draw_operator
from .subscribe_func import *
#import globals

FILEPATH = ""
class GENProperties(PropertyGroup):
    filepath_string : StringProperty(
        name = "filepath_string",
        description = "Filepath for base part",
        default = "",
        subtype = "FILE_PATH"
    )
    
    size_global : IntProperty(
        name = "Size",
        description = "Size of base",
        default = 20
    )
    
    auto_base : BoolProperty(
        name = "Autogen",
        description = "Automatically generate a base after generating a skeleton",
        default = False
    )
    
    auto_parent : BoolProperty(
        name = "Autoprnt",
        description = "Automatically parent base parts to skeleton",
        default = True
    )
    
    import_quality : EnumProperty(
        name  = "Parts Quality",
        description = "Select the quality of the imports (high, medium, low)",
        items = [
            ("HIGH_QUALITY", "High Quality", ""),
            ("MEDIUM_QUALITY", "Medium Quality", ""),
            ("LOW_QUALITY", "Low Quality", "")
        ],
        default = "MEDIUM_QUALITY"
    )
    
    more_rooms : BoolProperty(
        name  = "More Rooms",
        description = "Generate more rooms. (ONLY USE THIS WITH LARGE BASES, ONLY WORKS WITH SKEL GEN)",
        default = False
    )
    
    interior_generator: BoolProperty(
        name = "Generate Interior",
        description = "Generates interior for each part, can not be used with quality dropdown",
        default = False
    )
    
    exterior_generator: BoolProperty(
        name = "Exterior Generator",
        description = "Generates an exterior for the interior generator (ONLY USE WHEN GENERATING INTERIOR)",
        default = False
    )
    
    editing_windows: BoolProperty(
        name = "Editing Windows",
        default = True
    )
    
    random_windows: BoolProperty(
        name = "Random Windows",
        description = "Randomly generate windows",
        default = False
    )


class OT_OpenFileBrowser(Operator, ImportHelper):
    bl_idname = "gen.open_filebrowser"
    bl_label = "Get file"
    filter_glob : StringProperty(
        default = "*.blend",
        options={"HIDDEN"}
    )

    
    def execute(self, context):
        scene = context.scene
        gen_tool = scene.gen_tool
        gen_tool.filepath_string = self.filepath
        global FILEPATH
        FILEPATH = gen_tool.filepath_string
        print("FILEPATH FOUND", FILEPATH)
        return{"FINISHED"}


class Object_PT_Basic_Settings_panel(Panel):
    bl_idname = 'Object_PT_Basic_Settings_panel'
    bl_label = 'Basic Generation'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Base Gen'
    
    def draw(self, context):
        
        layout = self.layout
        scene = context.scene
        gen_tool = scene.gen_tool
        
        box = layout.box()
        box.label(text="Basic Generation")
        col = box.column()
        row = col.row(align = True)
        
        box1 = box.box()
        col = box1.column()
        #row.prop(gen_tool, "filepath_string", text ="File Path")
        row = col.row(align = True)
        row.operator("gen.open_filebrowser", text="Select Filepath")
        row = col.row(align = True)
        #row.label(text = "Uncheck relative paths (n-menu)")
        #row = col.row(align = True)
        #row.prop(gen_tool, "filepath_global", text ="File Path")
        row.operator('test.test_op', text='Base Gen').action = 'BASE_GEN'
        row = col.row(align = True)
        row.operator('test.test_op', text='Skel Gen').action = 'SKEL_GEN'
        row = col.row(align = True)
        row.prop(gen_tool, "size_global", text="Base Size")
        row = col.row(align = True)
        
        box2 = box.box()
        col = box2.column()
        
        row = col.row(align = True)
        row.prop(gen_tool, "auto_base", text="Automatically Generate Base")
        row = col.row(align = True)
        row.prop(gen_tool, "auto_parent", text="Automatically Parent To Skeleton")
        row = col.row(align = True)
        row.prop(gen_tool, "more_rooms", text="Generate More Rooms (Skel Gen)")
        row = col.row(align = True)
        row.prop(gen_tool,"import_quality", text = "")
        row = col.row(align = True)
        row.operator("gen.remove_double_mats", text = "Remove Double Mats")
        row = col.row(align = True)
        
class Object_PT_Interior_Settings_panel(Panel):
    bl_idname = 'Object_PT_Interior_Settings_panel'
    bl_label = 'Interior Generation'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Base Gen'
    
    
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        gen_tool = scene.gen_tool
        
        box = layout.box()
        col = box.column()
        row = col.row(align = True)
        
        
        row.prop(gen_tool,"interior_generator", text="Generate Interior")
        row = col.row(align = True)
        row.prop(gen_tool,"exterior_generator", text="Generate Exterior")
        row = col.row(align = True)
        row.operator("gen.windows", text="Toggle Window Select", icon="EVENT_OS")
        row = col.row(align = True)
        row.prop(gen_tool,"random_windows", text = "Random Window Gen")

class TEST_OT_test_op(Operator):
    bl_idname = 'test.test_op'
    bl_label = 'Test'
    bl_description = 'Test'
    bl_options = {'REGISTER', 'UNDO'}
    
    size = 20
    
    action: EnumProperty(
        items=[
            ('BASE_GEN', 'base gen', 'base gen'),
            ('SKEL_GEN', 'skel gen', 'skel gen')
        ]
    )

    def execute(self, context):
        if self.action == 'BASE_GEN':
            self.base_gen(context)
        if self.action == 'SKEL_GEN':
            self.skel_gen(context, self)
        return {'FINISHED'}
    
    def skel_gen(x,context, self):
        
        scene = context.scene
        gen_tool = scene.gen_tool
        
        
        # Variables
        obj = ao()
        previous = 2

        def extrude(direction):
            
            dirVec = Vector((0,0,0))
            
            if direction == 0:
                dirVec = Vector((1,0,0))
            if direction == 1:
                dirVec = Vector((-1,0,0))
            if direction == 2:
                dirVec = Vector((0,1,0))
            if direction == 3:
                dirVec = Vector((0,-1,0))
            
            bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":dirVec})


        def make_skeleton(previous_number):
            if obj.mode != "EDIT":
                bpy.ops.object.mode_set(mode="EDIT", toggle=False)
            
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
            bpy.ops.mesh.select_all(action = "SELECT")
            bpy.ops.mesh.merge(type="COLLAPSE")
            random_direction = 0
            for i in range(gen_tool.size_global):
                random_direction = random.randint(0,3)
                if random_direction == previous_number:
                    while random_direction == previous_number:
                        random_direction = random.randint(0,3)
                extrude(random_direction)
                previous_number = random_direction
            bpy.ops.mesh.select_all(action = "SELECT")
            bpy.ops.mesh.remove_doubles()
            bpy.ops.mesh.dissolve_limited()
            bpy.ops.object.mode_set(mode="OBJECT", toggle=False)
            select_object(obj, True)
        make_skeleton(previous)
        
        if gen_tool.auto_base == True:
            self.base_gen(context)
        
    def base_gen(self, context):
        tracemalloc.start()
        scene = context.scene
        gen_tool = scene.gen_tool
        
        global FILEPATH
        print(FILEPATH, "********")
        #FILEPATH = self.filepath
        
        #FILEPATH = gen_tool.filepath_string
        
        FILEPATH = FILEPATH.replace("\\", "/")
        # CHECK MEMORY ----------
        current, peak = tracemalloc.get_traced_memory()
            
        print(current/8*1000, peak/8*1000)
        if(len(FILEPATH) > 0):
            # arrays
            imports = []
            parts = []
            tubes = []
            rooms = []
            corners = []
            x_cons = []
            r_cons = []
            t_cons = []
            caps = []
            con_walls = []
            walls = []
            normal_walls = []
            normal_walls_tilt = []
            windows = []
            tubes_to_delete = []
            
            HQ_Parts_name = ["Tube_HQ", "Room_HQ", "Corner_HQ", "XCon_HQ", "RCon_HQ", "TCon_HQ", "Cap_HQ"]
            MQ_Parts_name = ["Tube_MQ", "Room_MQ", "Corner_MQ", "XCon_MQ", "RCon_MQ", "TCon_MQ", "Cap_MQ"]
            LQ_Parts_name = ["Tube_LQ", "Room_LQ", "Corner_LQ", "XCon_LQ", "RCon_LQ", "TCon_LQ", "Cap_LQ"]
            Ext_Parts_name = ["Tube_Ext", "Room_Ext", "Corner_Ext", "XCon_Ext", "RCon_Ext", "TCon_Ext", "Cap_Ext", "Room_Int_Con_Wall_Ext", "Room_Int_Wall_Ext", "Room_Int_Wall_Tilt_Ext", "Room_Int_Wall_Window"]

            Int_Parts_name = ["Tube_Int", "Room_Int", "Corner_Int", "XCon_Int", "RCon_Int", "TCon_Int", "Cap_HQ", "Room_Int_Con_Wall", "Room_Int_Wall", "Room_Int_Wall_Tilt", "Room_Int_Wall_Window"]
            
            importlist = [tubes, rooms, corners, x_cons, r_cons, t_cons, caps]
            importlist_interior = [tubes, rooms, corners, x_cons, r_cons, t_cons, caps, con_walls, walls, walls, windows]
            
            import_temp_name = ["Tube", "Room", "Corner", "XCon", "RCon", "TCon", "Cap"]
            import_temp_name_Interior = ["Tube_Int", "Room_Int", "Corner_Int", "XCon_Int", "RCon_Int", "TCon_Int", "Cap", "Room_Int_Con_Wall", "Room_Int_Wall"]
            
            
            if get_collection("parts_import"):
                pass
            else:
                # create collections
                parts_collection = create_collection("base_parts")
                parts_collection = get_collection("base_parts")
                import_collection = create_collection("parts_import")
                import_collection = get_collection("parts_import")

                # import parts
                
                def import_helper(tempfilename, templist):
                    bpy.ops.wm.append(filepath = "subnauticabaseparts.blend", directory = FILEPATH.strip()+"/Object/".strip(), filename = tempfilename, link = False)
                    print(tempfilename, "*****")
                    templist = get_objects_including(tempfilename)
                    imports.append(templist[0])
                    templist.clear()
                    
                # CHECK MEMORY ----------
                current, peak = tracemalloc.get_traced_memory()
                
                print(current/8000, peak/8000)
                
                if gen_tool.interior_generator == False:
                    if gen_tool.import_quality == "LOW_QUALITY":
                        for i in range(len(importlist)):
                            import_helper(LQ_Parts_name[i], importlist[i])
                        
                    elif gen_tool.import_quality == "HIGH_QUALITY":
                        for i in range(len(importlist)):
                            import_helper(HQ_Parts_name[i], importlist[i])
                            
                    elif gen_tool.import_quality == "MEDIUM_QUALITY":
                        for i in range(len(importlist)):
                            import_helper(MQ_Parts_name[i], importlist[i])
                else:
                    if gen_tool.exterior_generator:
                        for i in range(len(importlist_interior)):
                            import_helper(Ext_Parts_name[i], importlist_interior[i])
                    else:
                        for i in range(len(importlist_interior)):
                            import_helper(Int_Parts_name[i], importlist_interior[i])
                        
                        
                #import_helper("Cap_Final", caps, "Cap")
                
                move_objects_to_collection(imports, get_collection("parts_import"))

            if gen_tool.interior_generator == True:
                print(imports)
                for i, o in enumerate(imports):
                    o.name = "part%d" % i
                    o.to_mesh(preserve_all_data_layers = True)
                tube = get_object("part0")
                room = get_object("part1")
                corner = get_object("part2")
                x_con = get_object("part3")
                r_con = get_object("part4")
                t_con = get_object("part5")
                cap = get_object("part6")
                con_wall = get_object("part7")
                normal_wall = get_object("part8")
                normal_wall_tilt = get_object("part9")
                window = get_object("part10")
            else:    
                for i, o in enumerate(imports):
                    o.name = "part%d" % i
                    o.to_mesh(preserve_all_data_layers = True)
                tube = get_object("part0")
                room = get_object("part1")
                corner = get_object("part2")
                x_con = get_object("part3")
                r_con = get_object("part4")
                t_con = get_object("part5")
                cap = get_object("part6")
            
            
            
            # CHECK MEMORY ----------
            current, peak = tracemalloc.get_traced_memory()
            
            print(current/8000, peak/8000)
            
            
            bpy.ops.object.mode_set(mode='EDIT')
            
            
                
            # variables
            obj = bpy.context.active_object
            mesh = obj.data
            bm = bmesh.from_edit_mesh(mesh)
            scene = bpy.context.scene
            
            rename_object(obj, "skel")
            
            def findAngle(v, ind1, ind2):
                adir = v.link_edges[ind1].other_vert(v).co - v
                bdir = v.link_edges[ind2].other_vert(v).co - v
                return(adir.angle(bdir))

            def findAngleAbsolute(v, ind1):
                adir = v.link_edges[ind1].other_vert(v).co - v
                adir.z = 0
                return(adir.angle(mathutils.Vector((1,0,0))))

            def rotate_to_direction(source, dest, obj):
                k = dest.normalized().cross(source.normalized())
                if k.length <= 0.000001 and dest.dot(source) < 0:
                    rotate_around_axis(180, source.cross(mathutils.Vector((1,1,1))).normalized(), obj)
                else:
                    rotate_around_axis(math.asin(max(min(k.length, 1), -1))*(180/math.pi), k.normalized(), obj)
            
            def rotate_to_direction_z(source, dest, obj):
                k = dest.normalized().cross(source.normalized())
                if k.length <= 0.000001 and dest.dot(source) < 0:
                    rotate_around_axis(180, source.cross(mathutils.Vector((0,0,1))).normalized(), obj)
                else:
                    rotate_around_axis(math.asin(max(min(k.length, 1), -1))*(180/math.pi), k.normalized(), obj)
            
            def instance_object_new(ref, newname = None, col = None):
                deselect_all_objects()
                select_object(ref)
                bpy.ops.object.mode_set(mode = "OBJECT")
                bpy.ops.object.duplicate_move_linked()
                o = selected_object()
                if newname is not None:
                    o.name = newname
                if col is not None:
                    link_object_to_collection(o,col)
                return o
            
            def get_other_vert(v):
                v_other = []
                for e in v.link_edges:
                    v_other.append(e.other_vert(v))
                return v_other
                
            def instance_helper(orig_obj, new_name, new_location = None):
                new_obj = copy_object(orig_obj)
                rename_object(new_obj, new_name)
                parts.append(new_obj)
                
                if new_location != None:
                    location(new_obj, new_location)
                
                return new_obj
            
            def random_caps():
                for i in range(int(len(rooms)*0.7)):
                    random_room = random.randint(0, len(rooms))-1
                    caps.append(rooms.pop(random_room))
                    
            
            
            def random_rooms():
                if gen_tool.more_rooms:
                    for i in range(int(len(corners)*0.8)):
                        random_corner = random.randint(0, len(corners))-1
                        rooms.append(corners.pop(random_corner))
                else:
                    for i in range(int(len(corners)*0.5)):
                        random_corner = random.randint(0, len(corners))-1
                        rooms.append(corners.pop(random_corner))
                for x in rooms:
                    
                    # check every room vert, if other vert is in room list, pop and append to corner
                    
                    for i in get_other_vert(x[1]):
                        if (i.co, i) in rooms:
                            index = rooms.index((i.co, i))
                            corners.append(rooms.pop(index))
                    
            def deselect_verts():
                for v in obj.data.vertices:
                        v.select = False

            def getLocalXAxis(object):
                mat = object.matrix_world
                localX  = Vector((mat[0][0],mat[1][0],mat[2][0]))
                return localX
            
            def getDistanceOBJS(obj1, obj2):
                    return math.sqrt((obj1.location.x - obj2.location.x)**2 + (obj1.location.y-obj2.location.y)**2)

            def instance_rotate_wall(rot, instance_obj, parent_obj = None):
                deselect_all_objects()
                select_object(instance_obj)
                bpy.ops.transform.rotate(value=rot, orient_axis='Z', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
                if parent_obj != None:
                    deselect_all_objects()
                    select_object(instance_obj)
                    select_object(parent_obj)
                    bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
            
            def random_window_gen():
                deselect_all_objects()
                all_walls = get_objects_including("wall")
                to_windows = []
                for aw in all_walls:
                    if "con" in aw.name:
                        all_walls.remove(aw)
                    random_wall = random.randint(0,len(all_walls))
                    if random_wall % 3 == 0:
                        to_windows.append(aw)
                for wndw in to_windows:
                    instance_window = instance_helper(window, "window_instance", location(wndw))
                    rotation(instance_window, rotation(wndw))
                    if "tilt" in wndw.name:
                        deselect_all_objects()
                        select_object(instance_window)
                        bpy.ops.transform.rotate(value=-0.785398, orient_axis='Z', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
                    display_as_bounds(wndw)
                    hide_in_render(wndw)
                    hide_in_viewport(wndw)
                """
                for wall_count in range(int(len(all_walls)*0.8)):
                    print(wall_count)
                    walls = all_walls[wall_count]
                    if "con" not in walls.name:
                        #print(random_wall)
                        windows.append(all_walls.pop(random_wall))
                    for wndw in windows:
                        instance_window = instance_helper(window, "window_instance", location(wndw))
                        rotation(instance_window, rotation(wndw))
                        if "tilt" in wndw.name:
                            deselect_all_objects()
                            select_object(instance_window)
                            bpy.ops.transform.rotate(value=-0.785398, orient_axis='Z', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
                        display_as_bounds(wndw)
                        hide_in_render(wndw)
                        hide_in_viewport(wndw)"""

            # appending positions of vertices to proper arrays
            for v in bm.verts:
                obMat = obj.matrix_world
                
                if (len(v.link_edges) == 2):
                    corners.append((obMat @ v.co, v))
                 
                if (len(v.link_edges) == 1):
                    rooms.append((obMat @ v.co, v))
                    
                if (len(v.link_edges) == 3):
                    t_cons.append((obMat @ v.co, v))
                
                if (len(v.link_edges) == 4):
                    x_cons.append(obMat @ v.co)
            
            for e in bm.edges:
                obMat = obj.matrix_world
                tubes.append((obMat @ ((e.verts[0].co+e.verts[1].co)/2), obMat @ e.verts[0].co, obMat @ e.verts[1].co))
            
            
            # instancing objects at points specified in the arrays
            
            # CHECK MEMORY ----------
            current, peak = tracemalloc.get_traced_memory()
            
            print(current/8000, peak/8000)

            for t in tubes:
                #new_tube = instance_helper(tube, "tube_instance", t[0])
                
                new_tube = instance_helper(tube, "tube_instance")
                dir = t[1]-t[0]
                
                angle = 0
                
                if abs(dir.x) < abs(dir.y):
                    angle = 1
                rotate_around_z(angle*90, new_tube)
                
                
                location(new_tube, t[0])
            
            # CHECK MEMORY ----------
            current, peak = tracemalloc.get_traced_memory()
            
            print(current/8000, peak/8000)
            
            random_caps()
            random_rooms()
            for r in rooms:
                deselect_all_objects()
                select_object(obj)
                deselect_verts()
                bm.verts.ensure_lookup_table()
                bm.verts[r[1].index].select = True
                selected_verts =  [v for v in bm.verts if v.select]
                room_vert = selected_verts[0]
                room_other = get_other_vert(room_vert)
                
                # check direction for multiple rcons
                
                new_room = instance_helper(room, "room_instance", r[0])
                #apply_location(new_room)
                
                for bp in parts:
                    if "room" not in bp.name:
                        if "tube" in bp.name:
                            distance = getDistanceOBJS(new_room, bp)
                            if distance < 1:
                                tube_delete = get_object(bp)
                                tubes_to_delete.append(tube_delete)
                                rename_object(tube_delete, "tube_delete")
                                #get rotation of tubes
                                display_as_bounds(tube_delete)
                                hide_in_render(tube_delete)
                                hide_in_viewport(tube_delete)
                                
                                vert = ""
                                
                                for v in obj.data.vertices:
                                    if obj.matrix_world @ v.co == r[0]:
                                        vert = v
                                r_cons.append((vert, vert.index, location(tube_delete), rotation(tube_delete), new_room))
                
                if gen_tool.interior_generator:
                    new_tilt_wall_1 = instance_helper(normal_wall_tilt, "tilt_wall_instance", new_room.location)
                    new_tilt_wall_2 = instance_helper(normal_wall_tilt, "tilt_wall_instance", new_room.location)
                    new_tilt_wall_3 = instance_helper(normal_wall_tilt, "tilt_wall_instance", new_room.location)
                    new_tilt_wall_4 = instance_helper(normal_wall_tilt, "tilt_wall_instance", new_room.location)
                    
                    close_tubes = []
                    close_tubes_x = 0
                    close_tubes_y = 0
                    
                    room_connections = ""
                    
                    for td in tubes_to_delete:
                        get_close_tubes = getDistanceOBJS(new_room, td)
                        if get_close_tubes < 1:
                            close_tubes.append(td)
                    
                    for ct in close_tubes:
                        close_tubes_x += (ct.location.x - new_room.location.x)
                        close_tubes_y += (ct.location.y - new_room.location.y)
                    
                    if close_tubes_x ==  0 or close_tubes_y == 0:
                        if close_tubes_y == 0:
                            if close_tubes_x == 0.5:
                                room_connections = "+x"
                            elif close_tubes_x == -0.5:
                                room_connections = "-x"
                        
                        elif close_tubes_x == 0:
                            if close_tubes_y == 0.5:
                                room_connections = "+y"
                            elif close_tubes_y == -0.5:
                                room_connections = "-y"
                    else:
                        if close_tubes_x == 0.5:
                            if close_tubes_y == 0.5:
                                room_connections = "+x+y"
                            elif close_tubes_y == -0.5:
                                room_connections = "+x-y"
                        
                        elif close_tubes_x == -0.5:
                            if close_tubes_y == 0.5:
                                room_connections = "-x+y"
                            elif close_tubes_y == -0.5:
                                room_connections = "-x-y"
                    deselect_all_objects()
                    if len(room_connections) == 2:
                        new_con_wall = instance_helper(con_wall, "con_wall_instance", new_room.location)
                        new_normal_wall_1 = instance_helper(normal_wall, "normal_wall_instance", new_room.location)
                        new_normal_wall_2 = instance_helper(normal_wall, "normal_wall_instance", new_room.location)
                        new_normal_wall_3 = instance_helper(normal_wall, "normal_wall_instance", new_room.location)
                        deselect_all_objects()
                        if room_connections == "-x":
                            instance_rotate_wall(3.14159, new_normal_wall_1, new_room)
                            instance_rotate_wall(1.5708, new_normal_wall_2, new_room)
                            instance_rotate_wall(-1.5708, new_normal_wall_3, new_room)
                            
                            instance_rotate_wall(0, new_tilt_wall_1)
                            instance_rotate_wall(-1.5708, new_tilt_wall_2)
                            instance_rotate_wall(1.5708, new_tilt_wall_3)
                            instance_rotate_wall(3.14159, new_tilt_wall_4)
                            
                        elif room_connections == "+x":
                            instance_rotate_wall(3.14159, new_con_wall, new_room)
                            instance_rotate_wall(1.5708, new_normal_wall_1, new_room)
                            instance_rotate_wall(-1.5708, new_normal_wall_2, new_room)
                            
                            instance_rotate_wall(0, new_tilt_wall_1)
                            instance_rotate_wall(-1.5708, new_tilt_wall_2)
                            instance_rotate_wall(1.5708, new_tilt_wall_3)
                            instance_rotate_wall(3.14159, new_tilt_wall_4)
                        elif room_connections == "-y":
                            instance_rotate_wall(1.5708, new_con_wall, new_room)
                            instance_rotate_wall(3.14159, new_normal_wall_1, new_room)
                            instance_rotate_wall(-1.5708, new_normal_wall_2, new_room)
                            
                            instance_rotate_wall(0, new_tilt_wall_1)
                            instance_rotate_wall(-1.5708, new_tilt_wall_2)
                            instance_rotate_wall(1.5708, new_tilt_wall_3)
                            instance_rotate_wall(3.14159, new_tilt_wall_4)

                        elif room_connections == "+y":
                            instance_rotate_wall(-1.5708, new_con_wall, new_room)
                            instance_rotate_wall(3.14159, new_normal_wall_1, new_room)
                            instance_rotate_wall(1.5708, new_normal_wall_2, new_room)
                            
                            instance_rotate_wall(0, new_tilt_wall_1)
                            instance_rotate_wall(-1.5708, new_tilt_wall_2)
                            instance_rotate_wall(1.5708, new_tilt_wall_3)
                            instance_rotate_wall(3.14159, new_tilt_wall_4)
                        deselect_all_objects()
                        select_object(new_con_wall)
                        select_object(new_normal_wall_1)
                        select_object(new_normal_wall_2)
                        select_object(new_normal_wall_3)
                        select_object(new_room)
                    else:
                        new_con_wall_1 = instance_helper(con_wall, "con_wall_instance", new_room.location)
                        new_con_wall_2 = instance_helper(con_wall, "con_wall_instance", new_room.location)
                        new_normal_wall_1 = instance_helper(normal_wall, "normal_wall_instance", new_room.location)
                        new_normal_wall_2 = instance_helper(normal_wall, "normal_wall_instance", new_room.location)
                        deselect_all_objects()
                        if room_connections == "-x-y":
                            instance_rotate_wall(1.5708, new_con_wall_2, new_room)
                            instance_rotate_wall(-1.5708, new_normal_wall_1, new_room)
                            instance_rotate_wall(3.14159, new_normal_wall_2, new_room)
                            
                            instance_rotate_wall(0, new_tilt_wall_1)
                            instance_rotate_wall(-1.5708, new_tilt_wall_2)
                            instance_rotate_wall(1.5708, new_tilt_wall_3)
                            instance_rotate_wall(3.14159, new_tilt_wall_4)
                        elif room_connections == "-x+y":
                            instance_rotate_wall(-1.5708, new_con_wall_2, new_room)
                            instance_rotate_wall(1.5708, new_normal_wall_1, new_room)
                            instance_rotate_wall(3.14159, new_normal_wall_2, new_room)
                            
                            instance_rotate_wall(0, new_tilt_wall_1)
                            instance_rotate_wall(-1.5708, new_tilt_wall_2)
                            instance_rotate_wall(1.5708, new_tilt_wall_3)
                            instance_rotate_wall(3.14159, new_tilt_wall_4)
                        elif room_connections == "+x-y":
                            instance_rotate_wall(3.14159, new_con_wall_1, new_room)
                            instance_rotate_wall(1.5708, new_con_wall_2, new_room)
                            instance_rotate_wall(-1.5708, new_normal_wall_2, new_room)
                            
                            instance_rotate_wall(0, new_tilt_wall_1)
                            instance_rotate_wall(-1.5708, new_tilt_wall_2)
                            instance_rotate_wall(1.5708, new_tilt_wall_3)
                            instance_rotate_wall(3.14159, new_tilt_wall_4)
                        elif room_connections == "+x+y":
                            instance_rotate_wall(3.14159, new_con_wall_1, new_room)
                            instance_rotate_wall(-1.5708, new_con_wall_2, new_room)
                            instance_rotate_wall(1.5708, new_normal_wall_2, new_room)
                            
                            instance_rotate_wall(0, new_tilt_wall_1)
                            instance_rotate_wall(-1.5708, new_tilt_wall_2)
                            instance_rotate_wall(1.5708, new_tilt_wall_3)
                            instance_rotate_wall(3.14159, new_tilt_wall_4)
                        deselect_all_objects()
                        select_object(new_con_wall_1)
                        select_object(new_con_wall_2)
                        select_object(new_normal_wall_1)
                        select_object(new_normal_wall_2)
                        select_object(new_room)
                        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
                    for x in parts:
                        if new_room.location - x.location == mathutils.Vector((0,0,0)):
                            deselect_all_objects()
                            select_object(x)
                            select_object(new_room)
                            bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
                            print(x)
                
                del distance
            if gen_tool.random_windows:
                random_window_gen()
            # CHECK MEMORY ----------
            current, peak = tracemalloc.get_traced_memory()
            
            print(current/8000, peak/8000)
            
            for rc in r_cons:
                counter = 0
                new_r_con = instance_helper(r_con, "r_con_instance", rc[2])
                rotation(new_r_con, rc[3])
                deselect_all_objects()
                select_object(new_r_con)
                move_along_local_x(1, new_r_con)
                distance = getDistanceOBJS(rc[4], new_r_con)
                if distance > 1:
                    instance_rotate_wall(3.14159, new_r_con)
                rotation(new_r_con).x = 0
                rotation(new_r_con).y = 0
                location(new_r_con, rc[2])
                #rotate_around_z(180, new_r_con)
                #move_along_local_x(1.5, new_r_con)
                deselect_all_objects()
                select_object(obj)
                bpy.ops.object.mode_set(mode="EDIT")
                bpy.ops.mesh.select_all(action="DESELECT")
                bm.verts.ensure_lookup_table()
                #bpy.ops.object.mode_set(mode="OBJECT")
                bm.verts[rc[1]].select = True
                selected_verts =  [v for v in bm.verts if v.select]
                vert_a = selected_verts[0]
                vert_b = get_other_vert(vert_a)
                #vert_b_first = vert_b[0]
                
                """for x in vert_b:
                    print(x)
                a_x = vert_a.co.x
                a_y = vert_a.co.y
                
                
                b_x = vert_b_first.co.x
                b_y = vert_b_first.co.y
                
                #print(b_y, new_r_con)
                
                rotate_around_z(-90, new_r_con)
                
                if a_x == b_x:
                    if b_y - a_y > 0:
                        pass
                    else:
                        rotate_around_z(180, new_r_con)
                else:
                    if a_y == b_y:
                        if b_x < a_x:
                            rotate_around_z(90, new_r_con)
                        else:
                            rotate_around_z(-90, new_r_con)
                vert_b.remove(vert_b[0])"""
            
            # CHECK MEMORY ----------
            current, peak = tracemalloc.get_traced_memory()
            
            print(current/8000, peak/8000)
            
            for cp in caps:
                new_cap = instance_helper(cap, "cap_instance", cp[0])
                
                ov = get_other_vert(cp[1])
                
                ov_co = (obj.matrix_world @ ov[0].co)-cp[0]
                deselect_all_objects()
                select_object(new_cap)
                if ov_co.x != 0:
                    if ov_co.x == 1:
                        bpy.ops.transform.rotate(value=1.5708, orient_axis='Z', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
                    else:
                        bpy.ops.transform.rotate(value=-1.5708, orient_axis='Z', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
                else:
                    if ov_co.y == 1:
                        bpy.ops.transform.rotate(value=-3.14159, orient_axis='Z', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
                    else:
                        pass
                        #bpy.ops.transform.rotate(value=-3.14159, orient_axis='Z', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
            
            # CHECK MEMORY ----------
            current, peak = tracemalloc.get_traced_memory()
            
            print(current/8000, peak/8000)
            
            for c in corners:
                new_corner = instance_helper(corner, "corner_instance", c[0])
                
                linked_verts = []
                for l in c[1].link_edges:
                    linked_verts.append(l.other_vert(c[1]))
                # mimicing lines 86-88, but using information collected from linked verts
                connected_verts = (obMat @ linked_verts[0].co, obMat @ linked_verts[1].co)
                dirs = (connected_verts[0]-c[0], connected_verts[1]-c[0])
                
                
                combined_directions = dirs[0] + dirs[1]
                angle = 0
                x_dir = combined_directions.x
                y_dir = combined_directions.y
                
                
                if x_dir > 0 and y_dir > 0:
                    angle = 0
                if x_dir > 0 and y_dir < 0:
                    angle = 3
                if x_dir < 0 and y_dir > 0:
                    angle = 1
                if x_dir < 0 and y_dir < 0:
                    angle = 2
                instance_rotate_wall(math.radians(angle*90), new_corner)
                
                
                location(new_corner, c[0])

            # CHECK MEMORY ----------
            current, peak = tracemalloc.get_traced_memory()
            
            print(current/8000, peak/8000)
            
            for tc in t_cons:
                new_t_con = instance_helper(t_con, "t_con_instance", tc[0])
                deselect_all_objects()
                select_object(obj)
                bpy.ops.object.mode_set(mode="EDIT")
                bpy.ops.mesh.select_all(action="DESELECT")
                bm.verts.ensure_lookup_table()
                bm.verts[tc[1].index].select = True
                selected_verts =  [v for v in bm.verts if v.select]
                vert_a = selected_verts[0]
                vert_b = get_other_vert(vert_a)
                
                
                verts_location = []
                for e in vert_a.link_edges:
                    v_other = e.other_vert(vert_a)
                    verts_location.append(mathutils.Vector((round(v_other.co.x-tc[1].co.x, 0), round(v_other.co.y-tc[1].co.y, 0), round(v_other.co.z-tc[1].co.z, 0))))
                vector_x = 0
                vector_y = 0
                
                for vector in verts_location:
                    if vector.x != 0:
                        vector_x += vector.x
                    else:
                        vector_y += vector.y
                        
                if vector_x == 0:
                    if vector_y < 0:
                        pass
                    else:
                        rotate_around_z(180, new_t_con)
                else:
                    if vector_x < 0:
                        rotate_around_z(-90, new_t_con)
                    else:
                        rotate_around_z(90, new_t_con)
                    
            
            
            # CHECK MEMORY ----------
            current, peak = tracemalloc.get_traced_memory()
            
            print(current/8000, peak/8000)

            for xc in x_cons:
                new_x_con = instance_helper(x_con, "x_con_instance", xc)

            
            for p in parts:
                bpy.data.collections["base_parts"].objects.link(p)
            bpy.ops.object.mode_set(mode="OBJECT", toggle=False)
            
            if gen_tool.auto_parent == True:
                deselect_all_objects()
                for bp in parts:
                    if bp.parent == None:
                        select_object(bp, True)
                        set_parent(bp, obj)
            
            import_collection.hide_viewport = True
            import_collection.hide_render = True
            
            
            
            for n in locals():
                del n
            del parts
            del tubes
            del findAngle
            del findAngleAbsolute
            del rotate_to_direction
            del rotate_to_direction_z
            del instance_object_new
            del get_other_vert
            del imports
            del corners
            del r_cons
            del tubes_to_delete
            del Int_Parts_name
            del import_temp_name_Interior
            del import_helper
            del random_caps
            del random_rooms
            
            current, peak = tracemalloc.get_traced_memory()
            
            print(current/8000, peak/8000)
            
            def sizeof_fmt(num, suffix='B'):
                ''' by Fred Cirera,  https://stackoverflow.com/a/1094933/1870254, modified'''
                for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
                    if abs(num) < 1024.0:
                        return "%3.1f %s%s" % (num, unit, suffix)
                    num /= 1024.0
                return "%.1f %s%s" % (num, 'Yi', suffix)

            for name, size in sorted(((name, sys.getsizeof(value)) for name, value in locals().items()),
                                     key= lambda x: -x[1])[:100]:
                print("{:>30}: {:>8}".format(name, sizeof_fmt(size)))
class Object_PT_Window_Select(Operator):
    bl_idname = 'gen.windows'
    bl_label = 'Window generation'
    bl_description = 'Select walls to turn into windows'
    bl_options = {'REGISTER', 'UNDO'}
    
    
        
    

    
    def execute(self, context):
        layout = self.layout
        scene = context.scene
        gen_tool = scene.gen_tool
        deselect_all_objects()
        
        orig_view = ""
        
        for area in bpy.context.screen.areas:
            if area.type == "VIEW_3D":
                orig_view = area.spaces[0].shading.color_type
        
        if gen_tool.editing_windows == True:
            if len([area for area in bpy.context.screen.areas if area.type =='VIEW_3D' and area.spaces[0].local_view]) > 0:
                    for obj in get_all_objects():
                        bpy.msgbus.clear_by_owner(obj)
            ob = get_object("skel")
                
            for area in bpy.context.screen.areas:
                if area.type == "VIEW_3D":
                    area.spaces[0].region_3d.view_rotation = mathutils.Quaternion((1.0,0.0,0.0,0.0))
                    area.spaces[0].region_3d.view_perspective = "ORTHO"
                    area.spaces[0].shading.color_type = 'MATERIAL'
            #if material_exists("Window_Indicator") == False:
            #bpy.ops.wm.append(filepath = "subnauticabaseparts.blend", directory = FILEPATH.strip()+ "/Material/".strip(), filename = "Window_Indicator", link = False)
            for obj in get_all_objects():
                if len(obj.children) > 1:
                    if "room" in obj.name:
                        select_object(obj)
                        for child in obj.children:
                            select_object(child)
                        for so in selected_objects():
                            for i in range(len(so.data.materials)):
                                new_mat = so.data.materials[i].copy()
                                new_mat.diffuse_color = (1, 0, 0, 1)
                                so.data.materials[i] = new_mat
                        deselect_all_objects()
            #subscribe_to_click_event(ob)
            subscribe_obj(ob, go_to_local)
            gen_tool.editing_windows = not gen_tool.editing_windows
        else:
            for obj in get_all_objects():
                bpy.msgbus.clear_by_owner(obj)
                for i in range(len(obj.data.materials)):
                    mat = obj.data.materials[i]
                    mat.diffuse_color = (1, 1, 1, 1)
            gen_tool.editing_windows = not gen_tool.editing_windows
            for area in bpy.context.screen.areas:
                if area.type == "VIEW_3D":
                    area.spaces[0].shading.color_type = orig_view
        return {"FINISHED"}
    
    
    


class Object_PT_Remove_Double_Mats(Operator):
    bl_idname = "gen.remove_double_mats"
    bl_label = "Remove double materials"
    bl_description = "Removes double materials (.001, 0.002)"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        
        temp_obj = create_plane()

        #print(len(temp_obj.material_slots))
        og_mat = ""
        for add_mats in get_all_materials():
            add_material_to_object(temp_obj, add_mats)
            
            mat = add_mats.name.rpartition(".")
            
            if mat[1] == '':
                og_mat = add_mats
            #print(og_mat.name)
            
            for x in get_all_objects():
                if x != temp_obj:
                    obj_mats = x.data.materials
                    for i in range(0, len(obj_mats)):
                        obj_mats_partitioned = obj_mats[i].name.rpartition(".")
                        print(og_mat, "&&&&&&")
                        if obj_mats_partitioned[0] == og_mat.name:
                            #print("yesss")
                            print(obj_mats[i].name, og_mat.name)
                            obj_mats[i] = og_mat
                            #delete_material(obj_mats[i])
            
        delete_object(temp_obj)
        for all_mats in get_all_materials():
            if "." in all_mats.name:
                delete_material(all_mats)
        return {"FINISHED"}



classes = (
    GENProperties,
    TEST_OT_test_op,
    Object_PT_Basic_Settings_panel,
    Object_PT_Interior_Settings_panel,
    OT_OpenFileBrowser,
    Object_PT_Window_Select,
    Object_PT_Remove_Double_Mats,
    DP_OT_draw_operator
)

addon_keymaps = []

def register():
    for cls in classes:
        register_class(cls)
    bpy.types.Scene.gen_tool = PointerProperty(type=GENProperties)
    
    """my_keymap = {   'F12': "object.dp_ot_draw_operator",
                    'Y': "object.subscribe"}
    #my_keymap = {   'Y': "gen.subscribe"}
    kcfg = bpy.context.window_manager.keyconfigs.addon
    if kcfg:
        km = kcfg.keymaps.new(name='3D View', space_type='VIEW_3D')
        for k, v in my_keymap.items():
            new_shortcut = km.keymap_items.new(v, k, 'PRESS')
            addon_keymaps.append((km, new_shortcut))"""
    
    
    
    kcfg = bpy.context.window_manager.keyconfigs.addon
    if kcfg:
        km = kcfg.keymaps.new(name='3D View', space_type='VIEW_3D')
   
        kmi = km.keymap_items.new("object.dp_ot_draw_operator", "F12", 'PRESS')
        
        addon_keymaps.append((km, kmi))
    
 
 
def unregister():
    for cls in classes:
        unregister_class(cls)
    
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    del bpy.types.Scene.gen_tool
    
 
 
if __name__ == '__main__':
    register()