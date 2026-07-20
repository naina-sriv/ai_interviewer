import { useState } from "react";
import "../assets/css/StartInterview.css"
import { generateQuestionsAPI, startInterviewAPI } from "../services/interview";


const ALLOWED_FILE = ["application/pdf"];
const MAX_FILE_SIZE = 5 * 1024 * 1024;

const StartInterview = ({onClick}) => {
    const [jobTitle, setJobTitle] = useState("");
    const [jobDescription, setJobDescription] = useState("");
    const [resume, setResume] = useState(null);
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleFileUpload = (e) => {
        try {
            const file = e.target.files[0];

            if(!file) {
                return;
            }

            console.log(file.type)

            if(!ALLOWED_FILE.includes(file.type)) {
                setError("Only PDF allowed");
                return;
            }

            if(file.size > MAX_FILE_SIZE) {
                setError("File size mus be under 5mb.");
                return;
            }

            setError("");
            setResume(file);
        } catch (error) {
            console.error("Error: ", error);
        }
    }

    const handleFormSubmit = async (e) => {
        e.preventDefault();

        if(!jobTitle || !jobDescription || !resume) {
            setError("All fields are required!!!");
            return;
        }

        setLoading(true);
        setError("");

        try {

            const formData = new FormData();
            formData.append("job_title", jobTitle);
            formData.append("job_description", jobDescription);
            formData.append("resume", resume);

            // generate question endpoint
            const response = await generateQuestionsAPI(formData);

            // Start interview endpoint
            const data = await startInterviewAPI(response.session_id);

            onClick(data, response.session_id);


        } catch (error) {
            console.error("Error: ", error);
            setError("Something went wrong. Please try again in a minute.");
        } finally {
             setLoading(false);
        }
    }

    return (
    <div className="start-interview-container">
        <form className="start-interview-form glass-panel" onSubmit={handleFormSubmit}>
            <h1>AI Interview</h1>

            { error && <p className="error-message">{error}</p> }

            <div className="form-group">
                <label>Job Title</label>
                <input 
                    type="text"
                    placeholder="Enter Job Title"
                    required
                    value={jobTitle}
                    onChange={e => setJobTitle(e.target.value)}
                />
            </div>

             <div className="form-group">
                <label>Job Description</label>
                <textarea 
                    placeholder="Enter Job Description"
                    required
                    value={jobDescription}
                    onChange={e => setJobDescription(e.target.value)}
                />
            </div>

            <div className="form-group">
                <label>Resume (PDF)</label>
                <div className="file-upload-wrapper">
                    <div className="file-upload-custom">
                        <span className="file-name">{resume ? resume.name : "Click or Drag to Upload PDF"}</span>
                    </div>
                    <input
                        type="file"
                        accept=".pdf"
                        required
                        onChange={handleFileUpload}
                    />
                </div>
            </div>

            <div className="submit-container">
                <button type="submit" className="glow-btn" disabled={loading}>
                    { loading ? "Initializing..." : "Start Session"}
                </button>
            </div>
        </form>
    </div>
    );
}

export default StartInterview