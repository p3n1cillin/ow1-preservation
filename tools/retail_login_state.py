"""Read-only 104319 dump checks for initial lobby notifications.

Reports booleans only: no native bytes, account identifiers, keys or strings.
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


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dump',required=True)
    parser.add_argument('--out',help='optional exclusive-created JSON report')
    args=parser.parse_args()
    spec=importlib.util.spec_from_file_location('owned_dump',Path(__file__).parent/'offline-launch/re/mdump.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    dump=module.Dump(args.dump)
    try:result=inspect(dump)
    finally:dump.f.close()
    text=json.dumps(result,indent=2)+'\n'
    if args.out:
        with open(args.out,'x',encoding='utf-8') as output:output.write(text)
    print(text,end='')


if __name__=='__main__':main()
