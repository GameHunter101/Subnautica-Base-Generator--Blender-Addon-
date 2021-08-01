
bl_info = {
    "name": "Subnautica Base Generator",
    "author": "Lior Carmeli",
    "version": (1,0),
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
)
from bpy_extras.io_utils import ImportHelper
import bmesh
from easybpy import *
import mathutils
from mathutils.bvhtree import BVHTree
import math
import os
import re

FILEPATH = ""


class OBJECT_OT_subnautica_base_generator(Operator, ImportHelper):
    
    bl_label = "Generate Base"
    bl_idname = "object.generate_base"
    bl_description = "Generates a Subnautica base from a base mesh"
    bl_space_type = "VIEW_3D"
    bl_region_types = "UI"
    bl_options = {'REGISTER', 'UNDO'}
    
    filter_glob: StringProperty(
    default = "*.blend",
    options = {"HIDDEN"}
    )
    def execute(self, context):
        
        global FILEPATH
        FILEPATH = self.filepath
        #print(FILEPATH)
        
        FILEPATH = FILEPATH.replace("\\", "/")
        if(len(FILEPATH) > 1):
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

            # create collections
            parts_collection = create_collection("base_parts")
            parts_collection = get_collection("base_parts")
            import_collection = create_collection("parts_import")
            import_collection = get_collection("parts_import")

            # import parts

            bpy.ops.wm.append(filepath = "subnauticabaseparts.blend", directory = FILEPATH.strip()+"/Object/".strip(), filename = "Tube_Original", link = False)
            
            tubes = get_objects_including("Tube")
            imports.append(tubes[0])
            tubes.clear()

            
            bpy.ops.wm.append(filepath = "subnauticabaseparts.blend", directory = FILEPATH.strip()+"/Object/".strip(), filename = "Room_Original", link = False)
            
            rooms = get_objects_including("Room")
            imports.append(rooms[len(rooms)-1])
            rooms.clear()


            bpy.ops.wm.append(filepath = "subnauticabaseparts.blend", directory = FILEPATH.strip()+"/Object/".strip(), filename = "Corner_Original", link = False)

            corners = get_objects_including("Corner")
            imports.append(corners[0])
            corners.clear()


            bpy.ops.wm.append(filepath = "subnauticabaseparts.blend", directory = FILEPATH.strip()+"/Object/".strip(), filename = "XCon_Original", link = False)

            x_cons = get_objects_including("XCon")
            imports.append(x_cons[0])
            x_cons.clear()
            
            
            bpy.ops.wm.append(filepath = "subnauticabaseparts.blend", directory = FILEPATH.strip()+"/Object/".strip(), filename = "RCon_Original", link = False)

            r_cons = get_objects_including("RCon")
            imports.append(r_cons[0])
            r_cons.clear()
            
            
            
            bpy.ops.wm.append(filepath = "subnauticabaseparts.blend", directory = FILEPATH.strip()+"/Object/".strip(), filename = "TCon_Original", link = False)

            t_cons = get_objects_including("TCon")
            imports.append(t_cons[0])
            t_cons.clear()


            if parts_collection:
                for i, o in enumerate(imports):
                    o.name = "part%d" % i
                    o.to_mesh(preserve_all_data_layers = True)

            tube = get_object(imports[0])
            room = get_object(imports[1])
            corner = get_object(imports[2])
            x_con = get_object(imports[3])
            r_con = get_object(imports[4])
            t_con = get_object(imports[5])
            
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
                """for e in bm.edges:
                    for verts in e.verts:
                        if verts.index == v.index:
                            for v.link_edges:
                                return e.other_vert(v)"""
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
                apply_location(new_room)
                bm1 = bmesh.new()
                bm2 = bmesh.new()
                
                bm1.from_mesh(new_room.data)
                bm1.transform(new_room.matrix_world)
                room_BVH = BVHTree.FromBMesh(bm1)
                for bp in parts:
                    if "tube" in bp.name:
                        # detect if tubes overlap
                        bm2.from_mesh(bp.data)
                        bm2.transform(bp.matrix_world)
                        part_BVH = BVHTree.FromBMesh(bm2)
                        inter = room_BVH.overlap(part_BVH)
                        inter.append(bp)
                        if len(inter) > 2:
                            tube_delete = get_object(inter[len(inter)-1])
                            rename_object(tube_delete, "tube_delete")
                            #get rotation of tubes
                            display_as_bounds(bp)
                            hide_in_render(bp)
            

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
                
                #print(vert_b)
                verts_location = []
                for e in vert_a.link_edges:
                    v_other = e.other_vert(vert_a)
                    verts_location.append(v_other.co-tc[1].co)
                print(verts_location)
                    
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

            
            move_objects_to_collection(parts, parts_collection)
            move_objects_to_collection(imports, import_collection)
            
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(OBJECT_OT_subnautica_base_generator.bl_idname)

classes = (
    OBJECT_OT_subnautica_base_generator,
)
def register():
    from bpy.utils import register_class
    #register_class(OT_OpenFilebrowser)
    for cls in classes:
        register_class(cls)
    
    #bpy.types.Scene.my_tool = PointerProperty(type=MyProperties)
    
    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    from bpy.utils import unregister_class
    #unregister_class(OT_OpenFilebrowser)
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.my_tool
    
    bpy.types.VIEW3D_MT_object.remove(menu_func)

if __name__ == "__main__":
    register()
    