"""Read-only 104319 loading through running scene readiness snapshots.

Reports aggregate statuses and readiness only. No pointers or asset identifiers.
The caller supplies the client PID associated with the dump: it is an operand
of the original owner getter, not a request to open or modify that process.
"""
import struct
from retail_login_state import inspect, WORLD_VFT, IMAGE_SIZE, WORLD_STATES

SCENE_VFT = 0x2655fc8
SCENE_READY = 0xb59220
OWNER_VFT = 0x260be40
SECONDARY_VFT = 0x2618220
SCENE_OBJECT_VFT = 0x27abc08
MASK = (1 << 64) - 1


def loading_gates(dump, client_pid, limit=8):
    if not isinstance(client_pid, int) or isinstance(client_pid, bool) or not 0 < client_pid < 1 << 32:
        raise ValueError('saved client PID bound')
    if type(limit) is not int or not 1 <= limit <= 8:raise ValueError('world manager limit')
    inspect(dump)
    image = dump.image_base
    def read(address, size):
        data = dump.read(address, size)
        if len(data) != size:raise ValueError('incomplete scene diagnostic memory')
        return data
    def u(address, size=8):return int.from_bytes(read(address, size), 'little')
    dispatch = struct.unpack('<8I', read(image + 0xb4d8e4, 32))
    if dispatch != (0xb4ccca, 0xb4ccd4, 0xb4cce7, 0xb4ccf1, 0xb4ccfb, 0xb4cd05, 0xb4cd20, 0xb4cd0f):
        raise ValueError('world dispatch profile differs')
    # Exact original resource completion and scene boolean getters.
    for rva, expected in ((0xb4d910, bytes.fromhex('4863420885c07e20')),
                          (SCENE_READY, bytes.fromhex('0fb681a0000000c3'))):
        if read(image + rva, len(expected)) != expected:raise ValueError('loading getter profile differs')
    seed = 0x0a75eb31b884f74c ^ client_pid ^ 0xb668aee222e8c2a6
    key = (~0xeef881967912c76c ^ ((client_pid * 0x4997511ddd173d59) & MASK)) & MASK
    table = image + 0x2ee46d0
    def scene_progress(handle):
        # Original state/data getters 0x1b53d80/0x1b53d30 share this decode.
        expected = bytes.fromhex('488b815804000048ba2b2c1efcd260d5e4')
        for rva in (0x1b53d80, 0x1b53d30):
            if read(image+rva,len(expected))!=expected:raise ValueError('scene object getter profile differs')
        obj = u(handle)
        if not obj or obj % 8 or u(obj)!=image+SCENE_OBJECT_VFT:raise ValueError('scene object identity')
        controller = u(obj+0x458)^0xe4d560d2fc1e2c2b
        report = dict(controller_present=bool(controller),update_count=u(obj+0x478,4))
        if not controller:return report
        if controller % 8 or controller >= 0x800000000000:raise ValueError('scene controller alignment')
        state = u(controller+0x1a8,4)
        if state>32:raise ValueError('raw scene state bound')
        data = u(controller+0x1b0)
        report.update(raw_state=state,completion_data_present=bool(data))
        resources = []
        if data:
            if data % 8 or data >= 0x800000000000:raise ValueError('scene completion data alignment')
            report['load_progress']=u(data+0x3c,4)
            reference=u(data+0x18);control=reference&~63
            valid=reference!=MASK and bool(control)
            if valid:
                if control>=0x800000000000:raise ValueError('typed asset control alignment')
                flags=u(control+8,4)
                valid=((flags^reference)&63)==0
            asset=dict(reference_valid=valid,object_present=False,native_status=0)
            if valid:
                asset['object_present']=bool(u(control))
                # 0x173b910: unfinished ->2; finished+failed ->3; finished ->4.
                finished=bool(flags&0x10000);failed=bool(flags&0x8000)
                asset['native_status']=(3 if failed else 4) if finished else 2
            report['typed_asset']=asset
            for offset in (8,0x10):
                resource = u(data+offset)
                if resource and (resource % 8 or resource >= 0x800000000000):raise ValueError('scene completion resource alignment')
                item = dict(present=bool(resource))
                if resource:item['raw_state']=struct.unpack('<b',read(resource+0xac,1))[0]
                resources.append(item)
        report['completion_resources']=resources
        report['native_ready_condition']=state==5 and len(resources)==2 and all(
            item['present'] and item['raw_state']>=2 for item in resources)
        if u(controller+0x1a8,4)!=state or u(controller+0x1b0)!=data:
            raise ValueError('scene controller changed')
        return report
    managers = []
    for world in dump.find_all(struct.pack('<Q', image + WORLD_VFT)):
        if world % 8 or image <= world < image + IMAGE_SIZE:continue
        if u(world + 0x10) != image + SECONDARY_VFT:continue
        state = u(world + 0x18, 1)
        if state >= len(WORLD_STATES):raise ValueError('unknown world state')
        if state not in (6,7,8,9,10):continue
        owner = u(world + 8) ^ u(image + 0x2ee48a1) ^ 0x4dfd564467c27b96
        if not owner or owner % 8 or u(owner) != image + OWNER_VFT:raise ValueError('world owner identity')
        # Original 0x5855f0 getter, with the stack-only seed transform 0xb7c60.
        value = u(owner + 0x1d0)
        low, high = value & 0xffffffff, value >> 32
        high ^= (low - u(table + (key >> 52), 4)) & 0xffffffff
        value = ((high << 32) | low) & MASK
        high = (value >> 32) ^ (((u(table + (key & 0xfff)) >> 32) - low) & 0xffffffff)
        value = (((high << 32) | low) ^ seed) & MASK
        low = value & 0xffffffff
        high = (value >> 32) ^ ((0x2e213dd2 - low) & 0xffffffff)
        term = u(table + (key >> 52)) >> 32
        term = ((term << 9) | (term >> 23)) & 0xffffffff
        high ^= (low * 2 - term) & 0xffffffff
        scene = ((high << 32) | low) & MASK
        if not scene or scene % 8 or u(scene) != image + SCENE_VFT:
            raise ValueError('scene service identity or saved PID differs')
        if u(image + SCENE_VFT + 0x140) != image + SCENE_READY:raise ValueError('scene readiness method differs')
        ready = u(scene + 0xa0, 1)
        if ready not in (0, 1):raise ValueError('scene readiness boolean')
        active, pending = u(scene - 0x70), u(scene + 0x38)
        if any(pointer and (pointer % 8 or pointer >= 0x800000000000) for pointer in (active,pending)):
            raise ValueError('scene handle alignment')
        groups = []
        for offset in (0x50, 0x60, 0x88):
            count = struct.unpack('<i', read(world + offset + 8, 4))[0]
            if not 0 <= count <= 4096:raise ValueError('loading resource count bound')
            pointer = u(world + offset)
            if count and (not pointer or pointer % 8):raise ValueError('loading resource array alignment')
            statuses = {}
            for index in range(count):
                obj = u(pointer + index * 8)
                if not obj or obj % 8:raise ValueError('loading resource object alignment')
                status = struct.unpack('<b', read(obj + 0xac, 1))[0]
                statuses[str(status)] = statuses.get(str(status), 0) + 1
            groups.append(dict(count=count, raw_state_counts=statuses,
                               native_complete=all(int(status) >= 2 for status in statuses)))
            if u(world+offset)!=pointer or struct.unpack('<i',read(world+offset+8,4))[0]!=count:
                raise ValueError('loading resource array changed')
        if u(world+0x18,1)!=state or u(scene+0xa0,1)!=ready:
            raise ValueError('loading state changed')
        row=dict(state=WORLD_STATES[state], resource_groups=groups,
                             scene_ready=bool(ready),
                             active_scene_present=bool(active), pending_scene_present=bool(pending),
                             loading_complete=bool(ready) and all(g['native_complete'] for g in groups))
        if active:row['active_scene']=scene_progress(active)
        if pending:row['pending_scene']=scene_progress(pending)
        if u(scene-0x70)!=active or u(scene+0x38)!=pending:raise ValueError('scene handles changed')
        managers.append(row)
        if len(managers) > limit:raise ValueError('world manager count bound')
    return dict(managers=managers)
