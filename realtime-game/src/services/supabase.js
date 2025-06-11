import { createClient } from '@supabase/supabase-js'

// Конфигурация Supabase
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://kxzkfflbjmejbgbvxbcx.supabase.co'
const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt4emtmZmxiam1lamJnYnZ4YmN4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDg5MTg0NTEsImV4cCI6MjA2NDQ5NDQ1MX0.g6gTRyV2NjtRJUMe610nUqTr71hSv8L3EjQy9W0hZW4'

export const supabase = createClient(supabaseUrl, supabaseKey)

// Методы для работы с игроками
export const playerService = {
  // Добавить игрока в комнату
  async addPlayer(playerId, nickname, x, y, color) {
    const { data, error } = await supabase
      .from('players')
      .upsert({ 
        id: playerId, 
        nickname, 
        x, 
        y, 
        color,
        last_seen: new Date().toISOString()
      })
    
    if (error) {
      console.error('Error adding player:', error)
      throw error
    }
    return data
  },

  // Обновить позицию игрока
  async updatePlayerPosition(playerId, x, y) {
    const { data, error } = await supabase
      .from('players')
      .update({ 
        x, 
        y, 
        last_seen: new Date().toISOString() 
      })
      .eq('id', playerId)
    
    if (error) {
      console.error('Error updating player position:', error)
      throw error
    }
    return data
  },

  // Удалить игрока
  async removePlayer(playerId) {
    const { error } = await supabase
      .from('players')
      .delete()
      .eq('id', playerId)
    
    if (error) {
      console.error('Error removing player:', error)
      throw error
    }
  },

  // Подписка на изменения игроков
  subscribeToPlayers(callback) {
    const subscription = supabase
      .channel('players')
      .on('postgres_changes', 
        { 
          event: '*', 
          schema: 'public', 
          table: 'players' 
        }, 
        callback
      )
      .subscribe()

    return subscription
  },

  // Получить всех игроков
  async getAllPlayers() {
    const { data, error } = await supabase
      .from('players')
      .select('*')
    
    if (error) {
      console.error('Error fetching players:', error)
      throw error
    }
    return data || []
  }
} 