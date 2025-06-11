import { useEffect, useRef } from 'react'
import { GAME_CONFIG } from '../utils/gameUtils'
import './GameCanvas.css'

export const GameCanvas = ({ currentPlayer, otherPlayers }) => {
  const canvasRef = useRef(null)

  // Отрисовка игры
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    
    // Очищаем канвас
    ctx.clearRect(0, 0, GAME_CONFIG.CANVAS_WIDTH, GAME_CONFIG.CANVAS_HEIGHT)
    
    // Рисуем сетку для лучшей визуализации
    drawGrid(ctx)
    
    // Рисуем других игроков
    otherPlayers.forEach(player => {
      drawPlayer(ctx, player, false)
    })
    
    // Рисуем текущего игрока поверх остальных
    if (currentPlayer) {
      drawPlayer(ctx, currentPlayer, true)
    }
  }, [currentPlayer, otherPlayers])

  // Функция отрисовки сетки
  const drawGrid = (ctx) => {
    ctx.strokeStyle = '#f0f0f0'
    ctx.lineWidth = 1
    
    // Вертикальные линии
    for (let x = 0; x <= GAME_CONFIG.CANVAS_WIDTH; x += 50) {
      ctx.beginPath()
      ctx.moveTo(x, 0)
      ctx.lineTo(x, GAME_CONFIG.CANVAS_HEIGHT)
      ctx.stroke()
    }
    
    // Горизонтальные линии
    for (let y = 0; y <= GAME_CONFIG.CANVAS_HEIGHT; y += 50) {
      ctx.beginPath()
      ctx.moveTo(0, y)
      ctx.lineTo(GAME_CONFIG.CANVAS_WIDTH, y)
      ctx.stroke()
    }
  }

  // Функция отрисовки игрока
  const drawPlayer = (ctx, player, isCurrentPlayer) => {
    if (!player || typeof player.x !== 'number' || typeof player.y !== 'number') {
      return
    }

    // Рисуем квадрат игрока
    ctx.fillStyle = player.color || '#333'
    ctx.fillRect(
      Math.round(player.x), 
      Math.round(player.y), 
      GAME_CONFIG.PLAYER_SIZE, 
      GAME_CONFIG.PLAYER_SIZE
    )
    
    // Добавляем обводку для текущего игрока
    if (isCurrentPlayer) {
      ctx.strokeStyle = '#000'
      ctx.lineWidth = 2
      ctx.strokeRect(
        Math.round(player.x), 
        Math.round(player.y), 
        GAME_CONFIG.PLAYER_SIZE, 
        GAME_CONFIG.PLAYER_SIZE
      )
    }
    
    // Рисуем никнейм игрока
    if (player.nickname) {
      ctx.fillStyle = '#333'
      ctx.font = '12px Arial'
      ctx.textAlign = 'center'
      
      const textX = Math.round(player.x + GAME_CONFIG.PLAYER_SIZE / 2)
      const textY = Math.round(player.y - 5)
      
      // Добавляем фон для текста
      const textWidth = ctx.measureText(player.nickname).width
      ctx.fillStyle = 'rgba(255, 255, 255, 0.8)'
      ctx.fillRect(
        textX - textWidth / 2 - 2,
        textY - 12,
        textWidth + 4,
        14
      )
      
      // Рисуем текст
      ctx.fillStyle = isCurrentPlayer ? '#000' : '#333'
      ctx.fillText(player.nickname, textX, textY)
    }
  }

  return (
    <div className="game-canvas-container">
      <canvas
        ref={canvasRef}
        width={GAME_CONFIG.CANVAS_WIDTH}
        height={GAME_CONFIG.CANVAS_HEIGHT}
        className="game-canvas"
      />
    </div>
  )
} 