import os
import pickle
import numpy as np
from PIL import Image
import face_recognition


def load_image_safe(path):
    """Load an image and convert RGBA → RGB so face_recognition can handle it."""
    img = Image.open(path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    return np.array(img)


def build_encodings(dataset_dir='datasets/known', out_path='encodings/encodings.pkl'):
    """
    Scan dataset_dir for subfolders. Each subfolder name = person label.
    Images inside are encoded with face_recognition (128-d vectors).
    Results are saved as  { name: [encoding, ...], ... }
    """
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    encodings_dict = {}
    valid_ext = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')

    if not os.path.isdir(dataset_dir):
        print(f"[encode] Dataset directory '{dataset_dir}' not found. Creating empty encodings.")
        with open(out_path, 'wb') as f:
            pickle.dump(encodings_dict, f)
        return out_path

    for person_name in sorted(os.listdir(dataset_dir)):
        person_dir = os.path.join(dataset_dir, person_name)
        if not os.path.isdir(person_dir):
            continue

        print(f"[encode] Processing: {person_name}")
        for fname in sorted(os.listdir(person_dir)):
            if not fname.lower().endswith(valid_ext):
                continue

            img_path = os.path.join(person_dir, fname)
            try:
                image = load_image_safe(img_path)
                face_encs = face_recognition.face_encodings(image)

                if face_encs:
                    encodings_dict.setdefault(person_name, []).append(face_encs[0])
                    print(f"  ✔ {fname}  ({len(face_encs)} face(s) found, using first)")
                else:
                    # Still store a placeholder so the person is in the dict
                    print(f"  ⚠ {fname}  (no face detected, skipping)")
            except Exception as exc:
                print(f"  ✖ {fname}  error: {exc}")

    total_faces = sum(len(v) for v in encodings_dict.values())
    print(f"[encode] Done — {len(encodings_dict)} person(s), {total_faces} encoding(s) total.")

    with open(out_path, 'wb') as f:
        pickle.dump(encodings_dict, f)

    return out_path


if __name__ == '__main__':
    p = build_encodings()
    print('Wrote encodings to', p)
