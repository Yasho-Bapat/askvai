document.addEventListener('DOMContentLoaded', (event) => {
    const askButton = document.querySelector('.ask-button');
    const sendButton = document.querySelector('.send-button');
    const chatInput = document.querySelector('.chat-input');
    const modal = document.getElementById("responseModal");
    const modalContent = document.getElementById("modalPrompt");
    const span = document.getElementsByClassName("close-button")[0];

    const infoButton = document.querySelector('.info-button');
    const infoModal = document.getElementById("infoModal");
    const infoSpan = document.getElementsByClassName("close-button")[1]; // Corrected to close-button

    // Initially disable send button and chat input
    disableChat();

    askButton.addEventListener('click', () => {
        handleAskAIClick();
        enableChat();
        const chatMessages = document.querySelector('.chat-messages');
        chatMessages.innerHTML = '';
    });

    sendButton.addEventListener('click', () => {
        handleAskAIClick();
        disableChat();
    });

    chatInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            handleAskAIClick();
        }
    });

    // Close modals when clicking on close buttons
    span.onclick = function() {
        closeModal(modal);
    }

    infoSpan.onclick = function() {
        closeModal(infoModal);
    }

    // Close modals when clicking outside of them
    window.onclick = function(event) {
        if (event.target === modal) {
            closeModal(modal);
        } else if (event.target === infoModal) {
            closeModal(infoModal);
        }
    }

    // Handle message click to display modal
    document.addEventListener('click', function(event) {
        let messageElement = event.target;
        while (!messageElement.classList.contains('message')) {
            messageElement = messageElement.parentNode;
            if (messageElement === null) return; // If no message element is found, exit
        }

        const prompt = messageElement.getAttribute('data-prompt');
        if (prompt) {
            modalContent.innerHTML = `<strong>Request Payload:</strong><br>${prompt}`;
            modal.style.display = "block";
        }
    });

    infoButton.addEventListener('click', () => {
        infoModal.style.display = "block";
        // Default to showing the first tab when modal is opened
        document.getElementById("tab1").style.display = "block";
        document.getElementsByClassName("tablinks")[0].classList.add("active");
    });
});

function closeModal(modal) {
    modal.style.display = "none";
}

function handleAskAIClick() {
    const materialNameInput = document.querySelector('.material-name-input');
    const manufacturerInput = document.querySelector('.manufacturer-input');
    const workContentInput = document.querySelector('.work-content-input');
    const chatInput = document.querySelector('.chat-input');
    const additional_info = chatInput.value.trim();

    // Check if material name is provided
    if (!materialNameInput.value.trim()) {
        alert('Material Name is required');
        return;
    }

    // Display user message in chat window
    if (additional_info !== '') {
        displayMessage('User', additional_info);
        chatInput.value = '';
        disableChat();
    }

    showSpinner();

    fetch('/v1/ask-viridium-ai', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            material_name: materialNameInput.value,
            manufacturer_name: manufacturerInput.value,
            work_content: workContentInput.value,
            additional_info: additional_info
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Error in network response");
        }
        return response.json();
    })
    .then(data => {
        displayMessage('AI', data.result, JSON.stringify({
            material_name: materialNameInput.value,
            manufacturer_name: manufacturerInput.value,
            work_content: workContentInput.value,
            additional_info: additional_info
        }));
        enableChat();
    })
    .catch(error => {
        console.error('Error:', error);
        displayMessage('Error', 'An error occurred while getting the response from AI.');
    })
    .finally(() => {
        hideSpinner();
    });
}

function displayMessage(sender, message, prompt = null) {
    const chatWindow = document.querySelector('.chat-messages');
    const messageElement = document.createElement('div');

    messageElement.classList.add('message');
    if (sender === 'AI' && prompt !== null) {
        messageElement.setAttribute('data-prompt', prompt);
    }

    messageElement.innerHTML = (typeof message === 'object') ?
        `<strong>${sender}:</strong><br>${formatMessage(message)}` :
        `<strong>${sender}:</strong> ${message}`;

    chatWindow.appendChild(messageElement);
    chatWindow.scrollTop = chatWindow.scrollHeight; // Scroll to the bottom
}

function formatMessage(data) {
    let formattedMessage = '<div class="formatted-message">';
    for (const [key, value] of Object.entries(data)) {
        formattedMessage += `<div><strong>${formatKey(key)}:</strong> ${formatValue(value)}</div>`;
    }
    formattedMessage += '</div>';
    return formattedMessage;
}

function formatKey(key) {
    return key.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase());
}

function formatValue(value) {
    if (Array.isArray(value)) {
        return `<ul>${value.map(item => `<li>${item}</li>`).join('')}</ul>`;
    }
    return value !== null ? value : 'N/A';
}

function enableChat() {
    const sendButton = document.querySelector('.send-button');
    const chatInput = document.querySelector('.chat-input');

    sendButton.disabled = false;
    chatInput.disabled = false;
}

function disableChat() {
    const sendButton = document.querySelector('.send-button');
    const chatInput = document.querySelector('.chat-input');

    sendButton.disabled = true;
    chatInput.disabled = true;
}

function showSpinner() {
    document.getElementById('spinnerOverlay').style.display = 'flex';
}

function hideSpinner() {
    document.getElementById('spinnerOverlay').style.display = 'none';
}

function openTab(evt, tabName) {
    const tabcontent = document.getElementsByClassName("tabcontent");
    for (let i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    const tablinks = document.getElementsByClassName("tablinks");
    for (let i = 0; i < tablinks.length; i++) {
        tablinks[i].classList.remove("active");
    }

    document.getElementById(tabName).style.display = "block";

    evt.currentTarget.classList.add("active");
}
