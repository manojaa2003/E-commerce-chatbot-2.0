import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import "./ChatHistory.css";

function ChatHistory() {
  const navigate = useNavigate();

  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteLoading, setDeleteLoading] = useState(false);

  /*
   * Load chat history
   */
  const loadHistory = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await api.get("/chat/history");

      setMessages(
        Array.isArray(response.data)
          ? response.data
          : []
      );
    } catch (err) {
      console.error("History error:", err);

      if (err.response?.status === 401) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("token_type");

        navigate("/login");
        return;
      }

      setError(
        err.response?.data?.detail ||
          "Unable to load chat history."
      );
    } finally {
      setLoading(false);
    }
  };

  /*
   * Load when page opens
   */
  useEffect(() => {
    const token = localStorage.getItem("access_token");

    if (!token) {
      navigate("/login");
      return;
    }

    loadHistory();
  }, [navigate]);

  /*
   * Format date
   */
  const formatDate = (dateString) => {
    if (!dateString) {
      return "";
    }

    try {
      return new Date(dateString).toLocaleString([], {
        dateStyle: "medium",
        timeStyle: "short",
      });
    } catch {
      return "";
    }
  };

  /*
   * Go back to chat
   */
  const goToChat = () => {
    navigate("/chat");
  };

  /*
   * Open / close delete modal
   */
  const openDeleteModal = () => {
    setShowDeleteModal(true);
  };

  const closeDeleteModal = () => {
    if (deleteLoading) {
      return;
    }

    setShowDeleteModal(false);
  };

  /*
   * Delete all chat history
   */
  const deleteChatHistory = async () => {
    setDeleteLoading(true);
    setError("");

    try {
      await api.delete("/chat/delete");

      setMessages([]);
      setShowDeleteModal(false);
    } catch (err) {
      console.error("Delete chat history error:", err);

      if (err.response?.status === 401) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("token_type");

        navigate("/login");
        return;
      }

      setError(
        err.response?.data?.detail ||
          "Unable to delete chat history."
      );

      setShowDeleteModal(false);
    } finally {
      setDeleteLoading(false);
    }
  };

  return (
    <main className="history-page">
      {/* =====================================================
          HEADER
      ====================================================== */}
      <header className="history-header">
        <button
          className="back-button"
          onClick={goToChat}
          aria-label="Back to chat"
        >
          ←
        </button>

        <div className="history-header-text">
          <span className="history-eyebrow">
            SHOPASSIST
          </span>

          <h1>Chat History</h1>

          <p>Your previous shopping conversations</p>
        </div>

        {!loading && messages.length > 0 && (
          <span className="history-count">
            {messages.length}{" "}
            {messages.length === 1
              ? "message"
              : "messages"}
          </span>
        )}
      </header>

      {/* =====================================================
          CONTENT
      ====================================================== */}
      <section className="history-container">
        {loading && (
          <div className="history-loading-page">
            <span className="loading-spinner"></span>
            Loading your conversations...
          </div>
        )}

        {error && !loading && (
          <div className="history-error">
            <span className="history-error-icon">
              !
            </span>

            <div>
              <strong>Could not load history</strong>
              <p>{error}</p>
            </div>
          </div>
        )}

        {!loading &&
          !error &&
          messages.length === 0 && (
            <div className="empty-history">
              <div className="empty-history-icon">
                <span>✦</span>
              </div>

              <span className="empty-history-label">
                SHOPPING CONVERSATIONS
              </span>

              <h2>No conversations yet</h2>

              <p>
                Your product searches, comparisons, and
                recommendations will appear here.
              </p>

              <button
                className="start-chat-button"
                onClick={goToChat}
              >
                <span>✦</span>
                Start shopping
                <span className="button-arrow">→</span>
              </button>
            </div>
          )}

        {!loading &&
          !error &&
          messages.length > 0 && (
            <div className="history-list">
              <div className="history-list-title">
                <span>Conversation activity</span>
                <span className="history-list-line"></span>
              </div>

              {messages.map((message, index) => (
                <article
                  key={message.id ?? index}
                  className={`history-message ${
                    message.role
                  }`}
                >
                  <div className="history-avatar">
                    {message.role === "user" ? (
                      "You"
                    ) : (
                      "✦"
                    )}
                  </div>

                  <div className="history-content">
                    <div className="history-message-header">
                      <span className="history-role">
                        {message.role === "user"
                          ? "You"
                          : "ShopAssist"}
                      </span>

                      <span className="history-date">
                        {formatDate(message.created_at)}
                      </span>
                    </div>

                    <p>{message.content}</p>
                  </div>
                </article>
              ))}
            </div>
          )}
      </section>

      {/* =====================================================
          FOOTER
      ====================================================== */}
      <footer className="history-footer">
        <button
          className="back-to-chat"
          onClick={goToChat}
        >
          <span>←</span>
          Back to chat
        </button>

        {!loading && messages.length > 0 && (
          <button
            className="delete-history-button"
            onClick={openDeleteModal}
          >
            <span>⌫</span>
            Clear history
          </button>
        )}
      </footer>

      {/* =====================================================
          DELETE CONFIRMATION MODAL
      ====================================================== */}
      {showDeleteModal && (
        <div
          className="delete-modal-overlay"
          onClick={closeDeleteModal}
        >
          <div
            className="delete-modal"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="delete-modal-icon">
              ⌫
            </div>

            <span className="modal-eyebrow">
              PERMANENT ACTION
            </span>

            <h2>Clear chat history?</h2>

            <p>
              This will permanently remove all your
              saved conversations and product searches.
            </p>

            <div className="delete-information">
              <span>✦</span>
              <p>
                This action cannot be undone.
              </p>
            </div>

            <div className="delete-modal-actions">
              <button
                className="cancel-delete-button"
                onClick={closeDeleteModal}
                disabled={deleteLoading}
              >
                Keep history
              </button>

              <button
                className="confirm-delete-button"
                onClick={deleteChatHistory}
                disabled={deleteLoading}
              >
                {deleteLoading
                  ? "Clearing..."
                  : "Clear history"}
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}

export default ChatHistory;