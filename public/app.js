// DOM Elements
const form = document.getElementById("chat-form");
const input = document.getElementById("input");
const messages = document.getElementById("messages");
const settingsPanel = document.getElementById("settings-panel");
const simulationPanel = document.getElementById("simulation-panel");
const settingsToggle = document.getElementById("settings-toggle");
const simulationToggle = document.getElementById("simulation-toggle");
const saveSettings = document.getElementById("save-settings");
const pauseSimBtn = document.getElementById("pause-sim");
const resetSimBtn = document.getElementById("reset-sim");
const simulationStatus = document.querySelector(".simulation-status");
const simTime = document.getElementById("sim-time");
const authContainer = document.getElementById("auth-container");
const mainContainer = document.getElementById("main-container");
const pinInput = document.getElementById("pin-input");
const loginButton = document.getElementById("login-button");

// State variables
let history = [];
let simulationActive = true;
let simulationStartTime = new Date();
let simulationTimer;
let authenticated = false;
let settings = {
  provider: "simulator",
  model: "llama2",
  learningMode: true,
  memoryRetention: 75,
  personality: "balanced",
  apiKey: "",
  debugMode: false
};

// Initialize the application
function initApp() {
  // Check if user is already authenticated
  const isAuth = localStorage.getItem("authenticated");
  if (isAuth === "true") {
    authenticateUser();
  }

  // Load settings from localStorage if available
  const savedSettings = localStorage.getItem("simulatorSettings");
  if (savedSettings) {
    try {
      settings = JSON.parse(savedSettings);
      updateSettingsUI();
    } catch (e) {
      console.error("Error loading settings:", e);
    }
  }
}

// Authenticate user function
function authenticateUser() {
  authenticated = true;
  localStorage.setItem("authenticated", "true");

  // Hide auth container and show main container
  authContainer.style.opacity = "0";
  setTimeout(() => {
    authContainer.classList.add("hidden");
    mainContainer.classList.remove("hidden");

    // Add zoom effect
    document.body.classList.add("zoomed-in");

    setTimeout(() => {
      mainContainer.classList.add("visible");

      // Start the simulation timer
      startSimulationTimer();

      // Add a welcome message
      append("Welcome to Human Simulator! How can I help you today?", "bot");
    }, 100);
  }, 800);
}

// Update the settings UI based on current settings
function updateSettingsUI() {
  document.getElementById("llm-provider").value = settings.provider;
  document.getElementById("llm-model").value = settings.model;
  document.getElementById("learning-mode").checked = settings.learningMode;
  document.getElementById("memory-retention").value = settings.memoryRetention;
  document.getElementById("personality-preset").value = settings.personality;
  document.getElementById("api-key").value = settings.apiKey;
  document.getElementById("debug-mode").checked = settings.debugMode;
}

// Save settings from UI to state and localStorage
function saveSettingsFromUI() {
  settings.provider = document.getElementById("llm-provider").value;
  settings.model = document.getElementById("llm-model").value;
  settings.learningMode = document.getElementById("learning-mode").checked;
  settings.memoryRetention = document.getElementById("memory-retention").value;
  settings.personality = document.getElementById("personality-preset").value;
  settings.apiKey = document.getElementById("api-key").value;
  settings.debugMode = document.getElementById("debug-mode").checked;

  localStorage.setItem("simulatorSettings", JSON.stringify(settings));

  // Show a confirmation message
  append("Settings updated successfully.", "bot");
}

// Start the simulation timer
function startSimulationTimer() {
  simulationStartTime = new Date();
  simulationTimer = setInterval(updateSimulationTime, 1000);
  simulationActive = true;
  simulationStatus.textContent = "Active";
  simulationStatus.className = "simulation-status active";
}

// Update the simulation time display
function updateSimulationTime() {
  if (!simulationActive) return;

  const now = new Date();
  const diff = now - simulationStartTime;
  const hours = Math.floor(diff / 3600000).toString().padStart(2, '0');
  const minutes = Math.floor((diff % 3600000) / 60000).toString().padStart(2, '0');
  const seconds = Math.floor((diff % 60000) / 1000).toString().padStart(2, '0');

  simTime.textContent = `${hours}:${minutes}:${seconds}`;
}

// Toggle the simulation pause state
function toggleSimulationPause() {
  if (simulationActive) {
    clearInterval(simulationTimer);
    simulationActive = false;
    simulationStatus.textContent = "Paused";
    simulationStatus.className = "simulation-status paused";
    pauseSimBtn.innerHTML = `
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polygon points="5 3 19 12 5 21 5 3"></polygon>
      </svg>
    `;
    pauseSimBtn.title = "Resume Simulation";
  } else {
    simulationTimer = setInterval(updateSimulationTime, 1000);
    simulationActive = true;
    simulationStatus.textContent = "Active";
    simulationStatus.className = "simulation-status active";
    pauseSimBtn.innerHTML = `
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <rect x="6" y="5" width="4" height="14"></rect>
        <rect x="14" y="5" width="4" height="14"></rect>
      </svg>
    `;
    pauseSimBtn.title = "Pause Simulation";
  }
}

// Reset the simulation
function resetSimulation() {
  clearInterval(simulationTimer);
  history = [];
  messages.innerHTML = '';
  append("Simulation reset. Starting new session.", "bot");
  startSimulationTimer();
}

// Append a message to the chat
function append(text, cls) {
  const div = document.createElement("div");
  div.className = `message ${cls}`;

  // Create a text container for better styling
  const textSpan = document.createElement("span");
  textSpan.className = "message-text";
  textSpan.textContent = text;

  div.appendChild(textSpan);
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

// Event Listeners
window.addEventListener('DOMContentLoaded', initApp);

// Handle login button click
loginButton.addEventListener("click", () => {
  const pin = pinInput.value;
  // Default PIN is 00000
  if (pin === "00000" || pin === "") {
    authenticateUser();
  } else {
    // Show error for wrong PIN
    pinInput.classList.add("error");
    setTimeout(() => pinInput.classList.remove("error"), 1000);
  }
});

// Handle PIN input enter key
pinInput.addEventListener("keyup", (e) => {
  if (e.key === "Enter") {
    loginButton.click();
  }
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  append(text, "user");
  input.value = "";

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: text,
        history,
        settings: settings
      })
    });

    if (!res.ok) {
      throw new Error(`Server responded with status: ${res.status}`);
    }

    const data = await res.json();
    append(data.reply, "bot");
    history.push(`User: ${text}`);
    history.push(`Assistant: ${data.reply}`);
  } catch (error) {
    console.error("Error communicating with the server:", error);
    append("Sorry, there was an error communicating with the server. Please try again later.", "bot");
  }
});

// Toggle settings panel visibility
settingsToggle.addEventListener("click", () => {
  // If simulation panel is visible, hide it first
  if (simulationPanel.classList.contains("visible")) {
    simulationPanel.classList.remove("visible");
  }
  settingsPanel.classList.toggle("visible");
});

// Toggle simulation panel visibility
simulationToggle.addEventListener("click", () => {
  // If settings panel is visible, hide it first
  if (settingsPanel.classList.contains("visible")) {
    settingsPanel.classList.remove("visible");
  }
  simulationPanel.classList.toggle("visible");

  // Update simulation time when panel is opened
  if (simulationPanel.classList.contains("visible")) {
    updateSimulationTime();
  }
});

// Save settings
saveSettings.addEventListener("click", () => {
  saveSettingsFromUI();
  settingsPanel.classList.remove("visible");
});

// Pause/resume simulation
pauseSimBtn.addEventListener("click", toggleSimulationPause);

// Reset simulation
resetSimBtn.addEventListener("click", resetSimulation);

// Close panels when clicking outside
document.addEventListener("click", (e) => {
  if (!settingsPanel.contains(e.target) &&
    !settingsToggle.contains(e.target) &&
    !simulationPanel.contains(e.target) &&
    !simulationToggle.contains(e.target)) {
    settingsPanel.classList.remove("visible");
    simulationPanel.classList.remove("visible");
  }
});

// Add logout functionality
function logout() {
  localStorage.removeItem("authenticated");
  document.body.classList.remove("zoomed-in");
  mainContainer.classList.remove("visible");

  setTimeout(() => {
    mainContainer.classList.add("hidden");
    authContainer.classList.remove("hidden");
    authContainer.style.opacity = "1";
    pinInput.value = "";

    // Clear chat history
    history = [];
    messages.innerHTML = '';

    // Stop simulation timer
    if (simulationTimer) {
      clearInterval(simulationTimer);
    }
  }, 800);
}