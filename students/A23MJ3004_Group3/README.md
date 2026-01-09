# AI Task Automation System (Proof of Concept)

## Description
This project is an AI Task Automation System developed as a Proof of Concept (POC) for the Artificial Intelligence course (SECJ3553). The system simulates intelligent decision-making in an industrial environment by autonomously assigning tasks, managing workflows, monitoring machines, optimizing resources, and detecting anomalies.

The AI agent demonstrates:
- Knowledge Representation (A1): Modeling tasks, workers, machines, resources, workflows, and alerts.
- State Space Search (A2): Transitioning between system states by executing valid actions to improve system performance.
- PEAS Model (A3): Defining agent behavior through performance measures, environment, actuators, and sensors.

The system operates as an interactive simulation, enabling users to observe the step-by-step decision-making process of AI.

## How to Run the Code

### Prerequisites
- Python 3.9 or higher
- Required Python packages (listed in `requirements.txt`)

### Steps
1. Install dependencies:
   ```bash
   pip install -r requirements.txt

2. Run the application:
   python main.py

3. If you encounter the warning:
   WARNING: The script flask.exe is not in a PATH
   Run the following instead:
   python -m flask --app main run

4. Open your browser and access the system dashboard at:
   http://localhost:5000

## Expected Output
A web-based dashboard displaying the AI task automation simulation. Visualization of task statuses (Pending, In Progress, Completed) with progress percentages. Real-time display of worker availability and machine health states. Alerts are generated when machines exceed defined thresholds. A log of actions taken by the AI agent, showing task assignments, workflow progression, and maintenance decisions.
