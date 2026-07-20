import { useState } from "react";
import "../assets/css/ApiKeyModal.css";

const ApiKeyModal = ({ onSave }) => {
    const [apiKey, setApiKey] = useState("");

    const handleSubmit = (e) => {
        e.preventDefault();
        if (apiKey.trim()) {
            onSave(apiKey.trim());
        }
    };

    return (
        <div className="modal-overlay">
            <div className="api-key-modal glass-panel">
                <h2>Welcome to Smart AI Interviewer</h2>
                <p>Please enter your Google Gemini API Key to continue. Your key is stored locally in your browser and is only sent directly to our backend for processing your interview.</p>
                <form onSubmit={handleSubmit} className="api-key-form">
                    <input
                        type="password"
                        placeholder="GEMINI_API_KEY"
                        value={apiKey}
                        onChange={(e) => setApiKey(e.target.value)}
                        required
                    />
                    <button type="submit" className="glow-btn">Save Key & Start</button>
                </form>
            </div>
        </div>
    );
};

export default ApiKeyModal;
