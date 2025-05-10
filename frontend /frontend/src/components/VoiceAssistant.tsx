import React, { useState, useEffect, useRef } from 'react';
import { Room, RoomEvent, Track, type RemoteTrack, type RemoteTrackPublication } from 'livekit-client';

interface VoiceAssistantProps {
  userId: string;
  idToken: string;
  onLogout: () => void;
}

const VoiceAssistant: React.FC<VoiceAssistantProps> = ({ userId, idToken, onLogout }) => {
  const [livekitToken, setLivekitToken] = useState<string | null>(null);
  // Example room name, consider making this dynamic or configurable if needed
  const roomName = `assistant-room-${userId}`; 
  const [lkRoom, setLkRoom] = useState<Room | null>(null);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [agentAudioTrack, setAgentAudioTrack] = useState<RemoteTrack | null>(null);
  
  const [isFetchingToken, setIsFetchingToken] = useState<boolean>(false);
  const [fetchError, setFetchError] = useState<string | null>(null);
  
  const [isConnecting, setIsConnecting] = useState<boolean>(false);
  const [connectError, setConnectError] = useState<string | null>(null);

  const audioElRef = useRef<HTMLAudioElement>(null);

  const livekitWsUrl = import.meta.env.VITE_LIVEKIT_WS_URL;
  const tokenEndpointUrl = import.meta.env.VITE_TOKEN_ENDPOINT_URL;

  // Fetch LiveKit Token
  useEffect(() => {
    if (idToken && userId) {
      const fetchLkToken = async () => {
        setIsFetchingToken(true);
        setFetchError(null);
        if (!tokenEndpointUrl) {
          setFetchError("Token endpoint URL is not configured.");
          setIsFetchingToken(false);
          return;
        }
        try {
          console.log(`Fetching LiveKit token for room: ${roomName}, user: ${userId}`);
          const response = await fetch(tokenEndpointUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              firebase_id_token: idToken,
              room_name: roomName,
              participant_name: userId, // Or a display name if available
            }),
          });
          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Failed to fetch LiveKit token: ${response.statusText}`);
          }
          const data = await response.json();
          setLivekitToken(data.livekit_token);
          console.log("LiveKit token fetched successfully.");
        } catch (error: any) {
          console.error("Error fetching LiveKit token:", error);
          setFetchError(error.message || "An unknown error occurred while fetching the token.");
        } finally {
          setIsFetchingToken(false);
        }
      };
      fetchLkToken();
    }
  }, [idToken, userId, roomName, tokenEndpointUrl]);

  const connectToLiveKit = async () => {
    if (!livekitToken || !livekitWsUrl) {
      setConnectError("LiveKit token or WebSocket URL is missing.");
      return;
    }
    if (lkRoom?.state === 'connected' || isConnecting) {
        return;
    }

    setIsConnecting(true);
    setConnectError(null);
    console.log(`Attempting to connect to LiveKit room: ${roomName} at ${livekitWsUrl}`);

    const newRoom = new Room({
        // adaptiveStream: true, // Consider enabling for better performance in varying network conditions
        // dynacast: true,      // Consider enabling for better performance with multiple publishers
    });

    newRoom.on(RoomEvent.TrackSubscribed, (track: RemoteTrack, publication: RemoteTrackPublication, participant) => {
      console.log(`Track subscribed: ${track.sid}, kind: ${track.kind}, participant: ${participant.identity}`);
      // Assuming agent's identity is different from the current user's
      // and we are interested in the first audio track from a remote participant (the agent)
      if (track.kind === Track.Kind.Audio && participant.identity !== userId && !agentAudioTrack) {
        setAgentAudioTrack(track);
        console.log("Agent audio track set.");
      }
    });

    newRoom.on(RoomEvent.TrackUnsubscribed, (track: RemoteTrack, publication: RemoteTrackPublication, participant) => {
      console.log(`Track unsubscribed: ${track.sid}`);
      if (track === agentAudioTrack) {
        setAgentAudioTrack(null);
        console.log("Agent audio track unset.");
      }
    });

    newRoom.on(RoomEvent.Disconnected, (reason) => {
      console.log("Disconnected from LiveKit room:", reason);
      setIsConnected(false);
      setLkRoom(null);
      setAgentAudioTrack(null);
    });
    
    newRoom.on(RoomEvent.Reconnecting, () => {
        console.log("Reconnecting to LiveKit room...");
        setConnectError("Connection lost. Reconnecting...");
    });

    newRoom.on(RoomEvent.Reconnected, () => {
        console.log("Reconnected to LiveKit room.");
        setIsConnected(true);
        setConnectError(null); // Clear reconnecting message
    });


    try {
      await newRoom.connect(livekitWsUrl, livekitToken);
      console.log("Successfully connected to LiveKit room.");
      await newRoom.localParticipant.setMicrophoneEnabled(true);
      console.log("Microphone enabled.");
      setLkRoom(newRoom);
      setIsConnected(true);
    } catch (error: any) {
      console.error("Failed to connect to LiveKit:", error);
      setConnectError(error.message || "An unknown error occurred during connection.");
      setIsConnected(false);
    } finally {
      setIsConnecting(false);
    }
  };

  const disconnectFromLiveKit = async () => {
    if (lkRoom) {
      console.log("Disconnecting from LiveKit room...");
      await lkRoom.disconnect();
      // Event listeners should handle state cleanup (setIsConnected, setLkRoom, etc.)
    }
  };

  // Cleanup on component unmount
  useEffect(() => {
    return () => {
      if (lkRoom) {
        lkRoom.disconnect();
      }
    };
  }, [lkRoom]);

  // Attach/detach agent audio track to the <audio> element
  useEffect(() => {
    const audioElement = audioElRef.current;
    if (agentAudioTrack && audioElement) {
      console.log("Attaching agent audio track to element.");
      agentAudioTrack.attach(audioElement);
      return () => {
        console.log("Detaching agent audio track from element.");
        agentAudioTrack.detach(audioElement);
      };
    }
  }, [agentAudioTrack]);

  return (
    <div style={{ padding: '20px', textAlign: 'center', border: '1px solid #eee', margin: '20px', borderRadius: '8px' }}>
      <h2>Voice Assistant</h2>
      {/* <p>User ID: {userId}</p> */}

      {isFetchingToken && <p>Getting access token...</p>}
      {fetchError && <p style={{ color: 'red' }}>Token Error: {fetchError}</p>}

      {!isConnected && livekitToken && !isFetchingToken && (
        <button onClick={connectToLiveKit} disabled={isConnecting || !livekitWsUrl} style={buttonStyle}>
          {isConnecting ? 'Connecting...' : 'Connect to Voice Assistant'}
        </button>
      )}

      {isConnected && (
        <button onClick={disconnectFromLiveKit} disabled={isConnecting} style={{...buttonStyle, backgroundColor: '#ffc107'}}>
          Disconnect
        </button>
      )}
      
      {connectError && !isConnected && <p style={{ color: 'red', marginTop: '10px' }}>Connection Info: {connectError}</p>}
      {isConnected && <p style={{ color: 'green', marginTop: '10px' }}>Connected to Voice Assistant</p>}

      {/* Hidden audio player for agent's speech */}
      <audio ref={audioElRef} autoPlay style={{ display: 'none' }} />

      <button 
        onClick={onLogout} 
        style={{...buttonStyle, backgroundColor: '#dc3545', marginTop: '30px' }}
      >
        Logout
      </button>
    </div>
  );
};

const buttonStyle: React.CSSProperties = {
  marginTop: '20px', 
  padding: '12px 20px', 
  fontSize: '1em',
  backgroundColor: '#007bff', 
  color: 'white', 
  border: 'none', 
  borderRadius: '4px',
  cursor: 'pointer',
  margin: '5px'
};

export default VoiceAssistant; 