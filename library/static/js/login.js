function validateLoginForm() {
    validateUsername();
    validatePassword();
    const errors = document.querySelectorAll('.text-red-500:not(.hidden)');
    return errors.length === 0;
}

function validateUsername() {
    const username = document.getElementById('username').value;
    const usernameError = document.getElementById('usernameError');
    if (username.length < 3) {
        usernameError.classList.remove('hidden');
    } else {
        usernameError.classList.add('hidden');
    }
}

function validatePassword() {
    const password = document.getElementById('password').value;
    const passwordError = document.getElementById('passwordError');
    if (password.length < 6) {
        passwordError.classList.remove('hidden');
    } else {
        passwordError.classList.add('hidden');
    }
}
