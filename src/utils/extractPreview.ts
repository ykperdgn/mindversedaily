import type { MarkdownInstance } from 'astro';

interface PreviewConfig { type?: 'words' | 'break' | 'percent'; value?: number; }

export function extractPreview(raw: string, config: PreviewConfig = {}): string {
  const { type = 'words', value } = config;
  const startMarker = '<!-- preview-start -->';
  const endMarker = '<!-- preview-end -->';

  if (type === 'break') {
    const start = raw.indexOf(startMarker);
    const end = raw.indexOf(endMarker);
    if (start !== -1 && end !== -1 && end > start) {
      return raw.substring(start + startMarker.length, end).trim();
    }
  }

  // Remove frontmatter & HTML comments except preview markers
  const content = raw
    .replace(/^---[\s\S]*?---/,'')
    .replace(/<!--(?!\s*preview-(start|end)\s*-->)[\s\S]*?-->/g,'')
    .trim();

  const wordList = content.split(/\s+/);

  if (type === 'percent' && value) {
    const count = Math.max(1, Math.floor((value/100) * wordList.length));
    return wordList.slice(0, count).join(' ') + '…';
  }

  if (type === 'words' && value) {
    if (wordList.length <= value) return content;
    return wordList.slice(0, value).join(' ') + '…';
  }

  // Fallback: try markers or first 120 words
  const s = raw.indexOf(startMarker);
  const e = raw.indexOf(endMarker);
  if (s !== -1 && e !== -1 && e > s) {
    return raw.substring(s + startMarker.length, e).trim();
  }
  return wordList.slice(0, 120).join(' ') + (wordList.length > 120 ? '…' : '');
}
