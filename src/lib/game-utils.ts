// Type pour un jeu complet basé sur le schéma Prisma actuel
export interface Game {
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
  
  createdAt: Date;
  updatedAt: Date;
  
  // Relations (optionnelles pour les requêtes avec include)
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

// Helper pour obtenir l'icône de la plateforme
export function getPlatformIcon(platform?: string | null): string {
  if (!platform) return '📱';
  
  const platformLower = platform.toLowerCase();
  if (platformLower.includes('steam')) return './icons/steam.jfif';
  if (platformLower.includes('gog')) return './icons/gog.png';
  if (platformLower.includes('epic')) return './icons/epic.png';
  if (platformLower.includes('xboxone')) return './icons/xbox.png';
  if (platformLower.includes('battlenet')) return './icons/battlenet.png';
  if (platformLower.includes('windows')) return './icons/Pc.png';
  if (platformLower.includes('mac')) return './icons/apple.jfif';
  if (platformLower.includes('linux')) return '🐧';
  return '📱';
}

// Helper pour obtenir les plateformes supportées
export function getSupportedPlatforms(game: Game): string[] {
  if (!game.supported || game.supported.length === 0) {
    return [];
  }
  return game.supported.map(platform => platform.platform);
}

// Helper pour obtenir les tags du jeu
export function getGameTags(game: Game): string[] {
  if (!game.tags || game.tags.length === 0) {
    return [];
  }
  return game.tags.map(tag => tag.name);
}

// Helper pour obtenir les genres du jeu
export function getGameGenres(game: Game): string[] {
  if (!game.genres || game.genres.length === 0) {
    return [];
  }
  return game.genres.map(genre => genre.name);
}

// Helper pour obtenir les développeurs du jeu
export function getGameDevelopers(game: Game): string[] {
  if (!game.developers || game.developers.length === 0) {
    return [];
  }
  return game.developers.map(dev => dev.name);
}

// Helper pour obtenir les éditeurs du jeu
export function getGamePublishers(game: Game): string[] {
  if (!game.publishers || game.publishers.length === 0) {
    return [];
  }
  return game.publishers.map(pub => pub.name);
}

// Helper pour formater la date de sortie
export function formatReleaseDate(timestamp?: number | null): string | null {
  if (!timestamp) return null;
  return new Date(timestamp * 1000).toLocaleDateString('fr-FR');
}

// Helper pour obtenir l'image principale du jeu
export function getGameImage(game: Game): string | null {
  return game.verticalCover ?? 
         game.horizontalCover ?? 
         game.background ?? 
         game.logo ?? 
         game.squareIcon ?? 
         game.productCard ?? 
         null;
}

// Helper pour vérifier si un jeu a un tag spécifique
export function hasTag(game: Game, searchTag: string): boolean {
  const tags = getGameTags(game);
  return tags.some(tag => tag.toLowerCase().includes(searchTag.toLowerCase()));
}

// Helper pour vérifier si un jeu a un genre spécifique
export function hasGenre(game: Game, searchGenre: string): boolean {
  const genres = getGameGenres(game);
  return genres.some(genre => genre.toLowerCase().includes(searchGenre.toLowerCase()));
}

// Helper pour obtenir le score formaté
export function getFormattedScore(game: Game): string | null {
  if (game.myRating) {
    return `${game.myRating}/10 (Personnel)`;
  }
  if (game.score?.metacritic && game.score.metacritic > 0) {
    return `${game.score.metacritic}/100 (Metacritic)`;
  }
  if (game.score?.critics && game.score.critics > 0) {
    return `${game.score.critics}/10 (Critiques)`;
  }
  if (game.criticsScore > 0) {
    return `${game.criticsScore}/10`;
  }
  return null;
}
