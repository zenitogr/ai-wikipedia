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
          {articles.map((article: any) => {
            const decodedTitle = decodeURIComponent(article.title);
            const images = JSON.parse(article.images || '[]');
            const articleImage = images.length > 0 ? images[0] : null;

            return (
              <li key={article.id} className="cached-article">
                <Link href={`/article/${article.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                  {articleImage && (
                    <div className="cached-article-image">
                      <img src={articleImage.url} alt={decodedTitle} />
                    </div>
                  )}
                  <div className="cached-article-text"> {/* Optional: wrap text for layout */}
                    <h2 className="cached-article-title">{decodedTitle}</h2>
                    <p className="cached-article-content">{article.content?.substring(0, 500)}...</p>
                  </div>
                </Link>
              </li>
            );
          })}
        </ul>
      ) : (
        <p>No cached articles found.</p>
      )}
    </div>
  );
}