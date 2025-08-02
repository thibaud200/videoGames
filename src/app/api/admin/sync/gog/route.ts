import { NextResponse } from 'next/server';
import { db } from '~/lib/prisma';
import { setGameTags } from '~/lib/game-utils';

export async function POST() {
  try {
    console.log('🎮 Sync GOG simulée...');
    
    // Test avec un jeu GOG fictif (comme Steam)
    const testGame = await db.game.upsert({
      where: {
        externalId_platform: {
          externalId: "67890",
          platform: 'GOG'
        }
      },
      create: {
        externalId: "67890",
        title: "Test Game GOG",
        platform: 'GOG',
        category: "RPG",
        description: "Un jeu de test GOG",
        supportsWindows: true,
        supportsMac: true,
        supportsLinux: false,
        tags: setGameTags(["RPG", "Fantasy", "Test"])
      },
      update: {
        title: "Test Game GOG Updated",
        tags: setGameTags(["RPG", "Fantasy", "Updated"])
      }
    });

    return NextResponse.json({ 
      success: true, 
      message: "1 jeu GOG test créé",
      game: testGame
    });

  } catch (error) {
    console.error('❌ Erreur sync GOG:', error);
    return NextResponse.json({ 
      error: 'Erreur sync GOG' 
    }, { status: 500 });
  }
}