import React from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { X, Zap, Factory, Battery, TrendingUp, MapPin, Euro, Recycle, CalendarDays, Users, FlaskConical, Globe, BarChart3 } from 'lucide-react';
import { cn } from '../utils';
import { CountryStats, ManufacturingSite, NUTS2Region } from '../types';

// ── Subtype label helpers ────────────────────────────────────────────────────
const SUBTYPE_LABELS: Record<string, string> = {
  gigafactory: 'Gigafactory',
  recycling: 'Recycling Plant',
  'pack-assembly': 'Pack Assembly',
  'r-d-pilot': 'R&D / Pilot',
};

const subtypeLabel = (raw?: string) =>
  raw ? (SUBTYPE_LABELS[raw] ?? raw.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase())) : null;

const subtypeColor = (raw?: string) => {
  if (!raw) return 'bg-orange-100 text-orange-700';
  if (raw.includes('recycl')) return 'bg-teal-100 text-teal-700';
  if (raw.includes('gigafactor')) return 'bg-orange-100 text-orange-700';
  if (raw.includes('pack') || raw.includes('assembly')) return 'bg-amber-100 text-amber-700';
  return 'bg-slate-100 text-slate-600';
};

// ── Battery Site Content ─────────────────────────────────────────────────────
const BatterySiteContent: React.FC<{ site: ManufacturingSite }> = ({ site }) => (
  <div className="space-y-8">
    {/* Subtype badge */}
    {site.subtype && (
      <div className="flex items-center gap-2">
        <span className={cn('text-[10px] font-bold px-2.5 py-1 rounded-full uppercase tracking-widest', subtypeColor(site.subtype))}>
          {subtypeLabel(site.subtype)}
        </span>
      </div>
    )}

    {/* Key stats grid */}
    <div className="grid grid-cols-1 gap-4">
      {site.manufacturer && (
        <div className="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em] block mb-1">Operator</span>
          <div className="text-lg font-medium text-slate-900">{site.manufacturer}</div>
        </div>
      )}

      {/* Capacity — current & 2030 side by side if both present */}
      {(site.capacityGwh || site.capacityGwh2030) && (
        <div className="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm">
          <div className="flex items-center gap-2 mb-3">
            <div className="p-1.5 bg-orange-50 rounded-lg">
              <Battery className="w-4 h-4 text-orange-600" />
            </div>
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em]">Capacity</span>
          </div>
          <div className="flex items-end gap-4 flex-wrap">
            {site.capacityGwh && (
              <div>
                <div className="text-base font-mono font-semibold text-slate-900 break-words">{site.capacityGwh}</div>
                <div className="text-[10px] text-slate-400 mt-0.5">Current</div>
              </div>
            )}
            {site.capacityGwh && site.capacityGwh2030 && (
              <div className="text-slate-200 text-base font-light mb-1">→</div>
            )}
            {site.capacityGwh2030 && (
              <div>
                <div className="text-base font-mono font-semibold text-orange-600 break-words">{site.capacityGwh2030}</div>
                <div className="text-[10px] text-slate-400 mt-0.5">By 2030</div>
              </div>
            )}
          </div>
          {site.capacityCategory && (
            <div className="mt-2 text-xs text-slate-500">
              Tier: <span className="font-medium text-slate-700">{site.capacityCategory}</span>
              {site.capacityCategory2030 && site.capacityCategory2030 !== site.capacityCategory && (
                <span> → <span className="font-medium text-orange-600">{site.capacityCategory2030}</span></span>
              )}
            </div>
          )}
        </div>
      )}

      {site.materials && (
        <div className="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm">
          <div className="flex items-center gap-2 mb-2">
            <div className="p-1.5 bg-purple-50 rounded-lg">
              <FlaskConical className="w-4 h-4 text-purple-600" />
            </div>
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em]">Cell Chemistry</span>
          </div>
          <div className="text-sm font-medium text-slate-900">{site.materials}</div>
        </div>
      )}

      {site.investmentAmount && (
        <div className="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm">
          <div className="flex items-center gap-2 mb-2">
            <div className="p-1.5 bg-emerald-50 rounded-lg">
              <Euro className="w-4 h-4 text-emerald-600" />
            </div>
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em]">Investment</span>
          </div>
          <div className="text-base font-mono font-medium text-emerald-700 leading-snug">
            {site.investmentAmount}
          </div>
        </div>
      )}

      {/* Jobs */}
      {(site.jobsActual || site.jobs2030) && (
        <div className="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm">
          <div className="flex items-center gap-2 mb-3">
            <div className="p-1.5 bg-blue-50 rounded-lg">
              <Users className="w-4 h-4 text-blue-600" />
            </div>
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em]">Jobs</span>
          </div>
          <div className="flex items-end gap-4">
            {site.jobsActual && (
              <div>
                <div className="text-xl font-mono font-semibold text-slate-900">{site.jobsActual}</div>
                <div className="text-[10px] text-slate-400 mt-0.5">Current</div>
              </div>
            )}
            {site.jobsActual && site.jobs2030 && (
              <div className="text-slate-200 text-xl font-light mb-1">→</div>
            )}
            {site.jobs2030 && (
              <div>
                <div className="text-xl font-mono font-semibold text-blue-600">{site.jobs2030}</div>
                <div className="text-[10px] text-slate-400 mt-0.5">By 2030</div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Recovery rate for recycling plants */}
      {site.recoveryRate && (
        <div className="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm">
          <div className="flex items-center gap-2 mb-2">
            <div className="p-1.5 bg-teal-50 rounded-lg">
              <Recycle className="w-4 h-4 text-teal-600" />
            </div>
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em]">Recovery Rate</span>
          </div>
          <div className="text-lg font-mono font-medium text-teal-700">{site.recoveryRate}</div>
        </div>
      )}

      {/* Opening year */}
      {site.openingYear && (
        <div className="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm">
          <div className="flex items-center gap-2 mb-2">
            <div className="p-1.5 bg-slate-50 rounded-lg">
              <CalendarDays className="w-4 h-4 text-slate-500" />
            </div>
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em]">Opening Year</span>
          </div>
          <div className="text-xl font-mono font-semibold text-slate-900">{site.openingYear}</div>
        </div>
      )}
    </div>

    {/* Description */}
    {site.description && (
      <div>
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-3">Overview</h3>
        <p className="text-sm text-slate-600 leading-relaxed">{site.description}</p>
      </div>
    )}

    {/* Additional details row */}
    {(site.companyOriginCountry || site.companyOriginArea) && (
      <div className="pt-4 border-t border-slate-100">
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-3">Company Origin</h3>
        <div className="space-y-2">
          {site.companyOriginCountry && (
            <div className="flex justify-between items-center text-sm">
              <span className="text-slate-500">Country</span>
              <span className="font-medium text-slate-900">{site.companyOriginCountry}</span>
            </div>
          )}
          {site.companyOriginArea && (
            <div className="flex justify-between items-center text-sm">
              <span className="text-slate-500">Region</span>
              <span className="font-medium text-slate-900">{site.companyOriginArea}</span>
            </div>
          )}
        </div>
      </div>
    )}

  </div>
);

// ── Main Sidebar ─────────────────────────────────────────────────────────────
interface SidebarProps {
  country: CountryStats | null;
  site: ManufacturingSite | null;
  region: NUTS2Region | null;
  countryChargingStats: {
    totalChargepoints: number;
    totalGrowth: number;
    growthPercent: number;
    totalInvestment: number;
  } | null;
  countryBatteryStats: {
    siteCount: number;
    sectors: Record<string, number>;
    totalCapacityGwh: number | null;
  } | null;
  countryEvStats: {
    siteCount: number;
    topManufacturers: string[];
    produces: string[];
  } | null;
  onClose: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  country, site, region,
  countryChargingStats, countryBatteryStats, countryEvStats,
  onClose
}) => {
  const activeItem = country || site || region;
  const isSite = !!site;
  const isRegion = !!region;

  return (
    <AnimatePresence>
      {activeItem && (
        <motion.div
          key={activeItem.id}
          initial={{ x: '100%' }}
          animate={{ x: 0 }}
          exit={{ x: '100%' }}
          transition={{ type: 'spring', damping: 25, stiffness: 200 }}
          className="fixed top-0 right-0 h-full w-full sm:w-96 bg-white/95 backdrop-blur-md shadow-2xl z-50 overflow-y-auto border-l border-slate-200"
        >
          <div className="p-8">
            <div className="flex justify-between items-start mb-10">
              <div className="flex-1 pr-4">
                {isSite && (
                  <div className="flex items-center gap-2 mb-2 flex-wrap">
                    <div className={cn(
                      "w-2.5 h-2.5 rounded-full flex-shrink-0",
                      site.type === 'battery' ? "bg-orange-500" : "bg-indigo-500"
                    )} />
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                      {site.type === 'battery' ? 'Battery Plant' : 'EV Assembly'}
                    </span>
                    {site.type === 'battery' && site.sector && (
                      <span className="text-[10px] font-semibold text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full">
                        {site.sector}
                      </span>
                    )}
                  </div>
                )}
                <h2 className="text-4xl font-serif italic text-slate-900 leading-tight">
                  {isSite ? site.name : isRegion ? region!.nutsName : country!.name}
                </h2>
                {isSite && (
                  <p className="text-sm text-slate-500 mt-1 flex items-center gap-2">
                    <Globe className="w-3 h-3" />
                    {site.city && `${site.city}, `}{site.countryId}
                  </p>
                )}
              </div>
              <button
                onClick={onClose}
                className="p-2.5 hover:bg-slate-100 rounded-full transition-all text-slate-400 hover:text-slate-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="space-y-10">
              {isSite ? (
                site.type === 'battery' ? (
                  /* ── BATTERY SITE ── */
                  <BatterySiteContent site={site} />
                ) : (
                  /* ── EV ASSEMBLY SITE ── */
                  <div className="space-y-8">
                    <div className="grid grid-cols-1 gap-6">
                      {site.manufacturer && (
                        <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm">
                          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em] block mb-2">Manufacturer</span>
                          <div className="text-xl font-medium text-slate-900">{site.manufacturer}</div>
                        </div>
                      )}
                      {site.produces && (
                        <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm">
                          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em] block mb-2">Produces</span>
                          <div className="text-lg text-slate-700 leading-relaxed">{site.produces}</div>
                        </div>
                      )}
                      {site.brands && (
                        <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm">
                          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em] block mb-2">Brands</span>
                          <div className="text-lg text-slate-700 italic">{site.brands}</div>
                        </div>
                      )}
                      {site.investmentAmount && (
                        <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm">
                          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em] block mb-2">Investment</span>
                          <div className="text-2xl font-mono font-medium text-emerald-600">{site.investmentAmount}</div>
                        </div>
                      )}
                    </div>
                    {site.evConversionPlans && (
                      <div>
                        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-4">EV Conversion Plans</h3>
                        <p className="text-slate-600 leading-relaxed font-sans">{site.evConversionPlans}</p>
                      </div>
                    )}
                  </div>
                )
              ) : isRegion ? (
                <div className="space-y-8">
                  {/* Region Stats Grid */}
                  <div className="grid grid-cols-1 gap-6">
                    <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm">
                      <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 bg-emerald-50 rounded-xl">
                          <Zap className="w-5 h-5 text-emerald-600" />
                        </div>
                        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em]">Total Chargepoints</span>
                      </div>
                      <div className="text-3xl font-mono font-medium text-slate-900">
                        {region!.chargepointCount.toLocaleString()}
                      </div>
                    </div>

                    <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm">
                      <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 bg-indigo-50 rounded-xl">
                          <Euro className="w-5 h-5 text-indigo-600" />
                        </div>
                        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em]">Total Investment</span>
                      </div>
                      <div className="text-3xl font-mono font-medium text-slate-900">
                        €{(region!.totalInvestment / 1_000_000).toFixed(1)}M
                      </div>
                    </div>

                    <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm">
                      <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 bg-orange-50 rounded-xl">
                          <MapPin className="w-5 h-5 text-orange-600" />
                        </div>
                        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em]">Investment Density</span>
                      </div>
                      <div className="text-2xl font-mono font-medium text-slate-900 break-words">
                        {region!.investmentDensity > 1_000_000 ? (
                          <>
                            €{(region!.investmentDensity / 1_000).toFixed(0)}K
                            <span className="text-sm font-normal text-slate-400 ml-2">/km²</span>
                            <div className="text-xs text-orange-500 mt-2">⚠️ Area data may need recalculation</div>
                          </>
                        ) : (
                          <>
                            €{region!.investmentDensity.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                            <span className="text-sm font-normal text-slate-400 ml-2">/km²</span>
                          </>
                        )}
                      </div>
                    </div>

                    <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm">
                      <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 bg-green-50 rounded-xl">
                          <TrendingUp className="w-5 h-5 text-green-600" />
                        </div>
                        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em]">12-Month Growth</span>
                      </div>
                      <div className="flex items-baseline gap-2">
                        <div className="text-3xl font-mono font-medium text-slate-900">
                          +{region!.growthCount12mo.toLocaleString()}
                        </div>
                        <div className="text-lg font-mono font-medium text-green-600">
                          (+{region!.growthPercent12mo}%)
                        </div>
                      </div>
                      <div className="text-xs text-slate-400 mt-2">Jan 2025 - Jan 2026</div>
                    </div>
                  </div>

                  {/* Region Info */}
                  <div>
                    <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-4">Region Details</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-slate-500">Country</span>
                        <span className="text-sm font-medium text-slate-900">{region!.countryCode}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-slate-500">Area</span>
                        <span className="text-sm font-medium text-slate-900">{region!.areaKm2.toLocaleString()} km²</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-slate-500">NUTS ID</span>
                        <span className="text-sm font-mono font-medium text-slate-900">{region!.nutsId}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                /* ── COUNTRY PANEL ── */
                <div className="space-y-8">

                  {/* Headline: manufacturing footprint */}
                  {(countryBatteryStats || countryEvStats) && (
                    <div className="bg-slate-900 text-white rounded-3xl p-6">
                      <div className="flex items-center gap-2 mb-3">
                        <BarChart3 className="w-4 h-4 text-slate-400" />
                        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em]">E-Mobility Footprint</span>
                      </div>
                      <div className="text-4xl font-mono font-bold text-white">
                        {(countryBatteryStats?.siteCount ?? 0) + (countryEvStats?.siteCount ?? 0)}
                      </div>
                      <div className="text-sm text-slate-300 mt-1">
                        manufacturing {(countryBatteryStats?.siteCount ?? 0) + (countryEvStats?.siteCount ?? 0) === 1 ? 'site' : 'sites'} tracked
                        {countryBatteryStats && countryEvStats && (
                          <span className="text-slate-400"> — {countryBatteryStats.siteCount} battery · {countryEvStats.siteCount} EV</span>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Battery Supply Chain */}
                  {countryBatteryStats && (
                    <div>
                      <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                        <Battery className="w-3.5 h-3.5" /> Battery Supply Chain
                      </h3>
                      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
                        <div className="p-5 border-b border-slate-50">
                          <div className="text-2xl font-mono font-semibold text-slate-900">{countryBatteryStats.siteCount}</div>
                          <div className="text-xs text-slate-400 mt-0.5">
                            {countryBatteryStats.siteCount === 1 ? 'site' : 'sites'} in battery supply chain
                          </div>
                          {countryBatteryStats.totalCapacityGwh !== null && (
                            <div className="mt-2 text-sm text-slate-600">
                              ~<span className="font-mono font-semibold">{countryBatteryStats.totalCapacityGwh} GWh</span>
                              <span className="text-slate-400 text-xs ml-1">combined est. capacity</span>
                            </div>
                          )}
                        </div>
                        {Object.keys(countryBatteryStats.sectors).length > 0 && (
                          <div className="p-5">
                            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em] mb-3">Sectors</div>
                            <div className="flex flex-col gap-2">
                              {Object.entries(countryBatteryStats.sectors).map(([sector, count]) => (
                                <div key={sector} className="flex justify-between items-center text-sm">
                                  <span className="text-slate-600">{sector}</span>
                                  <span className="font-mono font-medium text-slate-900 tabular-nums">{count}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* EV Manufacturing */}
                  {countryEvStats && (
                    <div>
                      <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                        <Factory className="w-3.5 h-3.5" /> EV Manufacturing
                      </h3>
                      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
                        <div className="p-5 border-b border-slate-50">
                          <div className="text-2xl font-mono font-semibold text-slate-900">{countryEvStats.siteCount}</div>
                          <div className="text-xs text-slate-400 mt-0.5">
                            {countryEvStats.siteCount === 1 ? 'assembly plant' : 'assembly plants'}
                          </div>
                          {countryEvStats.produces.length > 0 && (
                            <div className="mt-2 flex flex-wrap gap-1.5">
                              {countryEvStats.produces.map(p => (
                                <span key={p} className="text-[10px] font-medium bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded-full">
                                  {p}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                        {countryEvStats.topManufacturers.length > 0 && (
                          <div className="p-5">
                            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em] mb-3">Key Manufacturers</div>
                            <div className="flex flex-col gap-2">
                              {countryEvStats.topManufacturers.map(m => (
                                <div key={m} className="text-sm text-slate-700 font-medium">{m}</div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Public Charging */}
                  {countryChargingStats && countryChargingStats.totalChargepoints > 0 && (
                    <div>
                      <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                        <Zap className="w-3.5 h-3.5" /> Public Charging
                      </h3>
                      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
                        <div className="p-5 border-b border-slate-50">
                          <div className="text-2xl font-mono font-semibold text-slate-900">
                            {countryChargingStats.totalChargepoints.toLocaleString()}
                          </div>
                          <div className="text-xs text-slate-400 mt-0.5">public chargepoints</div>
                        </div>
                        <div className="p-5 grid grid-cols-2 gap-4">
                          <div>
                            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em] mb-1">12-Month Growth</div>
                            <div className="text-lg font-mono font-semibold text-green-600">
                              +{countryChargingStats.growthPercent}%
                            </div>
                            <div className="text-xs text-slate-400">+{countryChargingStats.totalGrowth.toLocaleString()} points</div>
                          </div>
                          <div>
                            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em] mb-1">Est. Investment</div>
                            <div className="text-lg font-mono font-semibold text-slate-900">
                              {countryChargingStats.totalInvestment >= 1_000_000_000
                                ? `€${(countryChargingStats.totalInvestment / 1_000_000_000).toFixed(1)}B`
                                : `€${(countryChargingStats.totalInvestment / 1_000_000).toFixed(0)}M`}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* No data fallback */}
                  {!countryBatteryStats && !countryEvStats && !countryChargingStats && (
                    <p className="text-sm text-slate-400 italic">
                      No detailed data available for this country yet. Enable the layer toggles to explore available data.
                    </p>
                  )}
                </div>
              )}
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
