# 🚀 LAUNCH INSTRUCTIONS

**Cloud Field Campaign Scorecard - MVP Ready!**

---

## ✅ Current Status

- ✅ Backend API running on port 8000
- ✅ Frontend server running on port 3000
- ✅ Data parsed from 10 Tableau CSV files
- ✅ Dashboard with charts and filters

---

## 🌐 Access the App

**Open in your browser:**

```
http://localhost:3000
```

You should see:
- Summary stats (Total MDP, Clouds, etc.)
- MDP by Cloud (bar chart)
- MDP by Horseman (donut chart)
- MDP by Traffic Source (bar chart)
- Regional breakdown table

---

## 🛠️ If Servers Not Running

### Start Backend API:
```powershell
cd "C:\Users\ebirot\Desktop\Cloud Field Campaign Scorecard\backend"
venv\Scripts\uvicorn app.main:app --reload --port 8000
```

### Start Frontend:
```powershell
cd "C:\Users\ebirot\Desktop\Cloud Field Campaign Scorecard\backend"
venv\Scripts\python serve_frontend.py
```

---

## 📊 Features

### Current:
- ✅ Real-time data from Tableau exports
- ✅ Interactive charts (Chart.js)
- ✅ Filter controls (Quarter, Month, Region, Cloud)
- ✅ Responsive design (Tailwind CSS)
- ✅ Regional breakdown table
- ✅ Summary statistics

### Data Shown:
- Total MDP: **$1.4B**
- MDP by Cloud (top 8)
- MDP by Horseman (AE, BDR, Specialist, etc.)
- MDP by Traffic Source (Email, Paid, Organic, Events)
- Regional data by leader + cloud

---

## 🎨 UI/UX

**Design**: Clean, modern, professional
- **Colors**: Blue primary, green for positive, red for negative
- **Charts**: Interactive hover tooltips
- **Filters**: Dropdown selects (currently UI only, not filtering yet)
- **Mobile**: Responsive grid layout

---

## 🔄 To Refresh Data

1. **Export new CSV files from Tableau**:
   ```powershell
   cd backend
   venv\Scripts\python export_all_views.py
   ```

2. **Refresh browser** - data automatically reloads

---

## ⚡ Next Steps (if needed)

### Priority 1: Wire up filters
- Connect filter dropdowns to API queries
- Refresh dashboard when filters change

### Priority 2: Highlights/Lowlights
- Add input UI for campaign leaders
- Store in backend (JSON file or DB)

### Priority 3: Export to Google Slides
- Generate slide deck from data
- Download as PDF

---

## 🐛 Troubleshooting

### "Failed to load data" error:
- Check backend is running: http://localhost:8000/health
- Check CORS in browser console

### Page not loading:
- Check frontend server is running
- Try: http://localhost:3000/index.html

### Charts not showing:
- Check browser console for errors
- Verify Chart.js CDN loaded

---

## 📞 API Endpoints Available

**Base**: `http://localhost:8000`

- `GET /api/data/summary` - Overall stats
- `GET /api/data/regional` - Regional breakdown
- `GET /api/data/horseman` - Horseman breakdown
- `GET /api/data/traffic` - Traffic source breakdown
- `GET /api/data/clouds` - Cloud breakdown
- `GET /api/data/webinar` - Webinar data
- `GET /health` - API health check

**Swagger Docs**: http://localhost:8000/docs

---

## 🎉 DEMO READY!

**You can now:**
1. Show stakeholders the dashboard
2. Explain filters (will be wired up next)
3. Demonstrate data visualizations
4. Get feedback on design/UX

**Total time**: Built in ~3 hours! 🚀

---

## 📝 Notes

- Data is from Q2 exports (May 2026)
- Combines EMEA + AMER
- Filters are UI-only for now (to be wired up)
- ~$1.4B MDP tracked across 13 clouds
- 61 regional data points
- 6 horseman sources
- 5 traffic sources

**Next iteration**: Wire filters, add highlights input, export functionality
