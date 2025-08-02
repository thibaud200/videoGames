import { NextResponse } from 'next/server';
import { db } from '~/lib/prisma';

export async function POST() {
  try {
    console.log('🎮 Sync Steam simulée...');
    
    // Test avec un jeu fictif pour commencer
    const testGame = await (db.game.upsert as any)({
      where: {
        externalId_platform: {
          externalId: "12345",
          platform: 'STEAM' as const
        }
      },
      create: {
        externalId: "12345",
        title: "Test Game Steam",
        platform: 'STEAM' as const,
        supportsWindows: true,
        supportsMac: false,
        supportsLinux: false
      },
      update: {
        title: "Test Game Steam Updated",
        updatedAt: new Date()
      }
    });

    return NextResponse.json({ 
      success: true, 
      message: "1 jeu Steam test créé",
      game: testGame
    });

  } catch (error) {
    console.error('❌ Erreur sync Steam:', error);
    return NextResponse.json({ 
      error: 'Erreur sync Steam' 
    }, { status: 500 });
  }
}