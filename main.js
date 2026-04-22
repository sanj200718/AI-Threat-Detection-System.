function hideAll() {
  document.querySelectorAll('.section').forEach(s => s.classList.add('hidden'));
}

function showPage(pageId) {
  hideAll();
  const target = document.getElementById(pageId);
  if (target) target.classList.remove('hidden');
}

// Navigation Helpers
function showDashboard() { showPage('dashboard'); }
function showUpload() { showPage('upload'); }
function showAbout() { showPage('about'); }
function showThreatTypes() { showPage('threatTypes'); }
function showSignup() { showPage('signup'); }
function showLogin() { showPage('login'); }

// Dynamic Navigation
function showProfile() {
  loadUserProfile(); 
  showPage('profile');
}

function showHistory() {
  loadHistory();
  showPage('history');
}

// -------------------------------
// USER PROFILE LOGIC
function loadUserProfile() {
  // Pull the username saved during signup
  const savedUser = localStorage.getItem('activeUser') || "GuestAnalyst";
  const userElement = document.getElementById('display-username');
  if (userElement) {
    userElement.textContent = `@${savedUser}`;
  }
}

function completeSignup() {
  const user = document.getElementById('signup-user').value.trim();
  if(!user) return alert("Please enter a username");
  
  // Save for the profile page
  localStorage.setItem('activeUser', user);
  alert('Account created! Login to continue.');
  showLogin();
}

// -------------------------------
// 🔥 MAIN SCAN FUNCTION
// -------------------------------
async function startScan() {
  const fileInput = document.getElementById('file');
  if (fileInput.files.length === 0) {
    alert('Please select a file');
    return;
  }

  showPage('scanning');
  const formData = new FormData();
  formData.append('file', fileInput.files[0]);

  try {
    const response = await fetch('http://localhost:5000/api/upload', {
      method: 'POST',
      body: formData
    });

    const result = await response.json();
    const levelEl = document.getElementById('threat-level');
    const messageEl = document.getElementById('result-message');

    // 1. Set Status & Color
    if (result.status === "THREAT") {
      levelEl.textContent = "THREAT: " + result.severity;
      levelEl.className = "threat-level threat-high";
      messageEl.innerHTML = `<span style="color: #ff4d4d; font-weight: bold;">Security Risk Detected.</span>`;
    } else if (result.status === "SPAM") {
      levelEl.textContent = "SPAM";
      levelEl.className = "threat-level threat-medium";
      messageEl.innerHTML = `<span style="color: #ffa500; font-weight: bold;">⚠️ Suspicious Content.</span>`;
    } else {
      levelEl.textContent = "SECURE";
      levelEl.className = "threat-level secure";
      messageEl.innerHTML = `<span style="color: #2ecc71; font-weight: bold;">✅ File is Safe.</span>`;
    }

    // 2. Detailed Analysis
    let analysisHTML = `<div class="analysis-box" style="margin-top: 15px; text-align: left; padding: 12px; background: rgba(255,255,255,0.05); border-radius: 8px;">`;
    analysisHTML += `<p><strong>Confidence:</strong> ${result.confidence}%</p>`;
    analysisHTML += `<p><strong>Reason:</strong> <em>${result.reason}</em></p>`;
    
    if (result.findings && result.findings.length > 0) {
      analysisHTML += `<p><strong>Patterns:</strong> ${result.findings.join(", ")}</p>`;
    }
    
    analysisHTML += `<button onclick="showUpload()" style="margin-top:15px; width:100%;">Upload Another File</button>`;
    analysisHTML += `</div>`;

    messageEl.innerHTML += analysisHTML;
    showPage('result');

  } catch (error) {
    console.error("Error:", error);
    alert("Connection failed!");
    showDashboard();
  }
}

// -------------------------------
// HISTORY MANAGEMENT
// -------------------------------
async function loadHistory() {
  const list = document.getElementById('history-list');
  list.innerHTML = '<p>Loading logs...</p>';

  try {
    const response = await fetch('http://localhost:5000/api/results');
    const results = await response.json();
    list.innerHTML = ''; 

    if (results.length === 0) {
      list.innerHTML = '<p>No scan history available.</p>';
      return;
    }

    // Latest on top
    results.reverse().forEach(r => {
      const color = r.threat ? '#ff4d4d' : '#2ecc71';
      list.innerHTML += `
        <div class="box glass" style="border-left: 4px solid ${color}; margin-bottom: 10px; padding: 10px; text-align: left;">
          <div style="display: flex; justify-content: space-between;">
            <strong>${r.filename}</strong>
            <span style="color: ${color}">${r.threat ? 'THREAT' : 'SECURE'}</span>
          </div>
          <small>Severity: ${r.severity}</small>
        </div>
      `;
    });
  } catch (error) {
    list.innerHTML = '<p style="color: red;">Error fetching history.</p>';
  }
}

async function clearHistory() {
  if (!confirm("Are you sure you want to delete all scan history?")) return;
  try {
    const response = await fetch('http://localhost:5000/api/clear', { method: 'POST' });
    if (response.ok) loadHistory(); 
    else alert("Server failed to clear history.");
  } catch (error) {
    alert("Could not connect to server.");
  }
}