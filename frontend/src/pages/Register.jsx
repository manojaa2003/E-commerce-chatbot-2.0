import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../services/api";
import "./Register.css";

function Register() {
    const navigate = useNavigate();

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [message, setMessage] = useState("");

    const handleRegister = async (event) => {
        event.preventDefault();

        setLoading(true);
        setError("");
        setMessage("");

        try {
            const response = await api.post("/users", {
                email_id: email,
                password: password,
            });

            console.log("Registration response:", response.data);

            setMessage("OTP has been sent to your email.");

            sessionStorage.setItem(
                "verification_email",
                email
            );

            navigate("/verify-account");
        } catch (error) {
            console.error("Registration error:", error);

            if (error.response) {
                setError(
                    error.response.data?.detail ||
                    "Unable to create account."
                );
            } else {
                setError("Unable to connect to the server.");
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <main className="register-page">
            <section
                className="register-card"
                aria-labelledby="register-title"
            >
                <header className="register-header">
                    <div
                        className="register-logo"
                        aria-hidden="true"
                    >
                        ✦
                    </div>

                    <h1 id="register-title">
                        Create your account
                    </h1>

                    <p>
                        Join ShopAssist and get started today
                    </p>
                </header>

                <form
                    className="register-form"
                    onSubmit={handleRegister}
                    noValidate
                >
                    <div className="register-form-group">
                        <label htmlFor="register-email">
                            Email address
                        </label>

                        <input
                            id="register-email"
                            name="email"
                            type="email"
                            value={email}
                            onChange={(event) =>
                                setEmail(event.target.value)
                            }
                            placeholder="name@company.com"
                            autoComplete="email"
                            inputMode="email"
                            required
                        />
                    </div>

                    <div className="register-form-group">
                        <label htmlFor="register-password">
                            Password
                        </label>

                        <div className="register-password-wrapper">
                            <input
                                id="register-password"
                                name="password"
                                className="register-password-input"
                                type={
                                    showPassword
                                        ? "text"
                                        : "password"
                                }
                                value={password}
                                onChange={(event) =>
                                    setPassword(event.target.value)
                                }
                                placeholder="Create a password"
                                autoComplete="new-password"
                                minLength={8}
                                required
                            />

                            <button
                                type="button"
                                className="register-toggle-password"
                                onClick={() =>
                                    setShowPassword(
                                        (current) => !current
                                    )
                                }
                                aria-label={
                                    showPassword
                                        ? "Hide password"
                                        : "Show password"
                                }
                                aria-pressed={showPassword}
                                aria-controls="register-password"
                            >
                                {showPassword ? "Hide" : "Show"}
                            </button>
                        </div>

                        <span className="password-hint">
                            Use at least 8 characters.
                        </span>
                    </div>

                    {message && (
                        <p className="register-message">
                            {message}
                        </p>
                    )}

                    {error && (
                        <p
                            className="register-error"
                            role="alert"
                        >
                            {error}
                        </p>
                    )}

                    <button
                        type="submit"
                        className="register-button"
                        disabled={loading}
                    >
                        {loading ? (
                            <>
                                <span
                                    className="register-spinner"
                                    aria-hidden="true"
                                />
                                Creating account...
                            </>
                        ) : (
                            "Create Account"
                        )}
                    </button>
                </form>

                <p className="register-footer">
                    Already have an account?{" "}
                    <Link
                        to="/login"
                        className="register-link"
                    >
                        Login
                    </Link>
                </p>
            </section>
        </main>
    );
}

export default Register;