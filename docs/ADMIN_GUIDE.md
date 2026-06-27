# Admin Guide — CSP Cyber Awareness Portal

## Accessing the Admin Panel

URL: `/admin/`  
Login with a superuser account created during setup.

---

## Managing Survey Responses

- **View all responses**: Admin → Surveys → Survey Responses
- **Filter** by village, internet usage, awareness level, date
- **Export** selected responses to Excel via the action dropdown
- **Import** from Google Forms Excel: Admin action or visit `/reports/` → Import section
- **Awareness Score** is auto-computed from Q9–Q13 answers (scale 1–5)

---

## Adding Field Visits

1. Admin → Visits → Field Visits → Add
2. Set `Day Number` (unique, e.g., 1, 2, 3…) — this auto-generates the URL `/visits/1/`
3. Fill in: Title, Village, Date, Description
4. Add **Objectives** and **Activities** as JSON arrays (one item per line)
5. Attach photos via the **Visit Media** inline section

---

## Managing Villages

Villages are pre-loaded from fixture. To edit:
- Admin → Villages → Villages → click a village
- Update population, latitude/longitude, color accent
- The map on `/villages/` auto-updates from these coordinates

---

## Team Members

Admin → Team → Team Members → Add  
- Set **role**: `mentor`, `lead`, `member`, or `volunteer`
- `order` field controls display sequence
- Upload a **photo** for the profile card

---

## Gallery Photos

Admin → Gallery → Photos → Add  
- Upload image — thumbnail is auto-generated on save
- Set village, category, caption
- GPS lat/lng populate the gallery map if provided
- Use **before_after_pair** FK to link before/after comparison photos

---

## Site Settings (singleton)

Admin → Core → Site Settings  
- Toggle **Survey Open** on/off (shows the Closed page when off)
- Update college/contact info that appears in the footer

---

## User Roles

| Role | Permissions |
|------|-------------|
| `admin` | Full access to all admin features |
| `coordinator` | Can manage surveys, gallery, visits |
| `volunteer` | Can add survey responses only |
| `viewer` | Read-only (dashboard/reports) |

---

## Rebuilding the AI Knowledge Base

After adding new field visits or survey data:

```bash
python manage.py build_knowledge_base
```

Or via the web UI: visit `/ai/` and click **Rebuild KB** (staff only).

---

## Backup

```bash
python manage.py dumpdata --exclude auth.permission --exclude contenttypes > backup.json
```

Restore:
```bash
python manage.py loaddata backup.json
```
