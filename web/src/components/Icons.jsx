export function HexIcon({ children, size = 40 }) {
  return (
    <span className="hex-icon" style={{ width: size, height: size }} aria-hidden="true">
      {children}
    </span>
  );
}

export function IconHive() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
      <path d="M12 3 19 7v10l-7 4-7-4V7l7-4Z" />
      <path d="M12 8v8M8.5 10.5 12 12.5l3.5-2" />
    </svg>
  );
}

export function IconSensor() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
      <circle cx="12" cy="12" r="3" />
      <path d="M12 5V3M12 21v-2M5 12H3M21 12h-2M6.5 6.5 5 5M18 18l-1.5-1.5M6.5 17.5 5 19M18 6l-1.5 1.5" />
    </svg>
  );
}

export function IconChain() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
      <path d="M9 12a4 4 0 0 1 0-5.7l2-2a4 4 0 0 1 5.7 5.7l-1 1" />
      <path d="M15 12a4 4 0 0 1 0 5.7l-2 2a4 4 0 0 1-5.7-5.7l1-1" />
    </svg>
  );
}

export function IconQr() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
      <path d="M4 4h6v6H4zM14 4h6v6h-6zM4 14h6v6H4zM14 14h2v2h-2zM18 14h2v2h-2zM14 18h2v2h-2zM18 18h2v2h-2z" />
    </svg>
  );
}

export function IconMarket() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
      <path d="M4 10h16l-1 10H5L4 10Z" />
      <path d="M8 10V6a4 4 0 0 1 8 0v4" />
    </svg>
  );
}

export function IconLang() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
      <circle cx="12" cy="12" r="9" />
      <path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18" />
    </svg>
  );
}

export function IconYield() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
      <path d="M4 18V6M4 18h16" />
      <path d="M7 14l4-5 3 3 5-7" />
    </svg>
  );
}

export function IconBell() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
      <path d="M6 16V11a6 6 0 1 1 12 0v5l1.5 2h-15L6 16Z" />
      <path d="M10 20a2 2 0 0 0 4 0" />
    </svg>
  );
}

export function IconSearch() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
      <circle cx="11" cy="11" r="6" />
      <path d="M16 16l5 5" />
    </svg>
  );
}

export function HeroHive() {
  return (
    <svg className="hero-hive" viewBox="0 0 280 220" fill="none" aria-hidden="true">
      <g stroke="#9a6a16" strokeWidth="1.2" opacity="0.45">
        <polygon points="140,18 178,40 178,84 140,106 102,84 102,40" />
        <polygon points="178,84 216,106 216,150 178,172 140,150 140,106" />
        <polygon points="102,84 140,106 140,150 102,172 64,150 64,106" />
        <polygon points="140,106 178,128 178,172 140,194 102,172 102,128" />
      </g>
      <g fill="#d4b56a" opacity="0.85">
        <polygon points="140,40 166,55 166,85 140,100 114,85 114,55" />
      </g>
      <circle cx="140" cy="70" r="8" fill="#2b2218" />
    </svg>
  );
}

export function EmptyHive() {
  return (
    <svg viewBox="0 0 120 90" fill="none" className="empty-art" aria-hidden="true">
      <polygon points="60,8 92,26 92,62 60,80 28,62 28,26" stroke="#9a6a16" strokeWidth="1.4" />
      <path d="M44 48h32" stroke="#cbbda6" strokeWidth="1.4" />
    </svg>
  );
}
