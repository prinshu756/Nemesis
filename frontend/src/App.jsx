import React, { useState } from 'react';
import { NemesisProvider } from './hooks/useNemesisState.jsx';
import Sidebar from './components/Sidebar';
import TopBar from './components/TopBar';
import StrategicMap from './views/StrategicMap';
import UnitStatus from './views/UnitStatus';
import ThreatIntel from './views/ThreatIntel';
import Diagnostics from './views/Diagnostics';
import Scanlines from './effects/Scanlines';
import './App.css';

const VIEWS = {
  strat_map: StrategicMap,
  unit_stat: UnitStatus,
  threat_intel: ThreatIntel,
  diagnostics: Diagnostics,
};

function AppContent() {
  const [activeView, setActiveView] = useState('strat_map');
  const ViewComponent = VIEWS[activeView] || StrategicMap;

  return (
    <div className="app-layout">
      <Sidebar activeView={activeView} onNavigate={setActiveView} />
      <TopBar activeView={activeView} />
      <main className="app-content">
        <ViewComponent />
      </main>
      {/* CRT scanline overlay with scan beam and vignette */}
      <Scanlines opacity={0.4} showBeam={true} showVignette={true} flicker={true} />
    </div>
  );
}

export default function App() {
  return (
    <NemesisProvider>
      <AppContent />
    </NemesisProvider>
  );
}
