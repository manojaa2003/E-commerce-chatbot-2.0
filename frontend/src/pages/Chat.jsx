import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import "./Chat.css";

/* ============================================================
   PRODUCT PARSER
   ============================================================ */

const parseProducts = (content) => {
  if (!content || typeof content !== "string") {
    return null;
  }

  const productMatches = [
    ...content.matchAll(
      /(?:^|\n)\s*(\d+)\.\s+(.*?)(?=\n\s*\d+\.\s+|$)/gs
    ),
  ];

  if (productMatches.length === 0) {
    return null;
  }

  const products = productMatches
    .map((match) => {
      const productText = match[2].trim();

      const urlMatch = productText.match(/(https?:\/\/[^\s]+)/);

      const link = urlMatch
        ? urlMatch[1].replace(/[.,]+$/, "")
        : "";

      let textWithoutUrl = productText;

      if (urlMatch) {
        textWithoutUrl = productText
          .replace(urlMatch[0], "")
          .trim();
      }

      const priceMatch = textWithoutUrl.match(
        /(?:Rs\.?|₹)\s*([\d,]+(?:\.\d+)?)/i
      );

      const price = priceMatch ? priceMatch[1] : "";

      const ratingMatch = textWithoutUrl.match(
        /Rating\s*:\s*([\d.]+)/i
      );

      const rating = ratingMatch ? ratingMatch[1] : "";

      let name = textWithoutUrl;

      if (priceMatch) {
        name = name
          .substring(0, priceMatch.index)
          .trim();
      }

      name = name
        .replace(/:\s*$/, "")
        .trim();

      const brand = name.split(/\s+/)[0] || "";

      return {
        name,
        brand,
        price,
        rating,
        link,
      };
    })
    .filter((product) => product.name);

  const validProducts = products.filter(
    (product) =>
      product.price ||
      product.rating ||
      product.link
  );

  return validProducts.length > 0
    ? validProducts
    : null;
};

/* ============================================================
   PRODUCT CARD
   ============================================================ */

function ProductCard({ product, index }) {
  return (
    <article className="product-card">
      <div className="product-card-top">
        <span className="product-index">
          0{index + 1}
        </span>

        {product.brand && (
          <span className="product-brand">
            {product.brand}
          </span>
        )}
      </div>

      <h3 className="product-name">
        {product.name}
      </h3>

      <div className="product-details">
        {product.price && (
          <div className="product-detail">
            <span className="detail-label">
              Price
            </span>

            <span className="product-price">
              ₹{product.price}
            </span>
          </div>
        )}

        {product.rating && (
          <div className="product-detail">
            <span className="detail-label">
              Rating
            </span>

            <span className="product-rating">
              ★ {product.rating}
            </span>
          </div>
        )}
      </div>

      {product.link && (
        <a
          href={product.link}
          target="_blank"
          rel="noopener noreferrer"
          className="product-link"
        >
          View product
          <span aria-hidden="true">↗</span>
        </a>
      )}
    </article>
  );
}

/* ============================================================
   CHAT COMPONENT
   ============================================================ */

function Chat() {
  const navigate = useNavigate();

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [confirmationModal, setConfirmationModal] = useState(null);
  
  // Added responsive state for mobile sidebar
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  /* ==========================================================
     AUTOMATIC SCROLL
     ========================================================== */

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  }, [messages, loading]);

  /* ==========================================================
     CHECK LOGIN
     ========================================================== */

  useEffect(() => {
    const token =
      localStorage.getItem("access_token");

    if (!token) {
      navigate("/login");
    }
  }, [navigate]);

  /* ==========================================================
     NEW CHAT
     ========================================================== */

  const clearChat = () => {
    setMessages([]);
    setInput("");
    setShowSettings(false);
    setConfirmationModal(null);
    setIsSidebarOpen(false); // Close sidebar on mobile

    setTimeout(() => {
      textareaRef.current?.focus();
    }, 100);
  };

  /* ==========================================================
     SUGGESTION BUTTON
     ========================================================== */

  const useSuggestion = (text) => {
    setInput(text);

    setTimeout(() => {
      textareaRef.current?.focus();
    }, 100);
  };

  /* ==========================================================
     SETTINGS AND MODALS
     ========================================================== */

  const openLogoutModal = () => {
    setShowSettings(false);
    setConfirmationModal("logout");
  };

  const openDeleteModal = () => {
    setShowSettings(false);
    setConfirmationModal("delete");
  };

  const closeConfirmationModal = () => {
    if (loading) {
      return;
    }

    setConfirmationModal(null);
  };

  /* ==========================================================
     LOGOUT
     ========================================================== */

  const confirmLogout = async () => {
    setLoading(true);

    try {
      await api.post("/logout");
    } catch (error) {
      console.error("Logout API Error:", error);
    } finally {
      localStorage.removeItem("access_token");
      localStorage.removeItem("token_type");

      setConfirmationModal(null);
      setShowSettings(false);
      setLoading(false);

      navigate("/login");
    }
  };

  /* ==========================================================
     DELETE ACCOUNT
     ========================================================== */

  const confirmDeleteAccount = async () => {
    setLoading(true);

    try {
      await api.delete("/delete_user");

      localStorage.removeItem("access_token");
      localStorage.removeItem("token_type");

      setConfirmationModal(null);
      setShowSettings(false);
      setMessages([]);

      navigate("/login");
    } catch (error) {
      console.error("Delete Account Error:", error);

      if (
        error.response?.status === 401 ||
        error.response?.status === 403
      ) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("token_type");

        setConfirmationModal(null);
        navigate("/login");

        return;
      }

      alert(
        error.response?.data?.detail ||
          "Unable to delete your account. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  /* ==========================================================
     SEND MESSAGE
     ========================================================== */

  const sendMessage = async () => {
    const query = input.trim();

    if (!query || loading) {
      return;
    }

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: query,
      },
    ]);

    setInput("");
    setLoading(true);

    try {
      const response = await api.post("/chat", {
        query,
      });

      const aiResponse =
        response.data.response;

      const products =
        parseProducts(aiResponse);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: aiResponse,
          products,
        },
      ]);
    } catch (error) {
      console.error("Chat API Error:", error);

      if (error.response?.status === 401) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("token_type");

        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content:
              "Your session has expired. Please login again.",
            error: true,
          },
        ]);

        setTimeout(() => {
          navigate("/login");
        }, 1500);

        return;
      }

      if (error.response?.status === 422) {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content:
              "Invalid request. Please check your message.",
            error: true,
          },
        ]);

        return;
      }

      if (error.response) {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content:
              error.response.data?.detail ||
              "Something went wrong on the server.",
            error: true,
          },
        ]);

        return;
      }

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Unable to connect to the server. Please make sure your FastAPI backend is running.",
          error: true,
        },
      ]);
    } finally {
      setLoading(false);

      setTimeout(() => {
        textareaRef.current?.focus();
      }, 100);
    }
  };

  /* ==========================================================
     KEYBOARD HANDLING
     ========================================================== */

  const handleKeyDown = (event) => {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();
      sendMessage();
    }
  };

  /* ==========================================================
     RENDER
     ========================================================== */

  return (
    <div className="app">
      {/* Overlay background when mobile menu is open */}
      {isSidebarOpen && (
        <div 
          className="sidebar-overlay" 
          onClick={() => setIsSidebarOpen(false)}
        ></div>
      )}

      <aside className={`sidebar ${isSidebarOpen ? "open" : ""}`}>
        <button 
          className="mobile-close-btn" 
          onClick={() => setIsSidebarOpen(false)}
          aria-label="Close menu"
        >
          ✕
        </button>

        <div className="sidebar-brand">
          <div className="brand-mark">S</div>

          <div>
            <p className="brand-name">
              ShopAssist
            </p>

            <p className="brand-caption">
              Ecommerce companion
            </p>
          </div>
        </div>

        <div className="sidebar-top">
          <button
            className="new-chat-btn"
            onClick={clearChat}
          >
            <span className="button-icon">＋</span>
            <span>New chat</span>
          </button>

          <button
            className="chat-history-btn"
            onClick={() => {
              setIsSidebarOpen(false); // Close sidebar on mobile
              navigate("/chat-history");
            }}
          >
            <span className="button-icon">▤</span>
            <span>Chat history</span>
          </button>
        </div>

        <div className="sidebar-bottom">
          <div className="shopping-note">
            <span className="shopping-note-icon">
              ✦
            </span>

            <div>
              <p>Shopping made simpler</p>
              <span>
                Find products that fit your needs.
              </span>
            </div>
          </div>

          <button
            className="sidebar-settings-btn"
            onClick={() =>
              setShowSettings((prev) => !prev)
            }
          >
            <span className="button-icon">⚙</span>
            <span>Settings</span>
            <span className="settings-chevron">
              {showSettings ? "⌃" : "⌄"}
            </span>
          </button>

          {showSettings && (
            <div className="settings-card">
              <button
                className="settings-option logout-option"
                onClick={openLogoutModal}
              >
                <span>↪</span>
                <span>Logout</span>
              </button>

              <button
                className="settings-option delete-option"
                onClick={openDeleteModal}
              >
                <span>⌫</span>
                <span>Delete Account</span>
              </button>
            </div>
          )}
        </div>
      </aside>

      <main className="chat-container">
        <header className="chat-header">
          <div className="header-left">
            <button 
              className="mobile-menu-btn"
              onClick={() => setIsSidebarOpen(true)}
              aria-label="Open menu"
            >
              ☰
            </button>
            <div className="header-title">
              <div className="bot-logo">
                <span>✦</span>
              </div>

              <div>
                <h1>ShopAssist</h1>

                <div className="assistant-meta">
                  <span className="online-dot"></span>
                  <span>Online</span>
                  <span className="meta-divider">•</span>
                  <span>Product recommendations</span>
                </div>
              </div>
            </div>
          </div>

          <div className="header-badge">
            <span>AI shopping assistant</span>
          </div>
        </header>

        <section className="messages-container">
          {messages.length === 0 && !loading && (
            <div className="welcome-screen">
              <div className="welcome-orb">
                <div className="welcome-logo">✦</div>
              </div>

              <span className="welcome-eyebrow">
                YOUR PERSONAL SHOPPING GUIDE
              </span>

              <h2>
                Find something
                <span> you’ll love.</span>
              </h2>

              <p className="welcome-description">
                Tell me what you’re looking for, your
                budget, or your preferences. I’ll help
                you discover the right products.
              </p>

              <div className="suggestion-heading">
                <span>Try asking</span>
                <span className="suggestion-line"></span>
              </div>

              <div className="suggestions">
                <button
                  onClick={() =>
                    useSuggestion(
                      "Find the best laptops under ₹60000"
                    )
                  }
                >
                  <span className="suggestion-icon">
                    ◉
                  </span>
                  <span>
                    Find the best laptops under ₹60000
                  </span>
                  <span className="suggestion-arrow">
                    →
                  </span>
                </button>

                <button
                  onClick={() =>
                    useSuggestion(
                      "What are the payment types in this platfrom 💼"
                    )
                  }
                >
                  <span className="suggestion-icon">
                    ▣
                  </span>
                  <span>
                    What are the payment types in this platfrom 💼
                  </span>
                  <span className="suggestion-arrow">
                    →
                  </span>
                </button>

                <button
                  onClick={() =>
                    useSuggestion(
                      "How can you help for me 🧐"
                    )
                  }
                >
                  <span className="suggestion-icon">
                    ◇
                  </span>
                  <span>
                    How can you help for me 🧐
                  </span>
                  <span className="suggestion-arrow">
                    →
                  </span>
                </button>
              </div>

              <p className="welcome-footnote">
                You can ask about price, features, ratings..
              </p>
            </div>
          )}

          {messages.map((message, index) => (
            <div
              key={index}
              className={`message-row ${message.role}`}
            >
              <div className="avatar">
                {message.role === "user" ? (
                  "You"
                ) : (
                  <span>✦</span>
                )}
              </div>

              <div
                className={`message-content ${
                  message.error
                    ? "error-message"
                    : ""
                }`}
              >
                {message.role === "user" &&
                  message.content}

                {message.role === "assistant" &&
                  (message.error ? (
                    message.content
                  ) : message.products &&
                    message.products.length > 0 ? (
                    <div className="assistant-product-message">
                      <p className="recommendation-label">
                        Recommended for you
                      </p>

                      <div className="products-container">
                        {message.products.map(
                          (product, productIndex) => (
                            <ProductCard
                              key={productIndex}
                              product={product}
                              index={productIndex}
                            />
                          )
                        )}
                      </div>
                    </div>
                  ) : (
                    message.content
                  ))}
              </div>
            </div>
          ))}

          {loading && (
            <div className="message-row assistant">
              <div className="avatar">
                <span>✦</span>
              </div>

              <div className="typing-indicator">
                <span></span>
                <i></i>
                <i></i>
                <i></i>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </section>

        <div className="input-area">
          <div className="input-wrapper">
            <div className="input-leading-icon">
              ✦
            </div>

            <textarea
              ref={textareaRef}
              value={input}
              onChange={(event) =>
                setInput(event.target.value)
              }
              onKeyDown={handleKeyDown}
              placeholder="Ask about products, prices, features, or comparisons..."
              rows="1"
              disabled={loading}
              aria-label="Message ShopAssist"
            />

            <button
              className={`send-button ${
                input.trim() && !loading
                  ? "active"
                  : ""
              }`}
              onClick={sendMessage}
              disabled={
                !input.trim() || loading
              }
              aria-label="Send message"
            >
              ↑
            </button>
          </div>

          <div className="input-footer">
            <span>
              ShopAssist can make mistakes. Check important
              product details before buying.
            </span>

            <span>
              Enter to send · Shift + Enter for new line
            </span>
          </div>
        </div>
      </main>

      {confirmationModal === "logout" && (
        <div
          className="modal-overlay"
          onClick={closeConfirmationModal}
        >
          <div
            className="confirmation-modal"
            onClick={(event) =>
              event.stopPropagation()
            }
          >
            <div className="modal-icon">↪</div>

            <h2>Logout</h2>

            <p>
              Are you sure you want to logout from
              your account?
            </p>

            <div className="modal-actions">
              <button
                className="modal-btn modal-cancel-btn"
                onClick={closeConfirmationModal}
                disabled={loading}
              >
                Cancel
              </button>

              <button
                className="modal-btn modal-confirm-btn"
                onClick={confirmLogout}
                disabled={loading}
              >
                {loading
                  ? "Logging out..."
                  : "Logout"}
              </button>
            </div>
          </div>
        </div>
      )}

      {confirmationModal === "delete" && (
        <div
          className="modal-overlay"
          onClick={closeConfirmationModal}
        >
          <div
            className="confirmation-modal delete-modal"
            onClick={(event) =>
              event.stopPropagation()
            }
          >
            <div className="modal-icon">⌫</div>

            <h2>Delete Account</h2>

            <p>
              Are you sure you want to permanently
              delete your account?
            </p>

            <p className="warning-text">
              This action cannot be undone.
            </p>

            <div className="modal-actions">
              <button
                className="modal-btn modal-cancel-btn"
                onClick={closeConfirmationModal}
                disabled={loading}
              >
                Cancel
              </button>

              <button
                className="modal-btn modal-delete-btn"
                onClick={confirmDeleteAccount}
                disabled={loading}
              >
                {loading
                  ? "Deleting..."
                  : "Delete Account"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Chat;