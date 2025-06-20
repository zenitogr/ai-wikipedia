import './static/css/style.css'; // Assuming you want to keep your existing CSS
import Link from 'next/link'; // Import Link for navigation

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <header>
          <nav>
            <Link href="/" className="nav-button">Generate Article</Link>
            <Link href="/cached-articles" className="nav-button">Cached Articles</Link>
            <Link href="/about" className="nav-button">About</Link>
          </nav>
        </header>
        <div className="container">
          {children}
        </div>
      </body>
    </html>
  );
}