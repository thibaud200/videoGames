import { db } from '~/lib/prisma';
import type { Game } from '~/lib/game-utils';
import type { GameFilters, GameStatsResponse } from '~/lib/types';

export class GameService {
  /**
   * Récupère tous les jeux avec leurs relations
   */
  static async getAllGames(): Promise<Game[]> {
    return await db.game.findMany({
      include: {
        artworks: true,
        bonuses: true,
        dlcs: true,
        features: true,
        genres: true,
        developers: true,
        publishers: true,
        tags: true,
        themes: true,
        screenshots: true,
        videos: true,
        installers: true,
        patches: true,
        languagePacks: true,
        localizations: true,
        releases: true,
        items: true,
        supported: true,
        gameStats: true,
        score: true,
        releasesStats: true,
        ownedReleaseKeys: true,
      },
      orderBy: { title: 'asc' }
    }) as Game[];
  }

  /**
   * Récupère un jeu par son ID
   */
  static async getGameById(id: number): Promise<Game | null> {
    return await db.game.findUnique({
      where: { id },
      include: {
        artworks: true,
        bonuses: true,
        dlcs: true,
        features: true,
        genres: true,
        developers: true,
        publishers: true,
        tags: true,
        themes: true,
        screenshots: true,
        videos: true,
        installers: true,
        patches: true,
        languagePacks: true,
        localizations: true,
        releases: true,
        items: true,
        supported: true,
        gameStats: true,
        score: true,
        releasesStats: true,
        ownedReleaseKeys: true,
      },
    }) as Game | null;
  }

  /**
   * Récupère un jeu par son gameId externe
   */
  static async getGameByGameId(gameId: string): Promise<Game | null> {
    return await db.game.findUnique({
      where: { gameId },
      include: {
        artworks: true,
        bonuses: true,
        dlcs: true,
        features: true,
        genres: true,
        developers: true,
        publishers: true,
        tags: true,
        themes: true,
        screenshots: true,
        videos: true,
        installers: true,
        patches: true,
        languagePacks: true,
        localizations: true,
        releases: true,
        items: true,
        supported: true,
        gameStats: true,
        score: true,
        releasesStats: true,
        ownedReleaseKeys: true,
      },
    }) as Game | null;
  }

  /**
   * Recherche des jeux avec filtres
   */
  static async searchGames(filters: GameFilters): Promise<Game[]> {
    const where: Record<string, unknown> = {};

    // Filtre par recherche textuelle
    if (filters.search) {
      where.OR = [
        { title: { contains: filters.search, mode: 'insensitive' } },
        { summary: { contains: filters.search, mode: 'insensitive' } },
      ];
    }

    // Filtre par plateforme
    if (filters.platform) {
      where.platform = { contains: filters.platform, mode: 'insensitive' };
    }

    // Filtre par score
    if (filters.minScore !== undefined) {
      where.criticsScore = { gte: filters.minScore };
    }
    if (filters.maxScore !== undefined) {
      where.criticsScore = { ...(where.criticsScore as object), lte: filters.maxScore };
    }

    // Filtre par rating personnel
    if (filters.hasRating) {
      where.myRating = { not: null };
    }

    const include = {
      artworks: true,
      bonuses: true,
      dlcs: true,
      features: true,
      genres: true,
      developers: true,
      publishers: true,
      tags: true,
      themes: true,
      screenshots: true,
      videos: true,
      installers: true,
      patches: true,
      languagePacks: true,
      localizations: true,
      releases: true,
      items: true,
      supported: true,
      gameStats: true,
      score: true,
      releasesStats: true,
      ownedReleaseKeys: true,
    };

    // Filtre par genre
    if (filters.genre) {
      where.genres = {
        some: {
          name: { contains: filters.genre, mode: 'insensitive' }
        }
      };
    }

    // Filtre par tag
    if (filters.tag) {
      where.tags = {
        some: {
          name: { contains: filters.tag, mode: 'insensitive' }
        }
      };
    }

    // Filtre par développeur
    if (filters.developer) {
      where.developers = {
        some: {
          name: { contains: filters.developer, mode: 'insensitive' }
        }
      };
    }

    // Filtre par éditeur
    if (filters.publisher) {
      where.publishers = {
        some: {
          name: { contains: filters.publisher, mode: 'insensitive' }
        }
      };
    }

    return await db.game.findMany({
      where,
      include,
      orderBy: { title: 'asc' }
    }) as Game[];
  }

  /**
   * Récupère les statistiques globales
   */
  static async getGameStats(): Promise<GameStatsResponse> {
    const games = await this.getAllGames();
    
    const totalGames = games.length;
    const totalPlaytime = games.reduce((sum, game) => 
      sum + (game.gameStats?.playtime ?? 0), 0
    );
    
    const gamesWithScore = games.filter(game => 
      game.criticsScore > 0 || game.myRating !== null || (game.score?.critics ?? 0) > 0
    );
    const averageScore = gamesWithScore.length > 0 
      ? gamesWithScore.reduce((sum, game) => {
          const score = game.myRating ?? game.score?.critics ?? game.criticsScore;
          return sum + score;
        }, 0) / gamesWithScore.length
      : 0;

    // Distribution par plateforme
    const platformDistribution: Record<string, number> = {};
    games.forEach(game => {
      if (game.platform) {
        platformDistribution[game.platform] = (platformDistribution[game.platform] ?? 0) + 1;
      }
    });

    // Distribution par genre
    const genreDistribution: Record<string, number> = {};
    games.forEach(game => {
      game.genres?.forEach(genre => {
        genreDistribution[genre.name] = (genreDistribution[genre.name] ?? 0) + 1;
      });
    });

    // Top développeurs
    const developerCounts: Record<string, number> = {};
    games.forEach(game => {
      game.developers?.forEach(dev => {
        developerCounts[dev.name] = (developerCounts[dev.name] ?? 0) + 1;
      });
    });
    const topDevelopers = Object.entries(developerCounts)
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10);

    // Top éditeurs
    const publisherCounts: Record<string, number> = {};
    games.forEach(game => {
      game.publishers?.forEach(pub => {
        publisherCounts[pub.name] = (publisherCounts[pub.name] ?? 0) + 1;
      });
    });
    const topPublishers = Object.entries(publisherCounts)
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10);

    return {
      totalGames,
      totalPlaytime,
      averageScore,
      platformDistribution,
      genreDistribution,
      topDevelopers,
      topPublishers,
    };
  }

  /**
   * Met à jour la note personnelle d'un jeu
   */
  static async updateGameRating(id: number, rating: number | null): Promise<Game | null> {
    return await db.game.update({
      where: { id },
      data: { 
        myRating: rating,
        isModifiedByUser: 1,
      },
      include: {
        artworks: true,
        bonuses: true,
        dlcs: true,
        features: true,
        genres: true,
        developers: true,
        publishers: true,
        tags: true,
        themes: true,
        screenshots: true,
        videos: true,
        installers: true,
        patches: true,
        languagePacks: true,
        localizations: true,
        releases: true,
        items: true,
        supported: true,
        gameStats: true,
        score: true,
        releasesStats: true,
        ownedReleaseKeys: true,
      },
    }) as Game;
  }

  /**
   * Récupère tous les genres uniques
   */
  static async getAllGenres(): Promise<string[]> {
    const genres = await db.genre.findMany({
      select: { name: true },
      distinct: ['name'],
      orderBy: { name: 'asc' }
    });
    return genres.map(g => g.name);
  }

  /**
   * Récupère tous les tags uniques
   */
  static async getAllTags(): Promise<string[]> {
    const tags = await db.tag.findMany({
      select: { name: true },
      distinct: ['name'],
      orderBy: { name: 'asc' }
    });
    return tags.map(t => t.name);
  }

  /**
   * Récupère tous les développeurs uniques
   */
  static async getAllDevelopers(): Promise<string[]> {
    const developers = await db.developer.findMany({
      select: { name: true },
      distinct: ['name'],
      orderBy: { name: 'asc' }
    });
    return developers.map(d => d.name);
  }

  /**
   * Récupère tous les éditeurs uniques
   */
  static async getAllPublishers(): Promise<string[]> {
    const publishers = await db.publisher.findMany({
      select: { name: true },
      distinct: ['name'],
      orderBy: { name: 'asc' }
    });
    return publishers.map(p => p.name);
  }

  /**
   * Récupère toutes les plateformes uniques
   */
  static async getAllPlatforms(): Promise<string[]> {
    const platforms = await db.game.findMany({
      select: { platform: true },
      distinct: ['platform'],
      where: { platform: { not: null } },
      orderBy: { platform: 'asc' }
    });
    return platforms.map(p => p.platform!);
  }
}
