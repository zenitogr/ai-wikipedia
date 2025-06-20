import React from 'react';
import { getArticleById, insertArticle } from '../../../lib/db';
import { redirect } from 'next/navigation';
import { marked } from 'marked'; // Import marked library

interface ArticlePageProps {
  params: {
    id: string;
  };
}

export default async function ArticlePage({ params }: ArticlePageProps) {
  // Await params before accessing its properties
  const { id: articleId } = await params;

  let article = null;
  let generationError = null;

  try {
    // Try to fetch the article from the database
    article = await getArticleById(articleId);

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

        // Attempt to save the new article to the database
        await insertArticle(
          articleId,
          articleId, // Use articleId as title for now
          articleContent,
          JSON.stringify(images),
          JSON.stringify(imageSuggestions)
        );

        // Fetch the newly saved article
        article = await getArticleById(articleId);

      } catch (insertError: any) {
        console.error('Error during article insertion:', insertError);
        // Check if it's a duplicate key error (PostgreSQL error code '23505')
        if (insertError.code === '23505') {
          console.warn(`Duplicate key error for article ID ${articleId}. Attempting to fetch existing article.`);
          // If duplicate key, assume it was created concurrently and fetch it
          article = await getArticleById(articleId);
          if (!article) {
             // If fetching after duplicate key still fails, something is wrong
            generationError = new Error(`Failed to fetch article ${articleId} after duplicate key error.`);
          }
        } else {
          // Handle other insertion errors
          generationError = new Error(`Error generating or saving article: ${insertError.message}`);
        }
      }
    }
  } catch (fetchError: any) {
    console.error('Error fetching article:', fetchError);
    generationError = new Error(`Error fetching article: ${fetchError.message}`);
  }

  // If there was a generation or fetch error and no article was loaded
  if (generationError || !article) {
    return <div>Error loading or generating article: {generationError?.message || 'Unknown error'}</div>;
  }

  // Deserialize JSON strings
  const images = JSON.parse(article.images || '[]');
  const imageSuggestions = JSON.parse(article.image_suggestions || '[]');

  // Function to integrate images into article content
  const integrateImages = async (markdownContent: string, images: any[]) => {
    // Convert markdown to HTML first
    let htmlContent = await marked.parse(markdownContent);

    // Simple image insertion logic: insert an image after every 2nd paragraph, up to 3 images
    let imageIndex = 0;
    const paragraphs = htmlContent.split('</p>'); // Split by closing paragraph tag

    const contentWithImages = paragraphs.map((paragraph, index) => {
      let paragraphHtml = paragraph;

      if (paragraphHtml.trim() === '') return ''; // Skip empty parts

      // Re-add closing paragraph tag if it was removed by split
      if (index < paragraphs.length - 1) {
        paragraphHtml += '</p>';
      }

      // Insert image after every 2nd non-empty paragraph
      if (imageIndex < images.length && index > 0 && index % 2 === 0) {
        const img = images[imageIndex];
        const imageHtml = `
          <div class="article-image">
            <img src="${img.url}" alt="${img.description}" />
            <p>${img.description}</p>
          </div>
        `;
        // Insert image HTML before the closing paragraph tag if it exists, otherwise at the end
        if (paragraphHtml.endsWith('</p>')) {
             paragraphHtml = paragraphHtml.slice(0, -4) + imageHtml + '</p>';
        } else {
             paragraphHtml += imageHtml;
        }
        imageIndex++;
      }

      return paragraphHtml;
    }).join(''); // Join back without extra newlines, as marked handles paragraph breaks

    return contentWithImages;
  };

  // Generate Table of Contents from original markdown content
  const generateTableOfContents = (content: string) => {
    const headers = content.match(/^## .*|^### .*/gm);
    if (!headers) return '';

    let tocHtml = '<div class="table-of-contents"><h3>Contents</h3><ul>';
    headers.forEach(header => {
      const level = header.startsWith('## ') ? 2 : 3;
      const title = header.substring(level + 1).trim();
      const id = title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, ''); // Simple ID generation
      // Add IDs to the actual headers in the content (this requires modifying contentWithIntegratedImages)
      // For now, just generate the TOC links
      tocHtml += `<li class="toc-level-${level}"><a href="#${id}">${title}</a></li>`;
    });
    tocHtml += '</ul></div>';
    return tocHtml;
  };

  const tableOfContentsHtml = generateTableOfContents(article.content);

  // Integrate images into the HTML content generated by marked
  const contentWithIntegratedImages = await integrateImages(article.content, images);

  // Integrate Table of Contents into the content
  let finalArticleContent = contentWithIntegratedImages;
  if (tableOfContentsHtml) {
    // Find the position after the first paragraph or before the first header
    // This is more complex now that contentWithIntegratedImages is HTML
    // A simpler approach for now is to insert after the first <p> tag
    const firstParagraphEndIndex = finalArticleContent.indexOf('</p>');
    if (firstParagraphEndIndex !== -1) {
        finalArticleContent = finalArticleContent.slice(0, firstParagraphEndIndex + 4) + tableOfContentsHtml + finalArticleContent.slice(firstParagraphEndIndex + 4);
    } else {
        // If no paragraphs found, just prepend the TOC
        finalArticleContent = tableOfContentsHtml + finalArticleContent;
    }
  }


  // Prepare sidebar content
  const sidebarImage = images.length > 0 ? images[0] : null;

  return (
    <div className="article-container"> {/* Use article-specific container */}
      <div className="article-content">
        <h1>{decodeURIComponent(article.title)}</h1> {/* URL Decode the title */}
        {/* Render content with integrated images and TOC */}
        <div dangerouslySetInnerHTML={{ __html: finalArticleContent }} />
      </div>
      <div className="article-sidebar"> {/* Use article-specific sidebar class */}
        <h2>{decodeURIComponent(article.title)}</h2> {/* URL Decode the title in sidebar */}
        {sidebarImage && (
          <div className="sidebar-image">
            <img src={sidebarImage.url} alt={sidebarImage.description} />
            <p>{sidebarImage.description}</p>
          </div>
        )}
        {/* Add more sidebar content here if needed, e.g., a summary */}
        <p>This is a basic AI-generated article.</p>
        {/* Removed Image Suggestions from sidebar as per user feedback */}
      </div>
    </div>
  );
}