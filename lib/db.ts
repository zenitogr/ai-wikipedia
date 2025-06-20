import { neon } from '@neondatabase/serverless';

const sql = neon(process.env.DATABASE_URL!);

async function ensureTableExists() {
  await sql`
    CREATE TABLE IF NOT EXISTS articles (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        images TEXT,
        image_suggestions TEXT
    );
  `;
}

export async function getArticles() {
  await ensureTableExists();
  const articles = await sql`SELECT id, title, content, images, image_suggestions FROM articles`;
  return articles;
}

export async function getArticleById(id: string) {
  await ensureTableExists();
  const articles = await sql`SELECT title, content, images, image_suggestions FROM articles WHERE id = ${id}`;
  return articles[0]; // Assuming id is unique and returns at most one article
}

export async function insertArticle(id: string, title: string, content: string, images: string, image_suggestions: string) {
  await ensureTableExists();
  await sql`INSERT INTO articles (id, title, content, images, image_suggestions) VALUES (${id}, ${title}, ${content}, ${images}, ${image_suggestions})`;
}

export async function clearArticles() {
  await ensureTableExists();
  await sql`DELETE FROM articles`;
}