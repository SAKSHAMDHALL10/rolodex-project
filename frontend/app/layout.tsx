import type { Metadata } from "next";
import { Fraunces, Inter, IBM_Plex_Mono } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/hooks/useTheme";
import { ToastProvider } from "@/hooks/useToast";
import { Sidebar } from "@/components/layout/Sidebar";
import { MobileNav } from "@/components/layout/MobileNav";

const fraunces = Fraunces({
  subsets: ["latin"],
  variable: "--font-fraunces",
  weight: ["400", "500", "600"],
  style: ["normal", "italic"],
});

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

const plexMono = IBM_Plex_Mono({
  subsets: ["latin"],
  variable: "--font-plex-mono",
  weight: ["400", "500"],
});

export const metadata: Metadata = {
  title: "Rolodex — who do we know who does that?",
  description:
    "An AI-powered searchable rolodex: turn LinkedIn profiles into structured, " +
    "semantically searchable professional-relevance entries.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className={`${fraunces.variable} ${inter.variable} ${plexMono.variable} font-sans`}>
        <ThemeProvider>
          <ToastProvider>
            <div className="flex min-h-screen">
              <Sidebar />
              <main className="flex-1 pb-20 md:pb-0">
                <div className="mx-auto w-full max-w-6xl px-4 py-8 sm:px-6 lg:px-10">
                  {children}
                </div>
              </main>
            </div>
            <MobileNav />
          </ToastProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
