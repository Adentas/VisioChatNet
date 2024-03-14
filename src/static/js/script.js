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
