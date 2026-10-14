"""Read-only 104319 dump checks for initial lobby notifications.

Reports flags/counts/statuses only: no native bytes, identifiers, keys or strings.
These snapshots describe initial-data state, not menu/gameplay completion.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import struct

TIMESTAMP = 1661534873
IMAGE_SIZE = 58298368
ROOT_RVA = 0x2f586e0
COOKIE_RVA = 0x2ee4bd0
TABLE_MASK = 0x4e3494c633194824
ROOT_VFT = 0x2612358
LOGIN_VFT = 0x26113c8
KEYS_VFT = 0x2611510
PLAYER_VFT = 0x2610ea0
QUEUE_VFT = 0x2610c68
QUEUE_SERVICE_VFT = 0x260cd68
INSTANCE_VFT = 0x26775f0
# World-state manager (ctor 0x00b4a5b0): state byte +0x18, pending request +0x20.
WORLD_VFT = 0x2655d88
WORLD_STATES = ('SHUTDOWN', 'SHUTTING DOWN', 'WAITING', 'ABANDONING SCENES', 'HOTFIXING',
                'GLOBAL LOADING', 'WORLD LOADING', 'WORLD LOADED', 'WORLD REPLICATING',
                'GAME MODE LOADING', 'WORLD_RUNNING')


def inspect(dump):
    image = dump.image_base
    def read(address, size):
        data = dump.read(address,size)
        if len(data)!=size:raise ValueError('incomplete login diagnostic memory')
        return data
    def u(address):return struct.unpack('<Q',read(address,8))[0]
    if read(image,2)!=b'MZ':raise ValueError('missing client image header')
    pe=struct.unpack('<I',read(image+0x3c,4))[0]
    if not 0x40<=pe<=4096:raise ValueError('client PE header offset')
    header=read(image+pe,84)
    # The demonstrated unpacked runtime header reports Machine=0x0200;
    # the untouched file is 0x8664. Keep the observed in-memory profile exact.
    if (header[:4]!=b'PE\0\0' or struct.unpack_from('<H',header,4)[0]!=0x0200
        or struct.unpack_from('<H',header,24)[0]!=0x20b
        or struct.unpack_from('<I',header,8)[0]!=TIMESTAMP
        or struct.unpack_from('<I',header,80)[0]!=IMAGE_SIZE):
        raise ValueError('final-client image profile differs')
    root=u(image+ROOT_RVA)
    if not root or root%8 or u(root)!=image+ROOT_VFT:
        raise ValueError('original root identity differs')
    table=((TABLE_MASK-u(image+COOKIE_RVA))&0xffffffffffffffff)^u(root+0x140)
    if not table or table%8:raise ValueError('invalid native context table')
    login,keys,player=u(table+9*8),u(table+10*8),u(table+22*8)
    for pointer,vft in ((login,LOGIN_VFT),(keys,KEYS_VFT),(player,PLAYER_VFT)):
        if not pointer or pointer%8 or u(pointer)!=image+vft:
            raise ValueError('original login/key/player context identity differs')
    notification=read(keys+0x40,1)[0]
    player_marker=read(player+0x88,1)[0]
    if notification not in (0,1) or player_marker not in (0,1):raise ValueError('invalid notification flag')
    return dict(build=104319,identity_installed=any(read(login+0xe0,16)),
                key_notification_received=bool(notification),player_update_marker=bool(player_marker))


def world_states(dump, limit=8):
    """State name and request presence for each world-state manager instance.

    The client's own state-name table (0x00b4f760) supplies the names. Only the
    enum value and a pending-request boolean are reported.
    """
    needle=struct.pack('<Q',dump.image_base+WORLD_VFT)
    out=[]
    for address in dump.find_all(needle):
        if address%8 or dump.image_base<=address<dump.image_base+IMAGE_SIZE:continue
        data=dump.read(address,0x28)
        if len(data)!=0x28:continue
        state=data[0x18]
        if state>=len(WORLD_STATES):raise ValueError('unknown world state value')
        out.append(dict(state=WORLD_STATES[state],world_request_pending=any(data[0x20:0x28])))
        if len(out)>=limit:break
    return out


def queue_states(dump):
    """Read queue-record counts and the native instance-referral job presence.

    A job being present does not prove connection, authentication or map load.
    The 23332 marker's lifetime/meaning beyond its traced setter is unverified.
    No identifiers, endpoints, session inputs or native bytes are returned.
    """
    inspect(dump)  # exact image/root/initial-data identities must match first
    image = dump.image_base
    def read(address, size):
        data = dump.read(address,size)
        if len(data)!=size:raise ValueError('incomplete queue diagnostic memory')
        return data
    def u(address):return struct.unpack('<Q',read(address,8))[0]
    root=u(image+ROOT_RVA)
    table=((TABLE_MASK-u(image+COOKIE_RVA))&0xffffffffffffffff)^u(root+0x140)
    queue,instance,service=u(table+38*8),u(table+120*8),u(root+0x220)
    for pointer,vft in ((queue,QUEUE_VFT),(instance,INSTANCE_VFT),(service,QUEUE_SERVICE_VFT)):
        if not pointer or pointer%8 or u(pointer)!=image+vft:
            raise ValueError('original queue/instance service identity differs')
    counts=[]
    for offset in (0x10,0x38,0x60,0x88):
        count=struct.unpack('<i',read(service+offset+0x10,4))[0]
        if not 0<=count<=1024:raise ValueError('queue record count bound')
        counts.append(count)
    marker=read(queue+0x10f9,1)[0]
    if marker not in (0,1):raise ValueError('invalid 23332 marker')
    return dict(record_counts=counts,reply_23332_marker=bool(marker),
                instance_referral_job_present=bool(u(instance+0x20)))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dump',required=True)
    parser.add_argument('--out',help='optional exclusive-created JSON report')
    parser.add_argument('--world-state',action='store_true',
                        help='also scan for world-state manager state (slow on full dumps)')
    parser.add_argument('--queue-state',action='store_true',
                        help='also inspect bounded native queue and instance-referral state')
    parser.add_argument('--world-resource-state',action='store_true',
                        help='inspect catalogue/load-cache gates of WAITING world requests (slow)')
    parser.add_argument('--metadata-state',action='store_true',
                        help='inspect metadata entries, active/staged contexts and initialization completion')
    parser.add_argument('--preload-state',action='store_true',
                        help='inspect bounded engine preloader queue and submission counts')
    parser.add_argument('--resource-cache-state',action='store_true',
                        help='aggregate raw load states of existing resource-cache objects')
    parser.add_argument('--scene-state',action='store_true',
                        help='inspect loading through running resource completion and scene readiness')
    parser.add_argument('--client-pid',type=int,
                        help='original client PID associated with this dump (required for scene state)')
    parser.add_argument('--replication-state',action='store_true',
                        help='inspect selected-entity validity, resolution and first-person component prerequisite')
    args=parser.parse_args()
    if args.scene_state and args.client_pid is None:parser.error('--scene-state requires --client-pid')
    spec=importlib.util.spec_from_file_location('owned_dump',Path(__file__).parent/'offline-launch/re/mdump.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    dump=module.Dump(args.dump)
    try:
        result=inspect(dump)
        if args.queue_state:result['queue_state']=queue_states(dump)
        if args.world_state:result['world_state']=world_states(dump)
        if args.world_resource_state:
            from retail_resource_state import world_resource_states
            result['world_resource_state']=world_resource_states(dump)
        if args.metadata_state:
            from retail_metadata_state import metadata_state
            result['metadata_state']=metadata_state(dump)
        if args.preload_state:
            from retail_preload_state import preload_state
            result['preload_state']=preload_state(dump)
        if args.resource_cache_state:
            from retail_resource_state import resource_cache_state
            result['resource_cache_state']=resource_cache_state(dump)
        if args.scene_state:
            from retail_scene_state import loading_gates
            result['scene_state']=loading_gates(dump,args.client_pid)
        if args.replication_state:
            from retail_replication_state import replication_gates
            result['replication_state']=replication_gates(dump)
    finally:dump.f.close()
    text=json.dumps(result,indent=2)+'\n'
    if args.out:
        with open(args.out,'x',encoding='utf-8') as output:output.write(text)
    print(text,end='')


if __name__=='__main__':main()
