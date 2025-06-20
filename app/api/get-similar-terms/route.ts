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

async function getSimilarTerms(topic: string): Promise<string[]> {
  const prompt = `Say nothing else, only respond with this template: input_title (category - subcategory), realtive_wiki_title_1 (category - subcategory), relative_wiki_title_2 (category - subcategory), relative_wiki_title_N (category - subcategory). relative_wiki_titles are 10 similar wiki titles to the input_title with their category and subcategory. remember dont say anything except the template list!!! the input_title is: ${topic}`;
  const response = await getGroqCompletion(prompt, "meta-llama/llama-4-maverick-17b-128e-instruct", 0.5);
  return response.split(',').map(term => term.trim()).filter(term => term.length > 0);
}

export async function POST(request: Request) {
  try {
    const { topic } = await request.json();
    if (!topic) {
      return NextResponse.json({ error: 'Topic is required' }, { status: 400 });
    }

    const similarTerms = await getSimilarTerms(topic);
    return NextResponse.json({ similarTerms });
  } catch (error) {
    console.error('Error in get-similar-terms API:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}