const form = document.querySelector('#login-form');
const passwordInput = document.querySelector('#password');
const togglePassword = document.querySelector('#toggle-password');
const message = document.querySelector('#form-message');

togglePassword.addEventListener('click', () => {
  const isPassword = passwordInput.type === 'password';
  passwordInput.type = isPassword ? 'text' : 'password';
  togglePassword.textContent = isPassword ? 'Hide' : 'Show';
});

form.addEventListener('submit', (event) => {
  event.preventDefault();
  message.classList.remove('error');

  if (!form.checkValidity()) {
    message.textContent = 'Enter an email address and password to continue.';
    message.classList.add('error');
    form.reportValidity();
    return;
  }

  const formData = new FormData(form);
  fetch('/api/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: formData.get('email'),
      password: formData.get('password')
    })
  })
    .then(async (response) => {
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Unable to sign in');
      window.location.href = data.redirect;
    })
    .catch((error) => {
      message.textContent = error.message;
      message.classList.add('error');
    });
});
