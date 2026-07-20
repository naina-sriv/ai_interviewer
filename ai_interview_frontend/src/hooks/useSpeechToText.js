import { useEffect, useRef } from "react";

export const useSpeechToText = (onSilence) => {
  const recognitionRef = useRef(null);
  const slienceTimeRef = useRef(null);
  const onSlienceRef = useRef(onSilence);
  const transcriptRef = useRef("");
  const interimRef = useRef("");
  const isListeningRef = useRef(false);

  useEffect(() => {
    onSlienceRef.current = onSilence;
  }, [onSilence]);

  const startListening = () => {
    // Clear previous transcript across different questions
    transcriptRef.current = "";
    interimRef.current = "";
    isListeningRef.current = true;

    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      console.error("SpeechRecognition is not supported");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.lang = "en-US";
    recognition.interimResults = true;

    recognition.onresult = (event) => {
      let currentFinal = "";
      let currentInterim = "";

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        const text = result[0].transcript;

        if (result.isFinal) {
          currentFinal += text;
        } else {
          currentInterim += text;
        }
      }

      if (currentFinal) {
        transcriptRef.current = (transcriptRef.current + " " + currentFinal).trim();
      }
      interimRef.current = currentInterim;

      if (currentFinal || currentInterim) {
        resetSilenceTimer();
      }
    };

    recognition.onerror = (error) => {
      console.error("SpeechRecognition error", error);
    };

    recognition.onend = () => {
      // Chrome often stops listening automatically after a pause.
      // If we haven't manually stopped it, restart it automatically!
      if (isListeningRef.current) {
        try {
          recognition.start();
        } catch (e) {
          console.error("Failed to restart recognition", e);
        }
      }
    };

    try {
      recognition.start();
      recognitionRef.current = recognition;
    } catch (e) {
      console.error("Failed to start recognition", e);
    }
  };

  const resetSilenceTimer = () => {
    clearTimeout(slienceTimeRef.current);

    slienceTimeRef.current = setTimeout(() => {
      // Use both final and interim text in case the last word wasn't marked final
      const fullText = (transcriptRef.current + " " + interimRef.current).trim();
      onSlienceRef.current(fullText);
    }, 3000);
  };

  const stopListening = () => {
    isListeningRef.current = false;
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    clearTimeout(slienceTimeRef.current);
  };

  return {
    stopListening,
    resetSilenceTimer,
    startListening,
  };
};
