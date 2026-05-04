import { useState, useRef, useCallback } from 'react';
import Webcam from 'react-webcam';
import { Camera, Upload, Eye, Leaf, AlertTriangle, ShieldAlert, HeartPulse, ScanLine, Activity } from 'lucide-react';
import './App.css';

function App() {
  const [language, setLanguage] = useState('en');
  const [selectedImage, setSelectedImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [isCameraOpen, setIsCameraOpen] = useState(false);
  
  const webcamRef = useRef(null);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedImage(file);
      setPreview(URL.createObjectURL(file));
      setResult(null);
      setError(null);
      setIsCameraOpen(false);
    }
  };

  const dataURLtoFile = (dataurl, filename) => {
    var arr = dataurl.split(','), mime = arr[0].match(/:(.*?);/)[1],
        bstr = atob(arr[1]), n = bstr.length, u8arr = new Uint8Array(n);
    while(n--){
        u8arr[n] = bstr.charCodeAt(n);
    }
    return new File([u8arr], filename, {type:mime});
  }

  const capturePhoto = useCallback(() => {
    const imageSrc = webcamRef.current.getScreenshot();
    if (imageSrc) {
      const file = dataURLtoFile(imageSrc, 'camera-capture.jpeg');
      setSelectedImage(file);
      setPreview(imageSrc);
      setResult(null);
      setError(null);
      setIsCameraOpen(false);
    }
  }, [webcamRef]);

  const handleAnalyze = async () => {
    if (!selectedImage) return;
    
    setLoading(true);
    setError(null);
    
    const formData = new FormData();
    formData.append('file', selectedImage);
    formData.append('language', language);

    try {
      const apiUrl = import.meta.env.VITE_API_URL ? import.meta.env.VITE_API_URL : (import.meta.env.DEV ? 'http://localhost:8000' : '');
      const response = await fetch(`${apiUrl}/predict`, {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error('Analysis failed');
      }
      
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const translations = {
    en: {
      title: 'Agro Smart EYE',
      subtitle: 'AI-Powered Plant Health Diagnostics',
      upload: 'Upload Leaf Photo',
      camera: 'Use Camera',
      analyze: 'Run Diagnostics',
      analyzing: 'Analyzing...',
      disease: 'Detected Condition',
      confidence: 'Confidence',
      causes: 'Probable Causes',
      effects: 'Impact & Symptoms',
      suggestions: 'Recommended Treatment'
    },
    hi: {
      title: 'Agro Smart EYE',
      subtitle: 'एआई-संचालित पौधे स्वास्थ्य निदान',
      upload: 'फोटो अपलोड करें',
      camera: 'कैमरा उपयोग करें',
      analyze: 'निदान चलाएं',
      analyzing: 'विश्लेषण कर रहा है...',
      disease: 'पाया गया रोग',
      confidence: 'सटीकता',
      causes: 'संभावित कारण',
      effects: 'लक्षण और प्रभाव',
      suggestions: 'उपचार और देखभाल'
    }
  };

  const t = translations[language];

  return (
    <div className="app-container">
      {/* Sidebar for Desktop, Top Navbar for Mobile */}
      <nav className="navbar">
        <div className="logo-section">
          <div className="logo-icon-wrapper">
            <Eye className="logo-icon eye-icon" size={28} />
            <Leaf className="logo-icon leaf-icon" size={24} />
          </div>
          <div className="logo-text">
            <h1>{t.title}</h1>
          </div>
        </div>
        <div className="language-selector">
          <button 
            className={language === 'en' ? 'active' : ''} 
            onClick={() => setLanguage('en')}
          >
            EN
          </button>
          <button 
            className={language === 'hi' ? 'active' : ''} 
            onClick={() => setLanguage('hi')}
          >
            HI
          </button>
        </div>
      </nav>

      <main className="main-content">
        <div className="header-text">
          <h2>{t.subtitle}</h2>
        </div>

        <div className="input-section spotify-card">
          <div className="action-tabs">
            <button 
              className={`tab-btn ${!isCameraOpen ? 'active' : ''}`}
              onClick={() => setIsCameraOpen(false)}
            >
              <Upload size={18} /> {t.upload}
            </button>
            <button 
              className={`tab-btn ${isCameraOpen ? 'active' : ''}`}
              onClick={() => {
                setIsCameraOpen(true);
                setPreview(null);
                setSelectedImage(null);
                setResult(null);
              }}
            >
              <Camera size={18} /> {t.camera}
            </button>
          </div>

          <div className="media-container">
            {isCameraOpen ? (
              <div className="camera-wrapper">
                <Webcam
                  audio={false}
                  ref={webcamRef}
                  screenshotFormat="image/jpeg"
                  className="webcam-view"
                  videoConstraints={{ facingMode: "environment" }}
                />
                <button className="capture-btn" onClick={capturePhoto}>
                  <ScanLine size={20} /> Capture
                </button>
              </div>
            ) : (
              <label className="upload-area">
                <input 
                  type="file" 
                  accept="image/*" 
                  onChange={handleImageChange} 
                  className="hidden-input"
                />
                {preview ? (
                  <div className="preview-wrapper">
                    <img src={preview} alt="Preview" className="image-preview" />
                    <div className="preview-overlay">
                      <p>Click to change image</p>
                    </div>
                  </div>
                ) : (
                  <div className="upload-placeholder">
                    <Upload size={48} className="upload-icon" />
                    <span>{t.upload}</span>
                  </div>
                )}
              </label>
            )}
          </div>
          
          <button 
            className={`analyze-btn ${!selectedImage || loading ? 'disabled' : ''}`}
            onClick={handleAnalyze}
            disabled={!selectedImage || loading}
          >
            {loading ? (
              <><Activity className="spin" size={20} /> {t.analyzing}</>
            ) : (
              <>{t.analyze}</>
            )}
          </button>
          
          {error && <div className="error-msg"><AlertTriangle size={18} /> {error}</div>}
        </div>

        {result && (
          <div className="results-section spotify-card slide-up">
            <div className="result-hero">
              <div className="result-title-group">
                <span className="subtitle">{t.disease}</span>
                <h2 className="disease-name">{result.disease.replace(/___/g, ' - ').replace(/_/g, ' ')}</h2>
              </div>
              <div className="confidence-pill">
                {t.confidence}: {Math.round(result.confidence * 100)}%
              </div>
            </div>

            <div className="guidance-grid">
              <div className="guidance-card cause-card">
                <div className="card-header">
                  <AlertTriangle className="card-icon" size={20} />
                  <h3>{t.causes}</h3>
                </div>
                <ul>
                  {result.guidance.causes.map((cause, idx) => (
                    <li key={idx}>{cause}</li>
                  ))}
                </ul>
              </div>

              <div className="guidance-card effect-card">
                <div className="card-header">
                  <ShieldAlert className="card-icon" size={20} />
                  <h3>{t.effects}</h3>
                </div>
                <ul>
                  {result.guidance.effects.map((effect, idx) => (
                    <li key={idx}>{effect}</li>
                  ))}
                </ul>
              </div>

              <div className="guidance-card suggestion-card full-width">
                <div className="card-header">
                  <HeartPulse className="card-icon" size={20} />
                  <h3>{t.suggestions}</h3>
                </div>
                <ul>
                  {result.guidance.suggestions.map((suggestion, idx) => (
                    <li key={idx}>{suggestion}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>powered by <span className="highlight-text">PEAKS INTELLIGENCE</span></p>
      </footer>
    </div>
  );
}

export default App;
