import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';

const execAsync = promisify(exec);

interface GameData {
  id: number;
  title: string;
  platform: string;
  // ... autres propriétés
}

export async function callSteamModule(): Promise<GameData[]> {
  try {
    const scriptPath = path.join(process.cwd(), 'auth-api', 'steam', 'main.py');
    const { stdout } = await execAsync(`python "${scriptPath}"`);
    // Validation plus sûre
    if (!stdout || stdout.trim() === '') {
      return [];
    }
    const result = JSON.parse(stdout) as unknown;
    return Array.isArray(result) ? result as GameData[] : [];
  } catch (error) {
    console.error('Erreur Steam:', error);
    return [];
  }
}

export async function callGOGModule(): Promise<GameData[]> {
  try {
    const scriptPath = path.join(process.cwd(), 'auth-api', 'gog', 'main.py');
    const { stdout } = await execAsync(`python "${scriptPath}"`);
    // Validation plus sûre
    if (!stdout || stdout.trim() === '') {
      return [];
    }
    const result = JSON.parse(stdout) as unknown;
    return Array.isArray(result) ? result as GameData[] : [];
  } catch (error) {
    console.error('Erreur GOG:', error);
    return [];
  }
}