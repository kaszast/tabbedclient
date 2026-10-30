/**
 * TabbedClient - Fő Alkalmazásvezérlő Logika
 * Kezeli a témákat, az összecsukható oldalsávot, a füleket és a munkamenet-partíciókat.
 */

(function () {
  'use strict';

  // SVG Ikonok a sablonokhoz
  const ICONS = {
    whatsapp: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946.003-6.556 5.338-11.891 11.893-11.891 3.181.001 6.167 1.24 8.413 3.488 2.245 2.248 3.481 5.236 3.48 8.414-.003 6.557-5.338 11.892-11.893 11.892-1.99-.001-3.951-.5-5.688-1.448l-6.305 1.654zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884-.001 2.225.651 3.891 1.746 5.634l-.999 3.648 3.742-.981z"/></svg>',
    slack: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 15a2 2 0 0 1-2 2 2 2 0 0 1-2-2 2 2 0 0 1 2-2h2v2zm1 0a2 2 0 0 1 2-2 2 2 0 0 1 2 2v5a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-5zm2-7a2 2 0 0 1-2-2 2 2 0 0 1 2-2 2 2 0 0 1 2 2v2H9zm0 1a2 2 0 0 1 2 2 2 2 0 0 1-2 2H4a2 2 0 0 1-2-2 2 2 0 0 1 2-2h5zm7 2a2 2 0 0 1 2-2 2 2 0 0 1 2 2 2 2 0 0 1-2 2h-2v-2zm-1 0a2 2 0 0 1-2 2 2 2 0 0 1-2-2V6a2 2 0 0 1 2-2 2 2 0 0 1 2 2v5zm-2 7a2 2 0 0 1 2 2 2 2 0 0 1-2 2 2 2 0 0 1-2-2v-2h2zm0-1a2 2 0 0 1-2-2 2 2 0 0 1 2-2h5a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-5z"/></svg>',
    telegram: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/></svg>',
    gmail: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M24 5.457v13.909c0 .904-.732 1.636-1.636 1.636h-3.819V11.73L12 16.64l-6.545-4.91v9.273H1.636A1.636 1.636 0 0 1 0 19.366V5.457c0-2.023 2.309-3.178 3.927-1.964L12 9.5l8.073-6.007c1.618-1.214 3.927-.059 3.927 1.964z"/></svg>',
    discord: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028 14.09 14.09 0 0 0 1.226-1.994.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.929 1.793 8.18 1.793 12.061 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.894.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.028zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z"/></svg>',
    trello: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M19.5 2h-15A2.5 2.5 0 0 0 2 4.5v15A2.5 2.5 0 0 0 4.5 22h15a2.5 2.5 0 0 0 2.5-2.5v-15A2.5 2.5 0 0 0 19.5 2zm-8.5 13.5a1 1 0 0 1-1 1h-4a1 1 0 0 1-1-1v-9a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v9zm8-4a1 1 0 0 1-1 1h-4a1 1 0 0 1-1-1v-5a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v5z"/></svg>',
    messenger: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.477 2 2 6.145 2 11.258c0 2.914 1.455 5.517 3.735 7.173v3.569l3.435-1.892c.907.252 1.868.39 2.83.39 5.523 0 10-4.145 10-9.24C22 6.145 17.523 2 12 2zm1.06 12.443l-2.613-2.788-5.097 2.788 5.607-5.952 2.673 2.788 5.037-2.788-5.607 5.952z"/></svg>',
    calendar: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>',
    notion: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M4.459 4.208c.746.606 1.026.56 2.428.466l13.215-.793c.28 0 .047-.28-.046-.326L17.86 1.968c-.42-.326-.981-.7-2.055-.607L3.01 2.295c-.466.046-.56.28-.374.466zm.793 3.08v13.904c0 .747.373 1.027 1.214.98l14.523-.84c.841-.046.935-.56.935-1.167V6.354c0-.606-.233-.933-.748-.887l-15.176.887c-.56.046-.748.373-.748.934zm13.682.98c.093.374 0 .748-.374.794l-.84.14v10.125c-.467.28-.98.42-1.4.42-.7 0-.933-.233-1.494-.933l-5.32-8.35v7.886l1.4.327c.374.093.42.42.374.747l-3.36.187c-.093-.374 0-.748.374-.794l.98-.234V8.502l-1.307-.14c-.373-.047-.42-.42-.373-.747l3.454-.233 5.46 8.397V8.128l-1.213-.14c-.374-.047-.42-.42-.374-.747z"/></svg>',
    globe: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>',
    mail: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>'
  };

  class TabbedApp {
    constructor() {
      this.config = this.loadConfig();
      this.activeTabId = this.config.tabs[0]?.id || null;
      this.themeKeys = Object.keys(window.TabbedConfig.THEMES);
      
      if (window.location.search.includes('mode=sidebar')) {
        document.body.classList.add('sidebar-mode');
      }

      this.initDOMElements();
      this.initTheme();
      this.initSidebarState();
      this.initEventListeners();
      this.renderTabs();
      this.renderPresets();
      this.renderThemeSettings();

      if (this.activeTabId) {
        this.selectTab(this.activeTabId);
      }
    }

    // 1. Konfiguráció Kezelés (Helyi Perzisztencia)
    loadConfig() {
      try {
        const stored = localStorage.getItem('tabbed_client_config');
        if (stored) {
          const parsed = JSON.parse(stored);
          return { ...window.TabbedConfig.DEFAULT_CONFIG, ...parsed };
        }
      } catch (err) {
        console.warn('Nem sikerült betölteni a tárolt konfigurációt, alapértelmezett betöltése:', err);
      }
      return JSON.parse(JSON.stringify(window.TabbedConfig.DEFAULT_CONFIG));
    }

    saveConfig() {
      try {
        localStorage.setItem('tabbed_client_config', JSON.stringify(this.config));
        this.notifyBackendConfigChange();
      } catch (err) {
        console.error('Hiba a konfiguráció mentésekor:', err);
      }
    }

    notifyBackendConfigChange() {
      // Ha Tauri környezetben futunk
      if (window.__TAURI__) {
        window.__TAURI__.core.invoke('update_config', { config: this.config }).catch(() => {});
      }
      // Ha Python WebKitGTK wrapperben futunk
      if (window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.tabbedClient) {
        window.webkit.messageHandlers.tabbedClient.postMessage({
          type: 'CONFIG_CHANGED',
          config: this.config
        });
      }
    }

    // 2. DOM Elemek Inicializálása
    initDOMElements() {
      this.body = document.body;
      this.sidebar = document.getElementById('sidebar');
      this.tabsList = document.getElementById('tabs-list');
      this.collapseBtn = document.getElementById('btn-toggle-collapse');
      this.collapseIcon = document.getElementById('collapse-icon');
      this.mobileMenuBtn = document.getElementById('mobile-menu-btn');
      this.addTabModal = document.getElementById('add-tab-modal');
      this.settingsModal = document.getElementById('settings-modal');
      this.presetGrid = document.getElementById('modal-preset-grid');
      this.themeOptionsGrid = document.getElementById('theme-options-grid');
      this.activeUrlDisplay = document.getElementById('active-url-display');
      this.activePartitionDisplay = document.getElementById('active-partition-display');
      this.headerActiveTabTitle = document.getElementById('header-active-tab-title');
      this.footerProfileName = document.getElementById('footer-profile-name');
      this.webviewContainer = document.getElementById('webview-container');
    }

    // 3. Témarendszer (5 Jóváhagyott Stílus)
    initTheme() {
      const savedTheme = this.config.settings.theme || 'slate';
      this.setTheme(savedTheme, false);
    }

    setTheme(themeId, save = true) {
      if (!window.TabbedConfig.THEMES[themeId]) {
        themeId = 'slate';
      }
      
      // Előző téma osztályok eltávolítása
      this.themeKeys.forEach(t => this.body.classList.remove(`theme-${t}`));
      this.body.classList.add(`theme-${themeId}`);
      
      this.config.settings.theme = themeId;
      if (save) {
        this.saveConfig();
        this.renderThemeSettings();
      }
    }

    cycleTheme() {
      const current = this.config.settings.theme || 'slate';
      const currentIndex = this.themeKeys.indexOf(current);
      const nextIndex = (currentIndex + 1) % this.themeKeys.length;
      this.setTheme(this.themeKeys[nextIndex]);
    }

    // 4. Összecsukható Fülsáv (Desktop Kompakt Icon-Only Mód)
    initSidebarState() {
      const isCollapsed = Boolean(this.config.settings.sidebarCollapsed);
      this.setSidebarCollapsed(isCollapsed, false);
    }

    setSidebarCollapsed(collapsed, save = true) {
      if (collapsed) {
        this.sidebar.classList.add('collapsed');
        this.collapseIcon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7"></path>';
      } else {
        this.sidebar.classList.remove('collapsed');
        this.collapseIcon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7"></path>';
      }

      this.config.settings.sidebarCollapsed = collapsed;
      if (save) {
        this.saveConfig();
      }
    }

    toggleSidebarCollapse() {
      const currentState = this.sidebar.classList.contains('collapsed');
      this.setSidebarCollapsed(!currentState);
    }

    toggleMobileDrawer() {
      this.sidebar.classList.toggle('mobile-open');
    }

    // 5. Fülek Kezelése (Renderelés, Aktiválás, Törlés)
    renderTabs() {
      this.tabsList.innerHTML = '';
      
      this.config.tabs.sort((a, b) => a.order - b.order).forEach(tab => {
        const item = document.createElement('div');
        item.className = `tab-item ${tab.id === this.activeTabId ? 'active' : ''}`;
        item.dataset.tabId = tab.id;
        
        const profile = this.config.profiles.find(p => p.id === tab.profileId) || { name: tab.profileId };
        const iconSvg = ICONS[tab.icon] || ICONS.globe;

        item.innerHTML = `
          <div class="tab-item-content">
            <div class="tab-icon-box" style="color: ${tab.presetColor || 'inherit'}">
              ${iconSvg}
            </div>
            <div class="tab-text-group">
              <div class="tab-label">${this.escapeHTML(tab.name)}</div>
              <span class="tab-profile">${this.escapeHTML(profile.name)}</span>
            </div>
          </div>
          ${tab.unreadCount > 0 ? `<span class="tab-badge">${tab.unreadCount}</span>` : ''}
        `;

        item.addEventListener('click', () => {
          this.selectTab(tab.id);
          this.sidebar.classList.remove('mobile-open');
        });

        this.tabsList.appendChild(item);
      });
    }

    selectTab(tabId) {
      const tab = this.config.tabs.find(t => t.id === tabId);
      if (!tab) return;

      this.activeTabId = tabId;
      
      // Aktív osztály frissítése
      const allTabs = this.tabsList.querySelectorAll('.tab-item');
      allTabs.forEach(el => {
        if (el.dataset.tabId === tabId) {
          el.classList.add('active');
        } else {
          el.classList.remove('active');
        }
      });

      // Fejléc és címsor frissítése
      this.activeUrlDisplay.textContent = tab.url;
      this.activePartitionDisplay.textContent = `Profil: ${tab.profileId}`;
      this.headerActiveTabTitle.textContent = `· [${tab.name}]`;
      
      const profile = this.config.profiles.find(p => p.id === tab.profileId);
      if (profile) {
        this.footerProfileName.textContent = `Profil: ${profile.name}`;
      }

      // Webview aktiválása / váltása
      this.switchWebview(tab);
    }

    switchWebview(tab) {
      // Értesítjük a natív futtatót (Tauri vagy WebKitGTK Python) a tabváltásról
      if (window.__TAURI__) {
        window.__TAURI__.core.invoke('switch_tab', { tabId: tab.id, url: tab.url, profileId: tab.profileId }).catch(() => {});
      }
      if (window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.tabbedClient) {
        window.webkit.messageHandlers.tabbedClient.postMessage({
          type: 'SWITCH_TAB',
          tabId: tab.id,
          url: tab.url,
          profileId: tab.profileId
        });
      }

      // UI szimulált / beágyazott tartalom frissítése
      const placeholderTitle = document.getElementById('placeholder-title');
      const placeholderDesc = document.getElementById('placeholder-desc');
      if (placeholderTitle && placeholderDesc) {
        placeholderTitle.textContent = tab.name;
        placeholderDesc.innerHTML = `Webcím: <strong style="color: var(--text-main);">${this.escapeHTML(tab.url)}</strong><br>Adatvédelmi partíció: <code>data/profiles/${this.escapeHTML(tab.profileId)}</code><br><span style="color: #2ea043;">● Nulla külső telemetria és hirdetéskövető</span>`;
      }
    }

    addTab(newTabData) {
      const newId = `tab-${Date.now()}`;
      const newTab = {
        id: newId,
        name: newTabData.name || 'Új Fül',
        url: newTabData.url || 'https://google.com',
        presetId: newTabData.presetId || null,
        profileId: newTabData.profileId || 'default',
        icon: newTabData.icon || 'globe',
        notificationsEnabled: true,
        unreadCount: 0,
        order: this.config.tabs.length
      };

      this.config.tabs.push(newTab);
      this.saveConfig();
      this.renderTabs();
      this.selectTab(newId);
    }

    deleteActiveTab() {
      if (!this.activeTabId) return;
      if (this.config.tabs.length <= 1) {
        alert('Legalább egy fülnek maradnia kell az ablakban.');
        return;
      }

      const activeTab = this.config.tabs.find(t => t.id === this.activeTabId);
      if (!confirm(`Biztosan törölni szeretnéd a(z) "${activeTab.name}" fület?`)) {
        return;
      }

      this.config.tabs = this.config.tabs.filter(t => t.id !== this.activeTabId);
      this.saveConfig();
      this.activeTabId = this.config.tabs[0]?.id || null;
      this.renderTabs();
      if (this.activeTabId) {
        this.selectTab(this.activeTabId);
      }
    }

    // 6. Sablonok és Modálok
    renderPresets() {
      this.presetGrid.innerHTML = '';
      window.TabbedConfig.PRESETS.forEach(preset => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'btn-preset';
        btn.innerHTML = `
          <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background-color:${preset.iconColor}"></span>
          <span>${this.escapeHTML(preset.name)}</span>
        `;
        btn.addEventListener('click', () => {
          document.getElementById('new-tab-name').value = preset.name;
          document.getElementById('new-tab-url').value = preset.url;
          document.getElementById('new-tab-profile').value = preset.defaultProfile;
          this.selectedPreset = preset;
        });
        this.presetGrid.appendChild(btn);
      });
    }

    renderThemeSettings() {
      this.themeOptionsGrid.innerHTML = '';
      const currentTheme = this.config.settings.theme;

      Object.values(window.TabbedConfig.THEMES).forEach(t => {
        const card = document.createElement('div');
        card.className = `theme-option-card ${t.id === currentTheme ? 'active' : ''}`;
        card.innerHTML = `
          <div>
            <div style="font-weight: 700; font-size: 13px;">${this.escapeHTML(t.name)}</div>
            <div style="font-size: 11px; color: var(--text-muted); margin-top: 2px;">${this.escapeHTML(t.description)}</div>
          </div>
          <span style="font-size: 11px; padding: 2px 6px; border-radius: 4px; background-color: var(--border-color);">${t.type === 'dark' ? 'Sötét' : 'Világos'}</span>
        `;
        card.addEventListener('click', () => {
          this.setTheme(t.id, true);
        });
        this.themeOptionsGrid.appendChild(card);
      });
    }

    // 7. Eseménykezelők
    initEventListeners() {
      // Összecsukás gomb
      this.collapseBtn.addEventListener('click', () => this.toggleSidebarCollapse());

      // Mobil menü gomb
      this.mobileMenuBtn.addEventListener('click', () => this.toggleMobileDrawer());

      // Gyors témaváltó gomb
      document.getElementById('btn-theme-quicktoggle').addEventListener('click', () => this.cycleTheme());

      // Beállítások gomb
      document.getElementById('btn-open-settings').addEventListener('click', () => {
        this.settingsModal.classList.add('open');
      });

      // Új fül gomb
      document.getElementById('btn-open-add-tab').addEventListener('click', () => {
        document.getElementById('new-tab-name').value = '';
        document.getElementById('new-tab-url').value = '';
        this.selectedPreset = null;
        this.addTabModal.classList.add('open');
      });

      // Fül törlése gomb
      document.getElementById('btn-delete-tab').addEventListener('click', () => this.deleteActiveTab());

      // Új fül mentése
      document.getElementById('btn-save-new-tab').addEventListener('click', () => {
        const name = document.getElementById('new-tab-name').value.trim();
        const url = document.getElementById('new-tab-url').value.trim();
        const profileId = document.getElementById('new-tab-profile').value;

        if (!url) {
          alert('Kérlek adj meg egy érvényes webcímet (URL)!');
          return;
        }

        const formattedUrl = url.startsWith('http://') || url.startsWith('https://') ? url : `https://${url}`;

        this.addTab({
          name: name || 'Egyedi Oldal',
          url: formattedUrl,
          profileId: profileId,
          presetId: this.selectedPreset ? this.selectedPreset.id : null,
          icon: this.selectedPreset ? this.selectedPreset.icon : 'globe'
        });

        this.addTabModal.classList.remove('open');
      });

      // Modál záró gombok
      document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', () => {
          this.addTabModal.classList.remove('open');
          this.settingsModal.classList.remove('open');
        });
      });

      // Háttérre kattintva modál zárás
      [this.addTabModal, this.settingsModal].forEach(modal => {
        modal.addEventListener('click', (e) => {
          if (e.target === modal) {
            modal.classList.remove('open');
          }
        });
      });
    }

    escapeHTML(str) {
      if (!str) return '';
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
    }
  }

  // Alkalmazás példányosítása amikor a DOM készen áll
  document.addEventListener('DOMContentLoaded', () => {
    window.tabbedApp = new TabbedApp();
  });
})();
