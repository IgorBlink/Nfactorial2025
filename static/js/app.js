class VoiceAIAgent {
    constructor() {
        this.isRecording = false;
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.voices = [];
        this.selectedVoice = null;
        this.speechRate = 1.0;
        
        this.initElements();
        this.initSpeechRecognition();
        this.initSpeechSynthesis();
        this.bindEvents();
    }

    initElements() {
        this.startBtn = document.getElementById('startRecording');
        this.stopBtn = document.getElementById('stopRecording');
        this.statusText = document.getElementById('statusText');
        this.chatMessages = document.getElementById('chatMessages');
        this.textInput = document.getElementById('textInput');
        this.sendBtn = document.getElementById('sendText');
        this.voiceSelect = document.getElementById('voiceSelect');
        this.speedRange = document.getElementById('speedRange');
        this.speedValue = document.getElementById('speedValue');
    }

    initSpeechRecognition() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            this.showError('Ваш браузер не поддерживает распознавание речи. Попробуйте Chrome или Edge.');
            return;
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();
        
        this.recognition.continuous = false;
        this.recognition.interimResults = true;
        this.recognition.lang = 'ru-RU';

        this.recognition.onstart = () => {
            this.isRecording = true;
            this.updateStatus('Слушаю... Говорите!');
            this.startBtn.style.display = 'none';
            this.stopBtn.style.display = 'inline-block';
            this.startBtn.classList.add('recording');
        };

        this.recognition.onresult = (event) => {
            let transcript = '';
            let isFinal = false;

            for (let i = event.resultIndex; i < event.results.length; i++) {
                if (event.results[i].isFinal) {
                    transcript += event.results[i][0].transcript;
                    isFinal = true;
                } else {
                    this.updateStatus(`Распознаю: "${event.results[i][0].transcript}"`);
                }
            }

            if (isFinal && transcript.trim()) {
                this.processVoiceInput(transcript.trim());
            }
        };

        this.recognition.onerror = (event) => {
            console.error('Ошибка распознавания речи:', event.error);
            this.showError(`Ошибка распознавания: ${event.error}`);
            this.stopRecording();
        };

        this.recognition.onend = () => {
            this.stopRecording();
        };
    }

    initSpeechSynthesis() {
        // Загрузка голосов
        const loadVoices = () => {
            this.voices = this.synthesis.getVoices();
            this.populateVoiceSelect();
        };

        loadVoices();
        if (this.synthesis.onvoiceschanged !== undefined) {
            this.synthesis.onvoiceschanged = loadVoices;
        }
    }

    populateVoiceSelect() {
        this.voiceSelect.innerHTML = '';
        
        // Фильтруем русские голоса
        const russianVoices = this.voices.filter(voice => 
            voice.lang.startsWith('ru') || voice.name.toLowerCase().includes('russian')
        );
        
        // Если русских голосов нет, берем все доступные
        const availableVoices = russianVoices.length > 0 ? russianVoices : this.voices;
        
        availableVoices.forEach((voice, index) => {
            const option = document.createElement('option');
            option.value = index;
            option.textContent = `${voice.name} (${voice.lang})`;
            this.voiceSelect.appendChild(option);
        });

        // Выбираем первый русский голос по умолчанию
        if (availableVoices.length > 0) {
            this.selectedVoice = availableVoices[0];
        }
    }

    bindEvents() {
        this.startBtn.addEventListener('click', () => this.startRecording());
        this.stopBtn.addEventListener('click', () => this.stopRecording());
        
        this.sendBtn.addEventListener('click', () => this.sendTextMessage());
        this.textInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendTextMessage();
            }
        });

        this.voiceSelect.addEventListener('change', (e) => {
            const voiceIndex = parseInt(e.target.value);
            this.selectedVoice = this.voices[voiceIndex];
        });

        this.speedRange.addEventListener('input', (e) => {
            this.speechRate = parseFloat(e.target.value);
            this.speedValue.textContent = this.speechRate.toFixed(1);
        });
    }

    startRecording() {
        if (!this.recognition) {
            this.showError('Распознавание речи недоступно');
            return;
        }

        try {
            this.recognition.start();
        } catch (error) {
            console.error('Ошибка запуска записи:', error);
            this.showError('Не удалось запустить запись');
        }
    }

    stopRecording() {
        if (this.recognition && this.isRecording) {
            this.recognition.stop();
        }
        
        this.isRecording = false;
        this.startBtn.style.display = 'inline-block';
        this.stopBtn.style.display = 'none';
        this.startBtn.classList.remove('recording');
        this.updateStatus('Готов к записи');
    }

    async processVoiceInput(text) {
        this.updateStatus('Обрабатываю запрос...');
        this.addMessage(text, 'user');
        
        try {
            const response = await this.sendToAI(text);
            this.addMessage(response, 'ai');
            this.speakText(response);
        } catch (error) {
            console.error('Ошибка при обработке:', error);
            this.showError('Не удалось получить ответ от AI');
        }
    }

    async sendTextMessage() {
        const text = this.textInput.value.trim();
        if (!text) return;

        this.textInput.value = '';
        this.addMessage(text, 'user');
        
        try {
            const response = await this.sendToAI(text);
            this.addMessage(response, 'ai');
            this.speakText(response);
        } catch (error) {
            console.error('Ошибка при отправке:', error);
            this.showError('Не удалось отправить сообщение');
        }
    }

    async sendToAI(message) {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data.response;
    }

    speakText(text) {
        // Останавливаем предыдущую речь
        this.synthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        
        if (this.selectedVoice) {
            utterance.voice = this.selectedVoice;
        }
        
        utterance.rate = this.speechRate;
        utterance.pitch = 1;
        utterance.volume = 1;

        utterance.onstart = () => {
            this.updateStatus('Проговариваю ответ...');
        };

        utterance.onend = () => {
            this.updateStatus('Готов к записи');
        };

        utterance.onerror = (event) => {
            console.error('Ошибка синтеза речи:', event.error);
            this.updateStatus('Готов к записи');
        };

        this.synthesis.speak(utterance);
    }

    addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        const icon = sender === 'ai' ? '<i class="fas fa-robot"></i>' : '<i class="fas fa-user"></i>';
        contentDiv.innerHTML = `${icon} ${text}`;
        
        messageDiv.appendChild(contentDiv);
        this.chatMessages.appendChild(messageDiv);
        
        // Прокрутка к последнему сообщению
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    updateStatus(message) {
        this.statusText.textContent = message;
    }

    showError(message) {
        this.updateStatus(`Ошибка: ${message}`);
        this.addMessage(`❌ ${message}`, 'ai');
    }
}

// Инициализация приложения
document.addEventListener('DOMContentLoaded', () => {
    const app = new VoiceAIAgent();
    
    // Проверка поддержки необходимых API
    if (!window.speechSynthesis) {
        app.showError('Ваш браузер не поддерживает синтез речи');
    }
    
    console.log('Voice AI Agent инициализирован');
}); 