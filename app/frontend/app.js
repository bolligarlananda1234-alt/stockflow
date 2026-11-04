
const API_URL = "http://127.0.0.1:8000";

// Form elements
const loginForm = document.getElementById("loginForm");
const registerForm = document.getElementById("registerForm");

const loginTab = document.getElementById("loginTab");
const registerTab = document.getElementById("registerTab");

const message = document.getElementById("message");

// Switch to Login
loginTab.addEventListener("click", () => {
    loginForm.classList.remove("hidden");
    registerForm.classList.add("hidden");

    loginTab.classList.add("active");
    registerTab.classList.remove("active");

    message.textContent = "";
});

// Switch to Register
registerTab.addEventListener("click", () => {
    registerForm.classList.remove("hidden");
    loginForm.classList.add("hidden");

    registerTab.classList.add("active");
    loginTab.classList.remove("active");

    message.textContent = "";
});

// Registration API
registerForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const userData = {
        full_name: document.getElementById("fullName").value,
        email: document.getElementById("registerEmail").value,
        organization_name: document.getElementById("organizationName").value,
        password: document.getElementById("registerPassword").value
    };

    try {
        const response = await fetch(`${API_URL}/auth/register`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(userData)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Registration failed");
        }

        message.textContent = "Registration successful! Please login.";
        message.style.color = "green";

        registerForm.reset();

        loginTab.click();

    } catch (error) {
        message.textContent = error.message;
        message.style.color = "red";
    }
});

// Login API
loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const loginData = {
        email: document.getElementById("loginEmail").value,
        password: document.getElementById("loginPassword").value
    };

    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(loginData)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Login failed");
        }

        localStorage.setItem("access_token", data.access_token);

        message.textContent = "Login successful!";
        message.style.color = "green";

       window.location.href = "dashboard.html";

    } catch (error) {
        message.textContent = error.message;
        message.style.color = "red";
    }
});
