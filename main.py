"""
main.py  –  Threat Monitoring System entry point.

Usage
-----
    python main.py              # launch live camera feed (default)
    python main.py --simulate   # run simulated detection (no camera needed)
    python main.py --encode     # rebuild face encodings only
"""

import os
import sys
import pickle
import random

from encode_faces import build_encodings
from alerts.send_email import send_email
from alerts.send_sms import send_sms

ENC_PATH = 'encodings/encodings.pkl'


# ─── Helpers ──────────────────────────────────────────────────────────────────

def load_encodings(path=ENC_PATH):
    if not os.path.exists(path):
        print('[main] Encodings not found — building now…')
        build_encodings()
    try:
        with open(path, 'rb') as f:
            return pickle.load(f)
    except Exception as e:
        print('Failed to load encodings:', e)
        return {}


def simulate_detection(encodings):
    """Pick a random known person and fire stub alerts (no camera needed)."""
    if not encodings:
        print('No known encodings available.')
        return
    person = random.choice(list(encodings.keys()))
    print('Detected person:', person)
    send_email('bnikitha9618@gmail.com', 'Alert', f'Detected {person}')
    send_sms('+919618354541', f'Detected {person}')


# ─── CLI ──────────────────────────────────────────────────────────────────────

def print_banner():
    print()
    print('╔══════════════════════════════════════════╗')
    print('║     THREAT MONITORING SYSTEM  v2.0       ║')
    print('╠══════════════════════════════════════════╣')
    print('║  Modes:                                  ║')
    print('║   (default)    Live camera feed           ║')
    print('║   --simulate   Simulated detection        ║')
    print('║   --encode     Rebuild face encodings     ║')
    print('╚══════════════════════════════════════════╝')
    print()


if __name__ == '__main__':
    print_banner()

    args = sys.argv[1:]

    if '--encode' in args:
        print('[main] Rebuilding encodings…')
        build_encodings()
        print('[main] Done.')

    elif '--simulate' in args:
        enc = load_encodings()
        simulate_detection(enc)

    else:
        # Default: live camera feed
        print('[main] Starting live camera feed…')
        print('[main] Press "q" in the camera window to quit.\n')

        # Ensure encodings exist
        load_encodings()

        from camera_feed import run_camera_feed
        run_camera_feed()