document.addEventListener('DOMContentLoaded', () => {
  setupMenu();
  setupPage();
  updateUsername();
  setupBackButtons();
});

const api = async (url, body) => {
  const response = await fetch(url, {
    method: body ? 'POST' : 'GET',
    headers: body ? { 'Content-Type': 'application/json' } : {},
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.message || 'Something went wrong.');
  return data;
};

function setupMenu() {
  const toggle = document.getElementById('menuToggle');
  const menu = document.getElementById('navMenu');
  if (!toggle || !menu) return;
  toggle.addEventListener('click', () => {
    const isOpen = menu.classList.toggle('open');
    toggle.setAttribute('aria-expanded', String(isOpen));
    toggle.setAttribute('aria-label', isOpen ? 'Close navigation' : 'Open navigation');
  });
  menu.querySelectorAll('a').forEach(link => link.addEventListener('click', () => {
    menu.classList.remove('open');
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-label', 'Open navigation');
  }));
}

function setupBackButtons() {
  document.querySelectorAll('.advisory-back').forEach(el => {
    el.addEventListener('click', (e) => {
      // If there is a history to go back to, use it; otherwise follow the link's href
      try {
        if (window.history && window.history.length > 1) {
          e.preventDefault();
          window.history.back();
        }
      } catch (_) {
        // ignore and allow default navigation
      }
    });
  });
}

function setupPage() {
  const page = location.pathname.replace(/\.html$/, '');
  if (page.includes('login')) setupLogin();
  if (page.includes('signup')) setupSignup();
  if (page.includes('forgotpassword')) setupForgotPassword();
  if (page.includes('crop-advisory')) setupCropAdvisory();
  if (page.includes('fertilizer')) setupFertilizer();
  if (page.includes('chatbot')) setupChatbot();
  if (page.includes('support')) setupSupport();
}

async function updateUsername() {
  const element = document.getElementById('username');
  if (!element) return;
  try { element.textContent = (await api('/api/get-username')).username; } catch (_) {}
}

function setupLogin() {
  const form = document.getElementById('loginForm');
  if (!form) return;
  form.addEventListener('submit', async event => {
    event.preventDefault();
    try {
      await api('/api/login', { email: loginEmail.value.trim(), password: loginPassword.value });
      location.assign('/home');
    } catch (error) { alert(error.message); }
  });
}

function setupSignup() {
  const form = document.getElementById('signupForm');
  if (!form) return;
  form.addEventListener('submit', async event => {
    event.preventDefault();
    try {
      await api('/api/signup', { name: signupName.value.trim(), email: signupEmail.value.trim(), mobile: signupMobile.value.trim(), password: signupPassword.value });
      alert('Account created. You are now signed in.');
      location.assign('/home');
    } catch (error) { alert(error.message); }
  });
}

function setupForgotPassword() {
  const form = document.getElementById('resetForm');
  if (!form) return;
  form.addEventListener('submit', event => { event.preventDefault(); alert('Password reset needs a database/email service before it can be enabled.'); });
}

async function setupCropAdvisory() {
  const form = document.getElementById('cropAdvisoryForm');
  const box = document.getElementById('cropResultBox');
  if (!form) return;
  try {
    const { options } = await api('/api/crop-options');
    populateSelect('cropState', options.State_UT);
    populateSelect('soilType', options.Soil_Type);
    populateSelect('season', options.Season);
    populateSelect('waterAvailability', options.Water_Availability);
    populateSelect('temperature', options.Temperature_Range_C);
  } catch (error) { box.innerHTML = `<p class="result-placeholder">${escapeHtml(error.message)}</p>`; }
  form.addEventListener('submit', async event => {
    event.preventDefault();
    box.innerHTML = '<p>Finding the best crop…</p>';
    try {
      const data = await api('/api/crop-recommendation', {
        state: cropState.value, soil: soilType.value, season: season.value,
        water: waterAvailability.value, temperature: temperature.value,
      });
      box.innerHTML = `
        <div class="result-crop"><span>Recommended crop</span><strong>${escapeHtml(data.crop || data.recommendation)}</strong></div>
        <div class="result-reason"><h3>Why this is a suitable match</h3><p>${escapeHtml(data.reason || 'The selected farm conditions were used to make this recommendation.').replace(/\n/g, '<br>')}</p></div>
        <small class="result-source">${escapeHtml(data.reason_source || data.source || '')}</small>`;
    } catch (error) { box.innerHTML = `<p>${escapeHtml(error.message)}</p>`; }
  });
}

function populateSelect(id, values) {
  const select = document.getElementById(id);
  if (!select) return;
  const label = select.options[0]?.text || 'Select an option';
  select.innerHTML = `<option value="">${label}</option>`;
  values.forEach(value => select.add(new Option(value, value)));
}

function setupFertilizer() {
  const form = document.getElementById('fertilizerForm');
  const box = document.getElementById('fertResultBox');
  if (!form) return;
  form.addEventListener('submit', async event => {
    event.preventDefault();
    try {
      const data = await api('/api/fertilizer-recommendation', {
        crop: fertCrop.value, nitrogen: nitrogen.value, phosphorus: phosphorus.value,
        potassium: potassium.value, soil_ph: soilPh.value, organic: organicPreference.value,
      });
      box.innerHTML = `<p><strong>Recommendation</strong></p><p>${escapeHtml(data.recommendation)}</p>`;
    } catch (error) { box.innerHTML = `<p>${escapeHtml(error.message)}</p>`; }
  });
}

function setupChatbot() {
  const form = document.getElementById('chatForm');
  const messages = document.getElementById('chatMessages');
  const userInput = document.getElementById('userInput');
  if (!form || !messages || !userInput) return;
  setupVoiceInput(form);
  addMessage('Hello! Ask me about crops, water, soil, pests, or fertilizer.', 'bot', messages);
  form.addEventListener('submit', async event => {
    event.preventDefault();
    const message = userInput.value.trim(); if (!message) return;
    addMessage(message, 'user', messages);
    userInput.value = '';
    const loadingMessage = addMessage('Thinking…', 'bot', messages);
    try {
      const data = await api('/api/chatbot-response', { message });
      const reply = data.reply || 'I could not prepare a response right now.';
      updateMessage(loadingMessage, reply, 'bot');
    } catch (error) {
      updateMessage(loadingMessage, error.message, 'bot');
    }
  });
}

function setupVoiceInput(form) {
  const button = document.getElementById('voiceInput');
  const input = document.getElementById('userInput');
  const status = document.getElementById('voiceStatus');
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition || window.mozSpeechRecognition || window.msSpeechRecognition;
  if (!button || !input || !status) return;
  if (!SpeechRecognition) {
    button.disabled = true;
    button.title = 'Voice input is not supported by this browser';
    status.textContent = 'Voice input is not available in this browser. Use Chrome or Edge on localhost/HTTPS.';
    return;
  }

  button.disabled = false;
  button.textContent = 'Voice';
  button.title = 'Click to start voice input';
  status.textContent = 'Voice input ready. Click Voice and speak your question.';

  let recognition;
  try {
    recognition = new SpeechRecognition();
  } catch (creationError) {
    button.disabled = true;
    status.textContent = 'Voice recognition is not available in this browser instance.';
    return;
  }

  const preferredLanguage = /hi|hindi/i.test(navigator.language || '') ? 'hi-IN' : 'en-IN';
  recognition.lang = preferredLanguage;
  recognition.interimResults = true;
  recognition.continuous = true;
  recognition.maxAlternatives = 1;
  let listening = false;

  recognition.addEventListener('start', () => {
    listening = true;
    button.classList.add('is-listening');
    button.textContent = 'Listening';
    button.setAttribute('aria-label', 'Stop voice input');
    status.textContent = 'Listening... Speak your question now.';
  });

  recognition.addEventListener('result', event => {
    let transcript = '';
    let hasFinalResult = false;
    for (let index = event.resultIndex; index < event.results.length; index += 1) {
      const result = event.results[index];
      transcript += result[0].transcript;
      if (result.isFinal) {
        hasFinalResult = true;
      }
    }

    const finalTranscript = transcript.trim();
    if (finalTranscript) {
      input.value = finalTranscript;
      input.focus();
      if (hasFinalResult) {
        status.textContent = 'Voice input captured. Press Send to submit.';
      } else {
        status.textContent = 'Listening... Speak your question now.';
      }
    }
  });

  recognition.addEventListener('error', event => {
    const messages = {
      not_allowed: 'Microphone permission was denied. Allow microphone access and try again.',
      no_speech: 'No speech was detected. Try again and speak clearly.',
      audio_capture: 'No microphone was found. Check your microphone settings.',
      network: 'Voice recognition network error occurred. Check your internet connection.',
      aborted: 'Voice input was aborted. Try again.',
    };
    status.textContent = messages[event.error] || `Voice input error: ${event.error || 'unknown'}`;
    listening = false;
    button.classList.remove('is-listening');
    button.textContent = 'Voice';
    button.setAttribute('aria-label', 'Start voice input');
  });

  recognition.addEventListener('end', () => {
    listening = false;
    button.classList.remove('is-listening');
    button.textContent = 'Voice';
    button.setAttribute('aria-label', 'Start voice input');
    if (input.value) {
      status.textContent = 'Voice input captured. Press Send to submit.';
    } else {
      status.textContent = 'No voice text captured. Try again.';
    }
  });

  button.addEventListener('click', async () => {
    if (listening) {
      recognition.stop();
      return;
    }

    try {
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        status.textContent = 'Requesting microphone access...';
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        stream.getTracks().forEach(track => track.stop());
      }
      recognition.start();
    } catch (error) {
      status.textContent = error && error.name === 'NotAllowedError'
        ? 'Microphone permission was denied. Allow microphone access and try again.'
        : 'Voice input cannot start. Please try again.';
    }
  });
  status.textContent = 'Click Voice and speak your question.';
}

function addMessage(text, type, container) {
  const item = document.createElement('div'); item.className = `message ${type}`;
  const bubble = document.createElement('div'); bubble.className = 'bubble';
  if (type === 'bot') bubble.innerHTML = formatChatReply(text);
  else bubble.textContent = text;
  item.appendChild(bubble);
  container.appendChild(item); container.scrollTop = container.scrollHeight;
  return item;
}

function updateMessage(item, text, type) {
  const bubble = item?.querySelector('.bubble');
  if (!bubble) return;
  if (type === 'bot') bubble.innerHTML = formatChatReply(text);
  else bubble.textContent = text;
}

function formatChatReply(text) {
  const lines = String(text || '').split(/\r?\n/);
  const html = [];
  let bulletOpen = false;
  const closeBullets = () => { if (bulletOpen) { html.push('</ul>'); bulletOpen = false; } };
  lines.forEach(line => {
    const safe = escapeHtml(line.trim()).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    if (!safe) { closeBullets(); return; }
    if (/^-\s+/.test(line.trim())) {
      if (!bulletOpen) { html.push('<ul>'); bulletOpen = true; }
      html.push(`<li>${safe.replace(/^-\s+/, '')}</li>`);
      return;
    }
    closeBullets();
    html.push(`<p>${safe}</p>`);
  });
  closeBullets();
  return html.join('') || '<p>I could not prepare a response. Please try again.</p>';
}

function setupSupport() {
  const form = document.getElementById('supportForm');
  if (!form) return;
  form.addEventListener('submit', async event => {
    event.preventDefault();
    try {
      const data = await api('/api/submit-support', { name: supportName.value.trim(), phone: supportPhone.value.trim(), query: supportQuery.value.trim() });
      alert(data.message); form.reset();
    } catch (error) { alert(error.message); }
  });
}

async function logout() {
  try { await api('/api/logout', {}); } finally { location.assign('/'); }
}

function escapeHtml(value) {
  const element = document.createElement('div'); element.textContent = value || ''; return element.innerHTML;
}
