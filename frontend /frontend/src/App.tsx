import React, { useState, useEffect } from 'react';
import Login from './components/Login';
import Signup from './components/Signup';
import VoiceAssistant from './components/VoiceAssistant';
import { getAuth, onAuthStateChanged, type User } from 'firebase/auth';
import './App.css';
import { initializeApp } from 'firebase/app';

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

function App() {
  const [showLoginForms, setShowLoginForms] = useState(true);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [idToken, setIdToken] = useState<string | null>(null);
  const [userId, setUserId] = useState<string | null>(null);
  const [isLoadingAuth, setIsLoadingAuth] = useState(true);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      setIsLoadingAuth(true);
      if (user) {
        setCurrentUser(user);
        const token = await user.getIdToken();
        setIdToken(token);
        setUserId(user.uid);
        console.log("User is signed in from onAuthStateChanged, token set.");
      } else {
        setCurrentUser(null);
        setIdToken(null);
        setUserId(null);
        console.log("User is signed out from onAuthStateChanged.");
      }
      setIsLoadingAuth(false);
    });
    return () => unsubscribe();
  }, []);

  const handleLoginSuccess = (token: string, uid: string) => {
    setIdToken(token);
    setUserId(uid);
    console.log("Login successful via callback, token and UID set.");
  };

  const handleLogout = async () => {
    try {
      await auth.signOut();
      console.log("User signed out successfully.");
    } catch (error) {
      console.error("Logout error:", error);
    }
  };

  if (isLoadingAuth) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <h2>Loading...</h2>
      </div>
    );
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>Insta-Voice Assistant</h1>
      </header>
      <main>
        {currentUser && idToken && userId ? (
          <VoiceAssistant userId={userId} idToken={idToken} onLogout={handleLogout} />
        ) : (
          <>
            {showLoginForms ? (
              <Login onLoginSuccess={handleLoginSuccess} />
            ) : (
              <Signup />
            )}
            <div style={{ textAlign: 'center', marginTop: '20px' }}>
              <button 
                onClick={() => setShowLoginForms(!showLoginForms)} 
                style={{ 
                  padding: '10px 15px',
                  fontSize: '1em',
                  cursor: 'pointer',
                  backgroundColor: '#6c757d',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px'
                }}
              >
                {showLoginForms ? 'Need to create an account?' : 'Already have an account?'}
              </button>
            </div>
          </>
        )}
      </main>
      <footer>
        <p>&copy; 2024 Your Company</p>
      </footer>
    </div>
  );
}

export default App;
