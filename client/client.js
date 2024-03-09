navigator.mediaDevices.getUserMedia({ video: true }).then(enumerateDevices);

async function enumerateDevices() {
    let devices = await navigator.mediaDevices.enumerateDevices();
    devices.forEach(function(device, index) {
        if (device.deviceId != null && device.kind == 'videoinput') {
            let video_menu = document.getElementById('select-video-source')
            let video_item = document.createElement("option");
            video_item.innerText = device.label;
            video_item.value = device.deviceId;
            video_menu.appendChild(video_item);
        } else if(device.deviceId != null && device.kind == 'audioinput'){
            let audio_menu = document.getElementById('select-audio-source')
            let audio_item = document.createElement("option");
            audio_item.innerText = device.label;
            audio_item.value = device.deviceId;
            audio_menu.appendChild(audio_item);
        }
    }); 
}

var pc = null;

function negotiate () {
    return pc.createOffer().then(function (offer) {
        return pc.setLocalDescription(offer);
    }).then(function () {
        // wait for ICE gathering to complete
        return new Promise(function (resolve) {
            if (pc.iceGatheringState === 'complete') {
                resolve();
            } else {
                function checkState () {
                    if (pc.iceGatheringState === 'complete') {
                        pc.removeEventListener('icegatheringstatechange', checkState);
                        resolve();
                    }
                }
                pc.addEventListener('icegatheringstatechange', checkState);
            }
        });
    }).then(function () {
        var offer = pc.localDescription;
        return fetch('/offer', {
            body: JSON.stringify({
                sdp: offer.sdp,
                type: offer.type, 
            }),
            headers: {
                'Content-Type': 'application/json'
            },
            method: 'POST'
        });
    }).then(function (response) {
        return response.json();
    }).then(function (answer) {
        return pc.setRemoteDescription(answer);
    }).catch(function (e) {
        alert(e);
    });
}

function streamStart() {
    let audioSource = document.getElementById('select-audio-source').value;
    let videoSource = document.getElementById('select-video-source').value;
    options={
        video: {
            width :     { exact: 640 },
            height :    { exact: 360 },
            frameRate : { exact: 30 }
        },
        audio: true    
    } 
    navigator.mediaDevices.getUserMedia(options).then(function(stream) {
        document.getElementById('btn-stream-start').disabled = true;
        pc = new RTCPeerConnection({ sdpSemantics: 'unified-plan' });
        stream.getTracks().forEach(track => pc.addTrack(track, stream));
        negotiate();
    }).then(function(){
        document.getElementById('btn-stream-stop').disabled = false;
    }).catch(function(err) {
        alert(err);
        document.getElementById('btn-stream-start').disabled = false;
        document.getElementById('btn-stream-stop').disabled = true;
    });
}

function streamStop() {
    setTimeout(function() {
        pc.close();
    }, 500);
    document.getElementById('btn-stream-start').disabled = false;
    document.getElementById('btn-stream-stop').disabled = true;
    document.getElementById('video-stream').srcObject.getTracks().forEach(track => track.stop());
    document.getElementById('video-stream').srcObject = null;
}

document.getElementById('btn-stream-start').addEventListener('click', streamStart);
document.getElementById('btn-stream-stop').addEventListener('click', streamStop);
