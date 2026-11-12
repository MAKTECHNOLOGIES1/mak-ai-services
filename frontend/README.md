# 🌱 AgriPulse - Smart Agriculture Management Application (`mak-ui`)

A precision agriculture dashboard and farm management system built with **React 19**, **Vite**, and **Lucide Icons**.

---

## 🚀 Getting Started

### 1. Open Terminal and Navigate to the Project Folder:
```powershell
cd d:\Project\mak-ui
```

### 2. Start the Development Server:
```powershell
npm run dev
```

Then open your browser to the local URL displayed (typically `http://localhost:5173/`).

### 3. Build for Production:
```powershell
npm run build
```

---

## 🌾 Key Application Features

1. **📊 Overview & Sensor Telemetry Dashboard**
   - Real-time KPI summary (Average Soil Moisture, Crop Health Index, Active Pumps, Projected Harvest Revenue).
   - Weather micro-station widget with current temperature, humidity, wind speed, rain risk, and 5-day agricultural forecast.
   - Dynamic alert banners for irrigation deficits and impending precipitation.
   - Interactive live sync button to refresh field sensor telemetry.

2. **🌾 Crop & Field Management**
   - Interactive plot cards for Wheat, Basmati Paddy, Cotton, Tomatoes, Sweet Corn, and Greenhouse Bell Peppers.
   - Phenology progress bars showing growth stages (Sowing → Vegetative → Flowering → Harvest).
   - Live telemetry tiles: Soil moisture %, Soil pH, Nitrogen level, and expected harvest date.
   - Quick actions to log watering, apply foliar nutrients, view field dossiers, or register new plots.

3. **💧 Smart IoT Irrigation & Pump Control**
   - Solenoid valve actuators with interactive "Turn On / Stop Valve" controls.
   - Live water flow telemetry (L/min), line pressure (Bar), and solar power draw (kW).
   - Interactive soil moisture sliders to test sensor thresholds and trigger watering states.
   - Automation toggle for Sensor-based auto triggering.

4. **📈 Mandi Rates & APMC Market Tracker**
   - Live commodity spot prices per quintal across major mandis.
   - Government Minimum Support Price (MSP) comparison badges (+/- spread).
   - Category filtering (Grains, Cash Crops, Oilseeds, Horticulture) and search bar.
   - Built-in Harvest Revenue Calculator (estimate gross income by selecting crop and quintals).

5. **🔬 Crop Doctor & AI Pathogen Diagnostics**
   - Symptom-to-disease matching assistant with quick presets.
   - Pathogen database (Early Blight, Yellow Stripe Rust, Bacterial Leaf Blight, Leaf Curl Virus, Fall Armyworm, Powdery Mildew).
   - Dual remedy protocols: 🌿 Certified Organic bio-controls vs 🧪 Chemical fungicide/insecticide dosages.
   - Long-term agronomic prevention strategies.

6. **🧮 Precision Fertilizer & Seed Calculator**
   - Computes exact requirements of Urea (46% N), DAP (18:46:0), and MOP (60% K₂O) in kilograms and 50kg bag equivalents.
   - Adapts to soil textures (Loamy, Sandy light soil, Heavy clay).
   - Detailed 3-stage nutrient split schedule (Basal dose, 1st top dressing at CRI, 2nd top dressing at booting).
   - Certified seed weight calculation and total estimated cost.

7. **📅 Farm Activity & Task Planner**
   - Manage daily chores across Fertilization, Irrigation, Pest Control, Harvest Prep, and Maintenance.
   - Interactive checkboxes to toggle task completion with instant toast feedback.
   - Create new custom tasks with priority levels and labor assignments.
