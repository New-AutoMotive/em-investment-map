export interface CountryStats {
  id: string; // ISO 3166-1 alpha-3
  name: string;
  chargingDensity: number; // chargers per 100km
  evMarketShare?: number;
  description?: string;
  updatedAt?: string;
}

export interface ManufacturingSite {
  id: string;
  name: string;
  type: 'battery' | 'ev';
  /** Battery plant subtype, sourced from Cloud SQL `projects.type` */
  subtype?: 'gigafactory' | 'recycling' | 'pack-assembly' | 'r-d-pilot' | string;
  location: {
    lat: number;
    lng: number;
  };
  countryId: string;
  city?: string;
  description?: string;
  manufacturer?: string;
  // EV-specific fields
  produces?: string;
  brands?: string;
  evConversionPlans?: string;
  // Battery-specific fields (populated from Cloud SQL sync)
  capacityGwh?: string;        // Current capacity (e.g. "9 GWh")
  capacityGwh2030?: string;    // Projected 2030 capacity
  capacityCategory?: string;   // Categorical tier from capacity_category table
  capacityCategory2030?: string;
  materials?: string;          // Cell chemistry / materials
  openingYear?: string;
  jobsActual?: string;
  jobs2030?: string;
  recoveryRate?: string;       // For recycling plants
  companyOriginCountry?: string;
  companyOriginArea?: string;
  // Shared fields
  investmentAmount?: string;
  source?: string;
  sourceUrl?: string;
  /** Battery sector (e.g. "Cell Manufacturing", "Recycling") — used for map colour coding */
  sector?: string;
}

export interface NUTS2Region {
  nutsId: string;
  nutsName: string;
  countryCode: string;
  totalInvestment: number;
  chargepointCount: number;
  investmentDensity: number;
  minInvestment: number;
  maxInvestment: number;
  avgInvestment: number;
  areaKm2: number;
  countBefore2025: number;
  growthCount12mo: number;
  growthPercent12mo: number;
  geometry: any;
}

export type MapLayer = 'charging' | 'battery' | 'ev' | 'investment';

export interface FirestoreErrorInfo {
  error: string;
  operationType: 'create' | 'update' | 'delete' | 'list' | 'get' | 'write';
  path: string | null;
  authInfo: {
    userId?: string;
    email?: string;
    emailVerified?: boolean;
    isAnonymous?: boolean;
    tenantId?: string;
    providerInfo: {
      providerId: string;
      displayName: string;
      email: string;
      photoUrl: string;
    }[];
  };
}
