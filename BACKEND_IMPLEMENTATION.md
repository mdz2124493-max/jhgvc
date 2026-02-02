# Rust Backend Implementation for Ahanov Quest Completer

This directory contains the Rust backend code for the Ahanov Quest Completer.
It implements the core Discord game detection and RPC functionality.

## File Structure

```
src-tauri/
├── Cargo.toml              # Rust dependencies
├── src/
│   ├── main.rs            # Application entry point
│   ├── lib.rs             # Main library with Tauri commands
│   ├── runner.rs          # Discord RPC activity runner
│   └── rpc.rs             # Discord RPC client implementation
└── resources/
    └── dummy.exe          # Template dummy game executable
```

## Cargo.toml Dependencies

```toml
[package]
name = "ahanov-quest-completer"
version = "1.0.0"
edition = "2021"

[build-dependencies]
tauri-build = { version = "2.0", features = [] }

[dependencies]
tauri = { version = "2.0", features = ["protocol-asset"] }
tauri-plugin-dialog = "2.0"
tauri-plugin-http = "2.0"
tauri-plugin-opener = "2.0"
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
tokio = { version = "1.35", features = ["full"] }
discord-sdk = "0.3"
once_cell = "1.19"

[target.'cfg(windows)'.dependencies]
windows = { version = "0.52", features = [
    "Win32_Foundation",
    "Win32_System_Threading",
    "Win32_System_ProcessStatus",
] }
```

## lib.rs - Main Tauri Commands

```rust
use once_cell::sync::OnceCell;
use std::env;
use std::path::Path;
use std::sync::Mutex;
use tauri::{path::BaseDirectory, AppHandle, Emitter, Manager};

mod rpc;
mod runner;

// Global Discord RPC client instance
static DISCORD_CLIENT: OnceCell<Mutex<Option<rpc::Client>>> = OnceCell::new();

fn get_discord_client() -> &'static Mutex<Option<rpc::Client>> {
    DISCORD_CLIENT.get_or_init(|| Mutex::new(None))
}

/// Creates a fake/dummy game executable that Discord can detect
#[tauri::command(rename_all = "snake_case")]
async fn create_fake_game(
    handle: tauri::AppHandle,
    path: &str,
    executable_name: &str,
    app_id: i64,
) -> Result<String, String> {
    let exe_path = env::current_exe().unwrap_or_default();
    let exe_dir = exe_path.parent().unwrap_or_else(|| Path::new(""));

    let normalized_path = Path::new(path).to_string_lossy().to_string();

    let game_folder_path = exe_dir
        .join("games")
        .join(app_id.to_string())
        .join(normalized_path);

    // Create the game directory structure
    match std::fs::create_dir_all(&game_folder_path) {
        Ok(_) => {
            println!("Created directory: {:?}", game_folder_path);
        }
        Err(e) => return Err(format!("Failed to create directory: {}", e)),
    };

    // Get the dummy executable template
    let resource_path = handle
        .path()
        .resolve("data/dummy.exe", BaseDirectory::Resource)
        .unwrap_or_default();

    let target_executable_path = game_folder_path.join(executable_name);
    
    // Copy the template to create the fake game exe
    match std::fs::copy(&resource_path, &target_executable_path) {
        Ok(_) => Ok(format!("Created executable: {:?}", target_executable_path)),
        Err(e) => Err(format!("Failed to copy executable: {}", e)),
    }
}

/// Runs a background process for the fake game
#[tauri::command(rename_all = "snake_case")]
async fn run_background_process(
    name: &str,
    path: &str,
    executable_name: &str,
    app_id: i64,
) -> Result<String, String> {
    let exe_path = env::current_exe().unwrap_or_default();
    let exe_dir = exe_path.parent().unwrap_or_else(|| Path::new(""));

    let normalized_path = Path::new(path).to_string_lossy().to_string();

    let game_folder_path = exe_dir
        .join("games")
        .join(app_id.to_string())
        .join(normalized_path);
        
    let executable_path = game_folder_path.join(executable_name);
    
    // Start the dummy game process with the game title
    match std::process::Command::new(&executable_path)
        .args(["--title", name])
        .current_dir(game_folder_path)
        .spawn()
    {
        Ok(_) => Ok("Process started successfully".to_string()),
        Err(e) => Err(format!("Failed to start process: {}", e)),
    }
}

/// Stops a running game process
#[tauri::command(rename_all = "snake_case")]
async fn stop_process(exec_name: String) -> Result<(), String> {
    #[cfg(target_os = "windows")]
    {
        let output = std::process::Command::new("taskkill")
            .arg("/F")
            .arg("/IM")
            .arg(exec_name)
            .output()
            .map_err(|e| format!("Failed to execute taskkill: {}", e))?;

        if output.status.success() {
            Ok(())
        } else {
            Err(format!(
                "Failed to stop process: {}",
                String::from_utf8_lossy(&output.stderr)
            ))
        }
    }
    
    #[cfg(not(target_os = "windows"))]
    {
        Err("Process stopping is only supported on Windows".to_string())
    }
}

/// Connects to Discord RPC and sets activity
#[tauri::command(rename_all = "snake_case")]
fn connect_to_discord_rpc(handle: AppHandle, activity_json: String) {
    let app = handle.clone();

    let event_connecting = "client_connecting";
    let event_connected = "client_connected";
    let event_disconnect = "event_disconnect";

    let activity = runner::parse_activity_json(&activity_json).unwrap();

    let connecting_payload = serde_json::json!({
        "app_id": activity.app_id,
    });

    // Take any existing client out to disconnect it
    let _client_option = {
        let mut client_guard = get_discord_client().lock().unwrap();
        client_guard.take()
    };

    let task = tauri::async_runtime::spawn(async move {
        handle
            .emit(event_connecting, connecting_payload)
            .unwrap_or_else(|e| eprintln!("Failed to emit event: {}", e));

        let client = runner::set_activity(activity_json)
            .await
            .map_err(|e| {
                println!("Failed to set activity: {}", e);
            })
            .unwrap();

        let connected_payload = serde_json::json!({
            "app_id": activity.app_id,
        });

        {
            let mut client_guard = get_discord_client().lock().unwrap();
            *client_guard = Some(client);
        }

        handle
            .emit(event_connected, connected_payload)
            .unwrap_or_else(|e| {
                eprintln!("Failed to emit event: {}", e);
            });

        handle.listen(event_disconnect, move |_| {
            println!("Disconnecting from Discord RPC");
            let disconnect_task = tauri::async_runtime::spawn(async move {
                let client_option = {
                    let mut client_guard = get_discord_client().lock().unwrap();
                    client_guard.take()
                };
                if let Some(client) = client_option {
                    client.discord.disconnect().await;
                    println!("Disconnected from Discord RPC");
                }
            });
        });
    });

    app.listen(event_disconnect, move |_| {
        println!("Disconnecting from Discord RPC...");
        task.abort();
    });
}

/// Fetches the game list from Discord's API
#[tauri::command(rename_all = "snake_case")]
async fn fetch_gamelist_from_discord() -> tauri::ipc::Response {
    let res = tauri_plugin_http::reqwest::get(
        "https://discord.com/api/applications/detectable"
    ).await;
    
    match res {
        Ok(response) => {
            match response.text().await {
                Ok(text) => tauri::ipc::Response::new(text),
                Err(e) => tauri::ipc::Response::new(
                    format!("{{\"error\": \"Failed to read response: {}\"}}", e)
                ),
            }
        }
        Err(e) => tauri::ipc::Response::new(
            format!("{{\"error\": \"Failed to fetch: {}\"}}", e)
        ),
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_http::init())
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![
            create_fake_game,
            stop_process,
            connect_to_discord_rpc,
            run_background_process,
            fetch_gamelist_from_discord
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

## runner.rs - Discord RPC Activity Runner

```rust
use discord_sdk::activity::ActivityBuilder;
use serde::Deserialize;
use crate::rpc::{self, Client};

#[derive(Deserialize)]
pub struct ActivityParams {
    pub app_id: String,
    pub details: Option<String>,
    pub state: Option<String>,
    #[serde(rename = "largeImageKey")]
    pub large_image_key: Option<String>,
    #[serde(rename = "largeImageText")]
    pub large_image_text: Option<String>,
    pub timestamp: Option<i64>,
    pub activity_kind: Option<i32>,
}

pub struct CreateActivityResult {
    pub activity: ActivityBuilder,
    pub app_id: u64,
}

fn to_app_id(app_id: &str) -> Result<u64, std::num::ParseIntError> {
    app_id.parse::<u64>()
}

pub fn parse_activity_json(activity_json: &str) -> Result<ActivityParams, String> {
    serde_json::from_str(activity_json).map_err(|e| {
        format!("Failed to parse activity JSON: {}", e)
    })
}

pub fn create_activity(activity_json: String) -> Result<CreateActivityResult, String> {
    let activity: ActivityParams = parse_activity_json(&activity_json)?;

    let app_id: u64 = to_app_id(&activity.app_id)
        .map_err(|e| format!("Failed to parse app_id: {}", e))?;

    let details = activity.details.unwrap_or_default();
    let state = activity.state.unwrap_or_default();
    let large_image_key = activity.large_image_key.unwrap_or_default();
    let large_image_text = activity.large_image_text;
    let timestamp = activity.timestamp;
    let activity_kind = activity.activity_kind.unwrap_or(0);

    let mut rp = ActivityBuilder::default();

    // Set activity kind (Playing, Listening, Watching, Competing)
    rp = match activity_kind {
        0 => rp.kind(rpc::ds::activity::ActivityKind::Playing),
        2 => rp.kind(rpc::ds::activity::ActivityKind::Listening),
        3 => rp.kind(rpc::ds::activity::ActivityKind::Watching),
        5 => rp.kind(rpc::ds::activity::ActivityKind::Competing),
        _ => rp.kind(rpc::ds::activity::ActivityKind::Playing),
    };

    // Set details
    if !details.is_empty() {
        rp = rp.details(details);
    }

    // Set state
    if !state.is_empty() {
        rp = rp.state(state);
    }

    // Set timestamp
    if let Some(ts) = timestamp {
        rp = rp.start_timestamp(ts);
    }

    // Set large image
    if !large_image_key.is_empty() {
        rp = rp.assets(
            rpc::ds::activity::Assets::default().large(&large_image_key, large_image_text)
        );
    }

    Ok(CreateActivityResult {
        activity: rp,
        app_id,
    })
}

pub async fn set_activity(activity_json: String) -> Result<Client, String> {
    let activity_result = create_activity(activity_json)?;
    let app_id: i64 = activity_result.app_id as i64;
    let activity_builder = activity_result.activity;

    let client = rpc::make_client(app_id, rpc::ds::Subscriptions::ACTIVITY).await;
    
    client
        .discord
        .update_activity(activity_builder)
        .await
        .map_err(|e| format!("Failed to update activity: {}", e))?;

    Ok(client)
}
```

## rpc.rs - Discord RPC Client

```rust
pub use discord_sdk as ds;

pub struct Client {
    pub discord: ds::Discord,
    pub wheel: ds::wheel::Wheel,
    pub user: ds::user::User,
}

pub async fn make_client(app_id: ds::AppId, subs: ds::Subscriptions) -> Client {
    println!("Creating Discord client with app ID: {}", app_id);
    
    let (wheel, handler) = ds::wheel::Wheel::new(Box::new(|err| {
        println!("Discord RPC Error: {:?}", err);
    }));

    let mut user = wheel.user();

    let discord = ds::Discord::new(
        ds::DiscordApp::PlainId(app_id),
        subs,
        Box::new(handler)
    ).expect("Unable to create Discord client");
    
    user.0.changed().await.unwrap();

    let user = match &*user.0.borrow() {
        ds::wheel::UserState::Connected(user) => user.clone(),
        ds::wheel::UserState::Disconnected(err) => {
            panic!("Failed to connect to Discord: {}", err)
        }
    };

    println!("Connected to Discord, user: {:#?}", user);

    Client {
        discord,
        wheel,
        user,
    }
}
```

## main.rs - Application Entry Point

```rust
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    ahanov_quest_completer_lib::run()
}
```

## Building the Dummy Executable

The dummy executable (in `src-win/`) is a minimal Windows application that:

1. Creates a window with the game title
2. Runs indefinitely until closed
3. Has the same executable name as the real game
4. Is small (<200KB) and uses minimal resources

```rust
// src-win/src/main.rs
#![windows_subsystem = "windows"]

use windows::Win32::Foundation::{HWND, LPARAM, LRESULT, WPARAM};
use windows::Win32::UI::WindowsAndMessaging::*;

extern "system" fn window_proc(
    hwnd: HWND,
    msg: u32,
    wparam: WPARAM,
    lparam: LPARAM,
) -> LRESULT {
    match msg {
        WM_DESTROY => {
            unsafe { PostQuitMessage(0) };
            LRESULT(0)
        }
        _ => unsafe { DefWindowProcA(hwnd, msg, wparam, lparam) },
    }
}

fn main() {
    // Parse command line args for title
    let args: Vec<String> = std::env::args().collect();
    let title = if args.len() > 2 && args[1] == "--title" {
        &args[2]
    } else {
        "Ahanov Quest Completer"
    };

    // Create hidden window that Discord can detect
    // ... (window creation code)
    
    // Message loop
    // ... (message loop code)
}
```

## Integration Steps

1. **Create Tauri Project**: Use `npm create tauri-app`
2. **Add Dependencies**: Update `Cargo.toml` with the dependencies above
3. **Copy Backend Files**: Add `lib.rs`, `runner.rs`, `rpc.rs` to `src-tauri/src/`
4. **Build Dummy Executable**: Build `src-win` project separately
5. **Copy Resources**: Place `dummy.exe` in `src-tauri/resources/data/`
6. **Update Frontend**: Modify `app.js` to use Tauri invoke commands
7. **Test**: Run `npm run tauri dev`
8. **Build**: Run `npm run tauri build` for production

## Testing

```bash
# Development mode
npm run tauri dev

# Test RPC connection
# 1. Add a game in the UI
# 2. Click "Connect via RPC"
# 3. Check Discord client for activity

# Test executable creation
# 1. Add a game
# 2. Select an executable
# 3. Click "Install"
# 4. Check games/{app_id}/ folder for .exe
```

## Notes

- The dummy executable must be compiled separately for each platform
- Discord detection requires exact executable names
- RPC connections may be rate-limited by Discord
- Always test with Discord Developer Mode enabled
