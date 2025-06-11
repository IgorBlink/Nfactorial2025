import { useState } from 'react'
import './NicknameForm.css'

export const NicknameForm = ({ onSubmit }) => {
  const [nickname, setNickname] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (nickname.trim().length < 2) {
      alert('Никнейм должен быть минимум 2 символа')
      return
    }

    if (nickname.trim().length > 20) {
      alert('Никнейм не должен превышать 20 символов')
      return
    }

    setIsLoading(true)
    try {
      await onSubmit(nickname.trim())
    } catch (error) {
      console.error('Error joining game:', error)
      alert('Ошибка при входе в игру. Попробуйте еще раз.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="nickname-form-container">
      <div className="nickname-form">
        <h1>🎮 Multiplayer Squares</h1>
        <p>Введите ваш никнейм для входа в игру</p>
        
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            value={nickname}
            onChange={(e) => setNickname(e.target.value)}
            placeholder="Введите никнейм..."
            maxLength={20}
            disabled={isLoading}
            autoFocus
          />
          
          <button 
            type="submit" 
            disabled={isLoading || nickname.trim().length < 2}
          >
            {isLoading ? 'Подключение...' : 'Войти в игру'}
          </button>
        </form>

        <div className="game-instructions">
          <h3>Управление:</h3>
          <div className="controls">
            <span>W</span> - Вверх
            <span>S</span> - Вниз
            <span>A</span> - Влево
            <span>D</span> - Вправо
          </div>
        </div>
      </div>
    </div>
  )
} 