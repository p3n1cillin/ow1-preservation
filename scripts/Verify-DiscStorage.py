"""Read-only verification using an independently built CascLib DLL (Windows x64).

No online flags, decryption overrides, extraction or service connections.
Checks original executable and two English APM manifests against ROOT metadata.
"""
import argparse
import ctypes
import hashlib
import json
from pathlib import Path


def verify(folder, dll):
    library = ctypes.WinDLL(str(Path(dll).resolve()), use_last_error=True)
    handle = ctypes.c_void_p
    library.CascOpenStorage.argtypes = [ctypes.c_char_p, ctypes.c_uint32, ctypes.POINTER(handle)]
    library.CascOpenStorage.restype = ctypes.c_bool
    library.CascOpenFile.argtypes = [handle, ctypes.c_char_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(handle)]
    library.CascOpenFile.restype = ctypes.c_bool
    library.CascGetFileSize64.argtypes = [handle, ctypes.POINTER(ctypes.c_uint64)]
    library.CascGetFileSize64.restype = ctypes.c_bool
    library.CascReadFile.argtypes = [handle, ctypes.c_void_p, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32)]
    library.CascReadFile.restype = ctypes.c_bool
    library.CascCloseFile.argtypes = [handle]
    library.CascCloseStorage.argtypes = [handle]
    def check(result):
        if not result: raise OSError(ctypes.get_last_error(), 'CascLib verification failed')
    storage = handle()
    check(library.CascOpenStorage(str(Path(folder).resolve()).encode('mbcs'), 2, ctypes.byref(storage)))
    def read(name, flags=0):
        file = handle()
        check(library.CascOpenFile(storage, name, 2, flags, ctypes.byref(file)))
        try:
            length = ctypes.c_uint64()
            check(library.CascGetFileSize64(file, ctypes.byref(length)))
            if length.value > 32 * 1024 * 1024: raise ValueError('Verification file size limit')
            buffer = ctypes.create_string_buffer(length.value)
            count = ctypes.c_uint32()
            check(library.CascReadFile(file, buffer, length.value, ctypes.byref(count)))
            if count.value != length.value: raise ValueError('Incomplete CascLib read')
            return buffer.raw
        finally:
            library.CascCloseFile(file)
    try:
        report = json.loads((Path(folder) / 'storage-report.json').read_text())
        root_key = report['metadata']['root'][0]
        root = read(bytes.fromhex(root_key), 1)
        if hashlib.md5(root).hexdigest() != root_key: raise ValueError('ROOT content hash mismatch')
        files = {line.split('|')[4]:line.split('|')[0].lower() for line in root.decode('ascii').splitlines()[1:]}
        wanted = ['PtrClient/Overwatch.exe', 'Manifest/Win_SPWin_RDEV_LenUS_EExt.apm',
                  'Manifest/Win_SPWin_speech_RDEV_LenUS_EExt.apm']
        results = []
        for name in wanted:
            blob = read(name.encode('ascii'))
            if hashlib.md5(blob).hexdigest() != files[name]: raise ValueError('ROOT hash mismatch: ' + name)
            results.append({'name':name, 'bytes':len(blob), 'md5':files[name]})
        print(json.dumps({'storage_opened':True, 'root_verified':True, 'files_verified':results,
                          'native_game_resource_loading_verified':False}, indent=2))
    finally:
        library.CascCloseStorage(storage)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder'); parser.add_argument('--casclib', required=True)
    args = parser.parse_args()
    verify(args.folder, args.casclib)
