import Groq from 'groq-sdk';

const groq = new Groq({
  apiKey: process.env.NEXT_PUBLIC_GROQ_API_KEY,
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

export async function getSimilarTerms(topic: string): Promise<string[]> {
  const prompt = `Say nothing else, only respond with this template: input_title (category - subcategory), realtive_wiki_title_1 (category - subcategory), relative_wiki_title_2 (category - subcategory), relative_wiki_title_N (category - subcategory). relative_wiki_titles are 10 similar wiki titles to the input_title with their category and subcategory. remember dont say anything except the template list!!! the input_title is: ${topic}`;
  const response = await getGroqCompletion(prompt, "meta-llama/llama-4-maverick-17b-128e-instruct", 0.5);
  return response.split(',').map(term => term.trim()).filter(term => term.length > 0);
}

export async function generateArticle(topic: string): Promise<{ articleContent: string; imageSuggestions: string[] }> {
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