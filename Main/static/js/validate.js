document.getElementById('signupForm').addEventListener('submit', async function (e) {
    // Prevent form submission
    e.preventDefault();

    // Get form inputs
    const username = document.getElementById('username').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value.trim();
    const confirmPassword = document.getElementById('confirmPassword').value.trim();

    // Validate all fields are filled
    if (!username || !email || !password || !confirmPassword) {
        alert('All fields are required.');
        return;
    }

    // Validate email format
    const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailPattern.test(email)) {
        alert('Please enter a valid email address.');
        return;
    }

    // Validate password length
    if (password.length < 8) {
        alert('Password must be at least 8 characters long.');
        return;
    }

    // Validate passwords match
    if (password !== confirmPassword) {
        alert('Passwords do not match.');
        return;
    }

    // Check if username and email are unique
    try {
        const response = await fetch('/check-unique', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, email }),
        });

        const result = await response.json();

        if (result.username_exists) {
            alert('Username already exists. Please choose a different username.');
            return;
        }

        if (result.email_exists) {
            alert('Email is already registered. Please use a different email.');
            return;
        }

        // If all validations pass and both are unique, submit the form
        this.submit();
    } catch (error) {
        console.error('Error checking uniqueness:', error);
        alert('An error occurred. Please try again.');
    }
});
