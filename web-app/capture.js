const video = document.querySelector("#camera-preview");
const preview = document.querySelector("#photo-preview");
const status = document.querySelector("#camera-status");
const startButton = document.querySelector("#start-camera");
const takeButton = document.querySelector("#take-photo");
const retakeButton = document.querySelector("#retake-photo");
const useButton = document.querySelector("#use-photo");

let stream = null;
let photo = null;
let photoUrl = null;
let cameraRequest = 0;

function show(state, message) {
    const showingCamera = state === "live" || state === "capturing";
    const showingPhoto = state === "preview" || state === "selected";

    status.textContent = message;
    video.hidden = !showingCamera;
    preview.hidden = !showingPhoto;
    startButton.hidden = state !== "idle" && state !== "starting";
    startButton.disabled = state === "starting";
    takeButton.hidden = !showingCamera;
    takeButton.disabled = state !== "live";
    retakeButton.hidden = !showingPhoto;
    useButton.hidden = state !== "preview";
}

function stopCamera() {
    stream?.getTracks().forEach((track) => track.stop());
    stream = null;
    video.srcObject = null;
}

function clearPhoto() {
    if (photoUrl) URL.revokeObjectURL(photoUrl);
    preview.removeAttribute("src");
    photoUrl = null;
    photo = null;
}

async function startCamera() {
    if (!navigator.mediaDevices?.getUserMedia) {
        show("idle", "Camera access requires a supported browser on localhost or HTTPS.");
        return;
    }

    const request = ++cameraRequest;
    show("starting", "Waiting for camera access…");

    try {
        const camera = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
        if (request !== cameraRequest) {
            camera.getTracks().forEach((track) => track.stop());
            return;
        }

        stream = camera;
        for (const track of camera.getVideoTracks()) {
            track.addEventListener("ended", () => {
                if (stream !== camera) return;

                cameraRequest++;
                stopCamera();
                show(photo ? "preview" : "idle", "Camera disconnected. Reconnect it and try again.");
                (photo ? retakeButton : startButton).focus();
            }, { once: true });
        }
        video.srcObject = camera;
        await video.play();
        if (request !== cameraRequest) return;

        clearPhoto();
        show("live", "Frame your shot, then select Take Photo.");
        takeButton.focus();
    } catch (error) {
        if (request !== cameraRequest) return;

        stopCamera();
        const messages = {
            NotAllowedError: "Camera access was denied. Allow it in your browser settings and try again.",
            NotFoundError: "No camera was found. Connect a camera and try again.",
            NotReadableError: "The camera is unavailable. Close other apps using it and try again.",
        };
        show(photo ? "preview" : "idle", messages[error.name] ?? "Could not start the camera. Try again.");
        (photo ? retakeButton : startButton).focus();
    }
}

function takePhoto() {
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext("2d");

    if (!canvas.width || !canvas.height || !context) {
        show("live", "The camera frame is unavailable. Try again.");
        return;
    }

    const request = cameraRequest;
    show("capturing", "Taking photo…");
    context.drawImage(video, 0, 0);
    canvas.toBlob((image) => {
        if (request !== cameraRequest) return;
        if (!image) {
            show("live", "Could not take the photo. Try again.");
            takeButton.focus();
            return;
        }

        stopCamera();
        photo = image;
        photoUrl = URL.createObjectURL(photo);
        preview.src = photoUrl;
        show("preview", "Review your photo.");
        useButton.focus();
    }, "image/jpeg", 0.9);
}

startButton.addEventListener("click", startCamera);
takeButton.addEventListener("click", takePhoto);
retakeButton.addEventListener("click", startCamera);
useButton.addEventListener("click", () => {
    show("selected", "Photo selected.");
    retakeButton.focus();
    preview.dispatchEvent(new CustomEvent("photo-selected", { bubbles: true, detail: { photo } }));
});

window.addEventListener("pagehide", () => {
    cameraRequest++;
    stopCamera();
    clearPhoto();
    show("idle", "Turn on your camera to take a photo.");
});
