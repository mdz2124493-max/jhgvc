# ⚡ Quick Start Guide - Ahanov Quest Completer

Get up and running in under 5 minutes!

---

## 🚀 Instant Demo (No Installation)

Want to try it right now? Follow these steps:

### Method 1: Direct File Opening

1. **Download** all files from this folder
2. **Open** `index.html` in any modern web browser:
   - Chrome (recommended)
   - Firefox
   - Edge
   - Safari

3. **That's it!** The app is ready to use.

### Method 2: Local Server (Recommended)

For the best experience with a local server:

#### Using Python (if installed):
```bash
# Navigate to the project folder
cd ahanov-quest-completer

# Start server
python -m http.server 8000

# Open browser to:
# http://localhost:8000
```

#### Using Node.js (if installed):
```bash
# Install http-server globally (one-time)
npm install -g http-server

# Start server
http-server -p 8000

# Open browser to:
# http://localhost:8000
```

#### Using PHP (if installed):
```bash
php -S localhost:8000
```

---

## 📱 Using the Application

### Step 1: Search for a Game

1. Click on the **search bar** at the top
2. Type a game name (e.g., "Valorant", "Fortnite", "Minecraft")
3. Browse the **search results** dropdown

### Step 2: Add Games

1. Click the **"Add"** button next to any game in search results
2. The game appears in your **"Selected Games"** panel on the left
3. Repeat for multiple games if desired

### Step 3: Select a Game

1. **Click on a game card** in the Selected Games panel
2. The game highlights with a **green glow**
3. Game details appear in the **"Game Control"** panel on the right

### Step 4: Choose Your Method

#### Method A: Run via Dummy Executable (Windows Only)

1. In the Game Control panel, scroll to **EXECUTABLES**
2. Click **"Install"** next to an executable
   - Wait for installation confirmation
3. Click **"Run"** to start the game
   - The game status changes to "Running"
   - A green pulsing dot appears on the game card
4. **Check Discord** - you should now appear as playing!

#### Method B: Connect via RPC (Experimental)

1. In the Game Control panel, click **"Connect via RPC"**
2. Wait for connection confirmation
3. **Check Discord** - you should now appear as playing!
4. Click **"Disconnect RPC"** when done

### Step 5: Monitor Progress

- Check the **Statistics Dashboard** at the top:
  - **Total Games**: Your game library count
  - **Active Sessions**: Currently running games
  - **Quest Progress**: Auto-calculated based on activity
  - **Connection Status**: ONLINE when RPC connected

### Step 6: Stop Playing

- For **dummy executables**: Click **"Stop"** in the executable list
- For **RPC connections**: Click **"Disconnect RPC"**

---

## 🎯 Complete a Discord Quest

1. **Start a game** using either method above
2. **Keep it running** for at least 15 minutes (most quests require this)
3. **Monitor** the Quest Progress stat
4. **Check Discord** periodically for quest completion
5. **Stop** when complete

---

## 💡 Tips & Tricks

### For Best Results:

✅ **Use Chrome or Edge** - Best compatibility and performance
✅ **Keep Discord open** - Required for activity detection
✅ **Run one game at a time** - Reduces detection issues
✅ **Wait 15+ minutes** - Most quests require continuous activity
✅ **Check Discord status** - Verify activity is showing

### Common Issues:

❌ **Game not appearing in Discord?**
   - Restart Discord
   - Ensure Discord is updated
   - Try the RPC method instead

❌ **Search not working?**
   - Check internet connection (for API fetch)
   - Use the sample games (loaded automatically)

❌ **Can't install executable?**
   - This is normal in the web demo
   - For full functionality, use the Tauri version (see BACKEND_IMPLEMENTATION.md)

---

## 🎨 Customization

### Change Colors

Edit `styles.css` and modify these variables:

```css
:root {
    --cyber-blue: #00d9ff;      /* Primary color */
    --cyber-purple: #9d4edd;    /* Secondary color */
    --cyber-pink: #ff006e;      /* Danger color */
    --cyber-green: #00ff9f;     /* Success color */
}
```

### Change Fonts

Edit the Google Fonts import in `index.html`:

```html
<link href="https://fonts.googleapis.com/css2?family=Your+Font&display=swap" rel="stylesheet">
```

Then update CSS:

```css
body {
    font-family: 'Your Font', monospace;
}
```

---

## 🔧 Advanced Setup (Full Functionality)

For Windows users who want full executable creation and process management:

1. **Read** `BACKEND_IMPLEMENTATION.md`
2. **Install** Tauri prerequisites
3. **Build** the Rust backend
4. **Integrate** with this frontend
5. **Enjoy** full Discord Quest Completer functionality!

See the complete guide in the documentation.

---

## 📚 Learn More

- **README.md** - Comprehensive documentation
- **FEATURES_COMPARISON.md** - See what's new vs original
- **BACKEND_IMPLEMENTATION.md** - Full desktop app setup
- **LICENSE** - Usage terms and disclaimer

---

## ⚠️ Important Reminders

1. **Educational Purpose**: This tool is for learning and personal use
2. **Terms of Service**: Using this may violate Discord's ToS
3. **Use Responsibly**: Don't spam or abuse the system
4. **At Your Own Risk**: We're not liable for any consequences

---

## 🆘 Need Help?

### The Demo Version (Current):
- ✅ Works in any browser
- ✅ Full UI/UX experience
- ✅ Simulated game management
- ❌ No actual Discord integration (demo only)

### The Full Version (Requires Setup):
- ✅ Full Discord integration
- ✅ Real executable creation
- ✅ Actual process management
- ✅ Quest completion capability

To get the full version working, follow the **BACKEND_IMPLEMENTATION.md** guide.

---

## 🎉 You're All Set!

Enjoy using **Ahanov Quest Completer**!

Remember to:
- ⭐ Star the project if you like it
- 🐛 Report issues if you find bugs
- 💡 Suggest features for future versions
- 🤝 Contribute if you want to improve it

**Happy Quest Completing!** 🚀✨

---

*Made with ⚡ by the Ahanov Team*
