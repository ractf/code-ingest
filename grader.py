# code taken from
# https://github.com/DMOJ/judge-server/blob/fdc4fbcc59e021230c7d4336b3d0d54aba2884ea/dmoj/packet.py
# and https://github.com/DMOJ/judge-server/blob/master/dmoj/utils/unicode.py

import base64
import configparser
import json
import logging
import os
import socket
import ssl
import struct
import threading
import time
import traceback
import zlib

from ...bases import FlagTypePlugin

log = logging.getLogger(__name__)


def utf8bytes(maybe_text):
    if maybe_text is None:
        return None
    if isinstance(maybe_text, bytes):
        return maybe_text
    return maybe_text.encode('utf-8')


def utf8text(maybe_bytes, errors='strict'):
    if maybe_bytes is None:
        return None
    if isinstance(maybe_bytes, str):
        return maybe_bytes
    return maybe_bytes.decode('utf-8', errors)


class PacketManager:
    SIZE_PACK = struct.Struct('!I')

    def __init__(self, port, key, secure=False, no_cert_check=False,
                 cert_store=None):
        self.port = port
        self.key = key
        self._closed = False

        log.info('Preparing to listen on port %s', port)
        if secure:
            self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            self.ssl_context.options |= ssl.OP_NO_SSLv2
            self.ssl_context.options |= ssl.OP_NO_SSLv3

            if not no_cert_check:
                self.ssl_context.verify_mode = ssl.CERT_REQUIRED
                self.ssl_context.check_hostname = True

            if cert_store is None:
                self.ssl_context.load_default_certs()
            else:
                self.ssl_context.load_verify_locations(cafile=cert_store)
            log.info('Configured to use TLS.')
        else:
            self.ssl_context = None
            log.info('TLS not enabled.')

        self.secure = secure
        self.no_cert_check = no_cert_check
        self.cert_store = cert_store

        self._lock = threading.RLock()
        self.fallback = 4
        self.conn = None
        self.submissions_count = 0
        threading.Thread(target=self._listen, daemon=True).start()
        threading.Thread(target=self._keep_alive, daemon=True).start()

    def _listen(self):
        log.info('Listening on port %s', self.port)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("0.0.0.0", self.port))
            s.listen()
            while True:
                log.info("Listening...")
                self.conn, addr = s.accept()
                if self.ssl_context:
                    log.info('Starting TLS on: %s', self.port)
                    self.conn = self.ssl_context.wrap_socket(self.conn,
                                                             server_side=True)
                log.info('Waiting for handshake: %s', self.port)
                self.input = self.conn.makefile('rb')
                self.output = self.conn.makefile('wb', 0)
                handshake = self._read_single()
                self.problems = handshake['problems']
                self.runtimes = handshake['executors']
                self.judgeid = handshake['id']
                key = handshake['key']
                if key != self.key:
                    log.info('Invalid key')
                    self.conn.close()
                else:
                    log.info('Judge online')
                    self._send_packet({'name': 'handshake-success'})
                    return

    def _keep_alive(self):
        while True:
            time.sleep(60)
            try:
                self._send_packet({'name': 'ping', 'when': time.time()})
                log.info(self._read_single())
            except Exception:
                pass

    def __del__(self):
        self.close()

    def close(self):
        if self.conn and not self._closed:
            self.conn.shutdown(socket.SHUT_RDWR)
        self._closed = True

    def _read_single(self):
        try:
            data = self.input.read(PacketManager.SIZE_PACK.size)
        except socket.error:
            self._listen()
            return self._read_single()
        if not data:
            self._listen()
            return self._read_single()
        size = PacketManager.SIZE_PACK.unpack(data)[0]
        try:
            packet = zlib.decompress(self.input.read(size))
        except zlib.error:
            self._listen()
            return self._read_single()
        else:
            return json.loads(utf8text(packet))

    def _send_packet(self, packet: dict):
        for k, v in packet.items():
            if isinstance(v, bytes):
                # Make sure we don't have any garbage utf-8 from
                # e.g. weird compilers
                # *cough* fpc *cough* that could cause this routine to crash
                # We cannot use utf8text because it may not be text.
                packet[k] = v.decode('utf-8', 'replace')

        raw = zlib.compress(utf8bytes(json.dumps(packet)))
        with self._lock:
            self.output.writelines((PacketManager.SIZE_PACK.pack(len(raw)),
                                    raw))

    def submit(self, problem_id, language, source, time_limit, memory_limit):
        self.submissions_count += 1
        packet = {
            'name': 'submission-request',
            'submission-id': self.submissions_count,
            'problem-id': problem_id,
            'language': language,
            'source': source,
            'time-limit': time_limit,
            'memory-limit': memory_limit,
            'short-circuit': False,
            'meta': False,
        }
        self._send_packet(packet)
        try:
            cases = []
            while True:
                p = self._read_single()
                # log.info(p)
                if p['submission-id'] != self.submissions_count:
                    continue
                if p['name'] == 'test-case-status':
                    cases += p['cases']
                elif p['name'] == 'grading-end':
                    return {"success": True, "data": cases}
                elif p['name'] == 'compile-error':
                    return {"success": False, "data": p['log']}
                elif p['name'] == 'internal-error':
                    return {
                        "success": False,
                        "data": "Internal Error (invalid language?)"
                    }
        except Exception:  # connection reset by peer
            traceback.print_exc()
            raise SystemExit(1)


config = configparser.ConfigParser()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)-12.12s]"
    " [%(levelname)-5.5s]  %(message)s",
    handlers=[
        # logging.FileHandler("test.log"),
        logging.StreamHandler()
    ])
filename = os.environ.get("GRADER_CONFIG",
                          os.path.join(os.path.dirname(__file__),
                                       "ractf_grader.ini"))
try:
    with open(filename) as fp:
        config.read_file(fp)
except FileNotFoundError as e:
    raise ValueError(
        "Couldn't find config file {0} - consider setting env-var "
        "GRADER_CONFIG to point to the config file".format(
            filename
        )
    ) from e
port = config.getint("grader", "port")
key = config.get("grader", "key")
grader = PacketManager(port, key)


class CodeGraderPlugin(FlagTypePlugin):
    def check(self, attempt):
        # Flag is JSON
        # {"problem-id":"aplusb","time-limit":1,
        # "memory-limit":262144,"threshold":100}
        # time limit in seconds, memory limit in KiB,
        # points threshold for awarding flag
        problem_data = self.flag_info
        try:
            # print(attempt[6:-1])
            solution = base64.b64decode(attempt[6:-1]).decode("utf-8")
            # print(solution.partition("\n"))
            lang = solution.partition("\n")[0]
            src = solution.partition("\n")[2]
            # print(lang,src)
        except Exception:
            print(False, "Invalid encoding")
            return False
        ans = grader.submit(problem_data['problem-id'], lang, src,
                            problem_data['time-limit'], 
                            problem_data['memory-limit'])
        print(ans)
        if not ans["success"]:
            print(False, ans["data"])
            return False
        else:
            score = 0
            res = []
            for i in ans["data"]:
                score += i['points']
                status = i['status']
                if status & 4:
                    res.append('TLE')
                elif status & 8:
                    res.append('MLE')
                elif status & 64:
                    res.append('OLE')
                elif status & 2:
                    res.append('RTE')
                elif status & 16:
                    res.append('IR')
                elif status & 1:
                    res.append('WA')
                elif status & 32:
                    res.append('SC')
                else:
                    res.append('AC')
            print(score >= problem_data["threshold"], " ".join(res))
            return score >= problem_data["threshold"]


PLUGIN = CodeGraderPlugin
