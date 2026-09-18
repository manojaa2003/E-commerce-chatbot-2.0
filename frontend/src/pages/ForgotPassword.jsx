import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../services/api";
import "./ForgotPassword.css";

function ForgotPassword() {
    const navigate = useNavigate();

    const [email, setEmail] = useState("");
    const [otp, setOtp] = useState("");
    const [newPassword, setNewPassword] = useState("");

    const [otpSent, setOtpSent] = useState(false);
    const [showPassword, setShowPassword] = useState(false);

    const [loading, setLoading] = useState(false);

    const [message, setMessage] = useState("");
    const [error, setError] = useState("");

    // -----------------------------------------
    // STEP 1: REQUEST OTP
    // -----------------------------------------

    const handleForgotPassword = async (event) => {
        event.preventDefault();

        setLoading(true);
        setMessage("");
        setError("");

        try {
            const response = await api.post(
                "/users/forgot-password",
                {
                    email_id: email,
                }
            );

            console.log(
                "Forgot password response:",
                response.data
            );

            setMessage(
                "OTP has been sent to your registered email."
            );

            setOtpSent(true);
        } catch (error) {
            console.error(
                "Forgot password error:",
                error
            );

            if (error.response) {
                setError(
                    error.response.data?.detail ||
                    "Unable to send OTP."
                );
            } else {
                setError(
                    "Unable to connect to the server."
                );
            }
        } finally {
            setLoading(false);
        }
    };

    // -----------------------------------------
    // STEP 2: UPDATE PASSWORD
    // -----------------------------------------

    const handleUpdatePassword = async (event) => {
        event.preventDefault();

        setLoading(true);
        setMessage("");
        setError("");

        try {
            const response = await api.post(
                "/users/update-password",
                {
                    email_id: email,
                    otp: otp,
                    new_password: newPassword,
                }
            );

            console.log(
                "Update password response:",
                response.data
            );

            setMessage(
                "Password updated successfully. Redirecting to login..."
            );

            // Clear sensitive fields
            setOtp("");
            setNewPassword("");
            setShowPassword(false);

            setTimeout(() => {
                navigate("/login");
            }, 1500);
        } catch (error) {
            console.error(
                "Update password error:",
                error
            );

            if (error.response) {
                setError(
                    error.response.data?.detail ||
                    "Unable to update password."
                );
            } else {
                setError(
                    "Unable to connect to the server."
                );
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <main className="forgot-password-container">
            <section
                className="forgot-password-card"
                aria-labelledby="forgot-password-title"
            >
                <header className="forgot-password-header">
                    <div
                        className="forgot-password-logo"
                        aria-hidden="true"
                    >
                        ↻
                    </div>

                    <h1 id="forgot-password-title">
                        Forgot Password
                    </h1>

                    <p>
                        Reset your ShopAssist account password
                    </p>
                </header>

                {!otpSent && (
                    <>
                        <form
                            className="forgot-password-form"
                            onSubmit={handleForgotPassword}
                            noValidate
                        >
                            <div className="forgot-form-group">
                                <label htmlFor="forgot-email">
                                    Email address
                                </label>

                                <input
                                    id="forgot-email"
                                    name="email"
                                    type="email"
                                    value={email}
                                    onChange={(event) =>
                                        setEmail(
                                            event.target.value
                                        )
                                    }
                                    placeholder="name@company.com"
                                    autoComplete="email"
                                    inputMode="email"
                                    required
                                />
                            </div>

                            <button
                                type="submit"
                                className="forgot-action-button"
                                disabled={loading}
                            >
                                {loading ? (
                                    <>
                                        <span className="forgot-spinner" aria-hidden="true" />
                                        Sending OTP...
                                    </>
                                ) : (
                                    "Send OTP"
                                )}
                            </button>
                        </form>

                        <p className="forgot-password-footer">
                            Remember your password?{" "}
                            <Link to="/login">
                                Login
                            </Link>
                        </p>
                    </>
                )}

                {otpSent && (
                    <>
                        <form
                            className="forgot-password-form"
                            onSubmit={handleUpdatePassword}
                            noValidate
                        >
                            <div className="forgot-form-group">
                                <label htmlFor="forgot-confirm-email">
                                    Email address
                                </label>

                                <input
                                    id="forgot-confirm-email"
                                    type="email"
                                    value={email}
                                    disabled
                                />
                            </div>

                            <div className="forgot-form-group">
                                <label htmlFor="forgot-otp">
                                    Verification OTP
                                </label>

                                <input
                                    id="forgot-otp"
                                    name="otp"
                                    type="text"
                                    value={otp}
                                    onChange={(event) =>
                                        setOtp(
                                            event.target.value
                                        )
                                    }
                                    placeholder="Enter 6-digit OTP"
                                    maxLength={6}
                                    inputMode="numeric"
                                    pattern="[0-9]{6}"
                                    autoComplete="one-time-code"
                                    required
                                />
                            </div>

                            <div className="forgot-form-group">
                                <label htmlFor="forgot-new-password">
                                    New password
                                </label>

                                <div className="forgot-password-wrapper">
                                    <input
                                        id="forgot-new-password"
                                        name="new_password"
                                        type={
                                            showPassword
                                                ? "text"
                                                : "password"
                                        }
                                        value={newPassword}
                                        onChange={(event) =>
                                            setNewPassword(
                                                event.target.value
                                            )
                                        }
                                        placeholder="Create a new password"
                                        autoComplete="new-password"
                                        minLength={8}
                                        required
                                    />

                                    <button
                                        type="button"
                                        className="forgot-toggle-password"
                                        onClick={() =>
                                            setShowPassword(
                                                (current) =>
                                                    !current
                                            )
                                        }
                                        aria-label={
                                            showPassword
                                                ? "Hide password"
                                                : "Show password"
                                        }
                                        aria-pressed={showPassword}
                                        aria-controls="forgot-new-password"
                                    >
                                        {showPassword
                                            ? "Hide"
                                            : "Show"}
                                    </button>
                                </div>

                                <span className="forgot-password-hint">
                                    Use at least 8 characters.
                                </span>
                            </div>

                            <button
                                type="submit"
                                className="forgot-action-button"
                                disabled={loading}
                            >
                                {loading ? (
                                    <>
                                        <span className="forgot-spinner" aria-hidden="true" />
                                        Updating...
                                    </>
                                ) : (
                                    "Update Password"
                                )}
                            </button>
                        </form>

                        <p className="forgot-password-footer">
                            Remember your password?{" "}
                            <Link to="/login">
                                Login
                            </Link>
                        </p>
                    </>
                )}

                {message && (
                    <p
                        className="forgot-success"
                        role="status"
                    >
                        {message}
                    </p>
                )}

                {error && (
                    <p
                        className="forgot-error"
                        role="alert"
                    >
                        {error}
                    </p>
                )}
            </section>
        </main>
    );
}

export default ForgotPassword;