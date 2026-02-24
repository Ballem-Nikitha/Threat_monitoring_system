"""
camera_feed.py  –  Real-time camera monitoring with face recognition.

Features
--------
* Live webcam feed with face detection every N frames (configurable).
* Recognised faces get a GREEN box + name label.
* Unknown faces get a RED box + "UNKNOWN" label and trigger alerts.
* Captures a timestamped screenshot of every unknown detection to `captured/`.
* On-screen HUD showing FPS, detection count, and status.
* Press 'q' to quit.
"""

import os
import cv2
import time
import pickle
import datetime
import numpy as np
import face_recognition

from alerts.send_email import send_email
from alerts.send_sms import send_sms

# ─── Configuration ────────────────────────────────────────────────────────────
ENCODINGS_PATH      = 'encodings/encodings.pkl'
CAPTURE_DIR         = 'captured'
TOLERANCE           = 0.5          # face distance threshold (lower = stricter)
DETECT_EVERY_N      = 3            # run recognition every N frames (performance)
ALERT_COOLDOWN_SEC  = 30           # min seconds between repeated alerts for same type
SCALE_FACTOR        = 0.25         # downscale for faster detection (0.25 = 1/4 size)
CAMERA_INDEX        = 0            # webcam index

# Colours (BGR)
GREEN   = (0, 200, 0)
RED     = (0, 0, 220)
YELLOW  = (0, 220, 255)
WHITE   = (255, 255, 255)
BLACK   = (0, 0, 0)
DARK_BG = (30, 30, 30)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def load_encodings(path=ENCODINGS_PATH):
    """Load known face encodings from pickle file."""
    if not os.path.exists(path):
        print(f"[camera] Encodings file not found at '{path}'.")
        return {}, []
    with open(path, 'rb') as f:
        data = pickle.load(f)

    known_names = []
    known_encodings = []
    for name, enc_list in data.items():
        for enc in enc_list:
            known_names.append(name)
            known_encodings.append(enc)

    print(f"[camera] Loaded {len(known_encodings)} encoding(s) for {len(data)} person(s).")
    return known_names, known_encodings


def save_capture(frame, label='unknown'):
    """Save a timestamped screenshot to the captures directory."""
    os.makedirs(CAPTURE_DIR, exist_ok=True)
    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{label}_{ts}.jpg"
    filepath = os.path.join(CAPTURE_DIR, filename)
    cv2.imwrite(filepath, frame)
    print(f"[camera] Screenshot saved → {filepath}")
    return filepath


def draw_label(frame, text, x, y, color, bg_color=None):
    """Draw a text label with a filled background rectangle."""
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.6
    thickness = 1
    (tw, th), baseline = cv2.getTextSize(text, font, scale, thickness)
    bg = bg_color if bg_color else color

    # Background rectangle
    cv2.rectangle(frame, (x, y - th - 10), (x + tw + 8, y), bg, cv2.FILLED)
    # Text
    cv2.putText(frame, text, (x + 4, y - 6), font, scale, WHITE, thickness, cv2.LINE_AA)


def draw_hud(frame, fps, known_count, unknown_count, status):
    """Draw a heads-up display overlay on the top of the frame."""
    h, w = frame.shape[:2]

    # Semi-transparent top bar
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 48), DARK_BG, cv2.FILLED)
    cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)

    font = cv2.FONT_HERSHEY_SIMPLEX
    y = 32

    # FPS
    cv2.putText(frame, f"FPS: {fps:.1f}", (12, y), font, 0.55, GREEN, 1, cv2.LINE_AA)

    # Detection counts
    info = f"Known: {known_count}  |  Unknown: {unknown_count}"
    cv2.putText(frame, info, (160, y), font, 0.55, WHITE, 1, cv2.LINE_AA)

    # Status
    status_color = GREEN if status == 'SECURE' else RED
    cv2.putText(frame, status, (w - 200, y), font, 0.65, status_color, 2, cv2.LINE_AA)

    # Timestamp
    ts = datetime.datetime.now().strftime('%Y-%m-%d  %H:%M:%S')
    cv2.putText(frame, ts, (w - 220, h - 12), font, 0.45, YELLOW, 1, cv2.LINE_AA)


# ─── Main Feed Loop ──────────────────────────────────────────────────────────

def run_camera_feed():
    """Launch the live camera feed with face recognition."""

    known_names, known_encodings = load_encodings()

    if not known_encodings:
        print("[camera] ⚠  No known encodings loaded. All faces will be marked UNKNOWN.")

    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("❌ Cannot open camera. Check that a webcam is connected.")
        return

    print("[camera] Camera opened. Press 'q' to quit.")

    frame_count = 0
    fps = 0.0
    prev_time = time.time()
    last_alert_time = 0

    # Persistent detection results (carry forward between skipped frames)
    face_locations = []
    face_labels = []

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to grab frame.")
            break

        frame_count += 1
        display = frame.copy()

        # ── Face detection + recognition (every N frames) ─────────────
        if frame_count % DETECT_EVERY_N == 0:
            # Downscale for speed
            small = cv2.resize(frame, (0, 0), fx=SCALE_FACTOR, fy=SCALE_FACTOR)
            rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

            face_locations_raw = face_recognition.face_locations(rgb_small, model='hog')
            face_encs = face_recognition.face_encodings(rgb_small, face_locations_raw)

            face_locations = []
            face_labels = []

            for (top, right, bottom, left), enc in zip(face_locations_raw, face_encs):
                # Scale back up
                inv = int(1 / SCALE_FACTOR)
                top    *= inv
                right  *= inv
                bottom *= inv
                left   *= inv

                label = "UNKNOWN"

                if known_encodings:
                    distances = face_recognition.face_distance(known_encodings, enc)
                    best_idx = np.argmin(distances)
                    if distances[best_idx] <= TOLERANCE:
                        label = known_names[best_idx]

                face_locations.append((top, right, bottom, left))
                face_labels.append(label)

        # ── Draw bounding boxes ───────────────────────────────────────
        known_count = 0
        unknown_count = 0

        for (top, right, bottom, left), label in zip(face_locations, face_labels):
            if label == "UNKNOWN":
                unknown_count += 1
                color = RED
                box_thickness = 3

                # Alert + capture (with cooldown)
                now = time.time()
                if now - last_alert_time > ALERT_COOLDOWN_SEC:
                    last_alert_time = now
                    save_capture(frame, label='unknown')
                    send_email('bnikitha9618@gmail.com', '🚨 Threat Alert',
                               'Unknown person detected on camera feed.')
                    send_sms('+91 9618354541',
                             '🚨 Unknown person detected on camera feed.')
            else:
                known_count += 1
                color = GREEN
                box_thickness = 2

            # Bounding box
            cv2.rectangle(display, (left, top), (right, bottom), color, box_thickness)

            # Label
            draw_label(display, label.upper(), left, top, color)

        # ── HUD ───────────────────────────────────────────────────────
        current_time = time.time()
        fps = 1.0 / max(current_time - prev_time, 1e-6)
        prev_time = current_time

        status = 'THREAT' if unknown_count > 0 else 'SECURE'
        draw_hud(display, fps, known_count, unknown_count, status)

        # ── Show frame ────────────────────────────────────────────────
        cv2.imshow('Threat Monitoring System', display)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("[camera] Exiting…")
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    run_camera_feed()
