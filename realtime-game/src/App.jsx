import { useState, useEffect, useCallback } from 'react'
import { v4 as uuidv4 } from 'uuid'
import { NicknameForm } from './components/NicknameForm'
import { GameCanvas } from './components/GameCanvas'
import { PlayerInfo } from './components/PlayerInfo'
import { usePlayersSync } from './hooks/usePlayersSync'
import { useMovement } from './hooks/useMovement'
import { generateRandomColor } from './utils/gameUtils'
import './App.css'

function App() {
  const [gameState, setGameState] = useState('nickname') // 'nickname' | 'playing'
  const [currentPlayer, setCurrentPlayer] = useState(null)
  const [playerId] = useState(() => uuidv4())

  // Хуки для синхронизации и движения
  const { 
    otherPlayers, 
    isConnected, 
    addPlayer, 
    updatePlayerPosition, 
    removePlayer 
  } = usePlayersSync(playerId)

  const { position, setPlayerPosition } = useMovement(playerId, updatePlayerPosition)

  // Обновляем позицию текущего игрока
  useEffect(() => {
    if (currentPlayer && position) {
      setCurrentPlayer(prev => ({
        ...prev,
        x: position.x,
        y: position.y
      }))
    }
  }, [position]) // Убираем currentPlayer из зависимостей

  // Обработчик входа в игру
  const handleJoinGame = useCallback(async (nickname) => {
    try {
      const color = generateRandomColor()
      const startX = Math.random() * 700 + 50
      const startY = Math.random() * 500 + 50

      const newPlayer = {
        id: playerId,
        nickname,
        color,
        x: startX,
        y: startY
      }

      // Добавляем игрока в базу данных
      await addPlayer(playerId, nickname, startX, startY, color)
      
      // Устанавливаем позицию в хуке движения
      setPlayerPosition(startX, startY)
      
      // Сохраняем данные текущего игрока
      setCurrentPlayer(newPlayer)
      
      // Переключаемся в игровой режим
      setGameState('playing')
    } catch (error) {
      console.error('Error joining game:', error)
      throw error
    }
  }, [playerId, addPlayer, setPlayerPosition])

  // Очистка при выходе из игры
  useEffect(() => {
    const handleBeforeUnload = () => {
      if (currentPlayer) {
        removePlayer(playerId)
      }
    }

    window.addEventListener('beforeunload', handleBeforeUnload)

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload)
      if (currentPlayer) {
        removePlayer(playerId)
      }
    }
  }, [currentPlayer, playerId, removePlayer])

  // Обработчик ошибок подключения
  useEffect(() => {
    if (gameState === 'playing' && !isConnected) {
      console.warn('Connection lost. Attempting to reconnect...')
    }
  }, [isConnected, gameState])

  return (
    <div className="app">
      {gameState === 'nickname' && (
        <NicknameForm onSubmit={handleJoinGame} />
      )}
      
      {gameState === 'playing' && (
        <>
          <GameCanvas 
            currentPlayer={currentPlayer}
            otherPlayers={otherPlayers}
          />
          <PlayerInfo 
            currentPlayer={currentPlayer}
            otherPlayers={otherPlayers}
            isConnected={isConnected}
          />
        </>
      )}
    </div>
  )
}

export default App
