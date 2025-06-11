import { useState, useEffect, useCallback, useRef } from 'react'
import { getBoundedPosition, GAME_CONFIG } from '../utils/gameUtils'

export const useMovement = (playerId, onPositionUpdate) => {
  const [position, setPosition] = useState({ x: 400, y: 300 }) // Центр экрана
  const keysPressed = useRef(new Set())
  const positionUpdateTimer = useRef(null)
  const onPositionUpdateRef = useRef(onPositionUpdate)
  
  // Обновляем ref при изменении callback
  useEffect(() => {
    onPositionUpdateRef.current = onPositionUpdate
  }, [onPositionUpdate])

  // Отправка позиции с небольшой задержкой для оптимизации
  const schedulePositionUpdate = useCallback((newPosition) => {
    if (positionUpdateTimer.current) {
      clearTimeout(positionUpdateTimer.current)
    }
    
    positionUpdateTimer.current = setTimeout(() => {
      if (onPositionUpdateRef.current) {
        onPositionUpdateRef.current(playerId, newPosition.x, newPosition.y)
      }
    }, 50) // 50ms задержка для группировки обновлений
  }, [playerId])

  // Обновление позиции с проверкой границ
  const updatePosition = useCallback((dx, dy) => {
    setPosition(prevPosition => {
      const newX = prevPosition.x + dx
      const newY = prevPosition.y + dy
      const boundedPosition = getBoundedPosition(newX, newY)
      
      // Отправляем обновление только если позиция действительно изменилась
      if (boundedPosition.x !== prevPosition.x || boundedPosition.y !== prevPosition.y) {
        schedulePositionUpdate(boundedPosition)
      }
      
      return boundedPosition
    })
  }, [schedulePositionUpdate])

  // Обработка нажатий клавиш
  const handleKeyDown = useCallback((event) => {
    const key = event.key.toLowerCase()
    
    if (['w', 'a', 's', 'd'].includes(key)) {
      event.preventDefault()
      keysPressed.current.add(key)
    }
  }, [])

  const handleKeyUp = useCallback((event) => {
    const key = event.key.toLowerCase()
    
    if (['w', 'a', 's', 'd'].includes(key)) {
      event.preventDefault()
      keysPressed.current.delete(key)
    }
  }, [])

  // Обработка движения
  const processMovement = useCallback(() => {
    let dx = 0
    let dy = 0

    if (keysPressed.current.has('a')) dx -= GAME_CONFIG.MOVEMENT_SPEED
    if (keysPressed.current.has('d')) dx += GAME_CONFIG.MOVEMENT_SPEED
    if (keysPressed.current.has('w')) dy -= GAME_CONFIG.MOVEMENT_SPEED
    if (keysPressed.current.has('s')) dy += GAME_CONFIG.MOVEMENT_SPEED

    if (dx !== 0 || dy !== 0) {
      updatePosition(dx, dy)
    }
  }, [updatePosition])

  // Устанавливаем позицию (для инициализации)
  const setPlayerPosition = useCallback((x, y) => {
    const boundedPosition = getBoundedPosition(x, y)
    setPosition(boundedPosition)
  }, [])

  // Подключение обработчиков событий
  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown)
    window.addEventListener('keyup', handleKeyUp)

    return () => {
      window.removeEventListener('keydown', handleKeyDown)
      window.removeEventListener('keyup', handleKeyUp)
    }
  }, [handleKeyDown, handleKeyUp])

  // Игровой цикл для обработки движения
  useEffect(() => {
    const gameLoop = setInterval(processMovement, 16) // ~60 FPS

    return () => {
      clearInterval(gameLoop)
      if (positionUpdateTimer.current) {
        clearTimeout(positionUpdateTimer.current)
      }
    }
  }, [processMovement])

  return {
    position,
    setPlayerPosition
  }
} 