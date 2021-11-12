import bpy
from ..sollumz_properties import PolygonType, items_from_enums, BoundType, SOLLUMZ_UI_NAMES
from bpy.app.handlers import persistent
from .collision_materials import collisionmats
from ..resources.flag_preset import FlagPresetsFile
from ..tools.meshhelper import create_disc, create_cylinder, create_sphere, create_capsule, create_box
from mathutils import Vector, Matrix
import os


class CollisionMatFlags(bpy.types.PropertyGroup):
    none: bpy.props.BoolProperty(name="NONE", default=False)
    stairs: bpy.props.BoolProperty(name="STAIRS", default=False)
    not_climbable: bpy.props.BoolProperty(name="NOT CLIMBABLE", default=False)
    see_through: bpy.props.BoolProperty(name="SEE THROUGH", default=False)
    shoot_through: bpy.props.BoolProperty(name="SHOOT THROUGH", default=False)
    not_cover: bpy.props.BoolProperty(name="NOT COVER", default=False)
    walkable_path: bpy.props.BoolProperty(name="WALKABLE PATH", default=False)
    no_cam_collision: bpy.props.BoolProperty(
        name="NO CAM COLLISION", default=False)
    shoot_through_fx: bpy.props.BoolProperty(
        name="SHOOT THROUGH FX", default=False)
    no_decal: bpy.props.BoolProperty(name="NO DECAL", default=False)
    no_navmesh: bpy.props.BoolProperty(name="NO NAVMESH", default=False)
    no_ragdoll: bpy.props.BoolProperty(name="NO RAGDOLL", default=False)
    vehicle_wheel: bpy.props.BoolProperty(name="VEHICLE WHEEL", default=False)
    no_ptfx: bpy.props.BoolProperty(name="NO PTFX", default=False)
    too_steep_for_player: bpy.props.BoolProperty(
        name="TOO STEEP FOR PLAYER", default=False)
    no_network_spawn: bpy.props.BoolProperty(
        name="NO NETWORK SPAWN", default=False)
    no_cam_collision_allow_clipping: bpy.props.BoolProperty(
        name="NO CAM COLLISION ALLOW CLIPPING", default=False)


class CollisionProperties(CollisionMatFlags, bpy.types.PropertyGroup):
    collision_index: bpy.props.IntProperty(name='Collision Index', default=0)
    procedural_id: bpy.props.IntProperty(name="Procedural ID", default=0)
    room_id: bpy.props.IntProperty(name="Room ID", default=0)
    ped_density: bpy.props.IntProperty(name="Ped Density", default=0)
    material_color_index: bpy.props.IntProperty(
        name="Material Color Index", default=0)


class BoundFlags(bpy.types.PropertyGroup):
    unknown: bpy.props.BoolProperty(name="UNKNOWN", default=False)
    map_weapon: bpy.props.BoolProperty(name="MAP WEAPON", default=False)
    map_dynamic: bpy.props.BoolProperty(name="MAP DYNAMIC", default=False)
    map_animal: bpy.props.BoolProperty(name="MAP ANIMAL", default=False)
    map_cover: bpy.props.BoolProperty(name="MAP COVER", default=False)
    map_vehicle: bpy.props.BoolProperty(name="MAP VEHICLE", default=False)
    vehicle_not_bvh: bpy.props.BoolProperty(
        name="VEHICLE NOT BVH", default=False)
    vehicle_bvh: bpy.props.BoolProperty(name="VEHICLE BVH", default=False)
    ped: bpy.props.BoolProperty(name="PED", default=False)
    ragdoll: bpy.props.BoolProperty(name="RAGDOLL", default=False)
    animal: bpy.props.BoolProperty(name="ANIMAL", default=False)
    animal_ragdoll: bpy.props.BoolProperty(
        name="ANIMAL RAGDOLL", default=False)
    object: bpy.props.BoolProperty(name="OBJECT", default=False)
    object_env_cloth: bpy.props.BoolProperty(
        name="OBJECT_ENV_CLOTH", default=False)
    plant: bpy.props.BoolProperty(name="PLANT", default=False)
    projectile: bpy.props.BoolProperty(name="PROJECTILE", default=False)
    explosion: bpy.props.BoolProperty(name="EXPLOSION", default=False)
    pickup: bpy.props.BoolProperty(name="PICKUP", default=False)
    foliage: bpy.props.BoolProperty(name="FOLIAGE", default=False)
    forklift_forks: bpy.props.BoolProperty(
        name="FORKLIFT FORKS", default=False)
    test_weapon: bpy.props.BoolProperty(name="TEST WEAPON", default=False)
    test_camera: bpy.props.BoolProperty(name="TEST CAMERA", default=False)
    test_ai: bpy.props.BoolProperty(name="TEST AI", default=False)
    test_script: bpy.props.BoolProperty(name="TEST SCRIPT", default=False)
    test_vehicle_wheel: bpy.props.BoolProperty(
        name="TEST VEHICLE WHEEL", default=False)
    glass: bpy.props.BoolProperty(name="GLASS", default=False)
    map_river: bpy.props.BoolProperty(name="MAP RIVER", default=False)
    smoke: bpy.props.BoolProperty(name="SMOKE", default=False)
    unsmashed: bpy.props.BoolProperty(name="UNSMASHED", default=False)
    map_stairs: bpy.props.BoolProperty(name="MAP STAIRS", default=False)
    map_deep_surface: bpy.props.BoolProperty(
        name="MAP DEEP SURFACE", default=False)


class BoundProperties(bpy.types.PropertyGroup):
    procedural_id: bpy.props.IntProperty(name="Procedural ID", default=0)
    room_id: bpy.props.IntProperty(name="Room ID", default=0)
    ped_density: bpy.props.IntProperty(name="Ped Density", default=0)
    poly_flags: bpy.props.IntProperty(name="Poly Flags", default=0)
    inertia: bpy.props.FloatVectorProperty(name="Inertia")
    volume: bpy.props.FloatProperty(name="Volume", precision=3)


class CollisionMaterial(bpy.types.PropertyGroup):
    index: bpy.props.IntProperty('Index')
    name: bpy.props.StringProperty('Name')


class FlagPresetProp(bpy.types.PropertyGroup):
    index: bpy.props.IntProperty('Index')
    name: bpy.props.StringProperty('Name')


def get_flag_presets_path():
    name = 'flag_presets.xml'
    dir = bpy.utils.user_resource('SCRIPTS', "addons") + '\Sollumz'
    found = False
    for root, dirs, files in os.walk(dir):
        if name in files:
            found = True
            return os.path.join(root, name)

    if not found:
        raise FileNotFoundError(
            f"flag_presets.xml file not found! Please redownload this file from the github and place it in '{dir}\ybn'")


flag_presets = FlagPresetsFile()


def load_flag_presets():
    bpy.context.scene.flag_presets.clear()
    path = get_flag_presets_path()
    if os.path.exists(path):
        file = FlagPresetsFile.from_xml_file(path)
        flag_presets.presets = file.presets
        for index, preset in enumerate(flag_presets.presets):
            item = bpy.context.scene.flag_presets.add()
            item.name = preset.name
            item.index = index


def load_collision_materials():
    bpy.context.scene.collision_materials.clear()
    for index, mat in enumerate(collisionmats):
        item = bpy.context.scene.collision_materials.add()
        item.index = index
        item.name = mat.name


# Handler sets the default value of the CollisionMaterials collection on blend file load
@persistent
def on_file_loaded(_):
    load_collision_materials()
    load_flag_presets()


def update_bounds(self, context):
    if self.sollum_type == BoundType.BOX:
        create_box(self.data, 2, Matrix.Diagonal(
            Vector(self.bound_dimensions)))
    elif self.sollum_type == BoundType.SPHERE or self.sollum_type == PolygonType.SPHERE:
        create_sphere(mesh=self.data, radius=self.bound_radius)

    elif self.sollum_type == BoundType.CYLINDER:
        create_cylinder(mesh=self.data, radius=self.bound_radius,
                        length=self.bound_length)
    elif self.sollum_type == PolygonType.CYLINDER:
        create_cylinder(mesh=self.data, radius=self.bound_radius,
                        length=self.bound_length, rot_mat=Matrix())

    elif self.sollum_type == BoundType.DISC:
        create_disc(mesh=self.data, radius=self.bound_radius,
                    length=self.margin * 2)

    elif self.sollum_type == BoundType.CAPSULE:
        create_capsule(mesh=self.data, diameter=self.margin,
                       length=self.bound_radius, use_rot=True)
    elif self.sollum_type == PolygonType.CAPSULE:
        create_capsule(mesh=self.data, diameter=self.bound_radius / 2,
                       length=self.bound_length)


def register():
    bpy.types.Scene.poly_bound_type = bpy.props.EnumProperty(
        items=items_from_enums(PolygonType),
        name="Poly Type",
        default=PolygonType.TRIANGLE.value
    )

    bpy.types.Object.bound_properties = bpy.props.PointerProperty(
        type=BoundProperties)
    bpy.types.Object.margin = bpy.props.FloatProperty(
        name="Margin", precision=3, update=update_bounds, min=0)
    bpy.types.Object.bound_radius = bpy.props.FloatProperty(
        name="Radius", precision=3, update=update_bounds, min=0)
    bpy.types.Object.bound_length = bpy.props.FloatProperty(
        name="Length", precision=3, update=update_bounds, min=0)
    bpy.types.Object.bound_dimensions = bpy.props.FloatVectorProperty(
        name="Extents", precision=3, min=0, update=update_bounds, subtype='XYZ')

    #nest these in object.bound_properties ? is it possible#
    bpy.types.Object.composite_flags1 = bpy.props.PointerProperty(
        type=BoundFlags)
    bpy.types.Object.composite_flags2 = bpy.props.PointerProperty(
        type=BoundFlags)

    bpy.types.Scene.collision_material_index = bpy.props.IntProperty(
        name="Material Index")
    bpy.types.Scene.collision_materials = bpy.props.CollectionProperty(
        type=CollisionMaterial, name='Collision Materials')
    bpy.app.handlers.load_post.append(on_file_loaded)

    bpy.types.Scene.new_flag_preset_name = bpy.props.StringProperty(
        name='Flag Preset Name')
    bpy.types.Scene.flag_preset_index = bpy.props.IntProperty(
        name="Flag Preset Index")
    bpy.types.Scene.flag_presets = bpy.props.CollectionProperty(
        type=FlagPresetProp, name='Flag Presets')

    bpy.types.Material.collision_properties = bpy.props.PointerProperty(
        type=CollisionProperties)
    bpy.types.Material.collision_flags = bpy.props.PointerProperty(
        type=CollisionMatFlags)

    # COLLISION TOOLS UI PROPERTIES
    bpy.types.Scene.poly_bound_type = bpy.props.EnumProperty(
        # maybe remove PolygonType.TRIANGLE from list?
        items=items_from_enums(PolygonType),
        name="Type",
        default=PolygonType.BOX.value
    )
    bpy.types.Scene.poly_parent = bpy.props.PointerProperty(
        type=bpy.types.Object, name='Parent', description=f"Bounds will be parented to this object. Parent must be a {SOLLUMZ_UI_NAMES[BoundType.GEOMETRYBVH]} or {SOLLUMZ_UI_NAMES[BoundType.GEOMETRY]}.")

    bpy.types.Scene.composite_create_bvh = bpy.props.BoolProperty(
        name='BVH', description='If true, the operator will create GeometryBVH objects, otherwise it will create Geometry objects.', default=True)


def unregister():
    del bpy.types.Scene.poly_bound_type
    del bpy.types.Scene.poly_parent
    del bpy.types.Object.bound_properties
    del bpy.types.Object.composite_flags1
    del bpy.types.Object.composite_flags2
    del bpy.types.Scene.collision_material_index
    del bpy.types.Scene.collision_materials
    del bpy.types.Material.collision_properties
    del bpy.types.Scene.flag_presets
    del bpy.types.Scene.flag_preset_index
    del bpy.types.Scene.new_flag_preset_name

    bpy.app.handlers.load_post.remove(on_file_loaded)
