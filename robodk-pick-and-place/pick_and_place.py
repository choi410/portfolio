from robodk import robolink, robomath
from robodk import *
from robolink import *

RDK = robolink.Robolink()

# ----------------------------------------------------
# FILE PATHS (EDIT IF NEEDED)
# ----------------------------------------------------
ROBOT_FILE  = r'C:\RoboDK\Library\Hyundai-HH4.robot'
TABLE_FILE  = r'C:\RoboDK\Library\Object Table.wrl'
JIG_FILE    = r'C:\RoboDK\Library\HH4_Jig.stl'
PALLET_FILE = r'C:\RoboDK\Library\HH4_Pallet.stl'

TUBE1_FILE  = r'C:\RoboDK\Library\TubeType1.stl'
TUBE2_FILE  = r'C:\RoboDK\Library\TubeType2.stl'

TOOL_FILE   = r'C:\RoboDK\Library\OnRobot-Gecko-SP3-Single-Pad-Gripper.tool'
TOOL_NAME   = 'OnRobot_Gecko_SP3'

ROBOT_NAME   = 'Hyundai_HH4_1'
BASE_NAME    = 'Base_HH4_1'
TABLE_NAME   = 'Table'
JIG_NAME     = 'Jig_Assembly'
PALLET1_NAME = 'Pallet_TubeType1'
PALLET2_NAME = 'Pallet_TubeType2'
PALLET3_NAME = 'Pallet_Finished'

# ----------------------------------------------------
# PALLET GRID PARAMS
# ----------------------------------------------------
# Pallet1 TubeType1 grid
P1_NX, P1_NY = 3, 4
P1_X0, P1_Y0 = -180.0, -220.0
P1_DX, P1_DY = 80.0, 65.0
P1_Z        = 10.0

# Pallet2 TubeType2 grid
P2_NX, P2_NY = 3, 4
P2_X0, P2_Y0 = -190.0, -220.0
P2_DX, P2_DY = 80.0, 65.0
P2_Z        = 10.0

# Pallet3 Finished grid
P3_NX, P3_NY = 3, 4
P3_DX, P3_DY = 80.0, -65.0
P3_X0, P3_Y0, P3_Z = 0.0, 0.0, 0.0

# ----------------------------------------------------
# POSES (사용자가 RoboDK에서 다시 찍어서 수정 가능)
# ----------------------------------------------------
home_pose       = Pose(220.000,  -0.000, 250.000,  179.695, 0.000,   90.000)

pick1_app_pose  = Pose(405, -30, 50, -180.000, 0.573,  -90.000)
pick1_grip_pose = Pose(405, -30, -50, -180.000, 0.573,  -90.000)

jig_drop1_pose  = Pose(-11, -200.000,-40, -180.000, 0.573,  -90.000)
jig_drop2_pose  = Pose(-7,  -195.000,  0, -180.000, 0.573,  -90.000)
jig_app_pose    = Pose(-11, -200.000, 90, -180.000, 0.573,  -90.000)

final_drop_pose = Pose(79,  -489.000,-15, -180.000, 0.573,  -90.000)
final_app_pose  = Pose(79,  -489.000, 40, -180.000, 0.573,  -90.000)

pick2_app_pose  = Pose(-440,-55.000, 50, -180.000, 0.573,  -90.000)
pick2_grip_pose = Pose(-440,-55.000, -80, -180.000, 0.573,  -90.000)


# ----------------------------------------------------
# RESET / BUILD ENV
# ----------------------------------------------------
def reset_station():
    """Delete all items in the active station."""
    st_active = RDK.ActiveStation()
    active_name = st_active.Name()

    for st in RDK.ItemList(ITEM_TYPE_STATION):
        if st.Name() != active_name:
            st.Delete()

    for item in RDK.ItemList():
        if item.Type() in [
            ITEM_TYPE_OBJECT,
            ITEM_TYPE_ROBOT,
            ITEM_TYPE_FRAME,
            ITEM_TYPE_TOOL,
            ITEM_TYPE_TARGET,
        ]:
            item.Delete()


def create_table_and_fixtures():
    table = RDK.AddFile(TABLE_FILE)
    if not table.Valid():
        raise Exception('Failed to load TABLE_FILE')
    table.setName(TABLE_NAME)
    table.setPose(eye(4))

    jig = RDK.AddFile(JIG_FILE)
    if not jig.Valid():
        raise Exception('Failed to load JIG_FILE')
    jig.setName(JIG_NAME)
    jig.setParent(table)
    jig.setPose(Pose(60, -100, 0, 0, 0, 0))

    pallet1 = RDK.AddFile(PALLET_FILE)
    pallet1.setName(PALLET1_NAME)
    pallet1.setParent(table)
    pallet1.setPose(Pose(-230, 0, 0, 0, 0, 0))

    pallet2 = RDK.AddFile(PALLET_FILE)
    pallet2.setName(PALLET2_NAME)
    pallet2.setParent(table)
    pallet2.setPose(Pose(220, 0, 0, 0, 0, 90))

    pallet3 = RDK.AddFile(PALLET_FILE)
    pallet3.setName(PALLET3_NAME)
    pallet3.setParent(table)
    pallet3.setPose(Pose(110, 270, 0, 0, 0, 0))

    return table, jig, pallet1, pallet2, pallet3


def load_robot(table):
    robot = RDK.AddFile(ROBOT_FILE)
    if not robot.Valid():
        raise Exception('Failed to load ROBOT_FILE')
    robot.setName(ROBOT_NAME)

    base = RDK.AddFrame(BASE_NAME, table)
    base.setPose(Pose(0, -250, 230, 0, 0, 180))

    robot.setParent(base)
    robot.setPose(eye(4))
    return robot, base


def load_tool(robot):
    tool = RDK.Item(TOOL_NAME, ITEM_TYPE_TOOL)
    if not tool.Valid():
        tool = RDK.AddFile(TOOL_FILE)
        if not tool.Valid():
            raise Exception('Failed to load TOOL_FILE')
        tool.setName(TOOL_NAME)

    tool.setParent(robot)
    robot.setTool(tool)
    robot.setPoseTool(eye(4))
    return tool


def place_tubes_on_pallet_xy(
    pallet,
    tube_file,
    name_prefix,
    nx,
    ny,
    x0,
    y0,
    dx,
    dy,
    z_offset,
):
    """Create a grid of tubes on a pallet."""
    for obj in RDK.ItemList(ITEM_TYPE_OBJECT):
        if obj.Name().startswith(name_prefix + '_'):
            obj.Delete()

    cnt = 0
    for j in range(ny):
        for i in range(nx):
            cnt += 1
            x = x0 + dx * i
            y = y0 + dy * j
            pose_rel = transl(x, y, z_offset)
            tube = RDK.AddFile(tube_file)
            if not tube.Valid():
                raise Exception('Failed to load ' + tube_file)
            tube.setName(f'{name_prefix}_{cnt}')
            tube.setParent(pallet)
            tube.setPose(pose_rel)


# ----------------------------------------------------
# RECREATE TARGETS (옵션: GUI에서 시각화용)
# ----------------------------------------------------
def recreate_targets(base_frame):
    def mk(name, pose):
        tgt = RDK.AddTarget(name, base_frame)
        tgt.setPose(pose)
        return tgt

    mk('home',       home_pose)
    mk('pick1_app',  pick1_app_pose)
    mk('pick1_grip', pick1_grip_pose)
    mk('jig_app',    jig_app_pose)
    mk('jig_drop1',  jig_drop1_pose)
    mk('jig_drop2',  jig_drop2_pose)
    mk('final_app',  final_app_pose)
    mk('final_drop', final_drop_pose)
    mk('pick2_app',  pick2_app_pose)
    mk('pick2_grip', pick2_grip_pose)


# ----------------------------------------------------
# PALLET GRID POSE HELPER
# ----------------------------------------------------
def pallet_grid_pose_from_reference(base, pallet, ref_pose, nx, dx, dy, index):
    """
    base    : Base_HH4_1 프레임
    pallet  : 해당 팔레트 Item
    ref_pose: 기준 포즈(Mat, pick1_app 등)
    nx,dx,dy: 그리드 설정
    index   : 0,1,2,...
    return  : base 프레임 기준 Mat
    """
    T_table_base   = base.Pose()
    T_table_pallet = pallet.Pose()

    # 팔레트 좌표계에서 ref_pose
    T_pallet_ref = invH(T_table_pallet) * T_table_base * ref_pose

    col = index % nx
    row = index // nx

    T_offset     = transl(col * dx, row * dy, 0)
    T_pallet_tgt = T_offset * T_pallet_ref

    T_table_tgt = T_table_pallet * T_pallet_tgt
    T_base_tgt  = invH(T_table_base) * T_table_tgt
    return T_base_tgt


# ----------------------------------------------------
# ONE ASSEMBLY CYCLE (NO AttachClosest)
# ----------------------------------------------------
def one_cycle_attachclosest(
    robot,
    tool,
    jig,
    pallet1,
    pallet2,
    pallet3,
    base,
    index,
):
    """
    index 번째 칸을 사용해서:
      - Pallet1 에서 TubeType1_index pick
      - Pallet2 에서 TubeType2_index pick
      - Pallet3 의 index 칸에 완제품 drop
    """
    RDK.setRunMode(RUNMODE_SIMULATE)

    # 이 사이클에서 사용할 튜브 이름 (1부터 시작)
    idx1 = index + 1
    tube1_name = f'TubeType1_{idx1}'
    tube2_name = f'TubeType2_{idx1}'

    tube1 = RDK.Item(tube1_name, ITEM_TYPE_OBJECT)
    tube2 = RDK.Item(tube2_name, ITEM_TYPE_OBJECT)

    if not tube1.Valid():
        raise Exception(f'Cannot find object: {tube1_name}')
    if not tube2.Valid():
        raise Exception(f'Cannot find object: {tube2_name}')

    # ----- 동적 포즈 계산 -----
    # Pallet1 (TubeType1) pick 포즈
    p1_app  = pallet_grid_pose_from_reference(
        base, pallet1, pick1_app_pose,  P1_NX, P1_DX, P1_DY, index
    )
    p1_grip = pallet_grid_pose_from_reference(
        base, pallet1, pick1_grip_pose, P1_NX, P1_DX, P1_DY, index
    )

    # Pallet2 (TubeType2) pick 포즈
    p2_app  = pallet_grid_pose_from_reference(
        base, pallet2, pick2_app_pose,  P2_NX, P2_DX, P2_DY, index
    )
    p2_grip = pallet_grid_pose_from_reference(
        base, pallet2, pick2_grip_pose, P2_NX, P2_DX, P2_DY, index
    )

    # Pallet3 (Finished) drop 포즈
    f_app  = pallet_grid_pose_from_reference(
        base, pallet3, final_app_pose,  P3_NX, P3_DX, P3_DY, index
    )
    f_drop = pallet_grid_pose_from_reference(
        base, pallet3, final_drop_pose, P3_NX, P3_DX, P3_DY, index
    )

    # 0) home
    robot.MoveJ(home_pose)

    # 1) Pallet1: Tube1 pick (지정 튜브를 직접 붙임)
    robot.MoveJ(p1_app)
    robot.MoveJ(p1_grip)
    tube1.setParentStatic(tool)
    print('Picked from pallet1:', tube1.Name())
    robot.MoveJ(p1_app)

    # 2) Tube1 -> Jig
    robot.MoveJ(jig_app_pose)
    robot.MoveJ(jig_drop1_pose)
    tube1.setParentStatic(jig)
    robot.MoveJ(jig_app_pose)

    # 3) Pallet2: Tube2 pick
    robot.MoveJ(p2_app)
    robot.MoveJ(p2_grip)
    tube2.setParentStatic(tool)
    print('Picked from pallet2:', tube2.Name())
    robot.MoveJ(p2_app)

    # 4) Tube2 -> Jig, Tube1을 Tube2에 붙여서 조립
    robot.MoveJ(jig_app_pose)
    pause(0.3)
    robot.MoveL(jig_drop2_pose)
    tube2.setParentStatic(jig)
    tube1.setParentStatic(tube2)
    robot.MoveL(jig_app_pose)

    # 5) 조립품 pick (Tube2가 root)
    robot.MoveL(jig_app_pose)
    robot.MoveL(jig_drop2_pose)
    asm = tube2
    asm.setParentStatic(tool)
    robot.MoveL(jig_app_pose)

    # 6) Pallet3 의 index 칸에 drop
    robot.MoveJ(f_app)
    robot.MoveL(f_drop)
    asm.setParentStatic(pallet3)
    robot.MoveJ(f_app)

    # 7) home
    robot.MoveJ(home_pose)
    print(f'One cycle finished (index={index}).')


# ----------------------------------------------------
# MAIN
# ----------------------------------------------------
def main():
    reset_station()
    table, jig, pallet1, pallet2, pallet3 = create_table_and_fixtures()
    robot, base = load_robot(table)
    tool = load_tool(robot)

    place_tubes_on_pallet_xy(
        pallet=pallet1,
        tube_file=TUBE1_FILE,
        name_prefix='TubeType1',
        nx=P1_NX,
        ny=P1_NY,
        x0=P1_X0,
        y0=P1_Y0,
        dx=P1_DX,
        dy=P1_DY,
        z_offset=P1_Z,
    )
    place_tubes_on_pallet_xy(
        pallet=pallet2,
        tube_file=TUBE2_FILE,
        name_prefix='TubeType2',
        nx=P2_NX,
        ny=P2_NY,
        x0=P2_X0,
        y0=P2_Y0,
        dx=P2_DX,
        dy=P2_DY,
        z_offset=P2_Z,
    )

    recreate_targets(base)

    num_cycles = min(P1_NX * P1_NY, P2_NX * P2_NY, P3_NX * P3_NY)

    for idx in range(num_cycles):
        print(f'===== CYCLE {idx+1} / {num_cycles} =====')
        one_cycle_attachclosest(
            robot, tool, jig,
            pallet1, pallet2, pallet3,
            base, idx
        )


if __name__ == '__main__':
    main()

