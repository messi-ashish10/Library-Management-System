document.addEventListener("DOMContentLoaded", () => {
    const passwordField = document.getElementById("password");
    const strengthText = document.getElementById("strengthText");
    const strengthBar = document.getElementById("strengthBar");
    const passwordStrength = document.getElementById("passwordStrength");

    function checkPasswordStrength() {
        if (passwordField) {
            const password = passwordField.value;
            let strength = "Weak";
            let strengthWidth = "25%";

            if (password.length >= 5) {
                strength = "Medium";
                strengthWidth = "50%";
                if (/[A-Z]/.test(password) && /[0-9]/.test(password)) {
                    strength = "Strong";
                    strengthWidth = "100%";
                }
            }

            strengthText.textContent = strength;
            passwordStrength.classList.remove("hidden");
            strengthBar.style.width = strengthWidth;
            strengthBar.className = strength === "Strong" ? "h-1 rounded-full bg-green-500" : "h-1 rounded-full bg-yellow-500";
        }
    }

    if (passwordField) {
        passwordField.addEventListener("input", checkPasswordStrength);
    }
});
