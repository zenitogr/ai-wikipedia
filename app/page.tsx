'use client';

'use client';

import React, { useState } from 'react';

import Link from 'next/link';

export default function Page() {
  const [topic, setTopic] = useState('');
  const [similarTerms, setSimilarTerms] = useState<string[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (formData: FormData) => {
    setLoading(true);
    setError(null);
    setSimilarTerms(null);

    const searchTopic = formData.get('topic') as string;
    if (!searchTopic) {
      setError('Please enter a topic.');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch('/api/get-similar-terms', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ topic: searchTopic }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to fetch similar terms');
      }

      const data = await response.json();
      setSimilarTerms(data.similarTerms);

    } catch (err: any) {
      console.error('Error searching for similar terms:', err);
      setError(err.message || 'An error occurred while searching. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>AI Wikipedia</h1>
      <form action={handleSearch}>
        <input
          type="text"
          placeholder="Enter a topic"
          name="topic"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      {similarTerms && similarTerms.length > 0 && (
        <div>
          <h2>Similar Terms:</h2>
          <ul className="similar-terms-list">
            {similarTerms.map((term, index) => (
              <li key={index}>
                <Link href={`/article/${encodeURIComponent(term)}`}>
                  {term}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}