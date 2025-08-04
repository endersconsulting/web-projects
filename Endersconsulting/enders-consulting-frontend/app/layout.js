// app/layout.js
// This is the root layout file for the App Router.
// It should remain a Server Component for best performance.

import '../styles/globals.css';

// The metadata API is the correct way to handle <head> elements in Server Components.
export const metadata = {
  title: 'Enders Consulting - Professional Services',
  description: 'Enders Consulting professional services website built with Next.js and Flask.',
  icons: {
    icon: '/favicon.ico',
  },
};

export default function RootLayout({ children }) {
  return (
    // By adding suppressHydrationWarning, we tell React to ignore
    // attribute mismatches on the <html> tag caused by browser extensions.
    <html lang="en" suppressHydrationWarning>
      <body>{children}</body>
    </html>
  );
}