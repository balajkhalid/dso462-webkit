// Initialize the cart object
let cart = {};

async function loadProductDetails() {
  const params = new URLSearchParams(window.location.search);
  const productId = params.get("id");
  const userId = 10002; // Replace with dynamic user ID later

  if (!productId) {
    document.getElementById("product-details").innerText = "Product not found.";
    return;
  }

  try {
    // Fetch main product details
    const response = await fetch(`/products-details?productId=${productId}`);
    const product = await response.json();

    const productDetails = `
      <div class="product-detail">
        <img src="${product.image}" alt="${product.name}">
        <div class="product-info">
          <h2>${product.name}</h2>
          <p class="price">$${product.price}</p>
          <p>${product.description}</p>
          <button onclick="addToCart('${product.product_id}')">Add to Cart</button>
        </div>
      </div>
    `;

    document.getElementById("product-details").innerHTML = productDetails;

    // Fetch similar products
    const similarResponse = await fetch(
      `/similar-products?productId=${productId}&userId=${userId}`
    );
    const similarProducts = await similarResponse.json();
    console.log("Similar products:", similarProducts);

    renderSimilarProducts(similarProducts);
  } catch (error) {
    console.error("Error loading product:", error);
    document.getElementById("product-details").innerText =
      "Failed to load product.";
  }
}

// Render similar products section
function renderSimilarProducts(products) {
  const container = document.getElementById("similar-products");
  if (!products.length) {
    container.innerHTML = "<p>No similar products found.</p>";
    return;
  }

  let html = `<h3 class="similar-heading">Similar Products</h3><div class="similar-products-row">`;

  products.forEach((product) => {
    html += `
    <div class="similar-products-row">
      <div class="similar-card">
        <img src="${product.image}" alt="${product.name}">
        <h4>${product.name}</h4>
        <p class="price">$${product.price}</p>
        <button onclick="addToCart('${product.product_id}')">Add to Cart</button>
      </div>
      </div>
    `;
  });

  html += `</div>`;
  container.innerHTML = html;
}

// Add product to cart
function addToCart(productId) {
  if (cart[productId]) {
    cart[productId].quantity += 1;
  } else {
    cart[productId] = { quantity: 1 };
  }
  updateCartCount();
}

// Update the cart icon count
function updateCartCount() {
  const cartCount = Object.values(cart).reduce(
    (total, product) => total + product.quantity,
    0
  );
  document.getElementById("cartCount").textContent = cartCount;
}

loadProductDetails();
