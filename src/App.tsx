import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { AnimatePresence } from 'motion/react';
import { onSnapshot, collection } from 'firebase/firestore';
import { db } from './firebase';
import { CountryStats, ManufacturingSite, MapLayer, NUTS2Region } from './types';
import { COUNTRY_NAMES } from './constants';
import { Map } from './components/Map';
import { Sidebar } from './components/Sidebar';
import { WelcomeModal, shouldShowWelcome, resetWelcome } from './components/WelcomeModal';
import { AboutModal } from './components/AboutModal';
import { Zap, Factory, Battery, HelpCircle, Info } from 'lucide-react';
import { cn } from './utils';



export default function App() {
  const [countries, setCountries] = useState<CountryStats[]>([]);
  const [sites, setSites] = useState<ManufacturingSite[]>([]);
  const [nuts2Regions, setNuts2Regions] = useState<NUTS2Region[]>([]);
  const [activeLayers, setActiveLayers] = useState<MapLayer[]>([]);
  const [selectedCountryId, setSelectedCountryId] = useState<string | null>(null);
  const [selectedSiteId, setSelectedSiteId] = useState<string | null>(null);
  const [selectedRegionId, setSelectedRegionId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [showWelcome, setShowWelcome] = useState<boolean>(shouldShowWelcome);
  const [showAbout, setShowAbout] = useState(false);

  useEffect(() => {
    const unsubCountries = onSnapshot(collection(db, 'countries'), (snapshot) => {
      setCountries(snapshot.docs.map(doc => doc.data() as CountryStats));
      setLoading(false);
    });

    const unsubSites = onSnapshot(collection(db, 'sites'), (snapshot) => {
      setSites(snapshot.docs.map(doc => doc.data() as ManufacturingSite));
    });

    // Load NUTS2 regions from GeoJSON
    fetch('/nuts2_investment.geojson')
      .then(res => res.json())
      .then(data => {
        const regions = data.features.map((feature: any) => ({
          ...feature.properties,
          geometry: feature.geometry
        }));
        setNuts2Regions(regions);
        console.log(`Loaded ${regions.length} NUTS2 regions`);
      })
      .catch(err => console.error('Error loading NUTS2 data:', err));

    return () => {
      unsubCountries();
      unsubSites();
    };
  }, []);

  const toggleLayer = (layer: MapLayer) => {
    setActiveLayers(prev => 
      prev.includes(layer) ? prev.filter(l => l !== layer) : [...prev, layer]
    );
  };

  // ISO3→ISO2 mapping (stable — defined once outside renders)
  const ISO3_TO_ISO2: Record<string, string> = {
    'DEU': 'DE', 'FRA': 'FR', 'ESP': 'ES', 'ITA': 'IT', 'POL': 'PL',
    'NLD': 'NL', 'BEL': 'BE', 'CZE': 'CZ', 'GRC': 'EL', 'PRT': 'PT',
    'SWE': 'SE', 'HUN': 'HU', 'AUT': 'AT', 'BGR': 'BG', 'DNK': 'DK',
    'FIN': 'FI', 'SVK': 'SK', 'IRL': 'IE', 'HRV': 'HR', 'LTU': 'LT',
    'SVN': 'SI', 'LVA': 'LV', 'EST': 'EE', 'CYP': 'CY', 'LUX': 'LU',
    'MLT': 'MT', 'ROU': 'RO', 'NOR': 'NO', 'CHE': 'CH', 'ISL': 'IS',
    'LIE': 'LI'
  };

  // Memoised: only recomputes when selectedCountryId or source data changes
  const selectedCountry = useMemo(() =>
    countries.find(c => c.id === selectedCountryId) || (selectedCountryId ? {
      id: selectedCountryId,
      name: COUNTRY_NAMES[selectedCountryId] || 'Unknown Country',
      chargingDensity: 0,
      evMarketShare: 0,
      description: ''
    } : null),
    [countries, selectedCountryId]
  );

  const selectedSite = useMemo(
    () => sites.find(s => s.id === selectedSiteId),
    [sites, selectedSiteId]
  );

  const countryChargingStats = useMemo(() => {
    if (!selectedCountryId) return null;
    const iso2 = ISO3_TO_ISO2[selectedCountryId];
    const regions = nuts2Regions.filter(r => r.countryCode === iso2);
    if (regions.length === 0) return null;
    const totalChargepoints = regions.reduce((s, r) => s + r.chargepointCount, 0);
    const totalGrowth = regions.reduce((s, r) => s + r.growthCount12mo, 0);
    const totalInvestment = regions.reduce((s, r) => s + r.totalInvestment, 0);
    const baseline = regions.reduce((s, r) => s + r.countBefore2025, 0);
    return {
      totalChargepoints,
      totalGrowth,
      growthPercent: Math.round((baseline > 0 ? (totalGrowth / baseline * 100) : 0) * 10) / 10,
      totalInvestment,
    };
  }, [selectedCountryId, nuts2Regions]);

  const countryBatteryStats = useMemo(() => {
    if (!selectedCountryId) return null;
    const bSites = sites.filter(s => s.type === 'battery' && s.countryId === selectedCountryId);
    if (bSites.length === 0) return null;
    const sectors: Record<string, number> = {};
    bSites.forEach(s => { if (s.sector) sectors[s.sector] = (sectors[s.sector] || 0) + 1; });
    let total = 0, has = false;
    bSites.forEach(s => {
      if (s.capacityGwh && /gwh/i.test(s.capacityGwh)) {
        const m = s.capacityGwh.match(/(\d+(?:\.\d+)?)/);
        if (m) { total += parseFloat(m[1]); has = true; }
      }
    });
    return { siteCount: bSites.length, sectors, totalCapacityGwh: has ? Math.round(total * 10) / 10 : null };
  }, [selectedCountryId, sites]);

  const countryEvStats = useMemo(() => {
    if (!selectedCountryId) return null;
    const evSites = sites.filter(s => s.type === 'ev' && s.countryId === selectedCountryId);
    if (evSites.length === 0) return null;
    const mfg: Record<string, number> = {};
    evSites.forEach(s => { if (s.manufacturer) mfg[s.manufacturer] = (mfg[s.manufacturer] || 0) + 1; });
    const topManufacturers = Object.entries(mfg).sort((a, b) => b[1] - a[1]).slice(0, 4).map(([n]) => n);
    const prod = new Set<string>();
    evSites.forEach(s => {
      s.produces?.split(',').forEach(p => {
        const t = p.trim();
        if (t && !t.toLowerCase().includes('batter') && !t.toLowerCase().includes('engine')) prod.add(t);
      });
    });
    return { siteCount: evSites.length, topManufacturers, produces: [...prod] };
  }, [selectedCountryId, sites]);

  // Stable callbacks — prevent Map's useEffect from re-running on every render
  const handleCountrySelect = useCallback((id: string | null) => {
    setSelectedCountryId(id);
    if (id) { setSelectedSiteId(null); setSelectedRegionId(null); }
  }, []);

  const handleSiteSelect = useCallback((id: string | null) => {
    setSelectedSiteId(id);
    if (id) { setSelectedCountryId(null); setSelectedRegionId(null); }
  }, []);

  const handleRegionSelect = useCallback((id: string | null) => {
    setSelectedRegionId(id);
    if (id) { setSelectedCountryId(null); setSelectedSiteId(null); }
  }, []);

  const handleSidebarClose = useCallback(() => {
    setSelectedCountryId(null);
    setSelectedSiteId(null);
    setSelectedRegionId(null);
  }, []);

  return (
    <div className="flex h-screen w-screen bg-slate-50 overflow-hidden font-sans text-slate-900">
      {/* Main Content */}
      <main className="flex-1 relative flex flex-col">
        {/* Header */}
        <header className="absolute top-0 left-0 w-full px-4 sm:px-8 py-4 sm:py-8 z-10 pointer-events-none flex justify-between items-start">
          <div className="pointer-events-auto">
            <h1 className="text-2xl sm:text-4xl font-serif italic tracking-tight text-slate-900 mb-0.5 sm:mb-1 leading-tight">
              EU E-Mobility<br className="sm:hidden" /> Investment Map
            </h1>
            {/* Subtitle — hidden on mobile to save space */}
            <p className="hidden sm:block text-xs font-semibold text-slate-400 uppercase tracking-widest">
              Track the growth of Europe's multi-billion e-mobility industry
            </p>
            {/* Help + About links */}
            <div className="mt-2 sm:mt-3 flex items-center gap-3">
              <button
                onClick={() => { resetWelcome(); setShowWelcome(true); }}
                className="flex items-center gap-1.5 text-[10px] font-semibold text-slate-400 hover:text-slate-600 uppercase tracking-widest transition-colors"
              >
                <HelpCircle className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">How to use this map</span>
              </button>
              <span className="hidden sm:inline text-slate-200">·</span>
              <button
                onClick={() => setShowAbout(true)}
                className="flex items-center gap-1.5 text-[10px] font-semibold text-slate-400 hover:text-slate-600 uppercase tracking-widest transition-colors"
              >
                <Info className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">About the data</span>
              </button>
            </div>
          </div>

          {/* Layer Controls — desktop only; mobile uses bottom bar */}
          <div className="hidden sm:flex flex-col items-end gap-4 pointer-events-auto">
            <div className="flex flex-col gap-2">
              <LayerButton
                active={activeLayers.includes('investment')}
                onClick={() => toggleLayer('investment')}
                icon={<Zap className="w-4 h-4" />}
                label="Public Charging"
              />
              <LayerButton
                active={activeLayers.includes('battery')}
                onClick={() => toggleLayer('battery')}
                icon={<Battery className="w-4 h-4" />}
                label="Battery Manufacturing"
              />
              <LayerButton
                active={activeLayers.includes('ev')}
                onClick={() => toggleLayer('ev')}
                icon={<Factory className="w-4 h-4" />}
                label="EV Manufacturing"
              />
            </div>
          </div>
        </header>

        {/* Map Container */}
        <div className="flex-1">
          <Map
            countries={countries}
            sites={sites}
            nuts2Regions={nuts2Regions}
            activeLayers={activeLayers}
            selectedCountryId={selectedCountryId}
            selectedRegionId={selectedRegionId}
            onCountrySelect={handleCountrySelect}
            onSiteSelect={handleSiteSelect}
            onRegionSelect={handleRegionSelect}
          />
        </div>


      </main>

      {/* Sidebar */}
      <Sidebar
        country={selectedCountry}
        site={selectedSite}
        region={nuts2Regions.find(r => r.nutsId === selectedRegionId) || null}
        countryChargingStats={countryChargingStats}
        countryBatteryStats={countryBatteryStats}
        countryEvStats={countryEvStats}
        onClose={handleSidebarClose}
      />

      {/* Mobile Layer Bar — fixed bottom, visible on small screens only */}
      <div className="sm:hidden fixed bottom-0 left-0 right-0 z-20 bg-white/95 backdrop-blur-md border-t border-slate-200 px-3 py-2 flex gap-2 safe-bottom">
        <MobileLayerButton
          active={activeLayers.includes('investment')}
          onClick={() => toggleLayer('investment')}
          icon={<Zap className="w-4 h-4" />}
          label="Charging"
        />
        <MobileLayerButton
          active={activeLayers.includes('battery')}
          onClick={() => toggleLayer('battery')}
          icon={<Battery className="w-4 h-4" />}
          label="Battery"
        />
        <MobileLayerButton
          active={activeLayers.includes('ev')}
          onClick={() => toggleLayer('ev')}
          icon={<Factory className="w-4 h-4" />}
          label="EV"
        />
      </div>

      {/* Loading Overlay */}
      {loading && countries.length === 0 && (
        <div className="fixed inset-0 bg-slate-50 z-[100] flex items-center justify-center">
          <div className="flex flex-col items-center gap-4">
            <div className="w-12 h-12 border-4 border-emerald-500/20 border-t-emerald-500 rounded-full animate-spin" />
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-widest animate-pulse">Initializing Map Data</p>
          </div>
        </div>
      )}

      {/* Welcome Modal */}
      <AnimatePresence>
        {showWelcome && (
          <WelcomeModal onClose={() => setShowWelcome(false)} />
        )}
      </AnimatePresence>

      {/* About / Data Provenance Modal */}
      <AnimatePresence>
        {showAbout && (
          <AboutModal onClose={() => setShowAbout(false)} />
        )}
      </AnimatePresence>
    </div>
  );
}

interface LayerButtonProps {
  active: boolean;
  onClick: () => void;
  icon: React.ReactNode;
  label: string;
}

const LayerButton: React.FC<LayerButtonProps> = ({ active, onClick, icon, label }) => (
  <button
    onClick={onClick}
    className={cn(
      "flex items-center gap-3 px-4 py-2.5 rounded-full border transition-all shadow-sm text-xs font-medium",
      active 
        ? "bg-slate-900 border-slate-900 text-white shadow-slate-900/20" 
        : "bg-white/80 backdrop-blur-sm border-slate-200 text-slate-600 hover:bg-white"
    )}
  >
    {icon}
    {label}
  </button>
);

// Mobile bottom-bar layer button — full-width flex pill
interface MobileLayerButtonProps {
  active: boolean;
  onClick: () => void;
  icon: React.ReactNode;
  label: string;
}

const MobileLayerButton: React.FC<MobileLayerButtonProps> = ({ active, onClick, icon, label }) => (
  <button
    onClick={onClick}
    className={cn(
      "flex-1 flex flex-col items-center justify-center gap-1 py-2 rounded-xl border text-[10px] font-semibold transition-all",
      active
        ? "bg-slate-900 border-slate-900 text-white"
        : "bg-white border-slate-200 text-slate-500"
    )}
  >
    {icon}
    <span>{label}</span>
  </button>
);
