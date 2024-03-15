// Constants for image paths and names
const BOT_IMG = "./static/styles/img/robot.svg";
const PERSON_IMG = "./static/styles/img/user.svg";
const BOT_NAME = "Bot";
const PERSON_NAME = "You";

// Utility function to format dates
function formatDate(date) {
    const h = "0" + date.getHours();
    const m = "0" + date.getMinutes();
    return `${h.slice(-2)}:${m.slice(-2)}`;
}

// Function to append a message to the chat
function appendMessage(name, img, side, text, timestamp = formatDate(new Date())) {
    const msgerChat = document.querySelector(".msger-chat");
    const msgHTML = `
        <div class="msg ${side}-msg">
            <div class="msg-img" style="background-image: url('${img}')"></div>
            <div class="msg-bubble">
                <div class="msg-info">
                    <div class="msg-info-name">${name}</div>
                    <div class="msg-info-time">${timestamp}</div>
                </div>
                <div class="msg-text">${text}</div>
            </div>
        </div>`;
    msgerChat.insertAdjacentHTML("beforeend", msgHTML);
    msgerChat.scrollTop += 500;
    // Check if we are supposed to send this message to the backend
    if (side === "right") { // Assuming messages from the current user appear on the "right"
        sendMessageToBackend(currentChatId, currentUser, text, side, timestamp);
    }
}

function sendMessageToBackend(chatId, userId, text, side, timestamp) {
    fetch('/history/send_message', {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            chat_id: chatId,
            user_id: userId, // Ensure your backend handles authentication to associate the message with the correct user
            message_type: side === "left" ? "bot" : "user",
            text: text,
            timestamp: timestamp, // Your backend might automatically set the timestamp
        })
    })
        .then(response => response.json())
        .then(data => {
            console.log("Message sent successfully:", data);
        })
        .catch(error => {
            console.error("Error sending message:", error);
        });
}

// Function to handle file submission and upload
function fileSubmit() {
    const formData = new FormData();
    const imageFile = document.getElementById('imageInput').files[0];
    formData.append("file", imageFile);

    // Displaying the image in the chat
    const reader = new FileReader();
    reader.onload = function (e) {
        appendMessage(PERSON_NAME, PERSON_IMG, "right", `<img src="${e.target.result}" alt="Sent image" style="width: 100%;">`);
    };
    reader.readAsDataURL(imageFile);

    // Sending the image to the server
    fetch("/upload_predict", {
        method: "POST",
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            appendMessage(BOT_NAME, BOT_IMG, "left", data.result);
        })
        .catch(error => console.error("Error:", error));
}

// Ensure this function is called after the DOM fully loads
document.addEventListener("DOMContentLoaded", function () {
    // Initialization code for imageInput
    const imageInput = document.getElementById("imageInput");
    if (imageInput) {
        imageInput.addEventListener("change", fileSubmit);
    }

    // Authentication check and chat history loading
    fetch('/api/is_authenticated')
        .then(response => response.json())
        .then(data => {
            const chatHistoryElement = document.getElementById('chat-history');
            if (!chatHistoryElement) {
                console.error('No element with ID chat-history found');
                return;
            }

            if (data.authenticated) {
                chatHistoryElement.classList.remove('hidden');
                loadChatHistory(); // Load chat history if the user is authenticated
            } else {
                chatHistoryElement.classList.add('hidden');
            }
        })
        .catch(error => console.error('Error verifying authentication status:', error));
});

// History part of code ---------------------------------------


function loadChatHistory() {
    fetch('/history/get_user_chats')
        .then(response => response.json())
        .then(chats => {
            const chatList = document.getElementById('chat-history').querySelector('.list-unstyled');
            chatList.innerHTML = ''; // Clear existing chat list
            chats.forEach(chat => {
                const listItem = document.createElement('li');
                listItem.innerHTML = `
                  <div class="chat-entry">
                    <a href="javascript:void(0);" onclick="selectChat(${chat.id})">${chat.title}</a>
                    <button class="delete-chat-btn" onclick="deleteChat(${chat.id})">
                      <i class="fas fa-trash"></i>
                    </button>
                  </div>`;
                chatList.appendChild(listItem);
            });
        })
        .catch(error => console.error('Error loading chat history:', error));
} 

function deleteChat(chatId) {
    if (!confirm("Are you sure you want to delete this chat?")) {
        return; // Stop if the user does not confirm
    }

    fetch(`/history/delete_chat?chat_id=${chatId}`, { method: 'DELETE' })
        .then(response => {
            if (response.ok) {
                loadChatHistory(); // Reload the chat history to reflect the deletion
            } else {
                throw new Error('Failed to delete chat');
            }
        })
        .catch(error => console.error('Error deleting chat:', error));
}

function selectChat(chatId) {
    fetch(`/history/get_chat_history?chat_id=${chatId}`)
        .then(response => response.json())
        .then(messages => {
            // Clear current messages
            const msgerChat = document.querySelector('.msger-chat');
            msgerChat.innerHTML = '';

            // Append each message to the chat
            messages.forEach(msg => {
                const side = msg.message_type === "bot" ? "left" : "right";
                // Assuming 'name' and 'img' are properly set for both bot and user messages
                // You might need to adjust how 'img' is set based on your data structure
                const img = msg.message_type === "bot" ? BOT_IMG : PERSON_IMG; // Use your constants or logic to set the correct image
                const name = msg.message_type === "bot" ? BOT_NAME : PERSON_NAME;
                appendMessage(name, img, side, msg.text, msg.timestamp);
            });
        })
        .catch(error => console.error('Error loading chat messages:', error));
}
// Hrihoriev add

// Функція для прокручування сторінки до секції "About"
function scrollToAbout() {
    const aboutSection = document.querySelector('.about-section');
    aboutSection.scrollIntoView({ behavior: 'smooth' });
}

// Функція для прокручування сторінки до футера (секції "Contacts")
function scrollToContacts() {
    const footer = document.getElementById('footer');
    footer.scrollIntoView({ behavior: 'smooth' });
}

function scrollToTop() {
    const navigation = document.getElementById('navigation');
    navigation.scrollIntoView({ behavior: 'smooth' });
}

// Функція відкриття модального вікна
function openModal() {
    var modal = document.getElementById("myModal");
    modal.style.display = "block";
}

// Функція закриття модального вікна
function closeModal() {
    var modal = document.getElementById("myModal");
    modal.style.display = "none";
}

// Функція відкриття модального вікна реєстрації
function openSignupModal() {
    document.getElementById('signupModal').style.display = 'block';
}

// Функція закриття модального вікна реєстрації
function closeSignupModal() {
    document.getElementById('signupModal').style.display = 'none';
}
