# AI-submissions-2025
This repository is owned and maintained by the lecturer.
All student submissions must be made via Pull Request (PR) to ensure permanent record keeping, automated testing, and fair evaluation.

⚠️ Do NOT create your own repository for submission.
⚠️ Do NOT email or zip your code.

## Submission Method (Mandatory)

All students must submit their work by:

  Forking this repository → adding your code → creating a Pull Request

Submissions outside this method will not be evaluated.

## Folder Structure (IMPORTANT)

Each student must create one folder only inside the students/ directory.

📂 Folder naming format : students/<MatricNumber>_<FullName>/

Required Files (COMPULSORY)

Inside your folder, the following files are mandatory:

main.py
requirements.txt
README.md

1️⃣ main.py

The main entry point of your AI program.

The lecturer must be able to run your code using:

  python main.py

2️⃣ requirements.txt

List only the Python libraries required to run your project.

Example:

numpy
pandas
scikit-learn
matplotlib


⚠️ Do not include unnecessary or unused libraries.

3️⃣ README.md

Your README must include:

Project title

Brief project description

How to run the code

Expected output

## 📌 Example:

### AI Image Classification

This project classifies images using a CNN model.

#### How to Run
pip install -r requirements.txt
python main.py

#### Output
Accuracy will be printed in the terminal.

## 🔹 How to Submit (Step-by-Step)
Step 1: Fork the Repository

Click Fork (top-right of this page) to create your own copy.

Step 2: Add Your Folder

In your forked repo:

Go to students/

Create your folder using the required format

Add main.py, requirements.txt, and README.md

Step 3: Commit Your Changes

Commit your work with a clear message:

Add AI project submission - S12345_AliAhmad

Step 4: Open a Pull Request

Click Contribute → Open Pull Request

Ensure:

Base repository: Lecturer’s repo

Base branch: main

Submit your Pull Request

🔹 Automated Code Checking (GitHub Actions)

Once you submit a Pull Request:

Your code will be automatically executed

Results will appear under the Actions / Checks tab

Status meaning:

✅ Green: Code runs successfully

❌ Red: Error detected (check logs)

⚠️ Submissions with failing checks may receive reduced marks or zero marks, depending on assessment criteria.

🔹 Important Rules & Restrictions

❌ Do NOT modify or delete:

Other students’ folders

GitHub workflow files

Root-level files

❌ Do NOT include:

Large datasets

Pre-trained model files

External configuration dependencies

✅ Use small sample data or dummy inputs for demonstration.

## 🎯 YSMAI Demo & Presentation Guide

For the YSMAI HVAC Monitoring System (students/S12345_KhobaitSimran/):

### Quickest Demo (Streamlit)
```bash
pip install -r students/S12345_KhobaitSimran/requirements.txt
streamlit run streamlit_app.py
```
Opens at `http://localhost:8501` with interactive simulation.

### Full Stack Demo (React + Backend)

See [DEMO_SETUP.md](DEMO_SETUP.md) for complete instructions including:
- Backend setup
- React frontend integration
- Connection status & fallback modes
- Demo checklist for professor meeting

### Key Features Demonstrated
✅ Real-time SCADA dashboard (React + Tailwind + Recharts)
✅ FSM state machine with 1.5s debounce (NORMAL → ALERT)
✅ ML predictions (fault detection, anomaly scoring)
✅ Persistence task scheduling (~5s intervals)
✅ Fault injection toggle for testing
✅ Backend integration with graceful fallback to simulation

---

🔹 Late or Invalid Submissions

Pull Requests submitted after the deadline may be penalised.

Submissions without a successful GitHub Actions run may be considered not runnable.
