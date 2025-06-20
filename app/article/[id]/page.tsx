import React from 'react';
import { getArticleById, insertArticle } from '../../../lib/db';
import { redirect } from 'next/navigation';

interface ArticlePageProps {
  params: {
    id: string;
  };
}

export default async function ArticlePage({ params }: ArticlePageProps) {
  // Await params before accessing its properties
  const { id: articleId } = await params;

  // Try to fetch the article from the database
  let article = await getArticleById(articleId);

  // If article not found, generate and save it
  if (!article) {
    try {
      // Call the API route to generate the article and find images
      const baseUrl = process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : 'http://localhost:3000';
      const response = await fetch(`${baseUrl}/api/generate-article`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ topic: articleId }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to generate article');
      }

      const { articleContent, images, imageSuggestions } = await response.json();

      // Save the new article to the database
      await insertArticle(
        articleId,
        articleId, // Use articleId as title for now
        articleContent,
        JSON.stringify(images),
        JSON.stringify(imageSuggestions)
      );

      // Fetch the newly saved article
      article = await getArticleById(articleId);

      // If still no article, something went wrong
      if (!article) {
        return <div>Error generating article.</div>;
      }

    } catch (error: any) {
      console.error('Error generating article:', error);
      return <div>Error generating article: {error.message}</div>;
    }
  }

  // Deserialize JSON strings
  const images = JSON.parse(article.images || '[]');
  const imageSuggestions = JSON.parse(article.image_suggestions || '[]');

  return (
    <div className="container">
      <h1>{article.title}</h1>
      <div dangerouslySetInnerHTML={{ __html: article.content }} /> {/* Render markdown as HTML */}

      {images && images.length > 0 && (
        <div>
          <h2>Images</h2>
          <div className="image-gallery">
            {images.map((img: any, index: number) => (
              <div key={index} className="image-item">
                <img src={img.url} alt={img.description} />
                <p>{img.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {imageSuggestions && imageSuggestions.length > 0 && (
        <div>
          <h2>Image Suggestions</h2>
          <ul>
            {imageSuggestions.map((suggestion: string, index: number) => (
              <li key={index}>{suggestion}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}