"""Author-written loopback packets only; no native packet payload fixtures."""
import importlib.util
import json
from pathlib import Path
import socket
import threading
import unittest

spec=importlib.util.spec_from_file_location('instance_observer',Path(__file__).resolve().parents[1]/'tools/instance_probe.py')
probe=importlib.util.module_from_spec(spec);spec.loader.exec_module(probe)


class InstanceObserverTests(unittest.TestCase):
    def test_duration_guards(self):
        for value in (0,181,-1,True,1.0):
            with self.assertRaises(ValueError):probe.observe(value,lambda row:None)

    def test_real_loopback_sizes_and_no_payload_output(self):
        rows=[]; errors=[]; ready=threading.Event()
        def emit(row):
            rows.append(row)
            if row['event']=='listening':ready.set()
        def worker():
            try:probe.observe(1,emit)
            except Exception as error:errors.append(error);ready.set()
        thread=threading.Thread(target=worker);thread.start()
        try:
            self.assertTrue(ready.wait(2))
            self.assertEqual(errors,[])
            with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sender:
                for payload in (b'',b'author-private-fixture\x00',bytes(4096)):
                    sender.sendto(payload,('127.0.0.1',21120))
        finally:thread.join(3)
        self.assertFalse(thread.is_alive())
        self.assertEqual(errors,[])
        self.assertEqual([row['bytes'] for row in rows if row['event']=='datagram'],[0,23,4096])
        self.assertEqual(rows[-1],dict(event='ended',datagrams=3))
        output=json.dumps(rows)
        self.assertNotIn('author-private-fixture',output)
        self.assertNotIn('127.0.0.1',output)


if __name__=='__main__':unittest.main()
