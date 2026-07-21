import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Parses a free-text investment amount string into a numeric value in euros.
 * Returns null if no parseable figure is found.
 *
 * Handles patterns like:
 *   "€1 billion"           → 1_000_000_000
 *   "€800m to €1b"         → 800_000_000 (lower bound of range)
 *   "Over €1.2 billion"    → 1_200_000_000
 *   "€142m total"          → 142_000_000
 *   "€886,822"             → 886_822
 *   "No data available."   → null
 */
export function parseInvestmentAmount(str: string | undefined | null): number | null {
  if (!str) return null;
  const lower = str.toLowerCase();
  if (lower.includes('no data') || lower === 'n/a') return null;

  // Find all euro-prefixed numbers, taking the first (lowest) match for ranges
  // Matches patterns like: €1.2b, €800m, €1,200,000, €25 million, €1 billion
  const pattern = /€\s*([\d,]+(?:\.\d+)?)\s*(billion|bn|b|million|mn|m|k)?/gi;
  const matches = [...str.matchAll(pattern)];
  if (matches.length === 0) return null;

  // Use the first match (handles "€800m to €1b" → takes €800m)
  const [, rawNum, unit] = matches[0];
  const num = parseFloat(rawNum.replace(/,/g, ''));
  if (isNaN(num)) return null;

  const u = (unit || '').toLowerCase();
  if (u === 'billion' || u === 'bn' || u === 'b') return num * 1_000_000_000;
  if (u === 'million' || u === 'mn' || u === 'm') return num * 1_000_000;
  if (u === 'k') return num * 1_000;
  return num; // raw number (e.g. €886,822)
}

export enum OperationType {
  CREATE = 'create',
  UPDATE = 'update',
  DELETE = 'delete',
  LIST = 'list',
  GET = 'get',
  WRITE = 'write',
}

import { auth } from './firebase';

export function handleFirestoreError(error: unknown, operationType: OperationType, path: string | null) {
  const errInfo = {
    error: error instanceof Error ? error.message : String(error),
    authInfo: {
      userId: auth.currentUser?.uid,
      email: auth.currentUser?.email,
      emailVerified: auth.currentUser?.emailVerified,
      isAnonymous: auth.currentUser?.isAnonymous,
      tenantId: auth.currentUser?.tenantId,
      providerInfo: auth.currentUser?.providerData.map(provider => ({
        providerId: provider.providerId,
        displayName: provider.displayName || '',
        email: provider.email || '',
        photoUrl: provider.photoURL || ''
      })) || []
    },
    operationType,
    path
  };
  console.error('Firestore Error: ', JSON.stringify(errInfo));
  throw new Error(JSON.stringify(errInfo));
}
