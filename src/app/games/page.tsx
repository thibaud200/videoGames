import { db } from '~/lib/prisma';
import SafeImage from '~/components/SafeImage'; // Assurez-vous que le chemin est correct

import { 
  getGameTags, 
  getSupportedPlatforms, 
  getPlatformIcon, 
  getGameGenres,
  getGameDevelopers,
  getGamePublishers,
  formatReleaseDate,
  getGameImage,
  getFormattedScore,
  type Game 
} from '~/lib/game-utils';

export default async function GamesPage() {
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

  return (
    <div className="container mx-auto p-8 bg-gray-200">
      <h1 className="text-4xl font-bold mb-8 text-center">
        🎮 Games Centralizer
      </h1>
      
      <div className="mb-6 text-center">
        <p className="text-lg text-gray-600">
          {games.length} jeu{games.length > 1 ? 'x' : ''} dans votre bibliothèque
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {games.map((game) => {
          const gameImage = getGameImage(game);
          const tags = getGameTags(game);
          const genres = getGameGenres(game);
          const developers = getGameDevelopers(game);
          const publishers = getGamePublishers(game);
          const supportedPlatforms = getSupportedPlatforms(game);
          const releaseDate = formatReleaseDate(game.releaseDate);
          const score = getFormattedScore(game);

          return (
            <div key={game.id} className="bg-gray-100 rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
              {/* Image du jeu */}
              {gameImage && (
                <div className="relative h-48 bg-gray-200">
                  <SafeImage
					src={game.horizontalCover || '/placeholder.png'} // On donne une source, même si elle peut être vide
					fallbackSrc="/placeholder.png" // L'image à utiliser si la source est cassée
					alt={game.title}
					width={460}  // next/image requiert width et height
					height={215} // à ajuster selon vos besoins
					className="votre-classe-css" // Gardez vos classes
				  />
                </div>
              )}
              
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <h3 className="text-xl font-bold text-gray-800 line-clamp-2">
                    {game.title}
                  </h3>
				  <img
					src={getPlatformIcon(game.platform)}
					alt="Platform icon"
					className="w-5 h-5 ml-2 object-contain"
				  />
                </div>
                
                <div className="space-y-3">
                  {/* Plateforme et score */}
                  <div className="flex items-center justify-between">
                    {game.platform && (
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                        game.platform.toLowerCase().includes('steam') ? 'bg-blue-100 text-blue-800' :
                        game.platform.toLowerCase().includes('gog') ? 'bg-purple-100 text-purple-800' :
                        game.platform.toLowerCase().includes('epic') ? 'bg-gray-800 text-white' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {game.platform}
                      </span>
                    )}
                    {score && (
                      <span className="text-sm text-green-600 font-medium">
                        {score}
                      </span>
                    )}
                  </div>

                  {/* Date de sortie */}
                  {releaseDate && (
                    <div className="text-sm text-gray-600">
                      📅 {releaseDate}
                    </div>
                  )}

                  {/* Développeurs et éditeurs */}
                  {developers.length > 0 && (
                    <div className="text-sm text-gray-600">
                      <span className="font-medium">Dev:</span> {developers.slice(0, 2).join(', ')}
                      {developers.length > 2 && ` +${developers.length - 2}`}
                    </div>
                  )}

                  {publishers.length > 0 && (
                    <div className="text-sm text-gray-600">
                      <span className="font-medium">Pub:</span> {publishers.slice(0, 2).join(', ')}
                      {publishers.length > 2 && ` +${publishers.length - 2}`}
                    </div>
                  )}

                  {/* Plateformes supportées */}
                  {supportedPlatforms.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {supportedPlatforms.map((platform) => (
                        <span key={platform} className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs">
                          {platform}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Genres */}
                  {genres.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {genres.slice(0, 3).map((genre) => (
                        <span key={genre} className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs">
                          {genre}
                        </span>
                      ))}
                      {genres.length > 3 && (
                        <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs">
                          +{genres.length - 3}
                        </span>
                      )}
                    </div>
                  )}

                  {/* Tags */}
                  {tags.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {tags.slice(0, 3).map((tag) => (
                        <span key={tag} className="px-2 py-1 bg-indigo-100 text-indigo-700 rounded text-xs">
                          {tag}
                        </span>
                      ))}
                      {tags.length > 3 && (
                        <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs">
                          +{tags.length - 3}
                        </span>
                      )}
                    </div>
                  )}

                  {/* Résumé */}
                  {game.summary && (
                    <p className="text-gray-600 text-sm line-clamp-3">
                      {game.summary}
                    </p>
                  )}

                  {/* Statistiques de jeu */}
                  {game.gameStats && (
                    <div className="text-xs text-gray-500 border-t pt-2">
                      {game.gameStats.playtime > 0 && (
                        <div>⏱️ {Math.round(game.gameStats.playtime / 60)}h jouées</div>
                      )}
                      {game.gameStats.achievements > 0 && (
                        <div>🏆 {game.gameStats.achievements} succès</div>
                      )}
                    </div>
                  )}

                  {/* Indicateurs */}
                  <div className="flex justify-between items-center text-xs text-gray-500">
                    <div className="flex gap-2">
                      {game.dlcs && game.dlcs.length > 0 && (
                        <span className="bg-yellow-100 text-yellow-700 px-2 py-1 rounded">
                          {game.dlcs.length} DLC
                        </span>
                      )}
                      {game.screenshots && game.screenshots.length > 0 && (
                        <span className="bg-gray-100 text-gray-600 px-2 py-1 rounded">
                          📸 {game.screenshots.length}
                        </span>
                      )}
                    </div>
                    {game.isModifiedByUser === 1 && (
                      <span className="text-blue-600">✏️</span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {games.length === 0 && (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">🎮</div>
          <h2 className="text-2xl font-bold text-gray-600 mb-2">Aucun jeu trouvé</h2>
          <p className="text-gray-500">
            Votre bibliothèque de jeux est vide. Synchronisez vos jeux depuis Steam ou GOG pour commencer.
          </p>
        </div>
      )}
    </div>
  );
}