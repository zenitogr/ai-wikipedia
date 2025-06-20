import { NextResponse } from 'next/server';
import Groq from 'groq-sdk';

const groq = new Groq({
  apiKey: process.env.GROQ_API_KEY, // Use the server-side environment variable
});

async function getGroqCompletion(prompt: string, model: string, temperature: number = 1.0) {
  const completion = await groq.chat.completions.create({
    messages: [{ role: 'user', content: prompt }],
    model: model,
    temperature: temperature,
    max_tokens: 8192,
  });
  return completion.choices[0]?.message?.content || '';
}

async function generateArticleContent(topic: string): Promise<{ articleContent: string; imageSuggestions: string[] }> {
  const prompt = `
    Generate a Wikipedia article about ${topic}. Include 4-6 relevant section titles.
    Sections should be markdown headers.
    Also, suggest around 10 relevant short image search queries (without actually generating images) that could accompany this article.
    Format the short image suggestions as a list at the end of the article, each prefixed with 'IMAGE:'.
    Now, write the article:
    `;
  const response = await getGroqCompletion(prompt, "meta-llama/llama-4-maverick-17b-128e-instruct");

  const articleParts = response.split('IMAGE:');
  const articleContent = articleParts[0].trim();
  const imageSuggestions = articleParts.slice(1).map(img => img.trim()).filter(img => img.length > 0);

  return { articleContent, imageSuggestions };
}

const WIKIMEDIA_API_URL = "https://commons.wikimedia.org/w/api.php";

async function fetchWikimediaApi(params: Record<string, string>): Promise<any> {
  const url = new URL(WIKIMEDIA_API_URL);
  Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));

  try {
    const response = await fetch(url.toString());
    if (!response.ok) {
      console.error(`Wikimedia API request failed: ${response.statusText}`);
      return null;
    }
    return await response.json();
  } catch (error) {
    console.error("Error fetching from Wikimedia API:", error);
    return null;
  }
}

async function searchImages(query: string): Promise<{ url: string | null; fileName: string | null }> {
  const params = {
    action: "query",
    format: "json",
    list: "search",
    srsearch: `${query} filetype:bitmap|drawing|image|jpg|jpeg|png|gif|svg`,
    srnamespace: "6", // File namespace
    srlimit: "5", // Increase the number of results
    srprop: "snippet"
  };

  const data = await fetchWikimediaApi(params);

  if (!data || !data.query || !data.query.search || data.query.search.length === 0) {
    console.warn(`No search results found for query: ${query}`);
    return { url: null, fileName: null };
  }

  for (const result of data.query.search) {
    const fileName = result.title;
    const imageUrl = await getFileUrl(fileName);
    if (imageUrl) {
      console.debug(`Found file: ${fileName}`);
      return { url: imageUrl, fileName: fileName };
    }
  }

  console.warn(`No valid image found for query: ${query}`);
  return { url: null, fileName: null };
}

async function getFileUrl(fileName: string): Promise<string | null> {
  const params = {
    action: "query",
    format: "json",
    prop: "imageinfo",
    iiprop: "url",
    titles: fileName
  };

  const data = await fetchWikimediaApi(params);

  if (data && data.query && data.query.pages) {
    const pages = data.query.pages;
    for (const pageId in pages) {
      const page = pages[pageId];
      if (page.imageinfo && page.imageinfo.length > 0) {
        const imageUrl = page.imageinfo[0].url;
        console.debug(`Found image URL: ${imageUrl}`);
        return imageUrl;
      }
    }
  }

  console.warn(`No image info found for file: ${fileName}`);
  return null;
}

async function getImagesForSuggestions(imageSuggestions: string[]): Promise<{ description: string; url: string; fileName: string }[]> {
  const images: { description: string; url: string; fileName: string }[] = [];

  for (const suggestion of imageSuggestions) {
    console.info(`Searching for image: ${suggestion}`);
    const result = await searchImages(suggestion);

    if (result.url) {
      images.push({ description: suggestion, url: result.url, fileName: result.fileName! });
      continue;
    }

    const generalTerm = suggestion.split(',')[0].trim(); // Take the first part of the suggestion
    if (generalTerm && generalTerm !== suggestion) {
      console.info(`Trying general term: ${generalTerm}`);
      const generalResult = await searchImages(generalTerm);
      if (generalResult.url) {
        images.push({ description: suggestion, url: generalResult.url, fileName: generalResult.fileName! });
        continue;
      }
    }

    console.warn(`No image found for suggestion: ${suggestion}`);
  }

  console.info(`Total images found: ${images.length}`);
  return images;
}


export async function POST(request: Request) {
  try {
    const { topic } = await request.json();
    if (!topic) {
      return NextResponse.json({ error: 'Topic is required' }, { status: 400 });
    }

    const { articleContent, imageSuggestions } = await generateArticleContent(topic);
    const images = await getImagesForSuggestions(imageSuggestions);

    return NextResponse.json({ articleContent, images, imageSuggestions });
  } catch (error) {
    console.error('Error in generate-article API:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}