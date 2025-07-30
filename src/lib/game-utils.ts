// Gestion des tags pour SQLite
export function tagsToString(tags: string[]): string {
  return tags.join(',');
}

export function stringToTags(tagsString: string | null | undefined): string[] {
  return tagsString ? tagsString.split(',').filter(tag => tag.trim() !== '') : [];
}

// Type pour un jeu complet
export interface Game {
  id: number;
  externalId: string;
  title: string;
  platform: 'STEAM' | 'GOG' | 'EPIC' | 'OTHER';
  category?: string;
  description?: string;
  releaseDate?: Date;
  imageUrl?: string;
  supportsWindows: boolean;
  supportsMac: boolean;
  supportsLinux: boolean;
  tags?: string; // "RPG,Action,Fantasy"
  createdAt: Date;
  updatedAt: Date;
}

// Helpers pour les tags
export function getGameTags(game: Game): string[] {
  return stringToTags(game.tags);
}

export function setGameTags(tags: string[]): string {
  return tagsToString(tags);
}