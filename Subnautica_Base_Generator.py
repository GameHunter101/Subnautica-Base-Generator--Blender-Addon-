bl_info = {
    "name": "Subnautica Base Generator",
    "author": "Lior Carmeli",
    "version": (2,0),
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
from bpy_extras.io_utils import ImportHelper
import bmesh
from easybpy import *
import mathutils
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

FILEPATH = ""

class GENProperties(PropertyGroup):
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
    
    filepath_global : StringProperty(
        name = "filepath_string",
        description = "Filepath for base part",
        default = ""
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


    

class TEST_PT_panel(Panel):
    bl_idname = 'TEST_PT_panel'
    bl_label = 'Subnautica Base Generator'
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
        
        row.operator("gen.open_filebrowser", text="Select Filepath")
        row = col.row(align = True)
        row.operator('test.test_op', text='Base Gen').action = 'BASE_GEN'
        row = col.row(align = True)
        row.operator('test.test_op', text='Skel Gen').action = 'SKEL_GEN'
        row = col.row(align = True)
        row.prop(gen_tool, "size_global", text="Base Size")
        row = col.row(align = True)
        row.prop(gen_tool, "auto_base", text="Automatically Generate Base")
        row = col.row(align = True)
        row.prop(gen_tool, "auto_parent", text="Automatically Parent To Skeleton")
        row = col.row(align = True)
        row.prop(gen_tool,"import_quality", text = "")
        row = col.row(align = True)


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
        gen_tool.filepath_global = self.filepath
        global FILEPATH
        FILEPATH = gen_tool.filepath_global
        return{"FINISHED"}


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
        scene = context.scene
        gen_tool = scene.gen_tool
        
        global FILEPATH
        #FILEPATH = self.filepath
        
        FILEPATH = FILEPATH.replace("\\", "/")
        if(len(FILEPATH) > 0):
            # arrays
            imports = []
            parts = []
            tubes = []
            rooms = []
            corners = []
            t_cons = []
            x_cons = []
            r_cons = []
            tubes_to_delete = []
            
            if get_collection("parts_import"):
                pass
            else:
                # create collections
                parts_collection = create_collection("base_parts")
                parts_collection = get_collection("base_parts")
                import_collection = create_collection("parts_import")
                import_collection = get_collection("parts_import")

                # import parts
                
                if gen_tool.import_quality == "LOW_QUALITY":
                    bpy.ops.wm.append(filepath = "subnauticabaseparts.blend", directory = FILEPATH.strip()+"/Object/".strip(), filename = "Tube_LQ", link = False)
                    
                    tubes = get_objects_including("Tube")
                    imports.append(tubes[0])
                    tubes.clear()

                    
                    bpy.ops.wm.append(filepath = "subnauticabaseparts.blend", directory = FILEPATH.strip()+"/Object/".strip(), filename = "Room_LQ", link = False)
                    
                    rooms = get_objects_including("Room")
                    imports.append(rooms[len(rooms)-1])
                    rooms.clear()


                    bpy.ops.wm.append(filepath = "subnauticabaseparts.blend", directory = FILEPATH.strip()+"/Object/".strip(), filename = "Corner_LQ", link = False)

                    corners = get_objects_including("Corner")
                    imports.append(corners[0])
                    corners.clear()


                    bpy.ops.wm.append(filepath = "subnauticabaseparts.blend", directory = FILEPATH.strip()+"/Object/".strip(), filename = "XCon_LQ", link = False)

                    x_cons = get_objects_including("XCon")
                    imports.append(x_cons[0])
                    x_cons.clear()
                    
                    
                    bpy.ops.wm.append(filepath = "subnauticabaseparts.blend", directory = FILEPATH.strip()+"/Object/".strip(), filename = "RCon_LQ", link = False)

                    r_cons = get_objects_including("RCon")
                    imports.append(r_cons[0])
                    r_cons.clear()
                    
                    
                    
                    bpy.ops.wm.append(filepath = "subnauticabaseparts.blend", directory = FILEPATH.strip()+"/Object/".strip(), filename = "TCon_LQ", link = False)

                    t_cons = get_objects_including("TCon")
                    imports.append(t_cons[0])
                    t_cons.clear()
                    move_objects_to_collection(imports, get_collection("parts_import"))
                elif gen_tool.import_quality == "HIGH_QUALITY":
                    bpy.ops.wm.append(filepath = "subnauticabaseparts.blend", directory = FILEPATH.strip()+"/Object/".strip(), filename = "Tube_HQ", link = False)
                    
                    tubes = get_objects_including("Tube")
                    imports.append(tubes[0])
                    tubes.clear()

                    
                    bpy.ops.wm.append(filepath = "subnauticabaseparts.blend", directory = FILEPATH.strip()+"/Object/".strip(), filename = "Room_HQ", link = False)
                    
                    rooms = get_objects_including("Room")
                    imports.append(rooms[len(rooms)-1])
                    rooms.clear()


                    bpy.ops.wm.append(filepath = "subnauticabaseparts.blend", directory = FILEPATH.strip()+"/Object/".strip(), filename = "Corner_HQ", link = False)

                    corners = get_objects_including("Corner")
                    imports.append(corners[0])
                    corners.clear()


                    bpy.ops.wm.append(filepath = "subnauticabaseparts.blend", directory = FILEPATH.strip()+"/Object/".strip(), filename = "XCon_HQ", link = False)

                    x_cons = get_objects_including("XCon")
                    imports.append(x_cons[0])
                    x_cons.clear()
                    
                    
                    bpy.ops.wm.append(filepath = "subnauticabaseparts.blend", directory = FILEPATH.strip()+"/Object/".strip(), filename = "RCon_HQ", link = False)

                    r_cons = get_objects_including("RCon")
                    imports.append(r_cons[0])
                    r_cons.clear()
                    
                    
                    
                    bpy.ops.wm.append(filepath = "subnauticabaseparts.blend", directory = FILEPATH.strip()+"/Object/".strip(), filename = "TCon_HQ", link = False)

                    t_cons = get_objects_including("TCon")
                    imports.append(t_cons[0])
                    t_cons.clear()
                    move_objects_to_collection(imports, get_collection("parts_import"))
                    
                    
                    
                elif gen_tool.import_quality == "MEDIUM_QUALITY":
                    bpy.ops.wm.append(filepath = "subnauticabaseparts.blend", directory = FILEPATH.strip()+"/Object/".strip(), filename = "Tube_HQ", link = False)
                    
                    tubes = get_objects_including("Tube")
                    imports.append(tubes[0])
                    tubes.clear()

                    
                    bpy.ops.wm.append(filepath = "subnauticabaseparts.blend", directory = FILEPATH.strip()+"/Object/".strip(), filename = "Room_MQ", link = False)
                    
                    rooms = get_objects_including("Room")
                    imports.append(rooms[len(rooms)-1])
                    rooms.clear()


                    bpy.ops.wm.append(filepath = "subnauticabaseparts.blend", directory = FILEPATH.strip()+"/Object/".strip(), filename = "Corner_MQ", link = False)

                    corners = get_objects_including("Corner")
                    imports.append(corners[0])
                    corners.clear()


                    bpy.ops.wm.append(filepath = "subnauticabaseparts.blend", directory = FILEPATH.strip()+"/Object/".strip(), filename = "XCon_MQ", link = False)

                    x_cons = get_objects_including("XCon")
                    imports.append(x_cons[0])
                    x_cons.clear()
                    
                    
                    bpy.ops.wm.append(filepath = "subnauticabaseparts.blend", directory = FILEPATH.strip()+"/Object/".strip(), filename = "RCon_MQ", link = False)

                    r_cons = get_objects_including("RCon")
                    imports.append(r_cons[0])
                    r_cons.clear()
                    
                    
                    
                    bpy.ops.wm.append(filepath = "subnauticabaseparts.blend", directory = FILEPATH.strip()+"/Object/".strip(), filename = "TCon_MQ", link = False)

                    t_cons = get_objects_including("TCon")
                    imports.append(t_cons[0])
                    t_cons.clear()
                    move_objects_to_collection(imports, get_collection("parts_import"))


            for i, o in enumerate(imports):
                o.name = "part%d" % i
                o.to_mesh(preserve_all_data_layers = True)
            tube = get_object("part0")
            room = get_object("part1")
            corner = get_object("part2")
            x_con = get_object("part3")
            r_con = get_object("part4")
            t_con = get_object("part5")
            
            bpy.ops.object.mode_set(mode='EDIT')
            
            
                
            # variables
            obj = bpy.context.active_object
            mesh = obj.data
            bm = bmesh.from_edit_mesh(mesh)
            scene = bpy.context.scene
            
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
                for e in v.link_edges:
                    v_other = e.other_vert(v)
                    return v_other


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

            for t in tubes:
                new_tube = copy_object(tube)
                rename_object(new_tube, "tube_instance")
                new_tube.to_mesh(preserve_all_data_layers=True)
                parts.append(new_tube)
                dir = t[1]-t[0]
                
                angle = 0
                
                if abs(dir.x) < abs(dir.y):
                    angle = 1
                
                rotate_around_z(angle*90, new_tube)
                
                
                location(new_tube, t[0])
            
            
            for r in rooms:
                new_room = copy_object(room)
                rename_object(new_room, "room_instance")
                location(new_room, r[0])
                parts.append(new_room)
                #r_cons.append(r[0])
                for vert in obj.data.vertices:
                    if vert.co == r[0]:
                        r_cons.append((vert, vert.index))
                #apply_location(new_room)
                

                def getDistance(obj1, obj2):
                    return math.sqrt((obj1.location.x - obj2.location.x)**2 + (obj1.location.y-obj2.location.y)**2)
                
                for bp in parts:
                    if "tube" in bp.name:
                        
                        distance = getDistance(new_room, bp)
                        
                        if distance < 1:
                            tube_delete = get_object(bp)
                            rename_object(tube_delete, "tube_delete")
                            print(new_room.name, tube_delete.name)
                            #get rotation of tubes
                            display_as_bounds(tube_delete)
                            hide_in_render(tube_delete)
                            del distance

            for rc in r_cons:
                new_r_con = copy_object(r_con)
                rename_object(new_r_con, "r_con_instance")
                location(new_r_con, rc[0].co)
                parts.append(new_r_con)
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
                
                a_x = vert_a.co.x
                a_y = vert_a.co.y
                
                b_x = vert_b.co.x
                b_y = vert_b.co.y
                
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
                
                
            for c in corners:
                new_corner = copy_object(corner)
                rename_object(new_corner, "corner_instance")
                new_corner.to_mesh(preserve_all_data_layers=True)
                parts.append(new_corner)
                
                
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
                rotate_around_z(angle*90, new_corner)
                
                
                location(new_corner, c[0])

            
            for tc in t_cons:
                new_t_con = copy_object(t_con)
                rename_object(new_t_con, "t_con_instance")
                parts.append(new_t_con)
                location(new_t_con, tc[0])
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
                    verts_location.append(v_other.co-tc[1].co)
                
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
                    
            


            for xc in x_cons:
                new_x_con = copy_object(x_con)
                rename_object(new_x_con, "x_con_instance")
                parts.append(new_x_con)
                location(new_x_con, xc)

            
            for p in parts:
                bpy.data.collections["base_parts"].objects.link(p)
            bpy.ops.object.mode_set(mode="OBJECT", toggle=False)
            
            if gen_tool.auto_parent == True:
                deselect_all_objects()
                for bp in parts:
                    select_object(bp, True)
                    set_parent(bp, obj)
            
            import_collection.hide_viewport = True
            import_collection.hide_render = True
            
            
            for n in globals():
                del n
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
            del getDistance
            del imports
            del corners
                

classes = (
    GENProperties,
    TEST_OT_test_op,
    TEST_PT_panel,
    OT_OpenFileBrowser
)


def register():
    for cls in classes:
        register_class(cls)
    
    bpy.types.Scene.gen_tool = PointerProperty(type=GENProperties)
 
 
def unregister():
    for cls in classes:
        unregister_class(cls)
    del bpy.types.Scene.gen_tool
 
 
if __name__ == '__main__':
    register()