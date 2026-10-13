"""Bounded receive-only UDP observer for the owned instance experiment.

Listens exclusively on host loopback 21120. Use the launcher's opt-in
1119:21120 UDP bridge. Reports sizes/counts only and sends no protocol replies.
Receiving a datagram does not establish an authenticated game connection.
"""
import argparse
import json
import socket
import time


def observe(seconds, emit):
    if type(seconds) is not int or not 1 <= seconds <= 180:
        raise ValueError('instance observation must be bounded to 1..180 seconds')
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as listener:
        if hasattr(socket, 'SO_EXCLUSIVEADDRUSE'):
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        listener.bind(('127.0.0.1', 21120))
        listener.settimeout(0.25)
        emit(dict(event='listening',transport='UDP',port=21120))
        end=time.monotonic()+seconds
        count=0
        while time.monotonic()<end:
            try:data,peer=listener.recvfrom(4096)
            except socket.timeout:continue
            if peer[0]!='127.0.0.1':continue
            count+=1
            emit(dict(event='datagram',number=count,bytes=len(data)))
        emit(dict(event='ended',datagrams=count))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-for',type=int,default=180)
    parser.add_argument('--log',help='exclusive-created private JSON-lines report')
    args=parser.parse_args()
    output=open(args.log,'x',encoding='utf-8') if args.log else None
    try:
        def emit(value):
            line=json.dumps(value)
            print(line,flush=True)
            if output:output.write(line+'\n');output.flush()
        observe(args.run_for,emit)
    finally:
        if output:output.close()


if __name__=='__main__':main()
