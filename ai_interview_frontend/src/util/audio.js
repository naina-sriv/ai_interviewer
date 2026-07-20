// Cached voice reference
let selectedVoice = null;

const getHumanVoice = () => {
  if (selectedVoice) return selectedVoice;

  const voices = window.speechSynthesis.getVoices();

  // Priority list: most natural-sounding voices first
  const preferredVoices = [
    // Google's natural voices (Chrome)
    "Google UK English Female",
    "Google UK English Male",
    "Google US English",
    // Microsoft natural voices (Edge)
    "Microsoft Aria Online (Natural)",
    "Microsoft Jenny Online (Natural)",
    "Microsoft Guy Online (Natural)",
    "Microsoft Aria",
    "Microsoft Jenny",
    // macOS natural voices
    "Samantha",
    "Karen",
    "Daniel",
    // Fallback patterns
    "English (United Kingdom)",
    "English (United States)",
  ];

  // Try to find a preferred voice
  for (const name of preferredVoices) {
    const voice = voices.find((v) =>
      v.name.toLowerCase().includes(name.toLowerCase())
    );
    if (voice) {
      selectedVoice = voice;
      console.log(`Selected voice: ${voice.name}`);
      return selectedVoice;
    }
  }

  // Fallback: pick any English voice
  const englishVoice = voices.find((v) => v.lang.startsWith("en"));
  if (englishVoice) {
    selectedVoice = englishVoice;
    console.log(`Fallback voice: ${englishVoice.name}`);
    return selectedVoice;
  }

  return null;
};

// Pre-load voices (they load async in some browsers)
if (window.speechSynthesis) {
  window.speechSynthesis.onvoiceschanged = () => {
    getHumanVoice();
  };
  // Try immediately too (voices may already be loaded)
  getHumanVoice();
}

export const playAudio = (text, onEnd) => {
  if (!window.speechSynthesis) {
    console.error("Speech Synthesis is not supported in this browser");
    onEnd?.();
    return;
  }

  // Cancel any ongoing speech first
  window.speechSynthesis.cancel();

  // Small delay to let cancel() complete (fixes Chrome bug)
  setTimeout(() => {
    let utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "en-US";
    utterance.rate = 0.95;
    utterance.volume = 1;
    utterance.pitch = 1.05;

    // Use the best available human-like voice
    const voice = getHumanVoice();
    if (voice) {
      utterance.voice = voice;
    }

    utterance.onend = () => {
      onEnd?.();
    };

    utterance.onerror = (e) => {
      console.error("Speech synthesis error:", e);
      onEnd?.();
    };

    window.speechSynthesis.speak(utterance);

    // Chrome bug: long text gets cut off after ~15s. This keepalive prevents it.
    const keepAlive = setInterval(() => {
      if (!window.speechSynthesis.speaking) {
        clearInterval(keepAlive);
        return;
      }
      window.speechSynthesis.pause();
      window.speechSynthesis.resume();
    }, 10000);
  }, 100);
};
