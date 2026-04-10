import React from 'react';
import { motion } from 'motion/react';
import { X, Zap, Battery, Factory, AlertTriangle, Mail, ExternalLink } from 'lucide-react';

interface AboutModalProps {
  onClose: () => void;
}

export const AboutModal: React.FC<AboutModalProps> = ({ onClose }) => {
  return (
    <div className="fixed inset-0 z-[200] flex items-center justify-center p-4">
      {/* Overlay */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="absolute inset-0 bg-slate-900/60 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 10 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 10 }}
        transition={{ type: 'spring', damping: 28, stiffness: 280 }}
        className="relative bg-white rounded-3xl shadow-2xl w-full max-w-lg max-h-[85vh] overflow-y-auto"
        onClick={e => e.stopPropagation()}
      >
        {/* Close button */}
        <div className="sticky top-0 bg-white/95 backdrop-blur-sm px-8 pt-8 pb-4 flex items-start justify-between border-b border-slate-100 z-10">
          <div>
            <h2 className="text-2xl font-serif italic text-slate-900 leading-tight">About the Data</h2>
            <p className="text-xs text-slate-400 mt-1 font-medium">Sources, methodology &amp; disclaimer</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-full text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-all flex-shrink-0 ml-4"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="px-8 py-6 space-y-8">

          {/* About */}
          <section>
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-[0.15em] mb-3">About this map</h3>
            <p className="text-sm text-slate-600 leading-relaxed">
              The EU E-Mobility Investment Map is published by{' '}
              <span className="font-semibold text-slate-800">[PUBLISHER NAME]</span>.
              It tracks investment and infrastructure across three pillars of Europe's e-mobility
              sector: public charging infrastructure, battery manufacturing, and electric vehicle
              assembly. All data is correct as of <span className="font-semibold text-slate-800">January 2026</span>.
            </p>
          </section>

          {/* Data Sources */}
          <section>
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-[0.15em] mb-4">Data Sources</h3>
            <div className="space-y-4">

              {/* Public Charging */}
              <div className="bg-slate-50 rounded-2xl p-5">
                <div className="flex items-center gap-2.5 mb-2">
                  <div className="p-1.5 bg-emerald-100 rounded-lg flex-shrink-0">
                    <Zap className="w-4 h-4 text-emerald-600" />
                  </div>
                  <span className="text-sm font-semibold text-slate-800">Public Charging Infrastructure</span>
                </div>
                <p className="text-sm text-slate-600 leading-relaxed">
                  New AutoMotive analysis of data on public chargepoints across Europe,
                  aggregated to NUTS2 regional level. Includes chargepoint counts, 12-month
                  growth, and estimated infrastructure investment.
                </p>
                <p className="text-[11px] text-slate-400 font-medium mt-2">
                  Data correct as of January 2026
                </p>
              </div>

              {/* Battery Manufacturing */}
              <div className="bg-slate-50 rounded-2xl p-5">
                <div className="flex items-center gap-2.5 mb-2">
                  <div className="p-1.5 bg-orange-100 rounded-lg flex-shrink-0">
                    <Battery className="w-4 h-4 text-orange-600" />
                  </div>
                  <span className="text-sm font-semibold text-slate-800">Battery Manufacturing</span>
                </div>
                <p className="text-sm text-slate-600 leading-relaxed">
                  Sourced from New AutoMotive's European Battery Tracker — a curated database
                  of battery supply chain projects across Europe, covering gigafactories,
                  recycling plants, pack assembly facilities, and R&amp;D pilot sites.
                </p>
                <a
                  href="https://battery-tracker.newautomotive.org"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-600 hover:text-emerald-700 transition-colors mt-2"
                >
                  battery-tracker.newautomotive.org
                  <ExternalLink className="w-3 h-3" />
                </a>
                <p className="text-[11px] text-slate-400 font-medium mt-2">
                  Data correct as of January 2026
                </p>
              </div>

              {/* EV Manufacturing */}
              <div className="bg-slate-50 rounded-2xl p-5">
                <div className="flex items-center gap-2.5 mb-2">
                  <div className="p-1.5 bg-indigo-100 rounded-lg flex-shrink-0">
                    <Factory className="w-4 h-4 text-indigo-600" />
                  </div>
                  <span className="text-sm font-semibold text-slate-800">EV Manufacturing</span>
                </div>
                <p className="text-sm text-slate-600 leading-relaxed">
                  New AutoMotive analysis of publicly available information, including company
                  announcements, regulatory filings, and industry reports, supplemented by
                  information from industry sources.
                </p>
                <p className="text-[11px] text-slate-400 font-medium mt-2">
                  Data correct as of January 2026
                </p>
              </div>
            </div>
          </section>

          {/* Disclaimer */}
          <section>
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-[0.15em] mb-3">Disclaimer</h3>
            <div className="bg-amber-50 border border-amber-100 rounded-2xl p-5">
              <div className="flex items-start gap-3">
                <AlertTriangle className="w-4 h-4 text-amber-500 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-slate-600 leading-relaxed">
                  All information is provided in good faith and is believed to be accurate as
                  of January 2026. Investment figures are estimates where not publicly confirmed
                  and should be treated as indicative only. This map is for informational
                  purposes only and does not constitute investment, financial, or legal advice.
                  [PUBLISHER NAME] accepts no liability for decisions made on the basis of
                  information presented here.
                </p>
              </div>
            </div>
          </section>

          {/* Contact */}
          <section className="pb-2">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-[0.15em] mb-3">Data Corrections &amp; Updates</h3>
            <p className="text-sm text-slate-600 leading-relaxed mb-3">
              If you believe any information is inaccurate or out of date, please get in touch.
            </p>
            <a
              href="mailto:data@newautomotive.org"
              className="inline-flex items-center gap-2 bg-slate-900 text-white text-sm font-semibold px-5 py-2.5 rounded-full hover:bg-slate-700 transition-all"
            >
              <Mail className="w-4 h-4" />
              data@newautomotive.org
            </a>
          </section>

        </div>
      </motion.div>
    </div>
  );
};
