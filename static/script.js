const startButton = document.getElementById('start-button');
const responseElement = document.getElementById('response');

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognizer = new SpeechRecognition();
recognizer.continuous = true;
recognizer.interimResults = false;

let isListening = false;

recognizer.onstart = () => {
    console.log('Speech recognition started');
};

recognizer.onend = () => {
    console.log('Speech recognition ended');
};

recognizer.onerror = (event) => {
    console.error('Speech recognition error:', event.error);
};

recognizer.onresult = async (event) => {
    const transcript = event.results[event.resultIndex][0].transcript.toLowerCase();
    console.log('Transcript:', transcript);
    responseElement.textContent = `Heard: ${transcript}`; // Log what was heard

    try {
        const response = await fetch(`/query?q=${encodeURIComponent(transcript)}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const text = await response.text();
        console.log('Response:', text);
        responseElement.textContent += `\nResponse: ${text}`; // Log the response
        speak(text);
    } catch (error) {
        console.error('Error fetching response:', error);
        responseElement.textContent += `\nError fetching response: ${error}`;
    }
};

const speak = (text) => {
    const utterance = new SpeechSynthesisUtterance(text);
    window.speechSynthesis.speak(utterance);
};

startButton.addEventListener('click', () => {
    if (isListening) {
        recognizer.stop();
        startButton.textContent = 'Start Listening';
    } else {
        recognizer.start();
        startButton.textContent = 'Stop Listening';
    }
    isListening = !isListening;
});