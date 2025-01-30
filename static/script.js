document.getElementById('login-form').addEventListener('submit', async function (event) {
    event.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    const response = await fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
    });

    const result = await response.json();
    const messageElement = document.getElementById('response-message');

    if (response.status === 200) {
        messageElement.style.color = 'green';
        messageElement.textContent = `¡Bienvenido, ${result.name}!`;
    } else {
        messageElement.style.color = 'red';
        messageElement.textContent = result.message;
    }
});
