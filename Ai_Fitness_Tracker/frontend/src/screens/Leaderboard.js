import React, { useState, useEffect } from 'react';
import { 
  Trophy, 
  Zap, 
  Flame, 
  Swords, 
  Users, 
  Search, 
  UserPlus, 
  MessageCircle, 
  Check 
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import GlassCard from '../components/GlassCard';
import GradientButton from '../components/GradientButton';
import { useApi } from '../hooks/useApi';
import { useApp } from '../contexts/AppContext';
import { API_BASE_URL } from '../utils/api';

const Leaderboard = () => {
  const navigate = useNavigate();
  const { get, post } = useApi();
  const { sendDuelRequest } = useApp(); // Use sendDuelRequest from context
  const [filter, setFilter] = useState('global'); // 'global', 'friends', 'search'
  const [leaderboardData, setLeaderboardData] = useState([]);
  const [currentUser, setCurrentUser] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);

  useEffect(() => {
    if (filter !== 'search') {
      fetchLeaderboard();
    }
    fetchCurrentUser();
  }, [filter]);

  useEffect(() => {
    if (filter === 'search' && searchQuery.length > 2) {
      const delayDebounceFn = setTimeout(() => {
        handleSearch();
      }, 500);
      return () => clearTimeout(delayDebounceFn);
    }
  }, [searchQuery]);

  const handleSearch = async () => {
    setIsSearching(true);
    try {
      const data = await get(`/social/users/search?q=${searchQuery}`);
      if (data) {
        setSearchResults(data.map(item => ({
          ...item,
          score: item.points || 0,
          avatar: item.profile_image || '👤',
          level: item.level || 1,
          friendship_status: item.friendship_status
        })));
      }
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setIsSearching(false);
    }
  };

  const handleAddFriend = async (userId) => {
    try {
      await post(`/social/friend-request/${userId}`, {});
      alert('Friend request sent!');
      // Update local state
      const updateStatus = (u) => u.id === userId ? { ...u, friendship_status: 'pending' } : u;
      if (filter === 'search') {
        setSearchResults(prev => prev.map(updateStatus));
      } else {
        setLeaderboardData(prev => prev.map(updateStatus));
      }
    } catch (error) {
      console.error('Add friend failed:', error);
      alert(error.detail || 'Failed to send request');
    }
  };

  const handleAcceptFriend = async (userId) => {
    try {
      await post(`/social/friend-request/${userId}/accept`, {});
      alert('Friend request accepted!');
      const updateStatus = (u) => u.id === userId ? { ...u, friendship_status: 'accepted' } : u;
      if (filter === 'search') {
        setSearchResults(prev => prev.map(updateStatus));
      } else {
        setLeaderboardData(prev => prev.map(updateStatus));
      }
    } catch (error) {
      console.error('Accept friend failed:', error);
      alert(error.detail || 'Failed to accept request');
    }
  };

  const fetchLeaderboard = async () => {
    try {
      const endpoint = filter === 'global' ? '/social/leaderboard/global' : '/social/leaderboard/friends';
      const data = await get(endpoint);
      
      if (data && Array.isArray(data)) {
        const mappedData = data.map((item, index) => ({
          ...item,
          rank: item.rank || index + 1,
          score: item.points || item.score || 0,
          avatar: item.profile_image || item.avatar || '👤',
          isCurrentUser: item.id === currentUser?.id || item.friendship_status === 'self',
          username: item.username,
          streak: item.streak || 0,
          level: item.level || 1,
          friendship_status: item.friendship_status
        }));
        setLeaderboardData(mappedData);
      } else {
        setLeaderboardData([]);
      }
    } catch (error) {
      console.error('Fetch leaderboard failed:', error);
      setLeaderboardData([]);
    }
  };

  const fetchCurrentUser = async () => {
    try {
      const data = await get('/profile');
      if (data) {
        setCurrentUser(data);
      }
    } catch (error) {
      console.error('Fetch current user failed:', error);
    }
  };

  const getMockLeaderboard = () => [
    { rank: 1, username: 'FitKing', score: 9850, streak: 45, avatar: '👑', level: 25 },
    { rank: 2, username: 'IronWarrior', score: 9420, streak: 38, avatar: '⚔️', level: 23 },
    { rank: 3, username: 'FlexMaster', score: 9100, streak: 32, avatar: '💪', level: 22 },
    { rank: 4, username: 'BeastMode', score: 8750, streak: 28, avatar: '🦁', level: 21 },
    { rank: 5, username: 'FitWarrior', score: 8500, streak: 25, avatar: '🎯', level: 20, isCurrentUser: true },
    { rank: 6, username: 'GymRat', score: 8200, streak: 22, avatar: '🐀', level: 19 },
    { rank: 7, username: 'PowerLift', score: 7950, streak: 20, avatar: '🏋️', level: 18 },
    { rank: 8, username: 'CardioQueen', score: 7600, streak: 18, avatar: '👸', level: 17 },
  ];

  const handleDuelChallenge = (opponent) => {
    if (!opponent || !opponent.username) return;
    
    // Send challenge via WebSocket
    sendDuelRequest(opponent.username, 'squats'); // Default to squats for now
    alert(`Challenge sent to ${opponent.username}!`);
  };

  const handleInternalChat = (user) => {
    navigate(`/chat/${user.username}`);
  };

  const getRankColor = (rank) => {
    if (rank === 1) return 'text-yellow-500';
    if (rank === 2) return 'text-gray-400 dark:text-zinc-400';
    if (rank === 3) return 'text-orange-500';
    return 'text-gray-500 dark:text-zinc-500';
  };

  const getRankIcon = (rank) => {
    if (rank === 1) return '🥇';
    if (rank === 2) return '🥈';
    if (rank === 3) return '🥉';
    return rank;
  };

  const displayData = leaderboardData;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-black text-gray-900 dark:text-white p-6 pb-24 max-w-2xl mx-auto overflow-y-auto transition-colors duration-300">
      {/* Header */}
      <div className="flex justify-between items-center mb-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
        <div>
          <h1 className="text-3xl font-black">Leaderboard</h1>
          <p className="text-gray-500 dark:text-zinc-500">Compete with the best</p>
        </div>
        <div className="w-14 h-14 rounded-2xl bg-yellow-500/15 flex items-center justify-center">
          <Trophy size={32} className="text-yellow-500" />
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-2 mb-8 animate-in fade-in slide-in-from-bottom-4 duration-500 delay-100">
        {[
          { id: 'global', name: 'Global', icon: Users },
          { id: 'friends', name: 'Friends', icon: Users },
          { id: 'search', name: 'Search', icon: Search }
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setFilter(tab.id)}
            className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-xl font-bold transition-all ${
              filter === tab.id 
                ? 'bg-primary text-black scale-105' 
                : 'bg-white dark:bg-zinc-900/50 text-gray-500 dark:text-zinc-500 hover:bg-gray-100 dark:hover:bg-zinc-900 border border-gray-200 dark:border-transparent'
            }`}
          >
            <tab.icon size={16} />
            <span>{tab.name}</span>
          </button>
        ))}
      </div>

      {/* Search Bar */}
      {filter === 'search' && (
        <div className="mb-6 animate-in zoom-in-95 duration-300">
          <GlassCard className="flex items-center gap-3 px-4 py-3">
            <Search size={20} className="text-gray-500 dark:text-zinc-500" />
            <input
              type="text"
              placeholder="Search users..."
              className="bg-transparent border-none outline-none flex-1 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-zinc-500"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </GlassCard>
        </div>
      )}

      {/* List / Results */}
      <div className="space-y-4 mb-8">
        {(filter === 'search' ? searchResults : displayData).map((user, index) => (
          <GlassCard 
            key={user.id || user.rank} 
            className={`flex items-center justify-between p-4 animate-in fade-in slide-in-from-bottom-4 duration-500`}
            style={{ animationDelay: `${index * 50}ms` }}
          >
            <div className="flex items-center gap-4">
              {filter !== 'search' && (
                <div className={`w-8 text-center font-black ${getRankColor(user.rank)}`}>
                  {getRankIcon(user.rank)}
                </div>
              )}
              <div className="w-12 h-12 rounded-xl bg-gray-200 dark:bg-zinc-900 flex items-center justify-center overflow-hidden text-2xl">
                {user.avatar && user.avatar !== '👤' ? (
                  <img 
                    src={user.avatar.startsWith('http') ? user.avatar : `${API_BASE_URL}${user.avatar}`} 
                    alt={user.username} 
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.target.style.display = 'none';
                      e.target.parentElement.innerText = '👤';
                    }}
                  />
                ) : (
                  '👤'
                )}
              </div>
              <div>
                <p className={`font-bold ${user.isCurrentUser ? 'text-primary' : ''}`}>
                  {user.username} {user.isCurrentUser ? '(You)' : ''}
                </p>
                <div className="flex items-center gap-3 text-xs text-gray-500 dark:text-zinc-500 font-bold">
                  <span className="flex items-center gap-1">
                    <Flame size={12} className="text-orange-500" />
                    {user.streak || 0} days
                  </span>
                  <span className="flex items-center gap-1">
                    <Zap size={12} className="text-primary" />
                    Lvl {user.level || 1}
                  </span>
                </div>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <p className="text-xl font-black">{user.score || user.points || 0}</p>
              {!user.isCurrentUser && (
                <div className="flex gap-2">
                  {user.friendship_status === 'none' && (
                    <button 
                      onClick={() => handleAddFriend(user.id)}
                      className="p-2 bg-primary rounded-lg text-black hover:scale-110 transition-transform"
                    >
                      <UserPlus size={16} />
                    </button>
                  )}
                  {user.friendship_status === 'pending' && (
                    <div className="px-3 py-1 bg-gray-200 dark:bg-zinc-900 rounded-lg text-[10px] font-black text-gray-500 dark:text-zinc-500 uppercase">
                      Pending
                    </div>
                  )}
                  {user.friendship_status === 'received' && (
                    <button 
                      onClick={() => handleAcceptFriend(user.id)}
                      className="p-2 bg-primary rounded-lg text-black hover:scale-110 transition-transform"
                    >
                      <Check size={16} />
                    </button>
                  )}
                  {user.friendship_status === 'accepted' && (
                    <button 
                      onClick={() => handleInternalChat(user)}
                      className="p-2 bg-primary/15 rounded-lg text-primary hover:scale-110 transition-transform"
                      title="Chat"
                    >
                      <MessageCircle size={16} />
                    </button>
                  )}
                  <button 
                    onClick={() => handleDuelChallenge(user)}
                    className="p-2 bg-white dark:bg-zinc-900 rounded-lg text-gray-900 dark:text-white hover:scale-110 transition-transform border border-gray-200 dark:border-white/10 hover:bg-gray-100 dark:hover:bg-zinc-800"
                  >
                    <Swords size={16} />
                  </button>
                </div>
              )}
            </div>
          </GlassCard>
        ))}
      </div>

      {/* Duel Mode CTA */}
      <GlassCard className="p-6 border border-orange-500/30 animate-in fade-in slide-in-from-bottom-4 duration-500 delay-500">
        <div className="flex items-center gap-4 mb-4">
          <div className="w-12 h-12 rounded-xl bg-orange-500/15 flex items-center justify-center">
            <Swords size={24} className="text-orange-500" />
          </div>
          <div>
            <h2 className="text-xl font-black">Duel Mode</h2>
            <p className="text-sm text-gray-500 dark:text-zinc-500">Challenge anyone to a live workout battle</p>
          </div>
        </div>
        <GradientButton
          title="Find Match"
          colors={['#f97316', '#ea580c']}
          onPress={() => handleDuelChallenge(displayData[0])}
        />
      </GlassCard>
    </div>
  );
};

export default Leaderboard;
