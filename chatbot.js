// Space Pilates + Wellness Society — AI Chat Guide

// ── CLAUDE API ──
async function askClaude(messages) {
  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ messages })
  });
  const data = await res.json();
  if (data.error) throw new Error(data.error);
  return data.reply;
}

// ── RENDER MARKDOWN (basic) ──
function renderMarkdown(text) {
  return text
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>')
    .replace(/^/, '<p>')
    .replace(/$/, '</p>');
}

// ── BUILD WIDGET HTML ──
function buildWidget() {
  const el = document.createElement('div');
  el.id = 'sp-chat';
  el.innerHTML = `
    <div id="sp-chat-bubble" title="Chat with us">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <span class="sp-badge">1</span>
    </div>
    <div id="sp-chat-window">
      <div id="sp-chat-header">
        <div id="sp-chat-header-info">
          <div id="sp-chat-avatar"><img src="/assets/logo-icon-final.png" alt="Space Pilates" /></div>
          <div>
            <div id="sp-chat-name">Space Pilates</div>
            <div id="sp-chat-status">Ask us anything</div>
          </div>
        </div>
        <button id="sp-chat-close" aria-label="Close chat">✕</button>
      </div>
      <div id="sp-chat-messages"></div>
      <div id="sp-quick-replies"></div>
      <div id="sp-chat-input-row">
        <input id="sp-chat-input" type="text" placeholder="Message…" autocomplete="off" />
        <button id="sp-chat-send" aria-label="Send">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <line x1="22" y1="2" x2="11" y2="13" stroke="white" stroke-width="2" stroke-linecap="round"/>
            <polygon points="22 2 15 22 11 13 2 9 22 2" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
          </svg>
        </button>
      </div>
    </div>
  `;
  document.body.appendChild(el);
}

// ── INJECT STYLES ──
function injectStyles() {
  const style = document.createElement('style');
  style.textContent = `
    #sp-chat { position: fixed; z-index: 9999; bottom: 28px; right: 28px; font-family: 'IBM Plex Sans', sans-serif; }
    #sp-chat-bubble {
      width: 56px; height: 56px; border-radius: 50%;
      background: linear-gradient(135deg, #f0a0c0 0%, #f8c890 100%);
      display: flex; align-items: center; justify-content: center;
      cursor: pointer; box-shadow: 0 4px 20px rgba(0,0,0,0.14);
      transition: transform 0.2s, box-shadow 0.2s;
      position: relative;
    }
    #sp-chat-bubble:hover { transform: scale(1.06); box-shadow: 0 6px 24px rgba(0,0,0,0.22); }
    .sp-badge {
      position: absolute; top: -3px; right: -3px;
      width: 18px; height: 18px; border-radius: 50%;
      background: #e05a5a; color: white;
      font-size: 10px; font-weight: 700;
      display: flex; align-items: center; justify-content: center;
      border: 2px solid white;
    }
    #sp-chat-window {
      position: absolute; bottom: 68px; right: 0;
      width: 340px; max-height: 520px;
      background: #faf8f4; border-radius: 16px;
      box-shadow: 0 8px 40px rgba(0,0,0,0.14);
      display: none; flex-direction: column; overflow: hidden;
      border: 1px solid #e8e0d8;
    }
    #sp-chat-window.open { display: flex; }
    #sp-chat-header {
      display: flex; align-items: center; justify-content: space-between;
      padding: 14px 16px;
      background: linear-gradient(135deg, #fde8d8 0%, #f8d4e8 50%, #e8d4f4 100%);
      border-radius: 16px 16px 0 0;
    }
    #sp-chat-header-info { display: flex; align-items: center; gap: 10px; }
    #sp-chat-avatar {
      width: 34px; height: 34px; border-radius: 50%;
      background: white;
      display: flex; align-items: center; justify-content: center;
      overflow: hidden;
    }
    #sp-chat-avatar img { width: 100%; height: 100%; object-fit: contain; padding: 4px; }
    #sp-chat-name { font-size: 14px; font-weight: 600; color: #1a1614; line-height: 1.2; }
    #sp-chat-status { font-size: 11px; color: #4a4440; }
    #sp-chat-close {
      background: none; border: none; color: rgba(26,22,20,0.5);
      font-size: 16px; cursor: pointer; padding: 4px;
      transition: color 0.2s; line-height: 1;
    }
    #sp-chat-close:hover { color: #1a1614; }
    #sp-chat-messages {
      flex: 1; overflow-y: auto; padding: 18px;
      display: flex; flex-direction: column; gap: 12px;
      scroll-behavior: smooth; min-height: 0;
    }
    #sp-chat-messages::-webkit-scrollbar { width: 4px; }
    #sp-chat-messages::-webkit-scrollbar-track { background: transparent; }
    #sp-chat-messages::-webkit-scrollbar-thumb { background: #d8cfc6; border-radius: 2px; }
    .sp-msg { max-width: 84%; word-break: break-word; line-height: 1.55; }
    .sp-msg p { margin: 0 0 6px; }
    .sp-msg p:last-child { margin: 0; }
    .sp-msg-bot {
      align-self: flex-start;
      background: #ffffff;
      border: 1px solid #e8e0d8;
      border-radius: 4px 16px 16px 16px;
      padding: 12px 15px;
      font-size: 13.5px; color: #1a1614;
    }
    .sp-msg-user {
      align-self: flex-end;
      background: #1a1614;
      color: white;
      border-radius: 16px 16px 4px 16px;
      padding: 12px 15px; font-size: 13.5px;
    }
    .sp-typing {
      align-self: flex-start;
      background: #ffffff; border: 1px solid #e8e0d8;
      border-radius: 4px 16px 16px 16px;
      padding: 14px 18px;
      display: flex; gap: 5px; align-items: center;
    }
    .sp-typing span {
      width: 7px; height: 7px; background: #9a938c; border-radius: 50%;
      animation: sp-bounce 1.1s infinite ease-in-out;
    }
    .sp-typing span:nth-child(2) { animation-delay: 0.18s; }
    .sp-typing span:nth-child(3) { animation-delay: 0.36s; }
    @keyframes sp-bounce {
      0%, 60%, 100% { transform: translateY(0); }
      30% { transform: translateY(-6px); }
    }
    #sp-quick-replies {
      padding: 0 12px 10px;
      display: flex; flex-wrap: wrap; gap: 7px;
    }
    .sp-qr {
      background: white; border: 1.5px solid #1a1614;
      border-radius: 20px; padding: 6px 13px;
      font-size: 12px; font-weight: 500; color: #1a1614;
      cursor: pointer; transition: all 0.15s; white-space: nowrap;
    }
    .sp-qr:hover { background: #1a1614; color: white; }
    #sp-chat-input-row {
      display: flex; align-items: center; gap: 8px;
      padding: 12px 14px; border-top: 1px solid #e8e0d8;
    }
    #sp-chat-input {
      flex: 1; border: 1.5px solid #e8e0d8; border-radius: 24px;
      padding: 10px 16px; font-size: 14px; outline: none;
      transition: border-color 0.2s; color: #1a1614;
      background: white; font-family: inherit;
    }
    #sp-chat-input:focus { border-color: #1a1614; }
    #sp-chat-send {
      width: 38px; height: 38px; border-radius: 50%;
      background: #1a1614;
      border: none; cursor: pointer;
      display: flex; align-items: center; justify-content: center;
      transition: opacity 0.2s, transform 0.15s; flex-shrink: 0;
    }
    #sp-chat-send:hover { opacity: 0.88; transform: scale(1.05); }
    @media (max-width: 420px) {
      #sp-chat-window { width: calc(100vw - 24px); right: 12px; bottom: 76px; }
      #sp-chat { right: 16px; bottom: 20px; }
    }
  `;
  document.head.appendChild(style);
}

// ── CHAT ENGINE ──
function initChat() {
  const win = document.getElementById('sp-chat-window');
  const bubble = document.getElementById('sp-chat-bubble');
  const closeBtn = document.getElementById('sp-chat-close');
  const msgs = document.getElementById('sp-chat-messages');
  const qr = document.getElementById('sp-quick-replies');
  const input = document.getElementById('sp-chat-input');
  const sendBtn = document.getElementById('sp-chat-send');
  const badge = document.querySelector('.sp-badge');

  let isOpen = false;
  let hasOpened = false;
  let conversationHistory = [];

  function scrollToBottom() {
    setTimeout(() => msgs.scrollTop = msgs.scrollHeight, 50);
  }

  function addMessage(text, isUser = false) {
    const div = document.createElement('div');
    div.className = isUser ? 'sp-msg sp-msg-user' : 'sp-msg sp-msg-bot';
    div.innerHTML = isUser ? `<p>${text}</p>` : renderMarkdown(text);
    msgs.appendChild(div);
    scrollToBottom();
    return div;
  }

  function setQuickReplies(replies) {
    qr.innerHTML = '';
    if (!replies || !replies.length) return;
    replies.forEach(r => {
      const btn = document.createElement('button');
      btn.className = 'sp-qr';
      btn.textContent = r;
      btn.onclick = () => handleSend(r);
      qr.appendChild(btn);
    });
  }

  function showTyping() {
    const el = document.createElement('div');
    el.className = 'sp-typing';
    el.id = 'sp-typing-indicator';
    el.innerHTML = '<span></span><span></span><span></span>';
    msgs.appendChild(el);
    scrollToBottom();
  }

  function hideTyping() {
    const el = document.getElementById('sp-typing-indicator');
    if (el) el.remove();
  }

  async function handleSend(text) {
    const msg = (text || input.value).trim();
    if (!msg) return;
    input.value = '';
    qr.innerHTML = '';
    sendBtn.disabled = true;
    addMessage(msg, true);
    conversationHistory.push({ role: 'user', content: msg });
    showTyping();

    try {
      const reply = await askClaude(conversationHistory);
      hideTyping();
      addMessage(reply, false);
      conversationHistory.push({ role: 'assistant', content: reply });
      if (conversationHistory.length <= 2) {
        setQuickReplies(['Tell me about the classes', 'How much is it?', 'Never done Pilates', 'Class times today']);
      } else {
        setQuickReplies(['How do I join?', 'Tell me more', 'What about pricing?']);
      }
    } catch (err) {
      hideTyping();
      addMessage(`Sorry, something went wrong. You can reach us directly at hello@spacepilatesandwellness.com or on Instagram @space.Pilates.`, false);
    } finally {
      sendBtn.disabled = false;
    }
  }

  async function openChat() {
    isOpen = true;
    win.classList.add('open');
    badge.style.display = 'none';
    if (!hasOpened) {
      hasOpened = true;
      showTyping();
      try {
        conversationHistory.push({ role: 'user', content: 'Hi' });
        const reply = await askClaude(conversationHistory);
        hideTyping();
        addMessage(reply, false);
        conversationHistory.push({ role: 'assistant', content: reply });
        setQuickReplies(['Tell me about the classes', 'How much is it?', 'Never done Pilates', 'Class times today']);
      } catch {
        hideTyping();
        addMessage(`Hey! Welcome to Space Pilates. We're at 307 E 2nd St in Downtown Sanford. What brings you here today?`, false);
        setQuickReplies(['Tell me about the classes', 'How much is it?', 'Never done Pilates', 'Class times today']);
      }
    }
  }

  bubble.onclick = () => isOpen ? (isOpen = false, win.classList.remove('open')) : openChat();
  closeBtn.onclick = () => { isOpen = false; win.classList.remove('open'); };
  sendBtn.onclick = () => handleSend();
  input.addEventListener('keydown', e => { if (e.key === 'Enter') handleSend(); });
}

// ── INIT ──
(function() {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => { buildWidget(); injectStyles(); initChat(); });
  } else {
    buildWidget(); injectStyles(); initChat();
  }
})();
