import streamlit as st
import streamlit.components.v1 as components

# --- 1. STREAMLIT PAGE CONFIG ---
st.set_page_config(page_title="Digital Twin Voice", page_icon="🎙️", layout="centered")

st.title("🎙️ Digital Twin Command Center")
st.markdown("### RAG-Powered Voice & Email Agent")
st.write("Ensure your FastAPI backend (`vapi_server.py`) is running in a separate terminal!")

# --- 2. VAPI HTML/JS CODE ---
# We inject the exact same sleek UI, but format it to fit perfectly inside Streamlit
vapi_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/@vapi-ai/web/dist/vapi.bundle.js"></script>
    <style>
        body { background-color: #0e1117; color: #f8fafc; font-family: 'Inter', sans-serif; display: flex; justify-content: center; margin-top: 2rem;}
        .pulse-ring { animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: .5; transform: scale(1.05); }
        }
    </style>
</head>
<body>

    <div class="max-w-md w-full bg-slate-800 rounded-2xl shadow-lg p-8 border border-slate-700 text-center relative overflow-hidden">
        
        <div id="status-badge" class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-slate-700 text-slate-300 mb-8 transition-colors duration-300">
            <span id="status-dot" class="w-2 h-2 rounded-full bg-slate-400 mr-2"></span>
            <span id="status-text">System Standby</span>
        </div>

        <div class="relative flex justify-center mb-6">
            <div id="glow-ring" class="absolute inset-0 bg-blue-500 rounded-full blur-xl opacity-0 transition-opacity duration-300" style="width: 120px; height: 120px; margin: auto;"></div>
            <button id="call-button" class="relative z-10 w-28 h-28 rounded-full bg-gradient-to-br from-blue-600 to-indigo-700 text-white shadow-[0_0_30px_rgba(37,99,235,0.3)] hover:scale-105 transition-transform duration-200 flex flex-col items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 mb-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                </svg>
                <span id="btn-text" class="font-semibold text-xs">Start Call</span>
            </button>
        </div>

        <div class="mt-6 bg-slate-950 rounded-lg p-3 text-left border border-slate-700 h-28 overflow-y-auto w-full">
            <div class="text-xs font-mono text-emerald-400 mb-1">> Booting Voice Protocol...</div>
            <div id="live-logs" class="text-xs font-mono text-blue-300"></div>
        </div>

    </div>

    <script>
        // --- PUT YOUR KEYS HERE ---
        const PUBLIC_KEY = ; 
        const ASSISTANT_ID =;  

        const vapi = new window.Vapi(PUBLIC_KEY);

        const callBtn = document.getElementById('call-button');
        const btnText = document.getElementById('btn-text');
        const statusBadge = document.getElementById('status-badge');
        const statusDot = document.getElementById('status-dot');
        const statusText = document.getElementById('status-text');
        const glowRing = document.getElementById('glow-ring');
        const liveLogs = document.getElementById('live-logs');

        let isCalling = false;

        function log(msg) {
            liveLogs.innerHTML += `<div>> ${msg}</div>`;
            liveLogs.scrollTop = liveLogs.scrollHeight;
        }

        callBtn.addEventListener('click', () => {
            if (!isCalling) {
                log("Requesting microphone access...");
                vapi.start(ASSISTANT_ID);
                btnText.innerText = "Connecting...";
            } else {
                vapi.stop();
                btnText.innerText = "Start Call";
            }
        });

        vapi.on('call-start', () => {
            isCalling = true;
            btnText.innerText = "End Call";
            statusText.innerText = "Call Active";
            statusBadge.className = "inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-emerald-900 text-emerald-300 mb-8";
            statusDot.className = "w-2 h-2 rounded-full bg-emerald-400 mr-2 pulse-ring";
            glowRing.classList.remove('opacity-0');
            glowRing.classList.add('opacity-50', 'pulse-ring');
            callBtn.className = "relative z-10 w-28 h-28 rounded-full bg-gradient-to-br from-red-500 to-rose-700 text-white shadow-xl hover:scale-105 transition-transform duration-200 flex flex-col items-center justify-center";
            log("Connected. Say hello!");
        });

        vapi.on('call-end', () => {
            isCalling = false;
            btnText.innerText = "Start Call";
            statusText.innerText = "System Standby";
            statusBadge.className = "inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-slate-700 text-slate-300 mb-8";
            statusDot.className = "w-2 h-2 rounded-full bg-slate-400 mr-2";
            glowRing.classList.add('opacity-0');
            glowRing.classList.remove('opacity-50', 'pulse-ring');
            callBtn.className = "relative z-10 w-28 h-28 rounded-full bg-gradient-to-br from-blue-600 to-indigo-700 text-white shadow-xl hover:scale-105 transition-transform duration-200 flex flex-col items-center justify-center";
            log("Call disconnected.");
        });

        vapi.on('speech-start', () => { log("AI is speaking..."); });
        vapi.on('error', (e) => { log(`<span class="text-red-400">Error: ${e.message}</span>`); });
    </script>
</body>
</html>
"""

# --- 3. RENDER THE UI IN STREAMLIT ---
# We use st.components.v1.html to render the UI. 
# Streamlit automatically handles iframe permissions for the microphone in modern versions.
components.html(vapi_html, height=550)

st.markdown("---")
st.caption("Backend powered by ChromaDB & Gemini Pro")