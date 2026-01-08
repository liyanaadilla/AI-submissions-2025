
# Smart Waste Management System (SWMS)

**A multi-agent AI simulation designed to optimize urban waste collection operations in a smart city environment.**

---

## 🚀 How to Run 

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```bash
   python main.py
   ```

### Expected Output
*   The application will launch in your default web browser (Streamlit interface).
*   The **Manager Dashboard** will appear, displaying the city grid and initial configuration.
*   You will see the **Agent Cycle Control** panel to step through the simulation phases (Sense, Predict, Reason, Allocate, Plan, Adapt).
*   **Driver View**: A separate tab allows viewing the simulation from a truck driver's perspective.

---

## 📖 Project Description

The Smart Waste Management System (SWMS) demonstrates how intelligent agents can coordinate sensing, decision-making, and routing to improve efficiency in waste logistics. It integrates A* Pathfinding, Auction-Based Allocation, and Knowledge-Based Reasoning into a cohesive "Cognitive Agent Cycle".

### Key Features

- **Adaptive AI Agent** — Uses a 6-step cognitive cycle to solve logistics problems in real-time.
- **Dual View Interface** — Toggles between **Manager Dashboard** (system overview) and **Driver Mobile View** (truck navigation).
- **A\* Pathfinding** — Multi-objective route optimization balancing distance, overflow risk, and SLA compliance.
- **Auction-Based Allocation** — Distributed task assignment using Contract Net Protocol.
- **Predictive Analytics** — ETA-based overflow prediction for proactive collection.
- **Performance Verification** — **AI vs Baseline** dashboard quantifying efficiency gains (e.g., "35% Distance Saved").

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                        │
│             (Manager Dashboard / Driver View)                │
└─────────────────────────┬───────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│   Routing     │ │   Auction     │ │   Reasoning   │
│   (A* Search) │ │   (CNP)       │ │   (KR Rules)  │
└───────────────┘ └───────────────┘ └───────────────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │   Simulation Engine   │
              │   (Digital Twin)      │
              └───────────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │   City Grid (NetworkX)│
              │   Bins • Trucks       │
              └───────────────────────┘
```

### Core Modules

| Module         | File                    | Description                                        |
| -------------- | ----------------------- | -------------------------------------------------- |
| **Main App**   | `app.py`                | Streamlit UI, state management, simulation loop    |
| **Routing**    | `modules/routing.py`    | A\* pathfinding with multi-objective cost function |
| **Auction**    | `modules/auction.py`    | Contract Net Protocol for task allocation          |
| **Reasoning**  | `modules/reasoning.py`  | Knowledge-based rules for bin classification       |
| **Prediction** | `modules/prediction.py` | ETA computation and overflow forecasting           |
| **Simulation** | `modules/simulation.py` | City grid, bins, trucks, and event simulation      |
| **KPI**        | `modules/kpi.py`        | Performance tracking and baseline comparison       |

---

## 🚛 Driver Mobile View

To simulate the end-user experience, a dedicated **Driver View** tab is available. This interface mimics a mobile app used by truck drivers, displaying:
*   **Assigned Route List**: Cards for each bin assignment with real-time status (Pending/Collected).
*   **Live Telemetry**: Real-time GPS position, current load status, and 'Next Stop ETA'.
*   **Agent Controls**: Drivers can interact with the simulation (Next Step/Reset) directly from their dashboard.

---

## 🧠 AI Components

### 1. A\* Pathfinding Algorithm

The routing engine uses A\* search with a **multi-objective cost function**:

$$
\text{ETA}(b) = \frac{100 - \text{fill\_level}}{\text{fill\_rate}} \times \text{minutes\_per\_step}
$$

| Weight    | Parameter     | Description                                    |
| --------- | ------------- | ---------------------------------------------- |
| α (Alpha) | Distance      | Physical travel distance penalty               |
| β (Beta)  | Overflow Risk | Penalty for leaving high-risk bins uncollected |
| γ (Gamma) | SLA           | Penalty for missing service deadlines          |

**Heuristic:** Manhattan Distance — admissible for grid-based maps.

### 2. Auction-Based Task Allocation

Uses **Contract Net Protocol** for distributed decision-making:
1. Bins announce collection tasks.
2. Trucks compute **marginal cost bids** based on route insertion.
3. Lowest bidder wins the task.

### 3. Knowledge-Based Reasoning

Production rules encode domain knowledge:
```
Full(b)     ← fill_level(b) ≥ 80%
Urgent(b)   ← ETA(b) ≤ 120 minutes
Eligible(b) ← (Full(b) ∨ Urgent(b)) ∧ ¬Collected(b)
```

Bins are classified as:
- 🟢 **GREEN** — Eligible for service
- 🟠 **ORANGE** — Urgent but blocked (capacity/constraints)
- ⚫ **GREY** — Not relevant for current cycle

---

## 🔄 Simulation Loop

The agent follows a 6-step cognitive cycle:

| Step | Phase              | Description                                              |
| ---- | ------------------ | -------------------------------------------------------- |
| 1    | **Sense**          | Scan IoT sensors for bin fill levels and truck positions |
| 2    | **Predict**        | Identify bins at risk of overflow within 120 minutes     |
| 3    | **Reason**         | Apply KR rules to classify all bins (GREEN/ORANGE/GREY)  |
| 4    | **Allocate**       | Run auction protocol to assign bins to trucks            |
| 5    | **Plan & Execute** | Compute A\* routes and execute collection. **Displays AI vs Baseline Performance Dashboard.** |
| 6    | **Adapt**          | Handle dynamic events. **Generates Cycle Summary Report.** |

---

## Configuration

Use the sidebar to configure simulation parameters:

### General Parameters
| Parameter        | Default | Description                      |
| ---------------- | ------- | -------------------------------- |
| Grid Size        | 10      | City grid dimensions (N×N)       |
| Sensor Nodes     | 15      | Smart bins in the city           |
| Fleet Size       | 3       | Number of garbage trucks         |

### AI Hyperparameters
| Parameter | Default | Description                      |
| --------- | ------- | -------------------------------- |
| α (Alpha) | 1.0     | Distance weight in cost function |
| β (Beta)  | 0.3     | Overflow risk weight             |
| γ (Gamma) | 0.5     | SLA penalty weight               |

---

## 📊 Key Performance Indicators

The system tracks:
- **Overflow Count** — Bins reaching 100% capacity
- **Total Distance** — Cumulative travel distance
- **AI vs Baseline** — Comparison proving efficiency gains over naive routing
- **Route Computation Time** — A\* algorithm performance

---

## 🛠️ Technologies
- **[Streamlit](https://streamlit.io/)** — Interactive web application framework
- **[NetworkX](https://networkx.org/)** — Graph algorithms and road network modeling
- **[Plotly](https://plotly.com/)** — Interactive data visualizations
- **[NumPy](https://numpy.org/)** — Numerical computations
