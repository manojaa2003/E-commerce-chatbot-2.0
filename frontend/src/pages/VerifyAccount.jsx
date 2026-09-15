import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../services/api";
import "./VerifyAccount.css";

function VerifyAccount() {

    const navigate = useNavigate();

    const [email, setEmail] = useState("");
    const [otp, setOtp] = useState("");

    const [loading, setLoading] = useState(false);
    const [resending, setResending] = useState(false);

    const [message, setMessage] = useState("");
    const [error, setError] = useState("");

    /*
     * Get email from sessionStorage
     * when the page loads.
     */
    useEffect(() => {

        const storedEmail =
            sessionStorage.getItem(
                "verification_email"
            );

        if (!storedEmail) {

            /*
             * No registration in progress.
             * Send user back to register.
             */
            navigate("/register");

            return;
        }

        setEmail(storedEmail);

    }, [navigate]);


    // =========================================
    // VERIFY OTP
    // =========================================

    const handleVerify = async (event) => {

        event.preventDefault();

        setLoading(true);
        setError("");
        setMessage("");

        try {

            const response = await api.post(
                "/users/verify-account",
                {
                    email_id: email,
                    otp: otp
                }
            );

            console.log(
                "Account verification response:",
                response.data
            );

            setMessage(
                "Account verified successfully. Redirecting to login..."
            );

            /*
             * Verification is complete.
             * Remove temporary email.
             */
            sessionStorage.removeItem(
                "verification_email"
            );

            setOtp("");

            /*
             * Go to login after successful verification.
             */
            setTimeout(() => {

                navigate("/login");

            }, 1500);

        } catch (error) {

            console.error(
                "Account verification error:",
                error
            );

            if (error.response) {

                setError(
                    error.response.data?.detail ||
                    "Invalid OTP."
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


    // =========================================
    // RESEND OTP
    // =========================================

    const handleResendOtp = async () => {

        setResending(true);
        setError("");
        setMessage("");

        try {

            const response = await api.post(
                "/users/resend-otp",
                {
                    email_id: email
                }
            );

            console.log(
                "Resend OTP response:",
                response.data
            );

            setMessage(
                "A new OTP has been sent to your email."
            );

            setOtp("");

        } catch (error) {

            console.error(
                "Resend OTP error:",
                error
            );

            if (error.response) {

                setError(
                    error.response.data?.detail ||
                    "Unable to resend OTP."
                );

            } else {

                setError(
                    "Unable to connect to the server."
                );
            }

        } finally {

            setResending(false);
        }
    };


    return (
        <div className="auth-container">

            <h1>Verify Your Account</h1>

            <p>
                We sent a verification OTP to:
            </p>

            <strong>
                {email}
            </strong>


            {/* ================================= */}
            {/* OTP FORM */}
            {/* ================================= */}

            <form onSubmit={handleVerify}>

                <div>

                    <label>
                        Enter OTP
                    </label>

                    <input
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
                        required
                    />

                </div>


                <button
                    type="submit"
                    disabled={
                        loading ||
                        otp.length !== 6
                    }
                >
                    {loading
                        ? "Verifying..."
                        : "Verify Account"}
                </button>

            </form>


            {/* ================================= */}
            {/* RESEND */}
            {/* ================================= */}

            <button
                type="button"
                onClick={handleResendOtp}
                disabled={resending}
            >
                {resending
                    ? "Sending..."
                    : "Resend OTP"}
            </button>


            {/* ================================= */}
            {/* SUCCESS */}
            {/* ================================= */}

            {message && (
                <p className="success">
                    {message}
                </p>
            )}


            {/* ================================= */}
            {/* ERROR */}
            {/* ================================= */}

            {error && (
                <p className="error">
                    {error}
                </p>
            )}


            {/* ================================= */}
            {/* LOGIN */}
            {/* ================================= */}

            <p>
                Already verified?{" "}
                <Link to="/login">
                    Login
                </Link>
            </p>

        </div>
    );
}

export default VerifyAccount;