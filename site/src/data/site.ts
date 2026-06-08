export const siteConfig = {
  title: 'AI Agent Automations',
  description:
    'A focused directory of practical AI automations you can run as-is, adapt to your tools, or use as starting points for your own agent workflows.',
  heroKicker: 'ai-agent-automations / index',
  heroTitlePrefix: 'Ready-to-run AI',
  heroTitleAccent: 'automations',
  heroTitleSuffix: 'for real workflows.',
  worksWithLabel: 'Works with:',
  repoUrl: 'https://github.com/ChmaraX/ai-agent-automations',
  repoName: 'ChmaraX/ai-agent-automations',
  repoKicker: 'GitHub repository',
  repoCta: 'Star ★',
  heroVideoSrc: '/media/home-hero.webm',
  logos: [
    { src: '/logos/codex.png', alt: 'Codex', className: 'agent-logo-codex' },
    { src: '/logos/claude.png', alt: 'Claude', className: 'agent-logo-claude' },
    { src: '/logos/cursor.png', alt: 'Cursor', className: 'agent-logo-cursor' },
  ],
} as const;

export type SiteConfig = typeof siteConfig;
