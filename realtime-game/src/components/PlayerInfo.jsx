import './PlayerInfo.css'

export const PlayerInfo = ({ currentPlayer, otherPlayers, isConnected }) => {
  const totalPlayers = otherPlayers.length + (currentPlayer ? 1 : 0)

  return (
    <div className="player-info">
      <div className="connection-status">
        <div className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
          {isConnected ? '🟢 Подключен' : '🔴 Отключен'}
        </div>
        <div className="players-count">
          Игроков в сети: {totalPlayers}
        </div>
      </div>

      <div className="players-list">
        <h3>Игроки:</h3>
        
        {currentPlayer && (
          <div className="player-item current">
            <div 
              className="player-color" 
              style={{ backgroundColor: currentPlayer.color }}
            ></div>
            <span className="player-name">{currentPlayer.nickname} (Вы)</span>
          </div>
        )}

        {otherPlayers.map(player => (
          <div key={player.id} className="player-item">
            <div 
              className="player-color" 
              style={{ backgroundColor: player.color }}
            ></div>
            <span className="player-name">{player.nickname}</span>
          </div>
        ))}

        {totalPlayers === 0 && (
          <div className="no-players">
            Игроков нет
          </div>
        )}
      </div>

      <div className="game-controls">
        <h3>Управление:</h3>
        <div className="controls-grid">
          <div className="control-key">W</div>
          <div className="control-key">A</div>
          <div className="control-key">S</div>
          <div className="control-key">D</div>
        </div>
        <p>Используйте WASD для движения</p>
      </div>
    </div>
  )
} 