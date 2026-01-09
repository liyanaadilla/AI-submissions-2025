# AI Task Automation System

Industrial AI automation dashboard for monitoring tasks, machines, workers, and resources with real-time state visualization and AI decision-making simulation.

## Features

- **PEAS Model Implementation**: Sense-Reason-Act cycle
- **Real-time Monitoring**: Tasks, workers, machines, and resources
- **AI Decision Making**: Automated task assignment and resource optimization
- **Anomaly Detection**: Predictive maintenance alerts
- **Interactive Dashboard**: Four-page navigation system

## Liabrary installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

Start the server:
```bash
python main.py
```

## If this "WARNING: The script flask.exe is not in a PATH" occured

Start the server using:
```bash
python -m flask --app main run
```

Access the dashboard at: **http://localhost:5000**

## Usage

- **Overview Page**: View metrics and control simulation
- **Tasks & Progress**: Monitor task status and worker assignments
- **Workers & Machines**: Check machine conditions and worker status
- **Resources & Alerts**: View resource allocation and active alerts

## Controls

- **Execute Step**: Run one AI decision cycle
- **Start/Stop Auto Run**: Toggle automatic execution (2-second intervals)
- **Reset**: Reset system to initial state

## Educational POC

This is a proof-of-concept demonstrating AI agent behavior using the PEAS model and state space search for educational purposes.
