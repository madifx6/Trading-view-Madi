import "./globals.css";

export const metadata = {
  title: "MADI TERMINAL — Independent Professional Forex Trading Platform",
  description: "Next-generation professional Forex charting, backtesting, and trading terminal.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
