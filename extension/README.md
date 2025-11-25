# Browser Extension - Installation Guide

## Features

- 🔍 Check any URL with one click
- 🖱️ Right-click context menu
- 📊 See verdict and confidence
- 🎯 View top contributing features
- 📜 Auto-save check history
- 🔔 Desktop notifications

## Install in Chrome

1. **Open Chrome Extensions**
   - Go to `chrome://extensions/`
   - Enable "Developer mode" (top right)

2. **Load Extension**
   - Click "Load unpacked"
   - Select the `extension` folder
   - Extension icon will appear in toolbar

3. **Test It**
   - Click the extension icon
   - Or right-click any link → "Check URL for Phishing"

## Install in Firefox

1. **Open Firefox Add-ons**
   - Go to `about:debugging#/runtime/this-firefox`

2. **Load Extension**
   - Click "Load Temporary Add-on"
   - Select `extension/manifest.json`
   - Extension icon will appear in toolbar

3. **Test It**
   - Click the extension icon
   - Or right-click any link → "Check URL for Phishing"

## How to Use

### Method 1: Extension Popup
1. Click extension icon in toolbar
2. Current page URL will show automatically
3. Click "Check This Page"
4. Or enter any URL manually

### Method 2: Context Menu
1. Right-click any link on a webpage
2. Select "Check URL for Phishing"
3. Get instant notification with verdict

### Method 3: Manual Entry
1. Click extension icon
2. Type or paste URL
3. Click "Check URL"

## What You'll See

**Benign URL** (Safe)
- ✓ Green badge
- High confidence score
- Safe to visit

**Malicious URL** (Dangerous)
- ✗ Red/orange badge
- High confidence score
- DO NOT visit!

**Suspicious URL** (Caution)
- ⚠ Pink badge
- Medium confidence
- Proceed with caution

## Features Explained

**Top Features** - Shows why the URL was flagged:
- `suspicious_keywords` - Contains words like "login", "verify"
- `url_length` - Unusually long URL
- `char_entropy` - Random-looking domain
- `has_ip_address` - Uses IP instead of domain
- `hyphen_count` - Too many hyphens

## Requirements

- Backend must be running at `http://localhost:8000`
- Chrome 88+ or Firefox 109+

## Troubleshooting

### Extension won't load
- Make sure you selected the `extension` folder, not a file
- Check that all files are present (manifest.json, popup.html, etc.)

### "Failed to check URL" error
- Make sure backend is running: `./run_backend.sh`
- Check backend is at http://localhost:8000
- Test API: http://localhost:8000/health

### Context menu not showing
- Reload the extension
- Right-click on a link (not empty space)

### Icons not showing
- Icons are in `extension/icons/` folder
- Reload the extension after adding icons

## Privacy

- URLs are sent to your local backend only
- No data sent to external servers
- History stored locally in browser
- Clear history: Right-click extension → Options → Clear

## Uninstall

**Chrome**: chrome://extensions/ → Remove
**Firefox**: about:addons → Remove

## Development

To modify the extension:

1. Edit files in `extension/` folder
2. Go to extensions page
3. Click reload icon on the extension
4. Test changes

## Files

```
extension/
├── manifest.json      # Extension config
├── popup.html         # Popup UI
├── popup.js          # Popup logic
├── background.js     # Background worker
└── icons/            # Extension icons
    ├── icon16.png
    ├── icon48.png
    └── icon128.png
```

## Tips

- Pin extension to toolbar for quick access
- Use keyboard shortcut (set in browser settings)
- Check URLs before clicking suspicious links
- Share extension with team members

## Support

If you encounter issues:
1. Check backend is running
2. Check browser console (F12)
3. Reload extension
4. Clear browser cache

---

**Version**: 1.0.0
**Compatibility**: Chrome 88+, Firefox 109+
**License**: MIT
