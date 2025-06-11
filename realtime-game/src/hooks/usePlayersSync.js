import { useState, useEffect, useCallback } from 'react'
import { playerService } from '../services/supabase'

export const usePlayersSync = (currentPlayerId) => {
  const [players, setPlayers] = useState({})
  const [isConnected, setIsConnected] = useState(false)

  // Инициализация подключения
  useEffect(() => {
    let subscription = null

    // Обновление списка игроков
    const updatePlayers = (playersData) => {
      const playersMap = {}
      playersData.forEach(player => {
        playersMap[player.id] = player
      })
      setPlayers(playersMap)
    }

    // Обработчик изменений в реальном времени
    const handleRealtimeChange = (payload) => {
      const { eventType, new: newRecord, old: oldRecord } = payload

      setPlayers(prevPlayers => {
        const newPlayers = { ...prevPlayers }

        switch (eventType) {
          case 'INSERT':
          case 'UPDATE':
            if (newRecord) {
              newPlayers[newRecord.id] = newRecord
            }
            break
          case 'DELETE':
            if (oldRecord?.id) {
              delete newPlayers[oldRecord.id]
            }
            break
          default:
            break
        }

        return newPlayers
      })
    }

    const initializeConnection = async () => {
      try {
        // Получаем текущих игроков
        const initialPlayers = await playerService.getAllPlayers()
        updatePlayers(initialPlayers)

        // Подписываемся на изменения
        subscription = playerService.subscribeToPlayers(handleRealtimeChange)
        setIsConnected(true)
      } catch (error) {
        console.error('Error initializing players sync:', error)
        setIsConnected(false)
      }
    }

    initializeConnection()

    // Очистка при размонтировании
    return () => {
      if (subscription) {
        subscription.unsubscribe()
      }
      setIsConnected(false)
    }
  }, []) // Используем только при монтировании

  // Добавление нового игрока
  const addPlayer = useCallback(async (playerId, nickname, x, y, color) => {
    try {
      await playerService.addPlayer(playerId, nickname, x, y, color)
    } catch (error) {
      console.error('Error adding player:', error)
    }
  }, [])

  // Обновление позиции игрока
  const updatePlayerPosition = useCallback(async (playerId, x, y) => {
    try {
      await playerService.updatePlayerPosition(playerId, x, y)
    } catch (error) {
      console.error('Error updating player position:', error)
    }
  }, [])

  // Удаление игрока
  const removePlayer = useCallback(async (playerId) => {
    try {
      await playerService.removePlayer(playerId)
    } catch (error) {
      console.error('Error removing player:', error)
    }
  }, [])

  // Получение других игроков (исключая текущего)
  const otherPlayers = Object.values(players).filter(player => 
    player.id !== currentPlayerId
  )

  return {
    players,
    otherPlayers,
    isConnected,
    addPlayer,
    updatePlayerPosition,
    removePlayer
  }
} 