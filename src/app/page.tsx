import Link from 'next/link';

export default function HomePage() {
  return (
    <main className="p-8 text-center">
      <h1 className="text-4xl font-bold mb-8">🎮 Games Centralizer</h1>
      
      <div className="space-y-4 bg-gray-200">
        <Link 
          href="/games" 
          className="inline-block bg-blue-500 hover:bg-blue-600 text-white font-bold py-3 px-6 rounded-lg transition-colors"
        >
          Voir mes jeux
        </Link>
        
        <p className="text-gray-600">
          Centralisez vos jeux Steam et GOG en un seul endroit !
        </p>
      </div>
    </main>
  );
}