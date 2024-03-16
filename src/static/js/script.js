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
        selectChat(initialChatId); // Replace initialChatId with the actual ID
    }
});

// History part of code ---------------------------------------
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

function loadChatHistory() {
    getCurrentChat(currentID => {
        fetch('/history/get_user_chats')
            .then(response => response.json())
            .then(chats => {
                const chatList = document.getElementById('chat-history').querySelector('.list-unstyled');
                chatList.innerHTML = ''; // Clear existing chat list
                chats.reverse().forEach(chat => {
                    const title = chat.id === currentID ? `Selected chat: ${chat.title}` : chat.title;
                    const listItem = document.createElement('li');
                    listItem.classList.add('chat-entry');
                    if (chat.id === currentID) {
                        listItem.classList.add('selected-chat');
                    }
                    listItem.innerHTML = `
                        <div class="chat-entry">
                            <a href="javascript:void(0);" onclick="selectChat(${chat.id})">${title}</a>
                            <button class="delete-chat-btn" onclick="deleteChat(${chat.id})">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>`;
                    chatList.appendChild(listItem);
                });

                // After loading chats, if there is a current chat ID, select it
                if (currentID) {
                    selectChat(currentID);
                }
            })
            .catch(error => console.error('Error loading chat history:', error));
    });
}

function updateChatList(chats, currentID) {
    const chatList = document.getElementById('chat-history').querySelector('.list-unstyled');
    chatList.innerHTML = '';

    chats.reverse().forEach(chat => {
        const title = chat.id === currentID ? `Selected chat: ${chat.title}` : chat.title;
        const listItem = document.createElement('li');
        listItem.innerHTML = `
            <div class="chat-entry ${chat.id === currentID ? 'selected-chat' : ''}">
                <a href="javascript:void(0);" onclick="selectChat(${chat.id})">${title}</a>
                <button class="delete-chat-btn" onclick="deleteChat(${chat.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
        chatList.appendChild(listItem);
    });
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
    console.log(`selectChat called with chatId: ${chatId}`);

    // Update the current chat ID on the backend
    fetch('/history/set_current_chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ chat_id: chatId })
    })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Failed to set current chat');
            }
        })
        .then(data => {
            // After setting the current chat ID, get the chat history
            return fetch(`/history/get_chat_history?chat_id=${chatId}`);
        })
        .then(response => {
            return response.json();
        })
        .then(messages => {
            const msgerChat = document.querySelector('.msger-chat');
            msgerChat.innerHTML = '';  // Clear current messages

            messages.forEach(msg => {
                const side = msg.message_type === "bot" ? "left" : "right";
                const img = msg.message_type === "bot" ? BOT_IMG : PERSON_IMG;
                const name = msg.message_type === "bot" ? BOT_NAME : PERSON_NAME;

                // Check if the message has text content and append it
                if (msg.text) {
                    appendMessage(name, img, side, msg.text, formatDate(new Date(msg.timestamp)));
                }

                // Check if the message has an image and append it
                if (msg.image) {
                    // When the server sends the image as a Base64 string
                    const imageHtml = `<img src="data:image/png;base64,${msg.image}" alt="Sent image" style="width: 100%;">`; // Ensure the MIME type matches your image data
                    appendMessage(name, img, side, imageHtml, formatDate(new Date(msg.timestamp)));
                }
            });
        })
        .catch(error => console.error('Error loading chat messages:', error));

    // After fetching chats, update the list
    fetch('/history/get_user_chats')
        .then(response => response.json())
        .then(chats => {
            updateChatList(chats, chatId); // Pass the current chat ID
        });
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
                logoutButton.onclick = function() {
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
    logoutButton.onclick = function() {
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
