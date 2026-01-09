// AI Task Automation System - Frontend JavaScript
let socket;
let currentState = null;
let currentMetrics = null;
let isAutoRunning = false;

document.addEventListener("DOMContentLoaded", () => {
    console.log("AI Task Automation System initializing...");
    initializeSocket();
    loadInitialState();
    setupNavigation();
    setupControls();
});

function initializeSocket() {
    console.log("Initializing Socket.IO connection...");
    
    // Connect to Socket.IO server
    socket = io();
    
    socket.on('connect', () => {
        console.log('Successfully connected to Socket.IO server');
    });
    
    socket.on('disconnect', () => {
        console.log('Disconnected from Socket.IO server');
    });
    
    socket.on('connected', (data) => {
        console.log('Server connection confirmed:', data);
    });
    
    socket.on('state_update', (data) => {
        console.log('Received real-time state update:', data);
        currentState = data.state;
        currentMetrics = data.metrics;
        
        // Update system overview if provided
        if (data.system_overview) {
            currentState.system_overview = data.system_overview;
        }
        
        updateUI();
    });
    
    socket.on('error', (error) => {
        console.error('Socket.IO error:', error);
    });
}

async function loadInitialState() {
    console.log("Loading initial system state...");
    try {
        const res = await fetch("/api/state");
        const data = await res.json();
        console.log("Initial state loaded:", data);
        
        currentState = data.state;
        currentMetrics = data.metrics;
        isAutoRunning = data.is_running;
        
        // Initialize system overview
        if (data.system_overview) {
            currentState.system_overview = data.system_overview;
        } else {
            // Calculate initial system overview
            currentState.system_overview = {
                active_tasks: currentState.tasks.filter(t => t.status === "in-progress").length,
                available_workers: currentState.workers.filter(w => w.status === "available").length,
                healthy_machines: currentState.machines.filter(m => m.status === "normal").length,
                critical_alerts: currentState.alerts.filter(a => a.severity === "high" && !a.resolved).length
            };
        }
        
        updateUI();
        updateAutoRunButton();
        
    } catch (error) {
        console.error("Failed to load initial state:", error);
        // Try to reconnect Socket.IO
        setTimeout(initializeSocket, 2000);
    }
}

function setupNavigation() {
    document.querySelectorAll(".nav-item").forEach(btn => {
        btn.addEventListener("click", () => {
            document.querySelectorAll(".nav-item").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            document.querySelectorAll(".page-content").forEach(p => p.classList.remove("active"));
            document.getElementById(`page-${btn.dataset.page}`).classList.add("active");
        });
    });
}

function setupControls() {
    const stepBtn = document.getElementById("btn-step");
    const autoRunBtn = document.getElementById("btn-auto-run");
    const resetBtn = document.getElementById("btn-reset");
    
    if (stepBtn) stepBtn.addEventListener("click", step);
    if (autoRunBtn) autoRunBtn.addEventListener("click", toggleAuto);
    if (resetBtn) resetBtn.addEventListener("click", reset);
}

async function step() {
    console.log("Executing manual step...");
    
    try {
        const res = await fetch("/api/step", { 
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            }
        });
        const data = await res.json();
        console.log("Step executed:", data);
        
        // Update local state with response
        currentState = data.state;
        currentMetrics = data.metrics;
        if (data.system_overview) {
            currentState.system_overview = data.system_overview;
        }
        
        updateUI();
    } catch (error) {
        console.error("Failed to execute step:", error);
    }
}

async function toggleAuto() {
    console.log("Toggling auto-run...");
    try {
        const res = await fetch("/api/toggle-auto-run", { 
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            }
        });
        const data = await res.json();
        console.log("Auto-run toggled:", data);
        
        isAutoRunning = data.is_running;
        updateAutoRunButton();
    } catch (error) {
        console.error("Failed to toggle auto-run:", error);
    }
}

function updateAutoRunButton() {
    const btn = document.getElementById("btn-auto-run");
    if (btn) {
        if (isAutoRunning) {
            btn.textContent = "Stop Auto Run";
            btn.className = "btn btn-warning";
            btn.innerHTML = "⏸ Pause";
        } else {
            btn.textContent = "Start Auto Run";
            btn.className = "btn btn-secondary";
            btn.innerHTML = "▷ Run AI";
        }
        console.log(`↺ Auto-run button updated: ${btn.textContent}`);
    }
}

async function reset() {
    console.log("↺ Resetting system...");
    try {
        const res = await fetch("/api/reset", { 
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            }
        });
        const data = await res.json();
        console.log("System reset:", data);
        
        currentState = data.state;
        currentMetrics = data.metrics;
        isAutoRunning = data.is_running;
        
        if (data.system_overview) {
            currentState.system_overview = data.system_overview;
        }
        
        updateUI();
        updateAutoRunButton();
        
    } catch (error) {
        console.error("Failed to reset system:", error);
    }
}

function updateUI() {
    console.log("Updating UI with current state...");
    console.log("Current state:", currentState);
    
    if (!currentState) {
        console.error("No current state available");
        return;
    }

    // Update System Overview
    updateSystemOverview();
    
    // Update Performance Metrics
    updateMetrics();
    
    // Update step counter
    updateStepCounter();
    
    // Render all components
    renderTasks();
    renderWorkers();
    renderMachines();
    renderResources();
    renderAlerts();
    renderLog();
}

function updateSystemOverview() {
    console.log("Updating system overview...");
    
    // Calculate if not provided
    if (!currentState.system_overview) {
        currentState.system_overview = {
            active_tasks: currentState.tasks.filter(t => t.status === "in-progress").length,
            available_workers: currentState.workers.filter(w => w.status === "available").length,
            healthy_machines: currentState.machines.filter(m => m.status === "normal").length,
            critical_alerts: currentState.alerts.filter(a => a.severity === "high" && !a.resolved).length
        };
    }
    
    console.log("System overview:", currentState.system_overview);
    
    // Update DOM elements
    const activeTasksEl = document.getElementById("active-tasks");
    const availableWorkersEl = document.getElementById("available-workers");
    const healthyMachinesEl = document.getElementById("healthy-machines");
    const criticalAlertsEl = document.getElementById("critical-alerts");
    
    if (activeTasksEl) {
        activeTasksEl.textContent = currentState.system_overview.active_tasks;
        console.log(`Active tasks: ${currentState.system_overview.active_tasks}`);
    }
    if (availableWorkersEl) {
        availableWorkersEl.textContent = currentState.system_overview.available_workers;
        console.log(`Available workers: ${currentState.system_overview.available_workers}`);
    }
    if (healthyMachinesEl) {
        healthyMachinesEl.textContent = currentState.system_overview.healthy_machines;
        console.log(`Healthy machines: ${currentState.system_overview.healthy_machines}`);
    }
    if (criticalAlertsEl) {
        criticalAlertsEl.textContent = currentState.system_overview.critical_alerts;
        console.log(`Critical alerts: ${currentState.system_overview.critical_alerts}`);
    }
}

function updateMetrics() {
    if (!currentMetrics) {
        console.warn("No metrics available");
        return;
    }

    console.log("Updating performance metrics:", currentMetrics);

    const taskTimeEl = document.getElementById("metric-task-time");
    const errorRateEl = document.getElementById("metric-error-rate");
    const downtimeEl = document.getElementById("metric-downtime");
    const efficiencyEl = document.getElementById("metric-efficiency");
    
    if (taskTimeEl) taskTimeEl.textContent = currentMetrics.avg_task_completion_time?.toFixed(1) || "0.0";
    if (errorRateEl) errorRateEl.textContent = Math.round(currentMetrics.error_reduction_rate) || "0";
    if (downtimeEl) downtimeEl.textContent = Math.round(currentMetrics.downtime_avoided) || "0";
    if (efficiencyEl) efficiencyEl.textContent = Math.round(currentMetrics.resource_efficiency) || "0";
}

function updateStepCounter() {
    const stepEl = document.getElementById("current-step");
    if (stepEl) {
        stepEl.textContent = currentState.current_step || 0;
        console.log(`Current step: ${currentState.current_step}`);
    }
}

function renderTasks() {
    const container = document.getElementById("tasks-container");
    const progressBar = document.getElementById("tasks-progress-bar");

    if (!container) {
        console.warn("Tasks container not found");
        return;
    }

    const completed = currentState.tasks.filter((t) => t.status === "completed").length;
    const inProgress = currentState.tasks.filter((t) => t.status === "in-progress").length;
    const pending = currentState.tasks.filter((t) => t.status === "pending").length;
    const total = currentState.tasks.length;
    const percentage = total > 0 ? (completed / total) * 100 : 0;

    console.log(`Tasks: ${completed} completed, ${inProgress} in-progress, ${pending} pending`);

    if (progressBar) {
        progressBar.innerHTML = `<div class="progress-fill" style="width: ${percentage}%"></div>`;
    }

    // Update task counts in the header
    const tasksHeader = document.querySelector('#page-tasks h2');
    if (tasksHeader) {
        tasksHeader.innerHTML = `
            Tasks Progress
            <div style="font-size: 0.8rem; color: var(--muted-foreground); margin-top: 5px;">
                Total Tasks: ${total} | Pending: ${pending} | In Progress: ${inProgress} | Completed: ${completed}
            </div>
        `;
    }

    // Render task cards
    container.innerHTML = currentState.tasks
        .map((task) => {
            const statusText = task.status === "in-progress" ? "In Progress" : 
                             task.status === "completed" ? "Completed" : "Pending";
            const statusClass = task.status === "in-progress" ? "in-progress" : 
                              task.status === "completed" ? "completed" : "pending";
            
            // Get worker name if assigned
            let assignedWorkerName = "";
            if (task.assigned_to) {
                const worker = currentState.workers.find(w => w.id === task.assigned_to);
                assignedWorkerName = worker ? worker.name : task.assigned_to;
            }
            
            return `
            <div class="task-card ${statusClass}">
                <div class="task-header">
                    <span class="task-name">${task.name}</span>
                    <span class="task-status ${statusClass}">${statusText}</span>
                </div>
                <div class="task-details">
                    <div>Priority: <strong>${task.priority}</strong></div>
                    ${assignedWorkerName ? `<div>Assigned to: <strong>${assignedWorkerName}</strong></div>` : ""}
                    ${task.completed_at ? `<div>Completed: <strong>${new Date(task.completed_at).toLocaleTimeString()}</strong></div>` : ""}
                </div>
            </div>
            `;
        })
        .join("");
}

function renderWorkers() {
    const container = document.getElementById("workers-container");
    if (!container) {
        console.warn("Workers container not found");
        return;
    }

    const available = currentState.workers.filter(w => w.status === "available").length;
    const busy = currentState.workers.filter(w => w.status === "busy").length;
    
    console.log(`Workers: ${available} available, ${busy} busy`);

    // Update workers header
    const workersHeader = document.querySelector('#page-operations .section-card:first-child h2');
    if (workersHeader) {
        workersHeader.innerHTML = `
            Available Workers
            <div style="font-size: 0.8rem; color: var(--muted-foreground); margin-top: 5px;">
                Total: ${currentState.workers.length} | Available: ${available} | Busy: ${busy}
            </div>
        `;
    }

    container.innerHTML = currentState.workers
        .map((worker) => {
            const statusText = worker.status === "busy" ? "Busy" : "Available";
            const statusClass = worker.status === "busy" ? "busy" : "available";
            
            // Get task name if assigned
            let currentTaskName = "";
            if (worker.current_task) {
                const task = currentState.tasks.find(t => t.id === worker.current_task);
                currentTaskName = task ? task.name : worker.current_task;
            }
            
            return `
            <div class="worker-card">
                <div class="worker-header">
                    <span class="worker-name">${worker.name}</span>
                    <span class="status-badge ${statusClass}">${statusText}</span>
                </div>
                <div class="worker-details">
                    <div>Skill: <strong>${worker.skill_type}</strong></div>
                    ${currentTaskName ? `<div>Current Task: <strong>${currentTaskName}</strong></div>` : ""}
                </div>
            </div>
            `;
        })
        .join("");
}

function renderMachines() {
    const container = document.getElementById("machines-container");
    if (!container) {
        console.warn("Machines container not found");
        return;
    }

    const normalMachines = currentState.machines.filter(m => m.status === "normal").length;
    const warningMachines = currentState.machines.filter(m => m.status === "warning").length;
    const criticalMachines = currentState.machines.filter(m => m.status === "critical").length;
    
    console.log(`Machines: ${normalMachines} normal, ${warningMachines} warning, ${criticalMachines} critical`);

    // Update machines header
    const machinesHeader = document.querySelector('#page-operations .section-card:last-child h2');
    if (machinesHeader) {
        machinesHeader.innerHTML = `
            Machine Conditions
            <div style="font-size: 0.8rem; color: var(--muted-foreground); margin-top: 5px;">
                Total: ${currentState.machines.length} | Normal: ${normalMachines} | Warning: ${warningMachines} | Critical: ${criticalMachines}
            </div>
        `;
    }

    container.innerHTML = currentState.machines
        .map((machine) => {
            const tempPercentage = Math.min((machine.temperature / 100) * 100, 100);
            const vibrationPercentage = Math.min((machine.vibration / 2) * 100, 100);
            
            return `
            <div class="machine-card">
                <div class="machine-header">
                    <span class="machine-name">${machine.name}</span>
                    <span class="status-badge ${machine.status}">${machine.status}</span>
                </div>
                <div class="machine-details">
                    <div class="machine-progress">
                        <span>Temperature: ${machine.temperature?.toFixed(1) || "0.0"}°C</span>
                        <div class="progress-bar-small">
                            <div class="progress-fill" style="width: ${tempPercentage}%"></div>
                        </div>
                    </div>
                    <div class="machine-progress">
                        <span>Vibration: ${machine.vibration?.toFixed(2) || "0.00"}</span>
                        <div class="progress-bar-small">
                            <div class="progress-fill" style="width: ${vibrationPercentage}%"></div>
                        </div>
                    </div>
                </div>
            </div>
            `;
        })
        .join("");
}

function renderResources() {
    const container = document.getElementById("resources-container");
    if (!container) {
        console.warn("Resources container not found");
        return;
    }

    const optimizedCount = currentState.resources.filter(r => r.is_optimized).length;
    
    console.log(`Resources: ${optimizedCount} optimized out of ${currentState.resources.length}`);

    container.innerHTML = currentState.resources
        .map((resource) => `
            <div class="resource-card">
                <div class="resource-header">
                    <span>${resource.name}</span>
                    <span>${resource.is_optimized ? "✓ Optimized" : "⚠ Not Optimized"}</span>
                </div>
                <div class="resource-bar">
                    <div class="resource-bar-fill" style="width: ${resource.current_usage || 0}%"></div>
                </div>
                <div style="margin-top: 0.5rem; font-size: 0.875rem; color: var(--muted-foreground);">
                    Current: ${resource.current_usage?.toFixed(0) || "0"}% | Optimal: ${resource.optimal_usage?.toFixed(0) || "0"}%
                </div>
            </div>
        `)
        .join("");
}

function renderAlerts() {
    const container = document.getElementById("alerts-container");
    if (!container) {
        console.warn("Alerts container not found");
        return;
    }

    const activeAlerts = currentState.alerts.filter(alert => !alert.resolved);
    const criticalAlerts = activeAlerts.filter(alert => alert.severity === "high");
    const warningAlerts = activeAlerts.filter(alert => alert.severity === "medium");
    const systemAlerts = activeAlerts.filter(alert => alert.type === "system");
    
    console.log(`Alerts: ${activeAlerts.length} active, ${criticalAlerts.length} critical, ${warningAlerts.length} warning`);

    // Update alerts header
    const alertsHeader = document.querySelector('#page-resources .section-card:last-child h2');
    if (alertsHeader) {
        alertsHeader.innerHTML = `
            Alert Triggers
            <div style="font-size: 0.8rem; color: var(--muted-foreground); margin-top: 5px;">
                System Alerts: ${systemAlerts.length} | Active: ${activeAlerts.length} | Critical: ${criticalAlerts.length} | Warning: ${warningAlerts.length}
            </div>
        `;
    }

    if (activeAlerts.length === 0) {
        container.innerHTML =
            '<div style="color: var(--muted-foreground); text-align: center; padding: 2rem;"> ⚠️ No active alerts</div>';
        return;
    }

    container.innerHTML = activeAlerts
        .map((alert) => `
            <div class="alert-item ${alert.severity}">
                <div style="font-weight: 600; margin-bottom: 0.25rem;">${alert.message}</div>
                <div style="font-size: 0.75rem; color: var(--muted-foreground);">
                    ${alert.type?.toUpperCase() || "SYSTEM"} • ${alert.severity || "MEDIUM"} • ${new Date(alert.timestamp).toLocaleTimeString()}
                </div>
            </div>
        `)
        .join("");
}

function renderLog() {
    const container = document.getElementById("action-log");
    if (!container) {
        console.warn("Action log container not found");
        return;
    }

    const recentActions = currentState.action_history ? 
                         [...currentState.action_history].reverse().slice(0, 10) : [];

    console.log(`Action log: ${recentActions.length} recent actions`);

    if (recentActions.length === 0) {
        container.innerHTML =
            '<div style="color: var(--muted-foreground); text-align: center; padding: 2rem;">📋 No actions recorded yet</div>';
        return;
    }

    container.innerHTML = recentActions
        .map((action) => {
            const time = action.timestamp ? new Date(action.timestamp).toLocaleTimeString() : "N/A";
            return `
            <div class="action-item">
                <strong>Step ${action.step || "0"}:</strong> ${action.details || action.message || "No details"}
                <span style="color: var(--muted-foreground); font-size: 0.75rem; margin-left: auto;">${time}</span>
            </div>
            `;
        })
        .join("");
}

// Add heartbeat to keep connection alive
setInterval(() => {
    if (socket && socket.connected) {
        socket.emit('heartbeat', { timestamp: Date.now() });
    }
}, 30000);
