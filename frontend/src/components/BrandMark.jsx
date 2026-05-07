export default function BrandMark({ className = "", size = 40, title = "StockMarketAnalyzer" }) {
  return (
    <svg
      viewBox="0 0 256 256"
      width={size}
      height={size}
      role="img"
      aria-label={title}
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      <rect width="256" height="256" rx="56" fill="#0F172A" />
      <rect x="24" y="24" width="208" height="208" rx="44" fill="url(#brandmark-bg)" />
      <path d="M64 168H192" stroke="#C7D2FE" strokeWidth="10" strokeLinecap="round" opacity="0.9" />
      <path d="M64 168V88" stroke="#C7D2FE" strokeWidth="10" strokeLinecap="round" opacity="0.9" />
      <rect x="86" y="124" width="18" height="44" rx="9" fill="#34D399" />
      <rect x="118" y="104" width="18" height="64" rx="9" fill="#F8FAFC" />
      <rect x="150" y="86" width="18" height="82" rx="9" fill="#34D399" />
      <path d="M76 146L108 128L128 138L160 96L182 106" stroke="#22C55E" strokeWidth="12" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx="182" cy="106" r="11" fill="#22C55E" />
      <defs>
        <linearGradient id="brandmark-bg" x1="40" y1="40" x2="216" y2="216" gradientUnits="userSpaceOnUse">
          <stop stopColor="#1E293B" />
          <stop offset="1" stopColor="#0B1220" />
        </linearGradient>
      </defs>
    </svg>
  );
}
