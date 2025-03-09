document.getElementById("loginForm").addEventListener("submit", function (event) {
    event.preventDefault();

    const adminEmail = "a@admin.com";
    const adminPassword = "a";

    const emailInput = document.getElementById("email").value;
    const passwordInput = document.getElementById("password").value;
    const errorMessage = document.getElementById("error-message");

    if (emailInput === adminEmail && passwordInput === adminPassword) {
        window.location.href = "/dashboard";
    } else {
        errorMessage.textContent = "❌ Invalid email or password!";
        errorMessage.style.display = "block";
    }
});

document.getElementById("email").addEventListener("input", function () {
    const emailInput = this.value;
    const emailError = document.getElementById("email-error");
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailPattern.test(emailInput)) {
        emailError.textContent = "Invalid email format";
        emailError.style.display = "block";
    } else {
        emailError.style.display = "none";
    }
});

function togglePassword() {
    const passwordField = document.getElementById("password");
    const toggleIcon = document.querySelector(".toggle-password");

    if (passwordField.type === "password") {
        passwordField.type = "text";
        toggleIcon.textContent = "👁️";
    } else {
        passwordField.type = "password";
        toggleIcon.textContent = "🙈";
    }
}