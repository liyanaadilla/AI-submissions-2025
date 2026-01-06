# YSMAI HVAC Monitoring System - Backend

## Overview

Real-time HVAC monitoring system with temperature simulation, state management, scheduling, and fault injection. This is the backend Python API that provides core simulation logic.

**Status:** ✅ Complete - Ready for frontend integration

---

## Quick Start

### Installation & Running

```bash
# No external dependencies required
python3 main.py
```

### Basic Usage

```python
from controller import SimulationController

ctrl = SimulationController(
    initial_temp=60,
    warmup_duration=5,
    drift_rate=0.5,
    threshold_high=85,
    threshold_low=50,
    debounce_sec=1.5,
)

# Run simulation
for i in range(100):
    result = ctrl.tick()
    print(f"Temp: {result['temperature']}°F, State: {result['state']}")
    if result['state_changed']:
        print(f"  ALERT: {result['alert_message']}")
```

---

## Files & Components

### Core Modules
- **`controller.py`** - Main API (SimulationController class)
- **`simulator.py`** - Temperature simulation with warmup, drift, faults
- **`agent.py`** - 3-state FSM with debounce logic
- **`scheduler.py`** - Min-heap task scheduler for persistence

### Testing
- **`test_unit.py`** - 19 unit tests (all passing)
- **`test_integration.py`** - 4 integration tests (all passing)

### Documentation & Examples
- **`API_CONTRACT.txt`** - Frozen API specification
- **`API_EXAMPLES.txt`** - 9 detailed usage examples
- **`sample_traces.json`** - 3 reference scenarios

### Generated Data
- **`generate_samples.py`** - Sample data generator
- **`samples/`** - Generated JSON sample files

---

## Testing

```bash
# Unit tests (19 tests)
python3 -m unittest test_unit -v

# Integration tests (4 tests)
python3 -m unittest test_integration -v

# Generate sample data
python3 generate_samples.py
```

---

## API Response Format

Each `tick()` returns:

```python
{
  "timestamp": float,           # Unix timestamp
  "temperature": float,         # °F (50-120)
  "state": str,                 # NORMAL|ALERT_HIGH|ALERT_LOW
  "state_changed": bool,        # True if state transitioned
  "alert_message": str|null,    # Alert text or None
  "scheduled_tasks": list,      # Due persistence tasks
  "simulation_time": float,     # Elapsed seconds
  "tick_count": int,            # Total ticks
}
```

---

## Key Features

✅ **3-State FSM** - NORMAL, ALERT_HIGH, ALERT_LOW with debounce
✅ **Temperature Simulation** - Warmup phase, drift, optional faults
✅ **Task Scheduling** - Auto-scheduled persistence tasks every 5s
✅ **JSON API** - Ready for frontend/Streamlit integration
✅ **23 Tests Passing** - Unit & integration test coverage
✅ **Zero Dependencies** - Python stdlib only
✅ **Frozen API Contract** - Stable, no breaking changes

---

## Default Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| `threshold_high` | 85°F | High alert threshold |
| `threshold_low` | 50°F | Low alert threshold |
| `debounce_sec` | 1.5s | State transition debounce |
| `drift_rate` | 0.5°F/s | Temperature drift rate |
| `warmup_duration` | 5.0s | Warmup phase duration |
| `update_interval` | 0.5s | Time between ticks |

---

## Architecture

```
SimulationController (Main API)
├── TemperatureSimulator (warmup, drift, faults)
├── YSMAI_Agent (3-state FSM, debounce)
└── Scheduler (min-heap task queue)
```

Data flow: Simulator → Agent → Scheduler → JSON response

---

## Documentation

- **[API_CONTRACT.txt](API_CONTRACT.txt)** - Complete API specification
- **[API_EXAMPLES.txt](API_EXAMPLES.txt)** - 9 usage examples
- **[sample_traces.json](sample_traces.json)** - 3 test scenarios

---

## Performance

- **tick() latency**: <5ms (Python, stdlib)
- **Response size**: 500-1000 bytes (JSON)
- **Memory**: <10MB per 1000 ticks
- **Stability**: 5+ minute runs without crashes

---

## Integration Ready

✅ JSON serialization for API consumers
✅ Fault injection testing support
✅ Persistence task auto-scheduling
✅ State transition logging
✅ Compatible with Streamlit frontend

See [API_EXAMPLES.txt](API_EXAMPLES.txt) for Streamlit integration pattern.

---

## Requirements

- Python 3.8+
- Standard library only: `json`, `time`, `heapq`, `random`
- No external packages needed

See `requirements.txt` for reference.

---

## Status

**Backend Component:** ✅ Complete
- Core modules: ✅ Ready
- Tests: ✅ 23/23 passing
- API Contract: ✅ Frozen
- Documentation: ✅ Complete
- Sample Data: ✅ Generated

**Ready for:** Frontend integration (Streamlit) with Nafis

---

## Author

Khubaib - Backend & Logic Owner
YSMAI Project - January 2026
