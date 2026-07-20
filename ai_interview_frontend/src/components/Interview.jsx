import "../assets/css/Interview.css"
import speaking from "../assets/images/speaking.gif";
import listening from "../assets/images/listening.gif";
import { APP_CONSTANT } from "../util/constant";

const Interview = ({ skipQuestion, endInterview, state }) => {
    return (
    <div className="interview-container glass-panel">
        {/* Col1: AI Bot */}
        <div className="interview-column">
            <div className="participant-section">
                <h2>AI Interviewer</h2>
                <div className={`avatar-ring ${state === APP_CONSTANT.ASKING ? 'active' : ''}`}>
                    {state === APP_CONSTANT.ASKING ? (
                        <img src={speaking} alt="Bot Speaking..." />
                    ) : (
                        <div className="gif-placeholder-gray"></div>
                    )}
                </div>
            </div>
        </div>

        {/* Col2: Buttons */}
        <div className="interview-column controls-section">
            <button onClick={skipQuestion} className="control-btn skip-btn">Skip Question</button>
            <button onClick={endInterview} className="control-btn end-btn">End Interview</button>
        </div>

        {/* Col3: Your Mic Image */}
        <div className="interview-column">
            <div className="participant-section">
                <h2>You</h2>
                <div className={`avatar-ring ${state === APP_CONSTANT.LISTENING ? 'active' : ''}`}>
                    {state === APP_CONSTANT.LISTENING ? (
                        <img src={listening} alt="You are Speaking..." />
                    ) : (
                        <div className="gif-placeholder-gray"></div>
                    )}
                </div>
            </div>
        </div>
    </div>
    );
}

export default Interview