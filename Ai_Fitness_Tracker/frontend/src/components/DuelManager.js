import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../contexts/AppContext';
import DuelInviteModal from './DuelInviteModal';

const DuelManager = () => {
  const { duelInvite, acceptDuel, rejectDuel, duelActive, duelData } = useApp();
  const navigate = useNavigate();

  useEffect(() => {
    if (duelActive && duelData) {
      console.log('[DuelManager] Navigating to Duel:', duelData);
      navigate('/live-workout', {
        state: {
          duelMode: true,
          opponent: { username: duelData.opponent },
          routine: { 
            id: 'duel', 
            name: 'Duel Challenge', 
            exercises: [{ name: duelData.exercise, sets: 1, reps: 20 }] 
          }
        }
      });
    }
  }, [duelActive, duelData, navigate]);

  return (
    <DuelInviteModal 
      invite={duelInvite} 
      onAccept={acceptDuel} 
      onDecline={rejectDuel} 
    />
  );
};

export default DuelManager;
