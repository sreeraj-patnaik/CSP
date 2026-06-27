/**
 * AI Chat Alpine.js component.
 * Sends the full conversation history to /ai/api/chat/ and renders
 * markdown-lite responses with source tags.
 */
function aiChat() {
  return {
    messages: [],
    inputText: '',
    typing: false,
    rebuilding: false,
    suggested: [
      'Which village has the highest cyber fraud rate?',
      'What percentage of respondents are aware of OTP rules?',
      'Summarize Day 1 field visit â€” objectives and outcomes.',
      'List all team members and their roles.',
      'Compare internet usage across villages.',
      'Which age group is most vulnerable to cyber fraud?',
      'What were the main challenges during field visits?',
      'What are the key recommendations from survey findings?',
    ],

    init() {
      fetch('/ai/api/suggested/')
        .then(r => r.json())
        .then(d => { if (d.questions?.length) this.suggested = d.questions; })
        .catch(() => {});
    },

    async sendMessage(text) {
      const question = (text || this.inputText).trim();
      if (!question || this.typing) return;

      this.inputText = '';
      this.messages.push({ role: 'user', content: question });
      this.typing = true;
      this.$nextTick(() => this.scrollToBottom());

      // Reset textarea height
      const ta = document.getElementById('chat-input');
      if (ta) { ta.style.height = 'auto'; }

      try {
        const resp = await fetch('/ai/api/chat/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.getCsrf(),
          },
          body: JSON.stringify({
            question,
            history: this.messages.slice(-10).map(m => ({
              role: m.role,
              content: m.content,
            })),
          }),
        });

        const data = await resp.json();
        if (!resp.ok || data.error) throw new Error(data.error || `HTTP ${resp.status}`);

        const answer = data.answer || 'Sorry, no response was generated.';
        this.messages.push({
          role: 'ai',
          content: answer,
          html: this.formatMarkdown(answer),
          sources: data.sources || [],
        });
      } catch (err) {
        const msg = err.message || 'Could not reach the assistant. Is Ollama running?';
        this.messages.push({
          role: 'ai',
          content: msg,
          html: this.formatMarkdown(msg),
          sources: [],
        });
      } finally {
        this.typing = false;
        this.$nextTick(() => this.scrollToBottom());
      }
    },

    clearChat() {
      this.messages = [];
      this.$nextTick(() => document.getElementById('chat-input')?.focus());
    },

    async rebuildKB() {
      if (!confirm('Rebuild the knowledge base? This may take a minute.')) return;
      this.rebuilding = true;
      try {
        const resp = await fetch('/ai/api/rebuild/', {
          method: 'POST',
          headers: { 'X-CSRFToken': this.getCsrf() },
        });
        const data = await resp.json();
        if (!resp.ok || data.error) throw new Error(data.error || `HTTP ${resp.status}`);
        CSP?.toast(`KB rebuilt: ${data.indexed || 0} chunks, ${data.context_length || 0} chars`, 'success');
      } catch (err) {
        CSP?.toast(err.message || 'Rebuild failed', 'error');
      } finally {
        this.rebuilding = false;
      }
    },

    handleKey(event) {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        this.sendMessage();
      }
    },

    autoResize(el) {
      el.style.height = 'auto';
      el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
    },

    scrollToBottom() {
      const el = document.getElementById('chat-scroll');
      if (el) el.scrollTop = el.scrollHeight;
    },

    formatMarkdown(text) {
      return String(text)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        // headings
        .replace(/^### (.+)$/gm, '<h3 style="color:#FFF6F6;font-weight:600;margin:0.75rem 0 0.25rem;">$1</h3>')
        .replace(/^## (.+)$/gm, '<h2 style="color:#FFF6F6;font-weight:700;font-size:1.05em;margin:0.75rem 0 0.25rem;">$1</h2>')
        // bold and italic
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        // inline code
        .replace(/`(.+?)`/g, '<code>$1</code>')
        // unordered list items
        .replace(/^[\s]*[-â€¢]\s+(.+)$/gm, '<li>$1</li>')
        // numbered list items
        .replace(/^[\s]*\d+\.\s+(.+)$/gm, '<li>$1</li>')
        // wrap consecutive <li> in a <ul>
        .replace(/(<li>.*<\/li>\n?)+/g, m => `<ul>${m}</ul>`)
        // horizontal rule
        .replace(/^---+$/gm, '<hr style="border-color:rgba(255,255,255,0.08);margin:0.75rem 0;">')
        // newlines
        .replace(/\n\n/g, '</p><p style="margin-top:0.5rem;">')
        .replace(/\n/g, '<br>');
    },

    getCsrf() {
      const m = document.cookie.match(/csrftoken=([^;]+)/);
      return m ? decodeURIComponent(m[1]) : '';
    },
  };
}

