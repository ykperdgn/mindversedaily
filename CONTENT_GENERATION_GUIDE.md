# MindVerse Content Generation System

## 🎯 Overview

The MindVerse blog now has a unified content generation system that supports both automatic and manual content creation in English and Turkish.

## 🚀 System Architecture

### Automatic Mode (Production)
- **API**: Groq (English only)
- **Frequency**: 3 times daily (09:00, 15:00, 21:00)
- **Language**: English (.en.md files)
- **Categories**: health, psychology, history, space, quotes, love
- **Articles**: 1 per category per run

### Manual Mode (On-demand)
- **English**: Groq API → .en.md files
- **Turkish**: Ollama API → .tr.md files
- **Categories**: All available categories
- **Flexible**: Custom count and category selection

## 📋 Quick Usage

### For English Content
```bash
# Quick generation (1 article each for health & psychology)
generate_english.bat health psychology

# Custom generation
python scripts/unified_content_generator.py --mode manual --language en --categories health space --count 2
```

### For Turkish Content
```bash
# Quick generation (1 article each for health & psychology)
generate_turkish.bat health psychology

# Custom generation
python scripts/unified_content_generator.py --mode manual --language tr --categories health space --count 2
```

### Interactive Manual Generation
```bash
generate_content_manual.bat
```

## 🔧 API Configuration

### Groq API (English)
- **Model**: mixtral-8x7b-32768
- **Rate Limit**: 2 seconds between requests
- **Output**: Professional English articles (800-1200 words)
- **File Suffix**: .en.md

### Ollama API (Turkish)
- **Model**: llama3:latest
- **Rate Limit**: 5 seconds between requests
- **Output**: Professional Turkish articles (800-1200 words)
- **File Suffix**: .tr.md

## 📁 File Structure

```
scripts/
├── unified_content_generator.py    # Main unified generator
├── groq_client.py                  # Groq API client
├── image_fetcher.py               # Image fetching utility
├── master_automation.py           # Automatic scheduling system
└── automation_config.json         # System configuration

# Quick Commands
├── generate_content_manual.bat    # Interactive content generation
├── generate_english.bat           # Quick English content
└── generate_turkish.bat           # Quick Turkish content
```

## ⚙️ Configuration

### Automation Config (automation_config.json)
```json
{
  "content_generation": {
    "automatic": {
      "enabled": true,
      "mode": "auto",
      "language": "en",
      "api": "groq",
      "articles_per_run": 1,
      "max_daily_articles": 6
    }
  }
}
```

## 🎛️ Command Line Options

### Unified Content Generator
```bash
python scripts/unified_content_generator.py [OPTIONS]

Options:
  --mode {auto,manual}     Generation mode (default: auto)
  --language {en,tr}       Content language (default: en)
  --categories CATEGORIES  Categories to generate for (space-separated)
  --count COUNT           Articles per category (default: 1)
```

### Examples
```bash
# Automatic mode (English only)
python scripts/unified_content_generator.py --mode auto

# Manual English content
python scripts/unified_content_generator.py --mode manual --language en --categories health psychology --count 2

# Manual Turkish content
python scripts/unified_content_generator.py --mode manual --language tr --categories health space --count 1
```

## 📊 Content Categories

### Available Categories
- **health**: Health and wellness topics
- **psychology**: Psychology and mental health
- **history**: Historical events and discoveries
- **space**: Space exploration and astronomy
- **quotes**: Inspirational quotes and wisdom
- **love**: Relationships and romance
- **business**: Business and entrepreneurship (Turkish only)
- **science**: Science and research (Turkish only)
- **world**: World news and events (Turkish only)

## 🔄 Automatic Scheduling

The system automatically generates English content 3 times daily:
- **09:00**: Morning content generation
- **15:00**: Afternoon content generation
- **21:00**: Evening content generation

Each run generates 1 article per category, totaling 6 articles daily.

## 🛠️ Manual Content Generation

### Interactive Mode
Run `generate_content_manual.bat` for guided content generation with options for:
1. English content (Groq API)
2. Turkish content (Ollama API)
3. Custom configuration

### Quick Commands
- `generate_english.bat [categories]` - Quick English content
- `generate_turkish.bat [categories]` - Quick Turkish content

### Direct Python Commands
```bash
# English content for specific categories
python scripts/unified_content_generator.py --mode manual --language en --categories health psychology history --count 1

# Turkish content for specific categories
python scripts/unified_content_generator.py --mode manual --language tr --categories health space quotes --count 2
```

## 📈 Monitoring and Logs

- **Logs**: Stored in `scripts/logs/`
- **Monitoring**: System health checks every 30 minutes
- **Status**: Check `automation_dashboard.html` for system status

## 🔧 Troubleshooting

### Common Issues
1. **Groq API Rate Limits**: System automatically handles rate limiting
2. **Ollama Not Running**: Ensure Ollama service is active for Turkish content
3. **Duplicate Titles**: System automatically prevents duplicate content
4. **File Permissions**: Ensure write permissions for `src/content/blog/`

### API Status Check
```bash
# Check Groq API
python scripts/groq_client.py

# Check Ollama API
curl http://localhost:11434/api/generate -d '{"model":"llama3:latest","prompt":"test"}'
```

## 📝 Content Quality

### English Content (Groq)
- Professional tone and structure
- SEO-optimized content
- Latest research and insights
- 800-1200 words per article

### Turkish Content (Ollama)
- Native Turkish writing style
- Cultural relevance
- Technical accuracy
- 800-1200 words per article

## 🚀 Deployment Integration

After content generation:
1. System automatically commits changes to Git
2. Vercel auto-deploys updated content
3. New articles appear on the live site within minutes

## 🔐 Security

- API keys stored in environment variables
- Rate limiting prevents API abuse
- Input validation and sanitization
- Secure file handling and permissions
