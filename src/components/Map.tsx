import React, { useEffect, useRef, useState, useMemo } from 'react';
import * as d3 from 'd3';
import { CountryStats, ManufacturingSite, MapLayer, NUTS2Region } from '../types';
import { cn } from '../utils';

interface MapProps {
  countries: CountryStats[];
  sites: ManufacturingSite[];
  nuts2Regions: NUTS2Region[];
  activeLayers: MapLayer[];
  selectedCountryId: string | null;
  selectedRegionId: string | null;
  onCountrySelect: (id: string | null) => void;
  onSiteSelect: (id: string | null) => void;
  onRegionSelect: (id: string | null) => void;
}

const ACTIVE_PROJECT_CODES = [
  'AUT', 'BEL', 'BGR', 'HRV', 'CYP', 'CZE', 'DNK', 'EST', 'FIN', 'FRA',
  'DEU', 'GRC', 'HUN', 'IRL', 'ITA', 'LVA', 'LTU', 'LUX', 'MLT', 'NLD',
  'POL', 'PRT', 'ROU', 'SVK', 'SVN', 'ESP', 'SWE', 'ISL', 'LIE', 'NOR', 'CHE'
];

// Fixed sector colour palette — 10 distinct colours that cycle if > 10 sectors
const SECTOR_PALETTE = [
  '#f97316', '#3b82f6', '#10b981', '#8b5cf6', '#ef4444',
  '#f59e0b', '#06b6d4', '#ec4899', '#84cc16', '#14b8a6',
];

const EUROSTAT_TO_ISO3: Record<string, string> = {
  'AT': 'AUT', 'BE': 'BEL', 'BG': 'BGR', 'HR': 'HRV', 'CY': 'CYP',
  'CZ': 'CZE', 'DK': 'DNK', 'EE': 'EST', 'FI': 'FIN', 'FR': 'FRA',
  'DE': 'DEU', 'EL': 'GRC', 'HU': 'HUN', 'IE': 'IRL', 'IT': 'ITA',
  'LV': 'LVA', 'LT': 'LTU', 'LU': 'LUX', 'MT': 'MLT', 'NL': 'NLD',
  'PL': 'POL', 'PT': 'PRT', 'RO': 'ROU', 'SK': 'SVK', 'SI': 'SVN',
  'ES': 'ESP', 'SE': 'SWE', 'IS': 'ISL', 'LI': 'LIE', 'NO': 'NOR', 'CH': 'CHE'
};

export const Map: React.FC<MapProps> = ({
  countries,
  sites,
  nuts2Regions,
  activeLayers,
  selectedCountryId,
  selectedRegionId,
  onCountrySelect,
  onSiteSelect,
  onRegionSelect
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [topoData, setTopoData] = useState<any>(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
  const [hoveredSite, setHoveredSite] = useState<{ site: ManufacturingSite; x: number; y: number } | null>(null);

  // Persistent D3 objects shared across split effects
  const gRef = useRef<any>(null);
  const projectionRef = useRef<{ projection: any; path: any } | null>(null);
  const zoomRef = useRef<any>(null);

  // Ref for selectedCountryId used in D3 click handlers — avoids stale closures
  // without adding selectedCountryId to Effect 1's dependency array
  const selectedCountryIdRef = useRef<string | null>(selectedCountryId);
  useEffect(() => { selectedCountryIdRef.current = selectedCountryId; }, [selectedCountryId]);

  // ── Load geo data + handle resize ──────────────────────────────────────────
  useEffect(() => {
    fetch('/NUTS_RG_01M_2024_4326.geojson')
      .then(res => res.json())
      .then(data => {
        const features = data.features
          .filter((f: any) => {
            const iso3 = EUROSTAT_TO_ISO3[f.properties.CNTR_CODE];
            return iso3 && ACTIVE_PROJECT_CODES.includes(iso3);
          })
          .map((f: any) => {
            const iso3 = EUROSTAT_TO_ISO3[f.properties.CNTR_CODE];
            const cntrCode = f.properties.CNTR_CODE;
            let geometry = f.geometry;

            if (cntrCode === 'FR' && geometry.type === 'MultiPolygon') {
              geometry = {
                ...geometry,
                coordinates: geometry.coordinates.filter((poly: any) => {
                  const [lng, lat] = poly[0][0];
                  return lng > -6 && lat > 41 && lat < 52;
                })
              };
            }
            if (cntrCode === 'NO' && geometry.type === 'MultiPolygon') {
              geometry = {
                ...geometry,
                coordinates: geometry.coordinates.filter((poly: any) => {
                  const lats = poly[0].map((c: any) => c[1]);
                  return lats.reduce((a: number, b: number) => a + b, 0) / lats.length < 74;
                })
              };
            }
            return {
              ...f, id: iso3, geometry,
              properties: { ...f.properties, name: f.properties.NAME_LATN || f.properties.NUTS_NAME }
            };
          });

        setTopoData({ type: 'FeatureCollection', features });
      })
      .catch(err => console.error('Error loading map data:', err));

    const handleResize = () => {
      if (svgRef.current?.parentElement) {
        setDimensions({
          width: svgRef.current.parentElement.clientWidth,
          height: svgRef.current.parentElement.clientHeight
        });
      }
    };
    window.addEventListener('resize', handleResize);
    handleResize();
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // ── Derived: colour scales ──────────────────────────────────────────────────
  const colorScale = useMemo(() => {
    const maxDensity = d3.max(countries, (d: CountryStats) => d.chargingDensity) || 100;
    return d3.scaleSequential(d3.interpolateYlGnBu).domain([0, maxDensity]);
  }, [countries]);

  const investmentColorScale = useMemo(() => {
    if (nuts2Regions.length === 0) return null;
    const values = nuts2Regions.filter(r => r.investmentDensity > 0).map(r => r.investmentDensity).sort((a, b) => a - b);
    if (values.length === 0) return null;
    // values is sorted ascending — last element is max
    const maxVal = values[values.length - 1] || 1000;
    return d3.scaleSequentialLog(d3.interpolateYlOrRd).domain([Math.max(values[0], 0.1), maxVal]);
  }, [nuts2Regions]);

  const sectorColorMap = useMemo((): Record<string, string> => {
    const sectors = Array.from(new Set<string>(
      sites.filter(s => s.type === 'battery' && typeof s.sector === 'string').map(s => s.sector as string)
    )).sort();
    const map: Record<string, string> = {};
    sectors.forEach((s, i) => { map[s] = SECTOR_PALETTE[i % SECTOR_PALETTE.length]; });
    return map;
  }, [sites]);

  // ── Effect 1: Base map ──────────────────────────────────────────────────────
  // Runs ONLY when geographic data or viewport changes.
  // Rebuilds SVG structure, projection, country shapes, and zoom.
  useEffect(() => {
    if (!topoData || topoData.features.length === 0 || dimensions.width === 0 || !svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();
    gRef.current = null;
    projectionRef.current = null;

    const projection = d3.geoConicConformal()
      .center([15, 52]).rotate([0, 0]).parallels([35, 65])
      .scale(dimensions.width * 0.8)
      .translate([dimensions.width / 2, dimensions.height / 2]);

    const path = d3.geoPath().projection(projection);
    projection.fitSize([dimensions.width - 100, dimensions.height - 100], topoData);

    const g = svg.append('g').attr('class', 'map-layer');
    gRef.current = g;
    projectionRef.current = { projection, path };

    svg.on('click', () => onCountrySelect(null));

    // Draw country paths with default fills (Effect 2 applies selection highlight)
    g.selectAll('path.country')
      .data(topoData.features)
      .enter()
      .append('path')
      .attr('class', (d: any) => cn(
        'country transition-colors duration-200 stroke-slate-300 stroke-[0.5px]',
        ACTIVE_PROJECT_CODES.includes(d.id) ? 'cursor-pointer hover:fill-slate-50' : 'cursor-default'
      ))
      .attr('fill', (d: any) => ACTIVE_PROJECT_CODES.includes(d.id) ? '#ffffff' : '#e2e8f0')
      .attr('d', path as any)
      .style('filter', 'drop-shadow(0 2px 4px rgba(0,0,0,0.1))')
      .on('click', (event, d: any) => {
        event.stopPropagation();
        if (ACTIVE_PROJECT_CODES.includes(d.id)) {
          // Use ref to avoid stale closure (Effect 1 doesn't re-run on selectedCountryId changes)
          onCountrySelect(selectedCountryIdRef.current === d.id ? null : d.id);
        }
      });

    const zoom = d3.zoom()
      .scaleExtent([1, 8])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
        // Keep site dots at a constant screen size regardless of zoom level
        const k = event.transform.k;
        g.selectAll('circle.site').attr('r', function() {
          return parseFloat((this as SVGCircleElement).getAttribute('data-base-r') || '5') / k;
        });
      });

    zoomRef.current = zoom;
    svg.call(zoom as any);

  }, [topoData, dimensions, onCountrySelect]);
  // ↑ selectedCountryId intentionally excluded — fills handled by Effect 2

  // ── Effect 2: Country selection highlight ───────────────────────────────────
  // Fast — only updates fill/class on existing paths. No geometry work.
  // Triggered independently when the user clicks a country.
  useEffect(() => {
    const g = gRef.current;
    if (!g) return;

    g.selectAll('path.country')
      .attr('fill', (d: any) => {
        if (!ACTIVE_PROJECT_CODES.includes(d.id)) return '#e2e8f0';
        return selectedCountryId === d.id ? '#10b981' : '#ffffff';
      })
      .attr('class', (d: any) => {
        const isActive = ACTIVE_PROJECT_CODES.includes(d.id);
        const isSelected = selectedCountryId === d.id;
        return cn(
          'country transition-colors duration-200 stroke-slate-300 stroke-[0.5px]',
          isActive ? 'cursor-pointer' : 'cursor-default',
          isActive && !isSelected ? 'hover:fill-slate-50' : ''
        );
      });
  }, [selectedCountryId, topoData, dimensions]);
  // ↑ topoData/dimensions ensure this runs after Effect 1 when the base map changes

  // ── Effect 3: NUTS2 investment layer ────────────────────────────────────────
  // Redraws only the NUTS2 overlay. Triggered by layer toggle or data changes.
  useEffect(() => {
    const g = gRef.current;
    const refs = projectionRef.current;
    if (!g || !refs) return;

    g.selectAll('path.nuts2').remove();

    if (!activeLayers.includes('investment') || nuts2Regions.length === 0 || !investmentColorScale) return;

    g.selectAll('path.nuts2')
      .data(nuts2Regions.filter(r => r.chargepointCount > 0))
      .enter()
      .append('path')
      .attr('class', 'nuts2 cursor-pointer transition-opacity')
      .attr('d', (d: NUTS2Region) => refs.path(d.geometry as any))
      .attr('fill', (d: NUTS2Region) => investmentColorScale(Math.max(d.investmentDensity, 1)))
      .attr('stroke', '#fff')
      .attr('stroke-width', (d: NUTS2Region) => selectedRegionId === d.nutsId ? 2 : 0.5)
      .attr('opacity', (d: NUTS2Region) => selectedRegionId === d.nutsId ? 1 : 0.7)
      .style('pointer-events', 'all')
      .on('click', (event, d: NUTS2Region) => {
        event.stopPropagation();
        onRegionSelect(selectedRegionId === d.nutsId ? null : d.nutsId);
      })
      .on('mouseover', function() { d3.select(this).attr('opacity', 0.9); })
      .on('mouseout', function(event, d: NUTS2Region) {
        d3.select(this).attr('opacity', selectedRegionId === d.nutsId ? 1 : 0.7);
      });

  }, [topoData, dimensions, activeLayers, nuts2Regions, investmentColorScale, selectedRegionId, onRegionSelect]);

  // ── Effect 4: Manufacturing sites layer ─────────────────────────────────────
  // Redraws only site circles. Triggered by layer toggle or data changes.
  useEffect(() => {
    const g = gRef.current;
    const refs = projectionRef.current;
    if (!g || !refs) return;

    g.selectAll('circle.site').remove();

    if (!activeLayers.includes('battery') && !activeLayers.includes('ev')) return;

    const filteredSites = sites.filter(s => activeLayers.includes(s.type));

    const getSiteFill = (d: ManufacturingSite): string => {
      if (d.type === 'ev') return '#6366f1';
      const sector = d.sector;
      if (sector && sector in sectorColorMap) return sectorColorMap[sector];
      return '#f97316';
    };

    // Base radii — kept intentionally small; zoom-invariant scaling prevents them growing on zoom
    const getSiteRadius = (d: ManufacturingSite): number => {
      if (d.type === 'ev') return 4;
      return (d.subtype || '').toLowerCase().includes('gigafactor') ? 6 : 5;
    };

    g.selectAll('circle.site')
      .data(filteredSites)
      .enter()
      .append('circle')
      .attr('class', 'site cursor-pointer transition-all duration-300')
      .attr('cx', (d: any) => refs.projection([(d as ManufacturingSite).location.lng, (d as ManufacturingSite).location.lat])?.[0] || 0)
      .attr('cy', (d: any) => refs.projection([(d as ManufacturingSite).location.lng, (d as ManufacturingSite).location.lat])?.[1] || 0)
      .attr('r', (d: any) => getSiteRadius(d as ManufacturingSite))
      .attr('data-base-r', (d: any) => getSiteRadius(d as ManufacturingSite))
      .attr('fill', (d: any) => getSiteFill(d as ManufacturingSite))
      .attr('stroke', '#fff')
      .attr('stroke-width', 1.5)
      .style('filter', 'drop-shadow(0 0 2px rgba(0,0,0,0.2))')
      .on('mouseover', (event, d: any) => {
        const [x, y] = d3.pointer(event, svgRef.current);
        setHoveredSite({ site: d as ManufacturingSite, x, y });
      })
      .on('mousemove', (event, d: any) => {
        const [x, y] = d3.pointer(event, svgRef.current);
        setHoveredSite({ site: d as ManufacturingSite, x, y });
      })
      .on('mouseout', () => setHoveredSite(null))
      .on('click', (event, d: any) => {
        event.stopPropagation();
        onSiteSelect((d as ManufacturingSite).id);
      });

  }, [topoData, dimensions, activeLayers, sites, sectorColorMap, onSiteSelect]);

  // ── Zoom reset ─────────────────────────────────────────────────────────────
  const resetZoom = () => {
    if (svgRef.current && zoomRef.current) {
      d3.select(svgRef.current)
        .transition()
        .duration(750)
        .call(zoomRef.current.transform, d3.zoomIdentity);
    }
  };

  return (
    <div className="w-full h-full bg-slate-200 relative overflow-hidden shadow-inner">
      <svg
        ref={svgRef}
        className="w-full h-full"
        viewBox={`0 0 ${dimensions.width} ${dimensions.height}`}
      />

      {/* Zoom Controls — raised above mobile bottom bar */}
      <div className="absolute bottom-20 right-4 sm:bottom-8 sm:right-8 flex flex-col gap-2 pointer-events-auto">
        <button
          onClick={resetZoom}
          className="bg-white/90 backdrop-blur-sm p-3 rounded-xl border border-slate-200 shadow-sm hover:bg-white transition-all text-slate-600"
          title="Reset View"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4h16v16H4z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v8m-4-4h8" />
          </svg>
        </button>
      </div>

      {/* Legends — raised above mobile bottom bar on small screens */}
      <div className="absolute bottom-20 left-4 sm:bottom-8 sm:left-8 flex flex-col gap-3">
        {activeLayers.includes('investment') && (
          <div className="bg-white/80 backdrop-blur-sm p-4 rounded-xl border border-slate-200 shadow-sm">
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Investment by Region</div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] text-slate-400">Low</span>
              <div className="h-2 w-32 rounded-full bg-gradient-to-r from-[#ffffe5] via-[#feb24c] to-[#b10026]" />
              <span className="text-[10px] text-slate-400">High</span>
            </div>
            <div className="text-[9px] text-slate-400 mt-2">NUTS2 Regions (€/km²)</div>
          </div>
        )}

        {(activeLayers.includes('battery') || activeLayers.includes('ev')) && (
          <div className="flex flex-col gap-2">
            {activeLayers.includes('battery') && Object.keys(sectorColorMap).length > 0 && (
              <div className="bg-white/80 backdrop-blur-sm px-3 py-2 rounded-xl border border-slate-200 shadow-sm">
                <div className="text-[9px] font-bold text-slate-400 uppercase tracking-widest mb-2">Battery Sector</div>
                {/* Scrollable on mobile so it doesn't overflow the screen */}
                <div className="flex flex-col gap-1.5 max-h-32 sm:max-h-none overflow-y-auto">
                  {Object.entries(sectorColorMap).map(([sector, colour]) => (
                    <div key={sector} className="flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: colour }} />
                      <span className="text-[10px] font-medium text-slate-600 leading-tight">{sector}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {activeLayers.includes('battery') && Object.keys(sectorColorMap).length === 0 && (
              <div className="flex items-center gap-2 bg-white/80 backdrop-blur-sm px-3 py-1.5 rounded-full border border-slate-200 shadow-sm">
                <div className="w-2 h-2 rounded-full bg-orange-500" />
                <span className="text-xs font-medium text-slate-600">Battery Manufacturing</span>
              </div>
            )}
            {activeLayers.includes('ev') && (
              <div className="flex items-center gap-2 bg-white/80 backdrop-blur-sm px-3 py-1.5 rounded-full border border-slate-200 shadow-sm">
                <div className="w-2 h-2 rounded-full bg-indigo-500" />
                <span className="text-xs font-medium text-slate-600">EV Manufacturing</span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Hover Tooltip */}
      {hoveredSite && (
        <div
          className="absolute z-50 pointer-events-none bg-slate-900/95 backdrop-blur-md text-white p-4 rounded-xl shadow-xl border border-white/10 max-w-sm"
          style={{ left: hoveredSite.x + 15, top: hoveredSite.y - 15, transform: 'translateY(-50%)' }}
        >
          <div className="flex items-center gap-2 mb-2">
            <div className={cn(
              "w-2.5 h-2.5 rounded-full",
              hoveredSite.site.type === 'battery' ? "bg-orange-500" : "bg-indigo-500"
            )} />
            <h4 className="text-base font-bold tracking-tight">{hoveredSite.site.name}</h4>
          </div>
          <div className="space-y-3">
            {hoveredSite.site.manufacturer && (
              <div>
                <span className="text-[9px] font-bold uppercase tracking-widest text-slate-500 block">Manufacturer</span>
                <span className="text-xs text-slate-200">{hoveredSite.site.manufacturer}</span>
              </div>
            )}
            {hoveredSite.site.produces && (
              <div>
                <span className="text-[9px] font-bold uppercase tracking-widest text-slate-500 block">Produces</span>
                <span className="text-xs text-slate-200">{hoveredSite.site.produces}</span>
              </div>
            )}
            {hoveredSite.site.brands && (
              <div>
                <span className="text-[9px] font-bold uppercase tracking-widest text-slate-500 block">Brands</span>
                <span className="text-xs text-slate-200 italic">{hoveredSite.site.brands}</span>
              </div>
            )}
          </div>
          <div className="mt-3 pt-3 border-t border-white/10 flex justify-between items-center">
            <span className="text-[9px] font-bold uppercase tracking-widest text-slate-500">
              {hoveredSite.site.type === 'battery' ? 'Battery Plant' : 'EV Assembly'}
            </span>
            <span className="text-[9px] font-bold text-slate-400">{hoveredSite.site.countryId}</span>
          </div>
        </div>
      )}
    </div>
  );
};
