import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { X, Zap, Battery, Factory, Globe, ChevronLeft, ChevronRight, Map } from 'lucide-react';
import { cn } from '../utils';

const STORAGE_KEY = 'em-map-welcome-seen';

// ── Card data ────────────────────────────────────────────────────────────────
interface Card {
  icon: React.ReactNode;
  iconBg: string;
  title: string;
  body: string;
  hint?: string; // small contextual note
}

const CARDS: Card[] = [
  {
    icon: <Map className="w-7 h-7 text-slate-700" />,
    iconBg: 'bg-slate-100',
    title: 'EU E-Mobility Investment Map',
    body: 'Explore the growth of Europe\'s multi-billion euro e-mobility sector — from public charging infrastructure to battery gigafactories and EV assembly plants.',
  },
  {
    icon: <Zap className="w-7 h-7 text-emerald-600" />,
    iconBg: 'bg-emerald-50',
    title: 'Public Charging Layer',
    body: 'Toggle on the Public Charging layer to see a heatmap of charging infrastructure investment intensity across NUTS2 regions.',
    hint: 'Click any coloured region to see chargepoint counts, 12-month growth, and estimated investment for that area.',
  },
  {
    icon: <Battery className="w-7 h-7 text-orange-600" />,
    iconBg: 'bg-orange-50',
    title: 'Battery Manufacturing',
    body: 'The Battery Manufacturing layer shows gigafactories, recycling plants, pack assembly facilities, and R&D sites across Europe, colour-coded by sector.',
    hint: 'Click any dot to see capacity, cell chemistry, jobs, and investment details.',
  },
  {
    icon: <Factory className="w-7 h-7 text-indigo-600" />,
    iconBg: 'bg-indigo-50',
    title: 'EV Manufacturing',
    body: 'The EV Manufacturing layer maps electric vehicle assembly plants — from passenger cars and vans to heavy-duty trucks and buses.',
    hint: 'Click any site to explore what\'s being built, by whom, and planned investment.',
  },
  {
    icon: <Globe className="w-7 h-7 text-sky-600" />,
    iconBg: 'bg-sky-50',
    title: 'Country Overviews',
    body: 'Click any highlighted country to pull up a summary of its EV market share, charging density, and total infrastructure investment.',
    hint: 'Layer controls are in the top-right corner. You can combine multiple layers at once.',
  },
];

// ── Component ────────────────────────────────────────────────────────────────
interface WelcomeModalProps {
  onClose: () => void;
}

export const WelcomeModal: React.FC<WelcomeModalProps> = ({ onClose }) => {
  const [current, setCurrent] = useState(0);
  const [direction, setDirection] = useState<1 | -1>(1);

  const goTo = (index: number) => {
    setDirection(index > current ? 1 : -1);
    setCurrent(index);
  };

  const prev = () => current > 0 && goTo(current - 1);
  const next = () => {
    if (current < CARDS.length - 1) {
      goTo(current + 1);
    } else {
      handleClose();
    }
  };

  const handleClose = () => {
    localStorage.setItem(STORAGE_KEY, '1');
    onClose();
  };

  const card = CARDS[current];
  const isLast = current === CARDS.length - 1;

  const variants = {
    enter: (dir: number) => ({ x: dir * 60, opacity: 0 }),
    center: { x: 0, opacity: 1 },
    exit: (dir: number) => ({ x: -dir * 60, opacity: 0 }),
  };

  return (
    <div className="fixed inset-0 z-[200] flex items-center justify-center p-4">
      {/* Overlay */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="absolute inset-0 bg-slate-900/60 backdrop-blur-sm"
        onClick={handleClose}
      />

      {/* Modal */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 10 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 10 }}
        transition={{ type: 'spring', damping: 28, stiffness: 280 }}
        className="relative bg-white rounded-3xl shadow-2xl w-full max-w-md overflow-hidden"
        onClick={e => e.stopPropagation()}
      >
        {/* Close button */}
        <button
          onClick={handleClose}
          className="absolute top-4 right-4 z-10 p-2 rounded-full text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-all"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Card content */}
        <div className="px-8 pt-10 pb-6 min-h-[260px] overflow-hidden relative">
          <AnimatePresence mode="wait" custom={direction}>
            <motion.div
              key={current}
              custom={direction}
              variants={variants}
              initial="enter"
              animate="center"
              exit="exit"
              transition={{ duration: 0.22, ease: 'easeInOut' }}
              className="flex flex-col gap-5"
            >
              {/* Icon */}
              <div className={cn('w-14 h-14 rounded-2xl flex items-center justify-center', card.iconBg)}>
                {card.icon}
              </div>

              {/* Text */}
              <div>
                <h2 className="text-xl font-serif italic text-slate-900 mb-2 leading-snug">
                  {card.title}
                </h2>
                <p className="text-sm text-slate-600 leading-relaxed">
                  {card.body}
                </p>
                {card.hint && (
                  <p className="mt-3 text-xs text-slate-400 leading-relaxed border-t border-slate-100 pt-3">
                    {card.hint}
                  </p>
                )}
              </div>
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Footer */}
        <div className="px-8 pb-8 flex items-center justify-between gap-4">
          {/* Dot indicators */}
          <div className="flex items-center gap-1.5">
            {CARDS.map((_, i) => (
              <button
                key={i}
                onClick={() => goTo(i)}
                className={cn(
                  'rounded-full transition-all duration-200',
                  i === current
                    ? 'w-5 h-2 bg-slate-800'
                    : 'w-2 h-2 bg-slate-300 hover:bg-slate-400'
                )}
              />
            ))}
          </div>

          {/* Navigation */}
          <div className="flex items-center gap-2">
            {current > 0 && (
              <button
                onClick={prev}
                className="p-2 rounded-full border border-slate-200 text-slate-500 hover:bg-slate-50 transition-all"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
            )}
            <button
              onClick={next}
              className={cn(
                'flex items-center gap-2 px-5 py-2.5 rounded-full text-sm font-semibold transition-all',
                isLast
                  ? 'bg-slate-900 text-white hover:bg-slate-700'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              )}
            >
              {isLast ? "Let's explore" : 'Next'}
              {!isLast && <ChevronRight className="w-4 h-4" />}
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

// ── Helper: check if modal should show ──────────────────────────────────────
export const shouldShowWelcome = (): boolean => {
  return !localStorage.getItem(STORAGE_KEY);
};

// ── Helper: reset welcome (for the "?" button) ───────────────────────────────
export const resetWelcome = (): void => {
  localStorage.removeItem(STORAGE_KEY);
};
