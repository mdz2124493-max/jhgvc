// Ahanov Quest Completer - Main Application Logic
// Advanced Discord Game Activity Simulator

class AhanovQuestCompleter {
    constructor() {
        this.gameDatabase = [];
        this.selectedGames = [];
        this.selectedGameId = null;
        this.runningGames = new Map();
        this.rpcConnection = null;
        this.isConnectedToRPC = false;
        
        this.init();
    }

    async init() {
        await this.loadGameDatabase();
        this.setupEventListeners();
        this.updateStats();
    }

    // Load Discord's detectable games database
    async loadGameDatabase() {
        try {
            // Try to fetch from Discord's API or use fallback
            const response = await fetch('https://discord.com/api/applications/detectable');
            if (response.ok) {
                this.gameDatabase = await response.json();
                this.showNotification('Game database loaded successfully', 'success');
            } else {
                throw new Error('Failed to fetch from Discord API');
            }
        } catch (error) {
            console.error('Failed to load game database:', error);
            // Fallback to sample data for demonstration
            this.gameDatabase = this.getSampleGames();
            this.showNotification('Using sample game database', 'info');
        }
        this.updateStats();
    }

    // Sample games for demonstration
    getSampleGames() {
        return [
            {
                id: '356875570916753438',
                name: 'VALORANT',
                publishers: [{ id: '356875221078245376', name: 'Riot Games' }],
                executables: [
                    { name: 'VALORANT-Win64-Shipping.exe', os: 'win32' },
                    { name: 'VALORANT.exe', os: 'win32' }
                ],
                third_party_skus: [],
                aliases: ['Valorant', 'VAL']
            },
            {
                id: '356876590342242305',
                name: 'League of Legends',
                publishers: [{ id: '356875221078245376', name: 'Riot Games' }],
                executables: [
                    { name: 'League of Legends.exe', os: 'win32' },
                    { name: 'LeagueClient.exe', os: 'win32' }
                ],
                third_party_skus: [],
                aliases: ['LoL', 'League']
            },
            {
                id: '356877880938070016',
                name: 'Minecraft',
                publishers: [{ id: '356877297458847744', name: 'Mojang' }],
                executables: [
                    { name: 'Minecraft.Windows.exe', os: 'win32' },
                    { name: 'javaw.exe', os: 'win32' }
                ],
                third_party_skus: [],
                aliases: ['MC']
            },
            {
                id: '438122941302046720',
                name: 'Fortnite',
                publishers: [{ id: '438122941302046721', name: 'Epic Games' }],
                executables: [
                    { name: 'FortniteClient-Win64-Shipping.exe', os: 'win32' }
                ],
                third_party_skus: [],
                aliases: ['FN']
            },
            {
                id: '356943499456937984',
                name: 'Apex Legends',
                publishers: [{ id: '356943383846608898', name: 'Electronic Arts' }],
                executables: [
                    { name: 'r5apex.exe', os: 'win32' }
                ],
                third_party_skus: [],
                aliases: ['Apex']
            }
        ];
    }

    setupEventListeners() {
        // Search input
        const searchInput = document.getElementById('searchInput');
        searchInput.addEventListener('input', (e) => this.handleSearch(e.target.value));
        searchInput.addEventListener('focus', () => {
            if (searchInput.value) {
                this.showSearchResults();
            }
        });

        // Click outside to close search results
        document.addEventListener('click', (e) => {
            const searchContainer = e.target.closest('.search-container');
            if (!searchContainer) {
                this.hideSearchResults();
            }
        });
    }

    handleSearch(query) {
        const searchResults = document.getElementById('searchResults');
        
        if (!query.trim()) {
            this.hideSearchResults();
            return;
        }

        const results = this.searchGames(query);
        this.displaySearchResults(results);
        this.showSearchResults();
    }

    searchGames(query) {
        const lowerQuery = query.toLowerCase();
        return this.gameDatabase.filter(game => {
            const nameMatch = game.name.toLowerCase().includes(lowerQuery);
            const aliasMatch = game.aliases?.some(alias => 
                alias.toLowerCase().includes(lowerQuery)
            );
            return nameMatch || aliasMatch;
        }).slice(0, 10); // Limit to 10 results
    }

    displaySearchResults(results) {
        const searchResults = document.getElementById('searchResults');
        
        if (results.length === 0) {
            searchResults.innerHTML = `
                <div class="search-result-item" style="cursor: default;">
                    <span class="game-name">No games found</span>
                </div>
            `;
            return;
        }

        searchResults.innerHTML = results.map(game => `
            <div class="search-result-item" data-game-id="${game.id}">
                <span class="game-name">
                    ${game.name}
                    <span class="verified-badge">✓</span>
                </span>
                <button class="btn btn-sm btn-primary" onclick="app.addGame('${game.id}')">
                    Add
                </button>
            </div>
        `).join('');
    }

    showSearchResults() {
        const searchResults = document.getElementById('searchResults');
        searchResults.classList.add('active');
    }

    hideSearchResults() {
        const searchResults = document.getElementById('searchResults');
        searchResults.classList.remove('active');
    }

    addGame(gameId) {
        const game = this.gameDatabase.find(g => g.id === gameId);
        if (!game) return;

        // Check if already added
        if (this.selectedGames.find(g => g.id === gameId)) {
            this.showNotification('Game already in your list', 'info');
            return;
        }

        // Add game with additional state
        const gameWithState = {
            ...game,
            uid: this.generateUID(),
            isInstalled: false,
            isRunning: false,
            installedExecutables: []
        };

        this.selectedGames.push(gameWithState);
        this.renderGameList();
        this.updateStats();
        this.hideSearchResults();
        this.showNotification(`${game.name} added successfully`, 'success');
        
        // Clear search
        document.getElementById('searchInput').value = '';
    }

    removeGame(uid) {
        const game = this.selectedGames.find(g => g.uid === uid);
        if (game && game.isRunning) {
            this.showNotification('Stop the game before removing', 'error');
            return;
        }

        this.selectedGames = this.selectedGames.filter(g => g.uid !== uid);
        
        if (this.selectedGameId === uid) {
            this.selectedGameId = null;
            this.renderActionPanel();
        }
        
        this.renderGameList();
        this.updateStats();
        this.showNotification('Game removed', 'success');
    }

    selectGame(uid) {
        this.selectedGameId = uid;
        this.renderGameList();
        this.renderActionPanel();
    }

    renderGameList() {
        const gameListContainer = document.getElementById('gameList');
        
        if (this.selectedGames.length === 0) {
            gameListContainer.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">🎮</div>
                    <p>No games selected yet</p>
                    <p style="font-size: 0.85rem; margin-top: 0.5rem;">Search and add verified games to get started</p>
                </div>
            `;
            return;
        }

        gameListContainer.innerHTML = this.selectedGames.map(game => {
            const isSelected = game.uid === this.selectedGameId;
            const isRunning = game.isRunning;
            const status = isRunning ? 'running' : (game.isInstalled ? 'installed' : 'ready');
            
            return `
                <div class="game-card ${isSelected ? 'selected' : ''} ${isRunning ? 'running' : ''}" 
                     onclick="app.selectGame('${game.uid}')">
                    <div class="game-header">
                        <span class="game-name">
                            ${game.name}
                            <span class="verified-badge">✓</span>
                        </span>
                        ${!isRunning ? `
                            <button class="remove-btn" onclick="event.stopPropagation(); app.removeGame('${game.uid}')">
                                Remove
                            </button>
                        ` : ''}
                    </div>
                    <div style="margin-top: 0.5rem;">
                        <span class="game-status status-${status}">
                            ${status}
                        </span>
                    </div>
                </div>
            `;
        }).join('');
    }

    renderActionPanel() {
        const actionContent = document.getElementById('actionContent');
        const game = this.selectedGames.find(g => g.uid === this.selectedGameId);

        if (!game) {
            actionContent.innerHTML = `
                <div class="empty-state" style="padding: 2rem;">
                    <div class="empty-state-icon">⚡</div>
                    <p>Select a game to view controls</p>
                </div>
            `;
            return;
        }

        actionContent.innerHTML = `
            <div class="game-info">
                <div class="info-row">
                    <span class="info-label">Name:</span>
                    <span class="info-value">${game.name}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Game ID:</span>
                    <span class="info-value">${game.id}</span>
                </div>
                ${game.publishers?.[0] ? `
                    <div class="info-row">
                        <span class="info-label">Publisher:</span>
                        <span class="info-value">${game.publishers[0].name}</span>
                    </div>
                ` : ''}
            </div>

            <button class="btn btn-primary btn-full" onclick="app.toggleRPC('${game.uid}')">
                ${this.isConnectedToRPC ? '🔌 Disconnect RPC' : '🚀 Connect via RPC'}
            </button>

            <div style="margin: 1.5rem 0; padding: 1rem 0; border-top: 1px solid var(--cyber-light-gray); border-bottom: 1px solid var(--cyber-light-gray);">
                <h3 style="font-family: 'Orbitron', sans-serif; font-size: 1.1rem; color: var(--cyber-purple); margin-bottom: 1rem;">
                    EXECUTABLES
                </h3>
                ${this.renderExecutables(game)}
            </div>

            <div class="game-info">
                <h3 style="font-family: 'Orbitron', sans-serif; font-size: 1rem; color: var(--cyber-blue); margin-bottom: 0.75rem;">
                    STATUS
                </h3>
                <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.5rem;">
                    Check Discord to see if your activity is displayed
                </p>
                <p style="color: ${game.isRunning ? 'var(--cyber-green)' : 'var(--text-secondary)'}; font-weight: 500;">
                    ${game.isRunning ? '🟢 Game is running' : '⚪ Not running'}
                </p>
            </div>
        `;
    }

    renderExecutables(game) {
        if (!game.executables || game.executables.length === 0) {
            return '<p style="color: var(--text-secondary); font-size: 0.85rem;">No executables available</p>';
        }

        return `
            <div class="executables-list">
                ${game.executables.map((exe, index) => {
                    const isInstalled = game.installedExecutables.includes(exe.name);
                    const isRunning = game.isRunning && game.runningExecutable === exe.name;
                    
                    return `
                        <div class="executable-item">
                            <div class="executable-info">
                                <div class="executable-name">
                                    ${exe.name}
                                    ${isRunning ? '<span style="color: var(--cyber-green);">●</span>' : ''}
                                </div>
                                <div class="executable-path">${exe.os || 'win32'}</div>
                            </div>
                            <div class="executable-actions">
                                ${!isInstalled ? `
                                    <button class="btn btn-sm btn-secondary" 
                                            onclick="app.installExecutable('${game.uid}', '${exe.name}')">
                                        Install
                                    </button>
                                ` : isRunning ? `
                                    <button class="btn btn-sm btn-danger" 
                                            onclick="app.stopExecutable('${game.uid}', '${exe.name}')">
                                        Stop
                                    </button>
                                ` : `
                                    <button class="btn btn-sm btn-success" 
                                            onclick="app.runExecutable('${game.uid}', '${exe.name}')">
                                        Run
                                    </button>
                                `}
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
    }

    async installExecutable(gameUid, executableName) {
        const game = this.selectedGames.find(g => g.uid === gameUid);
        if (!game) return;

        this.showNotification('Installing dummy executable...', 'info');

        // Simulate installation (in real implementation, this would create the dummy exe)
        setTimeout(() => {
            game.installedExecutables.push(executableName);
            game.isInstalled = true;
            this.renderGameList();
            this.renderActionPanel();
            this.updateStats();
            this.showNotification(`${executableName} installed successfully`, 'success');
        }, 1000);
    }

    async runExecutable(gameUid, executableName) {
        const game = this.selectedGames.find(g => g.uid === gameUid);
        if (!game) return;

        this.showNotification(`Starting ${game.name}...`, 'info');

        // Simulate running the game
        setTimeout(() => {
            game.isRunning = true;
            game.runningExecutable = executableName;
            this.runningGames.set(gameUid, {
                name: game.name,
                executable: executableName,
                startTime: Date.now()
            });
            
            this.renderGameList();
            this.renderActionPanel();
            this.updateStats();
            this.showNotification(`${game.name} is now running`, 'success');
        }, 800);
    }

    async stopExecutable(gameUid, executableName) {
        const game = this.selectedGames.find(g => g.uid === gameUid);
        if (!game) return;

        this.showNotification(`Stopping ${game.name}...`, 'info');

        setTimeout(() => {
            game.isRunning = false;
            game.runningExecutable = null;
            this.runningGames.delete(gameUid);
            
            this.renderGameList();
            this.renderActionPanel();
            this.updateStats();
            this.showNotification(`${game.name} stopped`, 'success');
        }, 500);
    }

    async toggleRPC(gameUid) {
        const game = this.selectedGames.find(g => g.uid === gameUid);
        if (!game) return;

        if (this.isConnectedToRPC) {
            this.disconnectRPC();
        } else {
            this.connectRPC(game);
        }
    }

    async connectRPC(game) {
        this.showNotification('Connecting to Discord RPC...', 'info');
        
        // Simulate RPC connection
        setTimeout(() => {
            this.isConnectedToRPC = true;
            this.rpcConnection = {
                gameId: game.id,
                gameName: game.name,
                connectedAt: Date.now()
            };
            
            this.renderActionPanel();
            this.updateStats();
            this.showNotification(`Connected to Discord RPC for ${game.name}`, 'success');
        }, 1500);
    }

    disconnectRPC() {
        this.showNotification('Disconnecting from Discord RPC...', 'info');
        
        setTimeout(() => {
            this.isConnectedToRPC = false;
            this.rpcConnection = null;
            
            this.renderActionPanel();
            this.updateStats();
            this.showNotification('Disconnected from Discord RPC', 'success');
        }, 500);
    }

    updateStats() {
        // Total games in database
        document.getElementById('totalGames').textContent = this.selectedGames.length;
        
        // Active sessions (running games)
        const activeSessions = this.runningGames.size;
        document.getElementById('activeSessions').textContent = activeSessions;
        
        // Quest progress (simulate based on running time)
        const progress = Math.min(100, activeSessions * 25);
        document.getElementById('questProgress').textContent = `${progress}%`;
        
        // Connection status
        const statusEl = document.getElementById('connectionStatus');
        if (this.isConnectedToRPC) {
            statusEl.textContent = 'ONLINE';
            statusEl.style.color = 'var(--cyber-green)';
        } else {
            statusEl.textContent = 'OFFLINE';
            statusEl.style.color = 'var(--text-secondary)';
        }
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease-out';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }

    generateUID() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }
}

// Initialize the application
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new AhanovQuestCompleter();
});
