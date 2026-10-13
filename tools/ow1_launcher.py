"""OW1 preservation launcher: local accounts + private server + original client.

    python tools/ow1_launcher.py configure --cert ... --key ... --ca ... \
        --lobby-private-key ... --lobby-integrity-key ... --lobby-modulus ...
    python tools/ow1_launcher.py create Tracer
    python tools/ow1_launcher.py list
    python tools/ow1_launcher.py play Tracer

`play` starts tools/bnet-probe.py as the local server for the chosen account
(battle tag and account id), then the bounded private client via
scripts/Start-PrivateClient.ps1, and stops the server when the client run ends.
Accounts are ours, not Battle.net accounts. Configuration, accounts and run
logs live under the ignored `.local/` directory.
"""
import argparse
import datetime
import getpass
import json
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from accounts import AccountStore  # noqa: E402

CONFIG = ROOT / '.local' / 'launcher.json'
RUNS = ROOT / '.local' / 'runs'
PORT = 21119
MAX_SECONDS = 180  # the launcher's CA diagnostics accept 1..180-second runs
FILES = ('cert', 'key', 'ca', 'lobby_private_key', 'lobby_integrity_key', 'lobby_modulus')


def load_config():
    if not CONFIG.exists():
        sys.exit('not configured: run `ow1_launcher.py configure ...` first')
    config = json.loads(CONFIG.read_text(encoding='utf-8'))
    missing = [name for name in FILES if not Path(config.get(name, '')).is_file()]
    if missing:
        sys.exit(f'configured files not found: {", ".join(missing)}')
    return config


def port_free():
    with socket.socket() as probe:
        try:
            probe.bind(('127.0.0.1', PORT))
            return True
        except OSError:
            return False


def owned_clients():
    """PIDs of test clients started from the preservation build folder (never other installs)."""
    out = subprocess.run(['powershell.exe', '-NoProfile', '-Command',
                          "Get-Process -Name Overwatch -ErrorAction SilentlyContinue | "
                          r"Where-Object { $_.Path -like '*\OW1-preservation-build\clients\*' } | "
                          "ForEach-Object { $_.Id }"], capture_output=True, text=True).stdout
    return [int(x) for x in out.split() if x.isdigit()]


def launcher_running():
    out = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq ow1-offline-launch.exe'],
                         capture_output=True, text=True).stdout
    return 'ow1-offline-launch.exe' in out


def wait_until(condition, seconds):
    deadline = time.time() + seconds
    while time.time() < deadline:
        if condition():
            return True
        time.sleep(2)
    return condition()


def early_exit(log_path):
    """True when the launcher reports the client exiting before it reached the server."""
    try:
        text = Path(log_path).read_text(encoding='utf-8', errors='replace')
    except OSError:
        return False
    return 'Client exited' in text and 'TLS observer' not in text


def cmd_configure(args):
    config = {name: str(Path(getattr(args, name)).resolve()) for name in FILES}
    config['handshake_delay'] = args.handshake_delay
    missing = [name for name in FILES if not Path(config[name]).is_file()]
    if missing:
        sys.exit(f'files not found: {", ".join(missing)}')
    CONFIG.parent.mkdir(parents=True, exist_ok=True)
    CONFIG.write_text(json.dumps(config, indent=2) + '\n', encoding='utf-8')
    print(f'configuration saved to {CONFIG}')


def cmd_create(args):
    store = AccountStore()
    password = None
    if not args.no_password:
        password = getpass.getpass('password (blank for none): ')
        if password and getpass.getpass('repeat password: ') != password:
            sys.exit('passwords differ')
    account = store.create(args.name, password or None)
    print(f"created {account['battle_tag']} (account {account['account_id']})")


def cmd_list(args):
    store = AccountStore()
    if not store.accounts:
        print('no accounts yet: `ow1_launcher.py create <name>`')
    for account in store.accounts:
        lock = 'password' if 'password' in account else 'no password'
        print(f"{account['battle_tag']:<20} account {account['account_id']}  ({lock})")


def cmd_delete(args):
    AccountStore().delete(args.name)
    print(f'deleted {args.name}')


def cmd_play(args):
    store = AccountStore()
    account = store.find(args.name)
    if account is None:
        sys.exit(f'no account {args.name!r}')
    password = getpass.getpass(f"password for {account['name']}: ") if 'password' in account else None
    store.verify(args.name, password)
    config = load_config()
    # The game runs one instance, and a finishing session stops its server just
    # after its client exits: give both up to a minute before refusing.
    if not wait_until(lambda: not launcher_running() and not owned_clients(), 60):
        sys.exit('a previous test client is still running (the game allows one instance): close it first')
    if not wait_until(port_free, 30):
        sys.exit(f'port {PORT} is busy: stop the previous server first')
    seconds = min(max(args.seconds, 1), MAX_SECONDS)
    stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    name = f"play-{account['name']}-{stamp}"
    RUNS.mkdir(parents=True, exist_ok=True)
    server_cmd = [sys.executable, str(ROOT / 'tools' / 'bnet-probe.py'),
                  '--cert', config['cert'], '--key', config['key'], '--log', str(RUNS / f'{name}-server.log'),
                  '--tls-max', '1.2', '--handshake-delay', str(config.get('handshake_delay', 25)), '--serve',
                  '--battle-tag', account['battle_tag'], '--account-id', str(account['account_id']),
                  '--lobby-private-key', config['lobby_private_key'],
                  '--lobby-integrity-key', config['lobby_integrity_key'],
                  '--lobby-peer-group', '13', '--gateway-catalogue', str(ROOT / 'protocol' / 'gateway-104319.json'),
                  '--lobby-login-schema', str(ROOT / 'protocol' / 'lobby-login-104319.json'),
                  '--lobby-initial-data', 'keys-hotfix-player-settings',
                  '--lobby-initial-delay', str(args.initial_delay)]
    with open(RUNS / f'{name}-server.out', 'w', encoding='utf-8') as out:
        server = subprocess.Popen(server_cmd, stdout=out, stderr=subprocess.STDOUT, cwd=ROOT)
    try:
        time.sleep(2)
        if server.poll() is not None:
            sys.exit(f'server failed to start; see {RUNS / (name + "-server.out")}')
        print(f"server up for {account['battle_tag']}; starting the client for {seconds} s")
        for attempt in (1, 2):
            log_name = name if attempt == 1 else f'{name}-retry'
            subprocess.run(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
                            str(ROOT / 'scripts' / 'Start-PrivateClient.ps1'), '-RunForSeconds', str(seconds),
                            '-LogName', log_name, '-TrustCaCertificate', config['ca'], '-ObserveTls',
                            '-TrustSocketCa', '-TrustLobbyKey', config['lobby_modulus']], check=True, cwd=ROOT)
            time.sleep(5)
            while launcher_running():
                time.sleep(3)
                if owned_clients():
                    break
            if owned_clients() or not early_exit(RUNS / f'{log_name}.log'):
                break
            # A client that exits at once usually met a still-closing instance.
            print('client exited at start; waiting for the previous instance and retrying once')
            wait_until(lambda: not launcher_running() and not owned_clients(), 60)
        while launcher_running():
            time.sleep(3)
        # The bounded diagnostic window has ended; keep serving while the game runs.
        while owned_clients():
            time.sleep(3)
        print(f'client closed; logs in {RUNS} ({name}*)')
    finally:
        server.terminate()
        try:
            server.wait(10)
        except subprocess.TimeoutExpired:
            server.kill()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)
    configure = sub.add_parser('configure', help='save server certificate and own lobby key paths')
    for name in FILES:
        configure.add_argument('--' + name.replace('_', '-'), required=True)
    configure.add_argument('--handshake-delay', type=int, default=25, choices=range(0, 61))
    configure.set_defaults(func=cmd_configure)
    create = sub.add_parser('create', help='create a local account')
    create.add_argument('name')
    create.add_argument('--no-password', action='store_true')
    create.set_defaults(func=cmd_create)
    sub.add_parser('list', help='list local accounts').set_defaults(func=cmd_list)
    delete = sub.add_parser('delete', help='delete a local account')
    delete.add_argument('name')
    delete.set_defaults(func=cmd_delete)
    play = sub.add_parser('play', help='start the private server and client as an account')
    play.add_argument('name')
    play.add_argument('--seconds', type=int, default=MAX_SECONDS)
    play.add_argument('--initial-delay', type=int, default=0, choices=range(0, 31),
                      help='seconds between the identity reply and the initial lobby data')
    play.set_defaults(func=cmd_play)
    args = parser.parse_args()
    try:
        args.func(args)
    except ValueError as error:
        sys.exit(str(error))


if __name__ == '__main__':
    main()
