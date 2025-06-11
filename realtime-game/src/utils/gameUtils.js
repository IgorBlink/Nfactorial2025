// Генерация случайного цвета
export const generateRandomColor = () => {
  const colors = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57',
    '#FF9FF3', '#54A0FF', '#5F27CD', '#00D2D3', '#FF9F43',
    '#FD79A8', '#FDCB6E', '#6C5CE7', '#A29BFE', '#FD79A8'
  ]
  return colors[Math.floor(Math.random() * colors.length)]
}

// Ограничение движения в границах игрового поля
export const clampPosition = (position, min, max) => {
  return Math.max(min, Math.min(max, position))
}

// Константы игры
export const GAME_CONFIG = {
  CANVAS_WIDTH: 800,
  CANVAS_HEIGHT: 600,
  PLAYER_SIZE: 4,
  MOVEMENT_SPEED: 1
}

// Проверка границ для игрока
export const getBoundedPosition = (x, y) => {
  const boundedX = clampPosition(x, 0, GAME_CONFIG.CANVAS_WIDTH - GAME_CONFIG.PLAYER_SIZE)
  const boundedY = clampPosition(y, 0, GAME_CONFIG.CANVAS_HEIGHT - GAME_CONFIG.PLAYER_SIZE)
  return { x: boundedX, y: boundedY }
} 