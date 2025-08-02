// lib/game-utils.ts

// Gestion des tags pour SQLite
export function tagsToString(tags: string[]): string {
  return tags.join(',');
}

export function stringToTags(tagsString: string | null | undefined): string[] {
  return tagsString && tagsString.trim() !== '' 
    ? tagsString.split(',').filter(tag => tag.trim() !== '') 
    : [];
}

// Type pour un jeu complet (avec enum correct)
export interface Game {
  id: number;
  externalId: string;
  title: string;
  platform: 'STEAM' | 'GOG' | 'EPIC' | 'OTHER';
  category?: string | null;
  description?: string | null;
  releaseDate?: Date | null;
  imageUrl?: string | null;
  supportsWindows: boolean;
  supportsMac: boolean;
  supportsLinux: boolean;
  tags?: string | null;
  createdAt: Date;
  updatedAt: Date;
}

// Helpers pour les tags
export function getGameTags(game: Pick<Game, 'tags'>): string[] {
  return stringToTags(game.tags);
}

export function setGameTags(tags: string[]): string | null {
  return tags.length > 0 ? tagsToString(tags) : null;
}

// Fonction utilitaire bonus
export function hasTag(game: Pick<Game, 'tags'>, searchTag: string): boolean {
  const tags = getGameTags(game);
  return tags.some(tag => tag.toLowerCase().includes(searchTag.toLowerCase()));
}

// Helper pour les plateformes
export function getPlatformIcon(platform: Game['platform']): string {
  switch (platform) {
    case 'STEAM':
      return './icons/steam.jfif';
    case 'GOG':
      return './icons/gog.png';
    case 'EPIC':
      return './icons/epic.png';
	case 'XBOXONE':
      return './icons/xbox.png';
	case 'WINDOWS':
      return './icons/Pc.png';
	case 'BATTLENET':
      return './icons/battlenet.png';
	case 'MAC':
      return './icons/apple.jfif';
	case 'LINUX':
      return '🐧'; 
    default:
      return '📱';
  }
}

// Helper pour formater les plateformes supportées
export function getSupportedPlatforms(game: Pick<Game, 'supportsWindows' | 'supportsMac' | 'supportsLinux'>): string[] {
  const platforms: string[] = [];
  if (game.supportsWindows) platforms.push('Windows');
  if (game.supportsMac) platforms.push('Mac');
  if (game.supportsLinux) platforms.push('Linux');
  return platforms;
}