import {
    BrowserRouter,
    Routes,
    Route,
    Navigate
} from "react-router-dom";

import Login from "./pages/Login";
import Register from "./pages/Register";
import VerifyAccount from "./pages/VerifyAccount";
import ForgotPassword from "./pages/ForgotPassword";
import Chat from "./pages/Chat";
import ChatHistory from "./pages/ChatHistory";

function App() {
    return (
        <BrowserRouter>

            <Routes>

                <Route
                    path="/"
                    element={<Navigate to="/login" />}
                />

                <Route
                    path="/login"
                    element={<Login />}
                />

                <Route
                    path="/register"
                    element={<Register />}
                />

                <Route
                    path="/verify-account"
                    element={<VerifyAccount />}
                />

                <Route
                    path="/forgot-password"
                    element={<ForgotPassword />}
                />

                <Route
                    path="/chat"
                    element={<Chat />}
                />

                <Route
                    path="/chat-history"
                    element={<ChatHistory />}
                />


            </Routes>

        </BrowserRouter>
    );
}

export default App;