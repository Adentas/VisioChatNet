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
}

// Function to handle file submission and upload
function fileSubmit() {
    const formData = new FormData();
    const imageFile = document.getElementById('imageInput').files[0];
    formData.append("file", imageFile);

    // Displaying the image in the chat
    const reader = new FileReader();
    reader.onload = function(e) {
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
document.addEventListener("DOMContentLoaded", function() {
    // If there are specific initializations or event listeners, add them here.
    const imageInput = document.getElementById("imageInput");
    if(imageInput) {
        imageInput.addEventListener("change", fileSubmit);
    }
});


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
    // Ваша логіка перевірки статусу авторизації користувача тут
    var isLoggedIn = true; // Припустимо, що користувач увійшов
    return isLoggedIn;
}

// Функція для оновлення навігаційного меню в залежності від статусу авторизації користувача
function updateNavigationMenu() {
    var isLoggedIn = checkAuthStatus();
    var loginButton = document.querySelector('.Login');
    var signUpButton = document.querySelector('.Sign-Up');
    var logoutButton = document.createElement('a');
    logoutButton.textContent = 'Log Out';
    logoutButton.className = 'Logout';
    logoutButton.href = '#'; // Додайте URL для виходу з системи
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

