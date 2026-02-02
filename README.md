# 🚀 Ahanov Quest Completer

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

> **Advanced Discord Game Activity Simulator** - Complete Discord Quests without installing massive game files

An enhanced, next-generation version of the Discord Quest Completer with a completely redesigned futuristic cyber-aesthetic frontend and advanced features.

---

## ✨ Features

### Core Functionality
- 🎮 **Simulate Discord Game Activity** - Appear as playing verified Discord games without installation
- ⚡ **Multiple Execution Methods** - Support for both dummy executables and Discord RPC
- 🔌 **Real-time RPC Connection** - Direct connection to Discord's Rich Presence Gateway
- 📊 **Live Statistics Dashboard** - Track active sessions, quest progress, and connection status
- 🎯 **Quest Completion** - Automatically track and complete Discord Quest requirements

### Advanced Features
- 🌐 **Modern Web Interface** - Sleek, futuristic cyber-aesthetic design
- 🔍 **Smart Game Search** - Fast, fuzzy search through verified Discord games
- 💾 **Session Management** - Track and manage multiple game sessions simultaneously
- 🎨 **Animated UI** - Smooth transitions, glowing effects, and dynamic backgrounds
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile devices
- ⚙️ **Executable Management** - Install and manage dummy game executables per game

### Visual Design
- 🌌 **Cyber-Futuristic Theme** - Animated grid backgrounds with floating orbs
- 💫 **Smooth Animations** - Carefully crafted micro-interactions and transitions
- 🎨 **Custom Typography** - Orbitron display font with JetBrains Mono for code
- ✨ **Glow Effects** - Dynamic neon glows and shadows for that cyberpunk feel

---

## 🏗️ Architecture

### Frontend (Web Interface)
- **Pure HTML/CSS/JavaScript** - No framework dependencies
- **Modern ES6+** - Clean, modular JavaScript
- **Responsive Design** - Mobile-first approach
- **Custom Animations** - CSS keyframes for smooth effects

### Backend Options

#### Option 1: Standalone Web Application (Current)
The current implementation is a pure frontend web application with simulated backend functionality. Perfect for:
- Quick demonstrations
- Testing the UI/UX
- Understanding the workflow

#### Option 2: Integration with Tauri/Electron (Recommended)
For full functionality, integrate with a desktop application framework:

**Tauri Backend (Rust)**
```rust
// Core functionality from original discord-quest-completer
#[tauri::command]
async fn create_fake_game(
    handle: tauri::AppHandle,
    path: &str,
    executable_name: &str,
    app_id: i64,
) -> Result<String, String> {
    // Creates dummy executable that Discord detects
}

#[tauri::command]
async fn run_background_process(
    name: &str,
    path: &str,
    executable_name: &str,
    app_id: i64,
) -> Result<String, String> {
    // Runs the dummy game process
}

#[tauri::command]
fn connect_to_discord_rpc(
    handle: AppHandle,
    activity_json: String,
) {
    // Connects to Discord RPC and sets activity
}
```

**Discord RPC Integration**
```rust
use discord_sdk::activity::ActivityBuilder;

pub async fn set_activity(activity_json: String) -> Result<Client, String> {
    let activity = create_activity(activity_json)?;
    let client = make_client(app_id, Subscriptions::ACTIVITY).await;
    client.discord.update_activity(activity).await?;
    Ok(client)
}
```

#### Option 3: Node.js Backend
For web-based deployment with real backend:

```javascript
const express = require('express');
const { Client } = require('discord-rpc');

app.post('/api/connect-rpc', async (req, res) => {
    const { appId, activity } = req.body;
    const rpc = new Client({ transport: 'ipc' });
    
    await rpc.login({ clientId: appId });
    await rpc.setActivity(activity);
    
    res.json({ success: true });
});
```

---

## 🚀 Installation & Setup

### Quick Start (Web Version)

1. **Clone or download** this repository
2. **Open `index.html`** in a modern web browser
3. **Start simulating!** Search for games and add them to your list

```bash
# Serve locally with Python
python -m http.server 8000

# Or with Node.js
npx http-server -p 8000

# Then open http://localhost:8000
```

### Full Desktop Application Setup

For full functionality with Discord integration:

1. **Install Tauri Prerequisites**
   - [Rust](https://www.rust-lang.org/tools/install)
   - [Node.js](https://nodejs.org/) (v18+)
   - [WebView2](https://developer.microsoft.com/en-us/microsoft-edge/webview2/) (Windows)

2. **Create Tauri Project**
```bash
npm create tauri-app@latest ahanov-quest-completer
cd ahanov-quest-completer
```

3. **Copy Files**
   - Copy `index.html`, `styles.css`, `app.js` to `src/` directory
   - Implement Rust backend commands (see Backend Implementation below)

4. **Build and Run**
```bash
npm install
npm run tauri dev    # Development
npm run tauri build  # Production
```

---

## 🎮 How It Works

### Method 1: Dummy Executable Simulation

1. **Executable Creation**: Creates small (~136KB) Windows executables that Discord recognizes
2. **Process Detection**: Discord detects the process by executable name and path
3. **Activity Display**: Your Discord status shows you're playing the game
4. **Quest Tracking**: Discord tracks the activity time for quest completion

```
User clicks "Install" 
    ↓
Create dummy .exe in games/{app_id}/{path}/{executable.exe}
    ↓
User clicks "Run"
    ↓
Execute the dummy process with game title
    ↓
Discord detects the process
    ↓
Rich Presence activity appears
```

### Method 2: Discord RPC Gateway

1. **Direct Connection**: Connects directly to Discord's RPC using the game's App ID
2. **Activity Update**: Sends Rich Presence activity updates
3. **Real-time Sync**: Updates activity in real-time without dummy executables
4. **Quest Support**: Experimental method that may trigger quest progress

```
User clicks "Connect via RPC"
    ↓
Connect to Discord RPC with App ID
    ↓
Send activity update with game details
    ↓
Discord displays the activity
    ↓
Maintain connection for quest duration
```

---

## 🎯 Usage Guide

### Adding Games

1. **Search**: Type game name in the search bar
2. **Browse**: View verified Discord games in the dropdown
3. **Add**: Click "Add" button next to the game
4. **Select**: Click on a game card to view its controls

### Running Games

#### Via Dummy Executable:
1. Select a game from your list
2. Choose an executable from the list
3. Click "Install" to create the dummy exe
4. Click "Run" to start the process
5. Check Discord for the activity

#### Via RPC Connection:
1. Select a game from your list
2. Click "Connect via RPC"
3. Wait for connection confirmation
4. Check Discord for the activity
5. Click "Disconnect RPC" when done

### Completing Quests

1. **Start Activity**: Run a game or connect via RPC
2. **Wait 15 Minutes**: Most quests require 15 minutes of playtime
3. **Monitor Progress**: Check the Quest Progress stat
4. **Verify in Discord**: Open Discord to confirm quest completion

---

## 🔧 Backend Implementation Guide

### Implementing the Rust Backend

Create `src-tauri/src/lib.rs`:

```rust
use tauri::{AppHandle, Manager};
use std::path::Path;

mod runner;
mod rpc;

#[tauri::command]
async fn create_fake_game(
    handle: AppHandle,
    path: &str,
    executable_name: &str,
    app_id: i64,
) -> Result<String, String> {
    let exe_path = std::env::current_exe().unwrap();
    let exe_dir = exe_path.parent().unwrap();
    
    let game_folder = exe_dir
        .join("games")
        .join(app_id.to_string())
        .join(path);
    
    std::fs::create_dir_all(&game_folder)
        .map_err(|e| format!("Failed to create directory: {}", e))?;
    
    let resource_path = handle
        .path()
        .resolve("data/dummy.exe", BaseDirectory::Resource)
        .unwrap();
    
    let target_path = game_folder.join(executable_name);
    
    std::fs::copy(&resource_path, &target_path)
        .map_err(|e| format!("Failed to copy executable: {}", e))?;
    
    Ok(format!("Created: {:?}", target_path))
}

#[tauri::command]
async fn run_game_process(
    name: &str,
    path: &str,
    executable_name: &str,
    app_id: i64,
) -> Result<String, String> {
    let exe_path = std::env::current_exe().unwrap();
    let exe_dir = exe_path.parent().unwrap();
    
    let game_folder = exe_dir
        .join("games")
        .join(app_id.to_string())
        .join(path);
    
    let executable_path = game_folder.join(executable_name);
    
    std::process::Command::new(&executable_path)
        .args(["--title", name])
        .current_dir(game_folder)
        .spawn()
        .map_err(|e| format!("Failed to start process: {}", e))?;
    
    Ok("Process started".to_string())
}

#[tauri::command]
async fn stop_game_process(exec_name: String) -> Result<(), String> {
    std::process::Command::new("taskkill")
        .arg("/F")
        .arg("/IM")
        .arg(exec_name)
        .output()
        .map_err(|e| format!("Failed to stop process: {}", e))?;
    
    Ok(())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            create_fake_game,
            run_game_process,
            stop_game_process,
        ])
        .run(tauri::generate_context!())
        .expect("error while running application");
}
```

### Frontend Integration with Tauri

Update `app.js` to call Tauri commands:

```javascript
// Instead of setTimeout simulation
async installExecutable(gameUid, executableName) {
    const game = this.selectedGames.find(g => g.uid === gameUid);
    if (!game) return;

    try {
        const exe = game.executables.find(e => e.name === executableName);
        
        const result = await window.__TAURI__.invoke('create_fake_game', {
            path: exe.launcher_path || '',
            executableName: exe.name,
            appId: parseInt(game.id)
        });
        
        game.installedExecutables.push(executableName);
        game.isInstalled = true;
        this.showNotification(`Installed ${executableName}`, 'success');
    } catch (error) {
        this.showNotification(`Failed to install: ${error}`, 'error');
    }
}

async runExecutable(gameUid, executableName) {
    const game = this.selectedGames.find(g => g.uid === gameUid);
    if (!game) return;

    try {
        const exe = game.executables.find(e => e.name === executableName);
        
        await window.__TAURI__.invoke('run_game_process', {
            name: game.name,
            path: exe.launcher_path || '',
            executableName: exe.name,
            appId: parseInt(game.id)
        });
        
        game.isRunning = true;
        game.runningExecutable = executableName;
        this.showNotification(`${game.name} is running`, 'success');
    } catch (error) {
        this.showNotification(`Failed to run: ${error}`, 'error');
    }
}
```

---

## ⚠️ Important Notes

### Discord Terms of Service

This tool operates in a gray area regarding Discord's Terms of Service:

- ✅ **Allowed**: Using Rich Presence for games you own
- ⚠️ **Gray Area**: Simulating game activity without actually playing
- ❌ **Prohibited**: Using for spam, fraud, or malicious purposes

**Recommendation**: Use responsibly and at your own risk. This is primarily an educational tool.

### Quest Completion Considerations

- Most quests require **15 minutes** of continuous activity
- Some quests may require **streaming** (experimental support)
- Quest rewards may be delayed or not granted if detected as simulation
- Your Discord account could be flagged for unusual activity patterns

### Technical Limitations

- **Windows Only** (currently) - Linux/macOS support requires additional work
- **Verified Games Only** - Only works with Discord-verified games
- **No Multiplayer** - Cannot join actual game servers
- **Detection Risk** - Discord may detect and prevent simulated activities

---

## 🎨 Customization

### Changing the Theme

Edit `styles.css` to modify colors:

```css
:root {
    --cyber-blue: #00d9ff;      /* Primary accent */
    --cyber-purple: #9d4edd;    /* Secondary accent */
    --cyber-pink: #ff006e;      /* Danger/remove */
    --cyber-green: #00ff9f;     /* Success/active */
}
```

### Adding Custom Games

Add games to the database in `app.js`:

```javascript
getSampleGames() {
    return [
        {
            id: 'YOUR_GAME_ID',
            name: 'Your Game Name',
            executables: [
                { name: 'YourGame.exe', os: 'win32' }
            ],
            aliases: ['Alias1', 'Alias2']
        }
    ];
}
```

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- Based on the original [discord-quest-completer](https://github.com/markterence/discord-quest-completer) by Mark Terence Tiglao
- Discord RPC implementation using [discord-sdk](https://crates.io/crates/discord-sdk)
- Font families: Orbitron and JetBrains Mono from Google Fonts

---

## 📞 Support

For issues, questions, or suggestions:

- Open an issue on GitHub
- Check existing documentation
- Review Discord's developer documentation

---

## 🔮 Future Enhancements

- [ ] Linux and macOS support
- [ ] Persistent game list storage
- [ ] Custom activity status builder
- [ ] Automated quest detection
- [ ] Multi-account support
- [ ] Stream simulation support
- [ ] Activity scheduling
- [ ] Analytics and statistics export

---

**Made with ⚡ by the Ahanov Team**

*Remember: Use responsibly and respect Discord's Terms of Service*
