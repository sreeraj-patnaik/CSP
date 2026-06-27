# User Guide — CSP Cyber Awareness Portal

## Portal Overview

The portal has six main sections accessible from the navbar:

| Section | URL | Description |
|---------|-----|-------------|
| Home | `/` | Landing page with animated stats and village overview |
| Villages | `/villages/` | Leaflet map + individual village pages |
| Field Visits | `/visits/` | Timeline of all project field visits |
| Survey | `/survey/` | 3-step awareness survey form |
| Analytics | `/analytics/` | Interactive charts and auto-insights |
| AI Assistant | `/ai/` | Chat with LLM using project data as context |
| Reports | `/reports/` | PDF, Excel, CSV downloads |
| Gallery | `/gallery/` | Photo gallery with masonry layout |
| Team | `/team/` | Project team and mentor information |

---

## Taking the Survey

1. Navigate to `/survey/` or click **Take Survey** in the navbar.
2. **Step 1 – Demographics**: Fill in your name (optional), age group, gender, education, occupation, and select your village.
3. **Step 2 – Internet Usage** (only shown if you use the internet): Select your device, connection type, daily usage hours, and internet purposes.
4. **Step 3 – Awareness**: Answer questions about OTP awareness, fraud experience, password habits, and safe browsing knowledge.
5. Click **Submit Survey**. You'll be redirected to the Thank You page.

> The form validates each step before advancing. Required fields are marked visually.

---

## Analytics Dashboard

- **Village filter**: Use the dropdown at the top to filter all charts to a single village.
- **Charts refresh** automatically when you change the village.
- **Auto-Insights** appear at the top — red/orange items indicate high-risk areas.
- Hover over any chart element for a tooltip with exact values.

---

## Gallery

- Switch between **Masonry** and **Grid** views using the toggle buttons.
- Filter by village, category (event/fieldwork/community/etc.), or search by caption.
- Click any photo to open the **lightbox** with full-size view.
- Use **← →** arrow keys or the on-screen buttons to navigate between photos.

---

## AI Assistant

1. Go to `/ai/` and type your question in the input box.
2. Press **Enter** (or Shift+Enter for a new line) to send.
3. The AI will answer using the survey data, village info, and field visit notes.
4. Click a **suggested question** chip to quickly ask pre-defined questions.
5. Source citations appear under the AI's response.

> Requires Ollama running locally. If unavailable, the assistant will show a helpful error message.

---

## Dark / Light Mode

Click the **sun/moon icon** in the top-right navbar to toggle between dark and light mode. Your preference is saved in your browser.

---

## Search

Click the **search icon** in the navbar and type to search villages, field visits, and team members. Results appear as a dropdown and link directly to the relevant page.
