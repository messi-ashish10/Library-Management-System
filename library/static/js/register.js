document.addEventListener("DOMContentLoaded", () => {
    const passwordField = document.getElementById("password");
    const strengthText = document.getElementById("strengthText");
    const strengthBar = document.getElementById("strengthBar");
    const passwordStrength = document.getElementById("passwordStrength");

    function resetPasswordStrength() {
        if (passwordField) {
            strengthText.textContent = "";
            passwordStrength.classList.add("hidden");
            strengthBar.style.width = "0%";
            strengthBar.className = "";
        }
    }

    if (passwordField) {
        passwordField.addEventListener("input", resetPasswordStrength);
    }
});
