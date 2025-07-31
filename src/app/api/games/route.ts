import { NextResponse } from 'next/server';
import { db } from '~/lib/prisma';
import type { Game } from '~/lib/game-utils';
import type { ApiGame } from '~/lib/types';

export async function GET() {
  try {
    const games = await db.game.findMany({
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

    const apiGames: ApiGame[] = games.map((game: Game) => ({
      id: game.id,
      gameId: game.gameId,
      title: game.title,
      summary: game.summary,
      platform: game.platform,
      releaseDate: game.releaseDate,
      criticsScore: game.criticsScore,
      myRating: game.myRating,
      all: game.all,
      unlocked: game.unlocked,
      isFromProductsApi: game.isFromProductsApi,
      isModifiedByUser: game.isModifiedByUser,
      state: game.state,
      parentGrk: game.parentGrk,
      
      // Images et médias
      background: game.background,
      horizontalCover: game.horizontalCover,
      verticalCover: game.verticalCover,
      logo: game.logo,
      squareIcon: game.squareIcon,
      productCard: game.productCard,
      
      // URLs et liens
      changelog: game.changelog,
      forum: game.forum,
      support: game.support,
      
      createdAt: game.createdAt.toISOString(),
      updatedAt: game.updatedAt.toISOString(),
      
      // Relations
      artworks: game.artworks,
      bonuses: game.bonuses,
      dlcs: game.dlcs,
      features: game.features,
      genres: game.genres,
      developers: game.developers,
      publishers: game.publishers,
      tags: game.tags,
      themes: game.themes,
      screenshots: game.screenshots,
      videos: game.videos,
      installers: game.installers,
      patches: game.patches,
      languagePacks: game.languagePacks,
      localizations: game.localizations,
      releases: game.releases,
      items: game.items,
      supported: game.supported,
      gameStats: game.gameStats,
      score: game.score,
      releasesStats: game.releasesStats,
      ownedReleaseKeys: game.ownedReleaseKeys,
    }));

    return NextResponse.json(apiGames);
  } catch (error) {
    console.error('Erreur API games:', error);
    return NextResponse.json({ error: 'Erreur serveur' }, { status: 500 });
  }
}
