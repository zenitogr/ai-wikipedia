import React from 'react';

export default function AboutPage() {
  return (
    <div className="container">
      <div className="about-page">
        <h1>About AI Wiki</h1>
        <p>Welcome to AI Wiki, a web application that generates Wikipedia-style articles based on user-provided topics. Our application leverages the power of AI through the Groq API to create informative and engaging content, and uses Wikimedia Commons to fetch related images.</p>

        <h2>Features</h2>
        <ul>
          <li>Generate Wikipedia-style articles with sections, images, and a sidebar.</li>
          <li>Dynamically generate a Table of Contents for each article.</li>
          <li>Fetch relevant images from Wikimedia Commons.</li>
          <li>Caching of generated articles for improved performance.</li>
          <li>User-friendly interface for searching and viewing articles.</li>
        </ul>

        <h2>Technologies Used</h2>
        <ul>
          <li><strong>Next.js</strong>: React framework for server-side rendering and routing.</li>
          <li><strong>React</strong>: JavaScript library for building user interfaces.</li>
          <li><strong>Groq</strong>: For generating article content using AI.</li>
          <li><strong>Wikimedia API</strong>: For searching and fetching images.</li>
          <li><strong>SQLite (via @vercel/postgres)</strong>: For caching generated articles.</li>
          <li><strong>Marked</strong>: For converting markdown article content to HTML.</li>
        </ul>

        <h2>Contributing</h2>
        <p>Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.</p>

        <h2>License</h2>
        <p>This project is licensed under the MIT License. See the LICENSE file for details.</p>

        <h2>Acknowledgments</h2>
        <ul>
          <li><a href="https://nextjs.org/">Next.js</a></li>
          <li><a href="https://react.dev/">React</a></li>
          <li><a href="https://groq.com/">Groq</a></li>
          <li><a href="https://commons.wikimedia.org/">Wikimedia Commons</a></li>
          <li><a href="https://marked.js.org/">Marked</a></li>
        </ul>
      </div>
    </div>
  );
}