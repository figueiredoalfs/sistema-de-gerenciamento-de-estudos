import React from 'react';

/**
 * Símbolo: dois hexágonos regulares pointy-top sobrepostos formando um S.
 *
 * R = 30  |  cx = 50  |  cy1 = 40  |  cy2 = cy1 + R = 70
 *
 * Vértices (V1 aponta para o NORTE, numeração horária):
 *   H1: V1(50,10)  V2(76,25)  V3(76,55)†  V4(50,70)  V5(24,55)  V6(24,25)
 *   H2: U1(50,40)  U2(76,55)  U3(76,85)   U4(50,100) U5(24,85)† U6(24,55)
 *   † isolado — não desenhado
 *
 * Restrições verificadas:
 *   V4(50,70) = centro de H2  ✓
 *   U1(50,40) = centro de H1  ✓
 *
 * Nó compartilhado (ponto único na cintura do S):
 *   V5 = U6 = (24, 55)
 *
 * Arestas removidas:
 *   H1: V2-V3 e V3-V4  →  V3 isolado
 *   H2: U4-U5 e U5-U6  →  U5 isolado
 *
 * Arestas visíveis (8 total):
 *   H1: V6-V1  V1-V2  V4-V5  V5-V6
 *   H2: U6-U1  U1-U2  U2-U3  U3-U4
 */
const Logo = ({ className = "h-12", showText = true }) => {
  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <svg
        viewBox="0 0 100 110"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="h-full w-auto drop-shadow-[0_0_12px_rgba(6,182,212,0.5)]"
      >
        <defs>
          <linearGradient id="sg" x1="50" y1="0" x2="50" y2="110" gradientUnits="userSpaceOnUse">
            <stop offset="0%"   stopColor="#06B6D4" />
            <stop offset="50%"  stopColor="#6366F1" />
            <stop offset="100%" stopColor="#A855F7" />
          </linearGradient>
          <filter id="glow" x="-80%" y="-80%" width="260%" height="260%">
            <feGaussianBlur stdDeviation="3" result="b" />
            <feMerge>
              <feMergeNode in="b" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* ── Diagonais internas (mais finas, por baixo) ─── */}
        <g stroke="url(#sg)" strokeWidth="2.5" strokeLinecap="round" strokeOpacity="0.55">
          {/* H1: V1–V5 e V6–V4 */}
          <line x1="50" y1="10" x2="24" y2="55" />  {/* V1–V5 */}
          <line x1="24" y1="25" x2="50" y2="70" />  {/* V6–V4 */}
          {/* H2: U1–U3 e U2–U4 */}
          <line x1="50" y1="40" x2="76" y2="85" />  {/* U1–U3 */}
          <line x1="76" y1="55" x2="50" y2="100" /> {/* U2–U4 */}
        </g>

        {/* ── Arestas ─────────────────────────────────────── */}
        <g stroke="url(#sg)" strokeWidth="4.5" strokeLinecap="round" strokeOpacity="0.85">
          {/* H1: sem V2-V3 e V3-V4 */}
          <line x1="24" y1="25" x2="50" y2="10" />  {/* V6–V1 */}
          <line x1="50" y1="10" x2="76" y2="25" />  {/* V1–V2 */}
          <line x1="50" y1="70" x2="24" y2="55" />  {/* V4–V5 */}
          <line x1="24" y1="55" x2="24" y2="25" />  {/* V5–V6 (vertical esquerda) */}

          {/* H2: sem U4-U5 e U5-U6 */}
          <line x1="24" y1="55" x2="50" y2="40" />  {/* U6–U1 */}
          <line x1="50" y1="40" x2="76" y2="55" />  {/* U1–U2 */}
          <line x1="76" y1="55" x2="76" y2="85" />  {/* U2–U3 (vertical direita) */}
          <line x1="76" y1="85" x2="50" y2="100" /> {/* U3–U4 */}
        </g>

        {/* ── Nós ─────────────────────────────────────────── */}
        {/* Topo — cyan */}
        <circle cx="50" cy="10"  r="7.5" fill="#06B6D4" filter="url(#glow)" />  {/* V1 */}
        <circle cx="76" cy="25"  r="6.5" fill="#1BADD4" />                       {/* V2 */}
        <circle cx="24" cy="25"  r="6.5" fill="#1BADD4" />                       {/* V6 */}

        {/* Cintura superior — indigo */}
        <circle cx="50" cy="40"  r="7"   fill="#4F72F0" />                       {/* U1 */}

        {/* Cintura — nó compartilhado V5=U6 (ponto único) */}
        <circle cx="24" cy="55"  r="8"   fill="#6366F1" filter="url(#glow)" />  {/* V5=U6 */}

        {/* Cintura direita */}
        <circle cx="76" cy="55"  r="6.5" fill="#6B68F2" />                       {/* U2 */}

        {/* Centro-baixo H1 */}
        <circle cx="50" cy="70"  r="7"   fill="#7C5CF4" />                       {/* V4 */}

        {/* Base — violet */}
        <circle cx="76" cy="85"  r="6.5" fill="#9055F5" />                       {/* U3 */}
        <circle cx="50" cy="100" r="7.5" fill="#A855F7" filter="url(#glow)" />  {/* U4 */}
      </svg>

      {showText && (
        <span className="text-2xl font-black tracking-tighter flex">
          <span className="text-brand-text">Skol</span>
          <span className="bg-clip-text text-transparent bg-gradient-to-br from-cyan-400 via-indigo-500 to-purple-600">
            AI
          </span>
        </span>
      )}
    </div>
  );
};

export default Logo;
