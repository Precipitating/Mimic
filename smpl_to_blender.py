import bpy
import numpy as np
from mathutils import Matrix, Vector
import pickle
import json
import sys

#### Change the variables here
###############################
smpl_model = r'C:\Users\duder\Desktop\Mimic\GVHMR\basicModel_m_lbs_10_207_0_v1.0.2.fbx'
target_model = r'C:\Users\duder\Desktop\someguy.fbx'
file = r'C:\Users\duder\Desktop\Mimic\GVHMR\outputs\demo\kick\hmr4d_results.pt_person-0.pkl'
high_from_floor = 1.5
##############################


with open(file, 'rb') as handle:
    results = pickle.load(handle)

part_match_custom_less2 = {'root': 'root', 'bone_00': 'Pelvis', 'bone_01': 'L_Hip', 'bone_02': 'R_Hip',
                           'bone_03': 'Spine1', 'bone_04': 'L_Knee', 'bone_05': 'R_Knee', 'bone_06': 'Spine2',
                           'bone_07': 'L_Ankle', 'bone_08': 'R_Ankle', 'bone_09': 'Spine3', 'bone_10': 'L_Foot',
                           'bone_11': 'R_Foot', 'bone_12': 'Neck', 'bone_13': 'L_Collar', 'bone_14': 'R_Collar',
                           'bone_15': 'Head', 'bone_16': 'L_Shoulder', 'bone_17': 'R_Shoulder', 'bone_18': 'L_Elbow',
                           'bone_19': 'R_Elbow', 'bone_20': 'L_Wrist', 'bone_21': 'R_Wrist',
                           'bone_22': 'L_Hand', 'bone_23': 'R_Hand',
                           }


### INICIO --- Inseri para utilizar no WHAM
def Rodrigues(rotvec):
    theta = np.linalg.norm(rotvec)
    r = (rotvec / theta).reshape(3, 1) if theta > 0. else rotvec
    cost = np.cos(theta)
    mat = np.asarray([[0, -r[2], r[1]],
                      [r[2], 0, -r[0]],
                      [-r[1], r[0], 0]], dtype=object)  # adicionei "",dtype=object" por que estava dando erro
    return (cost * np.eye(3) + (1 - cost) * r.dot(r.T) + np.sin(theta) * mat)


def rodrigues2bshapes(pose):
    rod_rots = np.asarray(pose).reshape(22, 3)
    mat_rots = [Rodrigues(rod_rot) for rod_rot in rod_rots]
    bshapes = np.concatenate([(mat_rot - np.eye(3)).ravel()
                              for mat_rot in mat_rots[1:]])
    return (mat_rots, bshapes)


############
def get_global_pose(global_pose, arm_ob, frame=None):
    arm_ob.pose.bones['m_avg_root'].rotation_quaternion.w = 0.0
    arm_ob.pose.bones['m_avg_root'].rotation_quaternion.x = -1.0

    bone = arm_ob.pose.bones['m_avg_Pelvis']

    root_orig = arm_ob.pose.bones['m_avg_root'].rotation_quaternion
    mw_orig = arm_ob.matrix_world.to_quaternion()
    pelvis_quat = Matrix(global_pose[0]).to_quaternion()

    bone.rotation_quaternion = pelvis_quat
    bone.keyframe_insert('rotation_quaternion', frame=frame)

    pelvis_applyied = arm_ob.pose.bones['m_avg_Pelvis'].rotation_quaternion
    bpy.context.view_layer.update()

    rot_world_orig = root_orig @ pelvis_applyied @ mw_orig  # pegar a rotacao em relacao ao mundo

    return rot_world_orig


def export_fbx():
    if "Cube" in bpy.data.objects:
        cube = bpy.data.objects["Cube"]
        bpy.data.objects.remove(cube, do_unlink=True)

    if "Armature" in bpy.data.objects:
        cube = bpy.data.objects["Armature"]
        mesh = bpy.data.objects["m_avg"]
        bpy.data.objects.remove(cube, do_unlink=True)
        bpy.data.objects.remove(mesh, do_unlink=True)


    fbx_export_path = r"C:\Users\duder\Desktop\Mimic\exported_animation.fbx"

    # export the whole scene
    bpy.ops.export_scene.fbx(
        filepath=fbx_export_path,
        use_selection=False,
        apply_scale_options='FBX_SCALE_ALL',
        bake_space_transform=True,
        object_types={'ARMATURE', 'MESH'},
        add_leaf_bones=False,
        bake_anim=True,
        bake_anim_use_all_bones=True,
        bake_anim_use_nla_strips=False,
        bake_anim_use_all_actions=False,
        bake_anim_force_startend_keying=True,
    )


###############

# apply trans pose and shape to character
# def apply_trans_pose_shape(trans, body_pose, shape, ob, arm_ob, obname, scene, cam_ob, frame=None):
def apply_trans_pose_shape(trans, body_pose, arm_ob, obname, frame=None):
    mrots, bsh = rodrigues2bshapes(body_pose)
    part_bones = part_match_custom_less2
    trans = Vector((trans[0], trans[1] - high_from_floor, trans[2]))

    arm_ob.pose.bones['m_avg_Pelvis'].location = trans
    arm_ob.pose.bones['m_avg_Pelvis'].keyframe_insert('location', frame=frame)

    arm_ob.pose.bones['m_avg_root'].rotation_quaternion.w = 0.0
    arm_ob.pose.bones['m_avg_root'].rotation_quaternion.x = -1.0

    for ibone, mrot in enumerate(mrots):
        if ibone < 22:  # incui essa parte por que no modelo que eu to usando nao tem bone para a mao
            bone = arm_ob.pose.bones['m_avg_' + part_bones['bone_%02d' % ibone]]
            bone.rotation_quaternion = Matrix(mrot).to_quaternion()

            if frame is not None:
                bone.keyframe_insert('rotation_quaternion', frame=frame)


import os


def init_scene(scene, params, gender='male', angle=0):
    path_fbx = smpl_model
    bpy.ops.import_scene.fbx(filepath=path_fbx, axis_forward='-Y', axis_up='-Z', global_scale=100)
    arm_ob = bpy.context.selected_objects[0]

    obj_gender = 'm'
    obname = '%s_avg' % obj_gender
    ob = bpy.data.objects[obname]

    print('success load')
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_all(action='DESELECT')
    cam_ob = ''
    arm_ob.animation_data_clear()

    return (ob, obname, arm_ob, cam_ob)


params = []
object_name = 'm_avg'
obj_gender = 'm'
scene = bpy.data.scenes['Scene']
ob, obname, arm_ob, cam_ob = init_scene(scene, params, obj_gender)

qtd_frames = len(results['smpl_params_global']['transl'])

print('qtd frames: ', qtd_frames)
for fframe in range(0, qtd_frames):
    bpy.context.scene.frame_set(fframe)
    #trans = results['smpl_params_global']['transl'][fframe]

    # animate in place, no translation
    trans = results['smpl_params_global']['transl'][0]
    global_orient = results['smpl_params_global']['global_orient'][fframe]
    body_pose = results['smpl_params_global']['body_pose'][fframe]
    body_pose_fim = body_pose.reshape(int(len(body_pose) / 3), 3)
    final_body_pose = np.vstack([global_orient, body_pose_fim])
    apply_trans_pose_shape(Vector(trans), final_body_pose, arm_ob, obname, fframe)
    bpy.context.view_layer.update()

arm_ob.pose.bones['m_avg_root'].rotation_quaternion.w = 1.0
arm_ob.pose.bones['m_avg_root'].rotation_quaternion.x = 0.0
arm_ob.pose.bones['m_avg_root'].rotation_quaternion.y = 0.0
arm_ob.pose.bones['m_avg_root'].rotation_quaternion.z = 0.0

arm_ob.pose.bones['m_avg_Pelvis'].constraints.new('COPY_LOCATION')
arm_ob.pose.bones["m_avg_Pelvis"].constraints[0].target = arm_ob
arm_ob.pose.bones["m_avg_Pelvis"].constraints[0].subtarget = "m_avg_Pelvis"

arm_ob.pose.bones['m_avg_Pelvis'].constraints.new('COPY_ROTATION')
arm_ob.pose.bones["m_avg_Pelvis"].constraints[1].target = arm_ob
arm_ob.pose.bones["m_avg_Pelvis"].constraints[1].subtarget = "m_avg_Pelvis"

# load target
target_fbx = target_model
bpy.ops.import_scene.fbx(
    filepath=target_fbx,
    axis_forward='-Z',
    axis_up='Y',  # Blender's default
    automatic_bone_orientation=True,
    global_scale=1.0,
)

print("Target armature loaded")

# set to same pose
for obj in bpy.data.objects:
    if obj.type == 'ARMATURE':
        obj.data.pose_position = 'REST'

# use rokkoko retargeter
bpy.context.scene.rsl_retargeting_armature_source = bpy.data.objects.get("Armature")
bpy.context.scene.rsl_retargeting_armature_target = bpy.data.objects.get("Armature.001")

argv = sys.argv
argv = argv[argv.index("--") + 1:]
bpy.context.scene.frame_end = int(float(argv[0]))
print(bpy.context.scene.frame_end)

selected_rig = "miaxmo.json"
json_path = f'mappings/{selected_rig}'

with open(json_path, 'r') as f:
    bone_mappings = json.load(f)


for source_bone, target_bone in bone_mappings:
    item = bpy.context.scene.rsl_retargeting_bone_list.add()
    item.bone_name_source = source_bone
    item.bone_name_target = target_bone

result = bpy.ops.rsl.retarget_animation()

export_fbx()