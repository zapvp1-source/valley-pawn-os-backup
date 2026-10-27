"""Valley Pawn Store Traffic: Nest SDM WebRTC helper. Secrets live OUTSIDE this folder
(VPST_DIR, default ~/.vpst: sdm_oauth.json + cameras.json). Never put secrets in Projects."""
import asyncio, json, os, sys, time, urllib.request, urllib.parse
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCBundlePolicy

VPST = os.environ.get('VPST_DIR', os.path.expanduser('~/.vpst'))
C = json.load(open(os.path.join(VPST, 'sdm_oauth.json')))
BASE = 'https://smartdevicemanagement.googleapis.com/v1/'

def token():
    d = urllib.parse.urlencode({'client_id': C['client_id'], 'client_secret': C['client_secret'],
        'refresh_token': C['refresh_token'], 'grant_type': 'refresh_token'}).encode()
    return json.load(urllib.request.urlopen('https://oauth2.googleapis.com/token', d))['access_token']

def command(at, dev, cmd, params):
    req = urllib.request.Request(BASE + dev + ':executeCommand', method='POST',
        data=json.dumps({'command': cmd, 'params': params}).encode(),
        headers={'Authorization': 'Bearer ' + at, 'Content-Type': 'application/json'})
    return json.load(urllib.request.urlopen(req))

def clean_answer(sdp):
    """SDM answer quirks: empty ICE foundation, and duplicated payload types/attributes
    in the video section (m=video ... 99 100 99 100). aiortc needs both fixed."""
    out, seen = [], set()
    for line in sdp.replace('a=candidate: ', 'a=candidate:0 ').split('\r\n'):
        if line.startswith('m='):
            seen = set()
            parts = line.split(' ')
            pts = list(dict.fromkeys(parts[3:]))
            line = ' '.join(parts[:3] + pts)
        elif line.startswith('a=') and not line.startswith('a=candidate') and line in seen:
            continue
        seen.add(line)
        out.append(line)
    sdp = '\r\n'.join(out)
    # SDM answers H264 as PT 99 (rtx 100) but actually sends PT 101 (rtx 102), which matches
    # our offer's packetization-mode=1 H264. Renumber the video section so aiortc routes it.
    head, sep, rest = sdp.partition('m=video')
    vid, sep2, tail = rest.partition('m=application')
    import re
    vid = re.sub(r'(?<![0-9])99(?![0-9])', 'PT101', vid)
    vid = re.sub(r'(?<![0-9])100(?![0-9])', 'PT102', vid)
    vid = vid.replace('PT101', '101').replace('PT102', '102')
    return head + sep + vid + sep2 + tail

def camera(store, name):
    for c in json.load(open(os.path.join(VPST, 'cameras.json'))):
        if c['store'] == store and c['name'] == name:
            return c
    raise KeyError(f'{store}/{name}')

async def open_stream(at, cam):
    """Return (pc, video_track_future, media_session_id). Caller must stop()."""
    pc = RTCPeerConnection(RTCConfiguration(bundlePolicy=RTCBundlePolicy.MAX_BUNDLE))  # SDM bundles all media on one transport
    pc.addTransceiver('audio', direction='recvonly')
    pc.addTransceiver('video', direction='recvonly')
    pc.createDataChannel('dataSendChannel')
    fut = asyncio.get_event_loop().create_future()
    @pc.on('track')
    def on_track(t):
        if t.kind == 'video' and not fut.done():
            fut.set_result(t)
    await pc.setLocalDescription(await pc.createOffer())
    res = command(at, cam['id'], 'sdm.devices.commands.CameraLiveStream.GenerateWebRtcStream',
                  {'offerSdp': pc.localDescription.sdp})['results']
    sdp = clean_answer(res['answerSdp'])
    await pc.setRemoteDescription(RTCSessionDescription(sdp, 'answer'))
    # aiortc does not pick up the bundled remote candidates on its own: add them explicitly to mid 0
    from aiortc.sdp import candidate_from_sdp
    for line in sdp.split('\r\n'):
        if line.startswith('a=candidate:') and ' udp ' in line.lower():
            cand = candidate_from_sdp(line[2:].split(':', 1)[1])
            cand.sdpMid, cand.sdpMLineIndex = '0', 0
            await pc.addIceCandidate(cand)
        elif line.startswith('m=video'):
            break
    return pc, fut, res['mediaSessionId']

async def stop(at, cam, pc, sid):
    try:
        command(at, cam['id'], 'sdm.devices.commands.CameraLiveStream.StopWebRtcStream', {'mediaSessionId': sid})
    except Exception:
        pass
    await pc.close()

async def snapshot(store, name, out, skip=15, timeout=30):
    at = token(); cam = camera(store, name)
    pc, fut, sid = await open_stream(at, cam)
    try:
        track = await asyncio.wait_for(fut, timeout)
        for i in range(skip + 1):
            f = await asyncio.wait_for(track.recv(), timeout)
        f.to_image().save(out, quality=85)
        return out
    finally:
        await stop(at, cam, pc, sid)

if __name__ == '__main__':
    print(asyncio.run(snapshot(sys.argv[1], sys.argv[2], sys.argv[3])))
