// Types pour l'API basés sur le schéma Prisma actuel
export interface ApiGame {
  id: number;
  gameId: string;
  title: string;
  summary?: string | null;
  platform?: string | null;
  releaseDate?: number | null; // Timestamp
  criticsScore: number;
  myRating?: number | null;
  all: number;
  unlocked: number;
  isFromProductsApi: number;
  isModifiedByUser: number;
  state?: string | null;
  parentGrk?: string | null;
  
  // Images et médias
  background?: string | null;
  horizontalCover?: string | null;
  verticalCover?: string | null;
  logo?: string | null;
  squareIcon?: string | null;
  productCard?: string | null;
  
  // URLs et liens
  changelog?: string | null;
  forum?: string | null;
  support?: string | null;
  
  createdAt: string;
  updatedAt: string;
  
  // Relations sérialisées pour l'API
  artworks?: Array<{ id: number; url: string; type?: string | null }>;
  bonuses?: Array<{ id: number; name: string; type?: string | null; url?: string | null; description?: string | null }>;
  dlcs?: Array<{ id: number; externalId: string; title: string; releaseDate?: number | null; price?: number | null }>;
  features?: Array<{ id: number; name: string }>;
  genres?: Array<{ id: number; name: string }>;
  developers?: Array<{ id: number; name: string }>;
  publishers?: Array<{ id: number; name: string }>;
  tags?: Array<{ id: number; name: string }>;
  themes?: Array<{ id: number; name: string }>;
  screenshots?: Array<{ id: number; url: string }>;
  videos?: Array<{ id: number; url: string; title?: string | null; description?: string | null; thumbnail?: string | null }>;
  installers?: Array<{ id: number; name: string; version?: string | null; platform?: string | null; language?: string | null; size?: number | null; url?: string | null }>;
  patches?: Array<{ id: number; version: string; releaseDate?: number | null; size?: number | null; description?: string | null; url?: string | null }>;
  languagePacks?: Array<{ id: number; language: string; name?: string | null }>;
  localizations?: Array<{ id: number; language: string; region?: string | null }>;
  releases?: Array<{ id: number; releaseKey: string; platform?: string | null; version?: string | null; releaseDate?: number | null }>;
  items?: Array<{ id: number; name: string; type?: string | null; description?: string | null }>;
  supported?: Array<{ id: number; platform: string }>;
  gameStats?: { id: number; playtime: number; achievements: number; lastPlayed?: number | null; timesLaunched: number } | null;
  score?: { id: number; critics: number; users: number; metacritic: number } | null;
  releasesStats?: Array<{ id: number; releaseKey: string; downloads: number; installs: number }>;
  ownedReleaseKeys?: Array<{ id: number; releaseKey: string }>;
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

// Types pour les filtres et recherches
export interface GameFilters {
  platform?: string;
  genre?: string;
  tag?: string;
  developer?: string;
  publisher?: string;
  minScore?: number;
  maxScore?: number;
  hasRating?: boolean;
  search?: string;
}

// Types pour les statistiques
export interface GameStatsResponse {
  totalGames: number;
  totalPlaytime: number;
  averageScore: number;
  platformDistribution: Record<string, number>;
  genreDistribution: Record<string, number>;
  topDevelopers: Array<{ name: string; count: number }>;
  topPublishers: Array<{ name: string; count: number }>;
}