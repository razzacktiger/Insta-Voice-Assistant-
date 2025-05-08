import React from 'react';

interface VoiceAssistantProps {
  userId: string;
  idToken: string; // You might need this to initialize LiveKit or other services
  onLogout: () => void;
}

const VoiceAssistant: React.FC<VoiceAssistantProps> = ({ userId, idToken, onLogout }) => {
  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h2>Welcome to the Voice Assistant!</h2>
      <p>Your User ID: {userId}</p>
      {/* <p>Your ID Token: {idToken} </p> */}
      {/* Displaying the full token can be very long and not usually necessary for the user to see */}
      <p>Voice assistant functionality will go here.</p>
      <button 
        onClick={onLogout} 
        style={{
          marginTop: '20px', 
          padding: '10px 15px', 
          backgroundColor: '#dc3545', 
          color: 'white', 
          border: 'none', 
          borderRadius: '4px' 
        }}
      >
        Logout
      </button>
    </div>
  );
};

export default VoiceAssistant; 