
const API_URL = "http://127.0.0.1:8000";

const token = localStorage.getItem("access_token");

// Check login
if (!token) {
    window.location.href = "index.html";
}

// Authorization headers
function getHeaders() {
    return {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
    };
}

// Load dashboard statistics
async function loadDashboard() {
    try {
        const response = await fetch(`${API_URL}/dashboard/`, {
            headers: getHeaders()
        });

        if (response.status === 401) {
            logout();
            return;
        }

        if (!response.ok) {
            throw new Error("Unable to load dashboard");
        }

        const data = await response.json();

        document.getElementById("totalProducts").textContent =
            data.total_products;

        document.getElementById("totalQuantity").textContent =
            data.total_quantity;

        document.getElementById("lowStockProducts").textContent =
            data.low_stock_products;

    } catch (error) {
        console.error(error);
        alert(error.message);
    }
}

// Load products
async function loadProducts() {
    try {
        const response = await fetch(`${API_URL}/products/`, {
            headers: getHeaders()
        });

        if (response.status === 401) {
            logout();
            return;
        }

        if (!response.ok) {
            throw new Error("Unable to load products");
        }

        const products = await response.json();

        const table = document.getElementById("productTable");
        table.innerHTML = "";

        products.forEach(product => {
            const row = document.createElement("tr");

            const values = [
                product.product_name,
                product.sku,
                product.quantity,
                product.cost_price,
                product.selling_price
            ];

            values.forEach(value => {
                const cell = document.createElement("td");
                cell.textContent = value ?? "";
                row.appendChild(cell);
            });

            const actionCell = document.createElement("td");
            actionCell.textContent = "View";
            row.appendChild(actionCell);

            table.appendChild(row);
        });

    } catch (error) {
        console.error(error);
        alert(error.message);
    }
}

// Add product
document.getElementById("productForm").addEventListener(
    "submit",
    async (event) => {
        event.preventDefault();

        const product = {
            product_name: document.getElementById("productName").value,
            sku: document.getElementById("sku").value,
            description: document.getElementById("description").value,
            quantity: Number(document.getElementById("quantity").value),
            cost_price: Number(document.getElementById("costPrice").value),
            selling_price: Number(document.getElementById("sellingPrice").value),
            low_stock_threshold: Number(document.getElementById("threshold").value)
        };

        try {
            const response = await fetch(`${API_URL}/products/`, {
                method: "POST",
                headers: getHeaders(),
                body: JSON.stringify(product)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || "Product could not be added");
            }

            document.getElementById("productMessage").textContent =
                "Product added successfully!";

            document.getElementById("productMessage").style.color = "green";

            event.target.reset();

            await loadDashboard();
            await loadProducts();

        } catch (error) {
            document.getElementById("productMessage").textContent =
                error.message;

            document.getElementById("productMessage").style.color = "red";
        }
    }
);

// Logout
function logout() {
    localStorage.removeItem("access_token");
    window.location.href = "index.html";
}

document.getElementById("logoutBtn").addEventListener("click", logout);

// Initial loading
loadDashboard();
loadProducts();
