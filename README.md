IoT-Enabled Intelligent Threat Monitoring & Surveillance System
📌 Project Overview

The Threat Monitoring System is an intelligent security solution that detects known persons, suspicious individuals, and potential threats using computer vision and deep learning.

The system uses a laptop camera to monitor surroundings and automatically triggers alerts when a suspicious person is detected.

This project is designed for home security, smart surveillance, and real-time threat detection.

Objectives

✔ Detect and recognize known persons
✔ Identify suspicious individuals
✔ Capture evidence images automatically
✔ Send SOS alerts via SMS & Email
✔ Provide real-time monitoring

System Workflow

1️⃣ Camera captures live video
2️⃣ System detects human faces
3️⃣ Face compared with:

Known persons dataset

Suspicious persons dataset
4️⃣ If known → ✅ Safe Mode
5️⃣ If suspicious → 🚨 Alert Mode
6️⃣ Capture photo → send alert

Technologies Used
👨‍💻 Programming

Python

🤖 Computer Vision & AI

OpenCV

face_recognition (dlib)

YOLO (Ultralytics)

📡 Alert System

Twilio (SMS alerts)

SMTP (Email alerts)

📦 Libraries
numpy

imutils

smtplib

datetime


Project Structure

Threat_monitoring_system/
│
├── models/
│   ├── dlib_face_recognition_resnet_model_v1.dat
│
├── dataset/
│   ├── known/
│   ├── suspicious/
│
├── captured_images/
│
├── main.py
├── alert_system.py
├── face_recognition_module.py
├── requirements.txt
└── README.md

Dataset
✔ Known Dataset

Contains images of authorized persons.

⚠ Suspicious Dataset

Contains images of blacklisted persons.
