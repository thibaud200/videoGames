import { PrismaClient } from '@prisma/client';

// Déclaration explicite des types
declare global {
  var __prisma: PrismaClient | undefined;
}

// Force la reconnaissance du modèle Game
const prisma = global.__prisma ?? new PrismaClient();

if (process.env.NODE_ENV === 'development') {
  global.__prisma = prisma;
}

// Export avec types forcés
export const db = prisma as PrismaClient & {
  game: {
    count: () => Promise<number>;
    findMany: (args?: unknown) => Promise<unknown[]>;
    upsert: (args: unknown) => Promise<unknown>;
    create: (args: unknown) => Promise<unknown>;
    findFirst: (args?: unknown) => Promise<unknown>;
  };
};

export { prisma };
export default prisma;