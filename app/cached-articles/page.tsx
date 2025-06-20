import React from 'react';
import Link from 'next/link';
import { getArticles } from '../../lib/db';

export default async function CachedArticlesPage() {
  const articles = await getArticles();

  return (
    <div className="container">
      <h1>Cached Articles</h1>
      {articles && articles.length > 0 ? (
        <ul className="cached-articles">
          {articles.map((article: any) => (
            <li key={article.id} className="cached-article">
              <Link href={`/article/${article.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                <h2 className="cached-article-title">{article.title}</h2>
                <p className="cached-article-content">{article.content?.substring(0, 500)}...</p>
              </Link>
            </li>
          ))}
        </ul>
      ) : (
        <p>No cached articles found.</p>
      )}
    </div>
  );
}