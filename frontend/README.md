# Minimalist GenAI Book - Reader App

This is the frontend companion app for the AI Book Generator. It provides a clean, Kindle-like reading experience for the generated chapters.

## Features
- 📖 **Kindle Aesthetic**: Serif fonts, optimized line height, and wide margins.
- 🌓 **Themes**: Choose between Paper, Ivory, and Dark mode.
- 📱 **Responsive**: Perfect reading experience on Phone, Tablet, and Desktop.
- ⚡ **Vite Powered**: Instant loading and smooth transitions.

## How to Deploy to GitHub Pages

1. **Create a new repository** on GitHub named `minimalist_genai_book`.
2. **Push this code** to that repository:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Kindle-like Reader"
   git remote add origin https://github.com/YOUR_USERNAME/minimalist_genai_book.git
   git push -u origin main
   ```
3. **Enable GitHub Pages**:
   - Go to Settings > Pages.
   - Set Build and deployment source to **GitHub Actions**.
   - The included workflow will automatically build and deploy the site.

## Syncing New Chapters

Whenever you generate new chapters in your main project, run:
```bash
python sync_to_web.py
```
Then commit and push the `frontend/public/content/` folder.
