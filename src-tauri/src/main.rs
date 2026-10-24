// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serde::{Deserialize, Serialize};
use std::sync::Mutex;
use tauri::{
    menu::{Menu, MenuItem},
    tray::{TrayIconBuilder, TrayIconEvent},
    AppHandle, Manager, WindowEvent,
};

#[derive(Debug, Serialize, Deserialize, Clone)]
struct SwitchTabPayload {
    tab_id: String,
    url: String,
    profile_id: String,
}

#[derive(Default)]
struct AppState {
    current_tab: Mutex<Option<SwitchTabPayload>>,
    config: Mutex<Option<serde_json::Value>>,
}

#[tauri::command]
fn switch_tab(tab_id: String, url: String, profile_id: String, state: tauri::State<AppState>) -> Result<String, String> {
    let payload = SwitchTabPayload {
        tab_id: tab_id.clone(),
        url: url.clone(),
        profile_id: profile_id.clone(),
    };
    let mut current = state.current_tab.lock().unwrap();
    *current = Some(payload);
    println!("[TabbedClient] Fülváltás: {} -> {} (profil: {})", tab_id, url, profile_id);
    Ok("OK".into())
}

#[tauri::command]
fn update_config(config: serde_json::Value, state: tauri::State<AppState>) -> Result<String, String> {
    let mut cfg = state.config.lock().unwrap();
    *cfg = Some(config.clone());
    let _ = std::fs::create_dir_all("data");
    let _ = std::fs::write("data/config.json", serde_json::to_string_pretty(&config).unwrap_or_default());
    Ok("OK".into())
}

#[tauri::command]
fn get_config() -> Result<serde_json::Value, String> {
    if let Ok(content) = std::fs::read_to_string("data/config.json") {
        if let Ok(val) = serde_json::from_str::<serde_json::Value>(&content) {
            return Ok(val);
        }
    }
    Ok(serde_json::json!({
        "version": "1.0.0",
        "settings": {
            "theme": "slate",
            "sidebarCollapsed": false,
            "minimizeToTrayOnClose": true,
            "startMinimized": false,
            "hardwareAcceleration": true
        },
        "profiles": [
            { "id": "default", "name": "Alapértelmezett" },
            { "id": "work", "name": "Munkahelyi" },
            { "id": "personal", "name": "Magán" }
        ],
        "tabs": []
    }))
}

fn main() {
    tauri::Builder::default()
        .manage(AppState::default())
        .invoke_handler(tauri::generate_handler![switch_tab, update_config, get_config])
        .setup(|app| {
            // Rendszertálca menü létrehozása
            let show_i = MenuItem::with_id(app, "show", "Ablak megjelenítése", true, None::<&str>)?;
            let quit_i = MenuItem::with_id(app, "quit", "Végleges kilépés", true, None::<&str>)?;
            let menu = Menu::with_items(app, &[&show_i, &quit_i])?;

            let _tray = TrayIconBuilder::new()
                .menu(&menu)
                .tooltip("TabbedClient - Zero Telemetry")
                .on_menu_event(|app, event| match event.id.as_ref() {
                    "show" => {
                        if let Some(window) = app.get_webview_window("main") {
                            let _ = window.show();
                            let _ = window.set_focus();
                        }
                    }
                    "quit" => {
                        app.exit(0);
                    }
                    _ => {}
                })
                .on_tray_icon_event(|tray, event| {
                    if let TrayIconEvent::Click { .. } = event {
                        let app = tray.app_handle();
                        if let Some(window) = app.get_webview_window("main") {
                            let _ = window.show();
                            let _ = window.set_focus();
                        }
                    }
                })
                .build(app)?;

            Ok(())
        })
        .on_window_event(|window, event| {
            if let WindowEvent::CloseRequested { api, .. } = event {
                // Bezáráskor (X) minimalizálás a tálcára a háttérműködéshez
                let _ = window.hide();
                api.prevent_close();
            }
        })
        .run(tauri::generate_context!())
        .expect("Hiba történt a TabbedClient Tauri alkalmazás futtatásakor");
}
