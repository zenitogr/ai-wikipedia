import { NextResponse } from 'next/server';
import { clearArticles } from '../../../lib/db';

export async function POST(request: Request) {
  const authHeader = request.headers.get('Authorization');
  const clearCacheToken = process.env.CLEAR_CACHE_TOKEN;

  if (!clearCacheToken || authHeader !== clearCacheToken) {
    return new NextResponse('Unauthorized', { status: 401 });
  }

  try {
    await clearArticles();
    console.log('Database cache cleared successfully.');
    return new NextResponse('Cache cleared successfully', { status: 200 });
  } catch (error) {
    console.error('Error clearing database cache:', error);
    return new NextResponse('Error clearing cache', { status: 500 });
  }
}