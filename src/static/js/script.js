// Constants for image paths and names
const BOT_IMG = "/static/styles/img/robot.svg";
const PERSON_IMG = "/static/styles/img/user.svg";
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
    fetch("/predict/get_predictions", {
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

    // Load chat history for authenticated users
    fetch('/auth/is_authenticated')
        .then(response => response.json())
        .then(data => {
            if (data.authenticated) {
                // Assume loadChatHistory function will load the list of chats
                loadChatHistory();
            } else {
                // Hide chat history for unauthenticated users
                document.getElementById('chat-history').classList.add('hidden');
            }
        })
        .catch(error => console.error('Error verifying authentication status:', error));

    // Automatically select the initial chat session for new users
    if (isNewUser()) { // Implement this check based on your application's logic
        debounceSelectChat(initialChatId); // Replace initialChatId with the actual ID
    }
});

// History part of code ---------------------------------------
// Global cache for chat list
let chatListCache = null;

function getCurrentChat(callback) {
    fetch('/history/get_current_chat')
        .then(response => response.json())
        .then(data => {
            if (data.chat_id) {
                callback(data.chat_id);  // Pass the chat_id to the callback function
            } else {
                // Handle no active chat session, which may involve creating one or prompting the user to select one
            }
        })
        .catch(error => console.error('Error retrieving current chat:', error));
}

// Function to refresh the chat list cache manually
function refreshChatListCache(callback) {
    fetch('/history/get_user_chats')
        .then(response => response.json())
        .then(chats => {
            chatListCache = chats; // Update the cache
            if (callback) callback(chats);
        })
        .catch(error => console.error('Error fetching chat list:', error));
}

// Function to load the chat history using the cached chat list
function loadChatHistory() {
    getCurrentChat(currentID => {
        // Use the cached chat list if it exists, otherwise fetch it
        if (chatListCache) {
            selectChatFromCache(currentID);
            updateChatList(chatListCache, currentID);
        } else {
            refreshChatListCache(chats => {
                selectChatFromCache(currentID);
                updateChatList(chats, currentID);
            });
        }
    });
}

function updateChatList(chats, currentID) {
    const chatList = document.getElementById('chat-history').querySelector('.list-unstyled');
    chatList.innerHTML = '';

    // Reset the selected chat on all items first
    document.querySelectorAll('.chat-entry').forEach(item => {
        item.classList.remove('selected-chat');
    });

    // Then, add chats to the list and mark the selected one
    chats.slice().reverse().forEach(chat => {
        const title = chat.title;
        const listItem = document.createElement('li');
        listItem.classList.add('chat-entry');
        if (chat.id === currentID) {
            listItem.classList.add('selected-chat'); // Mark the current chat as selected
        }
        listItem.innerHTML = `
            <div>
                <a href="javascript:void(0);" onclick="selectChat(${chat.id})">${title}</a>
                <button class="delete-chat-btn" onclick="deleteChat(${chat.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
        chatList.appendChild(listItem);
    });

    // Scroll to the selected chat if it exists in the list
    const selectedChatElement = chatList.querySelector('.selected-chat');
    if (selectedChatElement) {
        selectedChatElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}

// Helper function to select the chat from the cached list
function selectChatFromCache(currentID) {
    const chatExists = chatListCache && chatListCache.some(chat => chat.id === currentID);
    if (chatExists) {
        selectChat(currentID);
    } else {
        // If the current chat ID isn't found or no chats are cached, select the first one
        if (chatListCache && chatListCache.length > 0) {
            selectChat(chatListCache[0].id);
        }
    }
}

function deleteChat(chatId) {
    // Confirm chat deletion
    if (!confirm("Are you sure you want to delete this chat?")) {
        return; // Stop if the user does not confirm
    }

    // Check if the chat is the last one in the cache
    if (chatListCache && chatListCache.length === 1) {
        alert("You cannot delete the last chat.");
        return; // Stop the deletion if it's the last chat
    }

    // Perform the deletion
    fetch(`/history/delete_chat?chat_id=${chatId}`, { method: 'DELETE' })
        .then(response => {
            if (response.ok) {
                // Find the chat to delete by its ID
                const indexToDelete = chatListCache.findIndex(chat => chat.id === chatId);
                if (indexToDelete === -1) {
                    throw new Error("Chat not found in cache.");
                }

                // Remove the chat from the cache
                chatListCache.splice(indexToDelete, 1);

                // Since we display the chats in reverse order, calculate the next chat index accordingly
                let nextIndex = chatListCache.length - indexToDelete - 1;
                // If the deleted chat was the last one, select the new last chat
                if (nextIndex >= chatListCache.length) {
                    nextIndex = chatListCache.length - 1;
                }

                // Get the next chat ID after deletion to select
                let nextChatId = null;
                if (chatListCache.length > 0 && nextIndex >= 0) {
                    nextChatId = chatListCache[nextIndex].id;
                }

                // Update the visual chat list and select the new chat
                updateChatList(chatListCache, nextChatId); // Pass a reversed copy for rendering
                if (nextChatId !== null) {
                    selectChat(nextChatId, true);
                }
            } else {
                throw new Error('Failed to delete chat');
            }
        })
        .catch(error => console.error('Error deleting chat:', error));
}


let debounceTimer;
function debounceSelectChat(chatId, delay = 500) { // 500 ms delay by default
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
        selectChat(chatId);
    }, delay);
}

// Function to select a chat and update the cache
function selectChat(chatId, fromUserInteraction = false) {
    console.log(`selectChat called with chatId: ${chatId}`);

    if (fromUserInteraction) {
        // Update the current chat ID on the backend if the selection is from user interaction
        setCurrentChat(chatId);
    }

    // Get the chat history for the selected chat
    fetchChatMessages(chatId);

    // Visually update the selected chat
    updateVisualSelectedChat(chatId);
}

function setCurrentChat(chatId) {
    fetch('/history/set_current_chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ chat_id: chatId })
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to set current chat');
            }
        })
        .catch(error => console.error('Error setting current chat:', error));
}

function fetchChatMessages(chatId) {
    fetch(`/history/get_chat_history?chat_id=${chatId}`)
        .then(response => response.json())
        .then(messages => {
            const msgerChat = document.querySelector('.msger-chat');
            msgerChat.innerHTML = '';  // Clear current messages
            messages.forEach(msg => {
                const side = msg.message_type === "bot" ? "left" : "right";
                const img = msg.message_type === "bot" ? BOT_IMG : PERSON_IMG;
                const name = msg.message_type === "bot" ? BOT_NAME : PERSON_NAME;
                const imageHtml = `<img src="data:image/png;base64,${msg.image}" alt="Sent image" style="width: 100%;">`; // Ensure the MIME type matches your image data
                const content = msg.text || imageHtml;
                appendMessage(name, img, side, content, formatDate(new Date(msg.timestamp)));
            });
        })
        .catch(error => console.error('Error loading chat messages:', error));
}

function updateVisualSelectedChat(chatId) {
    const allChats = document.querySelectorAll('.chat-entry');
    allChats.forEach(chatElement => {
        chatElement.classList.remove('selected-chat');
    });

    const selectedChat = document.querySelector(`.chat-entry a[onclick*="selectChat(${chatId}"]`);
    if (selectedChat) {
        selectedChat.closest('.chat-entry').classList.add('selected-chat');
    }
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

// Функція, яка перевіряє, чи користувач увійшов
function checkAuthStatus() {
    fetch('/auth/is_authenticated')
        .then(response => response.json())
        .then(data => {
            const loginButton = document.querySelector('.Login');
            const signUpButton = document.querySelector('.Sign-Up');
            let logoutButton = document.querySelector('.Logout');

            if (data.authenticated) {
                if (!logoutButton) {
                    logoutButton = document.createElement('a');
                    logoutButton.textContent = 'Log Out';
                    logoutButton.className = 'Logout';
                    logoutButton.href = '/auth/logout';
                    logoutButton.onclick = function () {
                        fetch('/auth/logout').then(() => {
                            window.location.reload(); // Перезавантаження сторінки для оновлення стану UI
                        });
                    };
                    document.querySelector('.sign-options').appendChild(logoutButton);
                }
                loginButton.style.display = 'none';
                signUpButton.style.display = 'none';
            } else {
                if (logoutButton) {
                    logoutButton.parentNode.removeChild(logoutButton);
                }
                loginButton.style.display = 'block';
                signUpButton.style.display = 'block';
            }
        })
        .catch(error => console.error('Error verifying authentication status:', error));
}

document.addEventListener("DOMContentLoaded", function () {
    checkAuthStatus();
});


// Функція для оновлення навігаційного меню в залежності від статусу авторизації користувача
function updateNavigationMenu() {
    var isLoggedIn = checkAuthStatus();
    var loginButton = document.querySelector('.Login');
    var signUpButton = document.querySelector('.Sign-Up');
    var logoutButton = document.createElement('a');
    logoutButton.textContent = 'Log Out';
    logoutButton.className = 'Logout';
    logoutButton.href = '/auth/logout'; // Додайте URL для виходу з системи
    logoutButton.onclick = function () {
        isLoggedIn = false; // Встановлюємо значення isLoggedIn на false при натисканні кнопки "Log Out"
        var logoutButton = document.querySelector('.Logout');
        if (logoutButton) {
            logoutButton.parentNode.removeChild(logoutButton);
        }
        loginButton.style.display = 'block'; // Показуємо кнопку "Login"
        signUpButton.style.display = 'block'; // Показуємо кнопку "Sign Up"
    };

    if (isLoggedIn) {
        // Заміна кнопок "Login" та "Sign Up" на кнопку "Log Out"
        loginButton.style.display = 'none';
        signUpButton.style.display = 'none';
        document.querySelector('.sign-options').appendChild(logoutButton);
    } else {
        // Показати кнопки "Login" та "Sign Up", якщо користувач не увійшов
        loginButton.style.display = 'block';
        signUpButton.style.display = 'block';
        var logoutButton = document.querySelector('.Logout');
        if (logoutButton) {
            logoutButton.parentNode.removeChild(logoutButton);
        }
    }
}

// Виклик функції для оновлення навігаційного меню при завантаженні сторінки
updateNavigationMenu();
