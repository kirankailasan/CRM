document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const chatContainer = document.getElementById('chat-container');

    function getCSRFToken() {
        return document.cookie.split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
    }

    sendButton.addEventListener('click', function() {
        const message = userInput.value.trim();
        if (message) {
            addUserMessage(message);
            getBotResponse(message);
            userInput.value = '';
        }
    });

    userInput.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            sendButton.click();
        }
    });

    function addUserMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message-user-message';
        messageDiv.innerHTML = '<strong>You:</strong> ' + message;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function addBotMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message-bot-message';
        messageDiv.innerHTML = '<strong>Bot:</strong> ' + message;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function getBotResponse(message) {
        fetch('/get_bot_response/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            body: JSON.stringify({ message: message }),
        })
        .then(response => response.json())
        .then(data => {
            addBotMessage(data.response);
        })
        .catch(error => {
            addBotMessage("Error: Unable to connect to the chatbot.");
        });
    }

    // Toggle Chat Window
    window.toggleChat = function() {
        if (chatContainer.style.display === "none" || chatContainer.style.display === "") {
            chatContainer.style.display = "flex";
        } else {
            chatContainer.style.display = "none";
        }
    };
});