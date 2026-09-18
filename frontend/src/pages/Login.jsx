import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../services/api";
import "./Login.css";

function Login() {
    const navigate = useNavigate();

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const [rememberMe, setRememberMe] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const handleLogin = async (event) => {
        event.preventDefault();

        setLoading(true);
        setError("");

        try {
            const formData = new URLSearchParams();
            formData.append("username", email);
            formData.append("password", password);

            const response = await api.post("/login", formData, {
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            });

            localStorage.setItem(
                "access_token",
                response.data.access_token
            );

            localStorage.setItem(
                "token_type",
                response.data.token_type || "bearer"
            );

            if (rememberMe) {
                localStorage.setItem("remember_me", "true");
            } else {
                localStorage.removeItem("remember_me");
            }

            navigate("/chat");
        } catch (err) {
            if (err.response) {
                setError(
                    err.response.data?.detail ||
                    "Invalid email or password."
                );
            } else {
                setError("Unable to connect to the server.");
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <main className="auth-page">
            <section className="auth-card" aria-labelledby="login-title">
                <div className="auth-header">
                    <div className="auth-logo" aria-hidden="true">
                        ✦
                    </div>

                    <h1 id="login-title">Welcome back</h1>

                    <p>
                        Sign in to continue to your account
                    </p>
                </div>

                <form
                    onSubmit={handleLogin}
                    className="auth-form"
                    noValidate
                >
                    <div className="form-group">
                        <label htmlFor="email">Email address</label>

                        <input
                            id="email"
                            name="email"
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="name@company.com"
                            autoComplete="username"
                            inputMode="email"
                            required
                        />
                    </div>

                    <div className="form-group">
                        <div className="password-label-row">
                            <label htmlFor="password">
                                Password
                            </label>

                            <Link
                                to="/forgot-password"
                                className="auth-link password-help-link"
                            >
                                Forgot password?
                            </Link>
                        </div>

                        <div className="input-wrapper">
                            <input
                                id="password"
                                name="password"
                                className="password-input"
                                type={
                                    showPassword
                                        ? "text"
                                        : "password"
                                }
                                value={password}
                                onChange={(e) =>
                                    setPassword(e.target.value)
                                }
                                placeholder="Enter your password"
                                autoComplete="current-password"
                                required
                            />

                            <button
                                type="button"
                                className="toggle-password"
                                onClick={() =>
                                    setShowPassword(!showPassword)
                                }
                                aria-label={
                                    showPassword
                                        ? "Hide password"
                                        : "Show password"
                                }
                                aria-pressed={showPassword}
                            >
                                {showPassword ? "Hide" : "Show"}
                            </button>
                        </div>
                    </div>

                    <div className="form-row">
                        <label className="checkbox-label">
                            <input
                                type="checkbox"
                                checked={rememberMe}
                                onChange={(e) =>
                                    setRememberMe(e.target.checked)
                                }
                            />

                            <span>Remember me</span>
                        </label>
                    </div>

                    {error && (
                        <p className="error" role="alert">
                            {error}
                        </p>
                    )}

                    <button
                        type="submit"
                        className="auth-button"
                        disabled={loading}
                    >
                        {loading ? (
                            <>
                                <span
                                    className="button-spinner"
                                    aria-hidden="true"
                                />
                                Logging in...
                            </>
                        ) : (
                            "Login"
                        )}
                    </button>
                </form>

                <p className="auth-footer">
                    Don&apos;t have an account?{" "}
                    <Link
                        to="/register"
                        className="auth-link"
                    >
                        Create account
                    </Link>
                </p>
            </section>
        </main>
    );
}

export default Login;