import type { Metadata } from "next";
import { Inter, Lora } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-sans",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700", "800"],
});

const lora = Lora({
  variable: "--font-serif",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "Mike — Your Health Insurance Guide",
  description: "Understand your health insurance policy in plain language, verify coverage, and appeal claim denials.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${lora.variable} h-full antialiased dark`}
    >
      <body className="min-h-full flex flex-col bg-[#050816] text-[#f8fafc]">
        <div className="flex-1 flex flex-col">
          {children}
        </div>
        
        {/* Safety Disclaimer Footer */}
        <footer className="w-full text-center py-4 px-6 border-t border-white/5 bg-[#050816]/80 backdrop-blur-md text-[11px] text-slate-500 font-medium select-none z-10 shrink-0">
          <p className="max-w-3xl mx-auto leading-relaxed">
            Mike is an AI assistant, not an insurance broker or medical professional. Information provided is for general guidance only and must not be used as official claim authorizations or medical advice. Verify all coverage terms directly with your insurer before making healthcare decisions.
          </p>
        </footer>
      </body>
    </html>
  );
}
