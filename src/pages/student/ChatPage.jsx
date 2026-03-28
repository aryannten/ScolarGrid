import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../../context/useAuth';
import { api } from '../../lib/api';
import { Search, Send, Paperclip, Hash, Users, Clock, Plus, X, Copy, Check, File } from 'lucide-react';

const container = { hidden: { opacity: 0 }, show: { opacity: 1, transition: { staggerChildren: 0.05 } } };

export default function ChatPage() {
  const { user } = useAuth();
  const [groups, setGroups] = useState([]);
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [searchGroup, setSearchGroup] = useState('');
  const [showJoin, setShowJoin] = useState(false);
  const [joinCode, setJoinCode] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const [groupName, setGroupName] = useState('');
  const [copied, setCopied] = useState(false);
  const messagesEndRef = useRef(null);

  const fetchGroups = async () => {
    try {
      const resp = await api.get('/api/v1/chat/groups');
      setGroups(resp.groups || []);
    } catch (e) {
      console.error('Failed to fetch groups', e);
    }
  };

  useEffect(() => {
    fetchGroups();
  }, []);

  const fetchMessages = async (groupId) => {
    if (!groupId) return;
    try {
      const resp = await api.get(`/api/v1/chat/groups/${groupId}/messages?page_size=100`);
      setMessages(resp.messages || []);
      scrollToBottom();
    } catch (e) {
      console.error('Failed to fetch messages', e);
    }
  };

  useEffect(() => {
    if (selectedGroup) {
      fetchMessages(selectedGroup.id);
      
      // Basic 5-second polling
      const poll = setInterval(() => {
        fetchMessages(selectedGroup.id);
      }, 5000);
      return () => clearInterval(poll);
    } else {
      setMessages([]);
    }
  }, [selectedGroup]);

  const scrollToBottom = () => {
    setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  const filteredGroups = groups.filter(g => g.name.toLowerCase().includes(searchGroup.toLowerCase()));

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !selectedGroup) return;
    
    // Optimistic UI updates
    const tempMsg = {
      id: `m${Date.now()}`,
      sender_id: user?.id || 'temp',
      sender_name: user?.name || 'You',
      content: newMessage,
      created_at: new Date().toISOString(),
      type: 'text',
    };
    setMessages(prev => [...prev, tempMsg]);
    setNewMessage('');
    scrollToBottom();

    try {
      await api.post(`/api/v1/chat/groups/${selectedGroup.id}/messages`, { content: tempMsg.content });
      fetchMessages(selectedGroup.id);
    } catch (e) {
      console.error('Failed to send message', e);
    }
  };

  const handleJoinOrCreate = async () => {
    if (isCreating) {
      if (!groupName.trim()) return;
      try {
        const resp = await api.post('/api/v1/chat/groups', { name: groupName, description: '' });
        await fetchGroups();
        setSelectedGroup(resp);
        setShowJoin(false);
      } catch (e) {
        alert(e.message || 'Failed to create group');
      }
    } else {
      if (!joinCode.trim()) return;
      try {
        const resp = await api.post('/api/v1/chat/groups/join', { join_code: joinCode.trim() });
        await fetchGroups();
        setSelectedGroup(resp);
        setShowJoin(false);
      } catch (e) {
        alert(e.message || 'Failed to join group');
      }
    }
  };

  const copyCode = (code) => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const formatTime = (ts) => {
    if (!ts) return '';
    const d = new Date(ts);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="h-[calc(100vh-7rem)] flex gap-4">
      {/* Groups Panel */}
      <div className={`${selectedGroup ? 'hidden lg:flex' : 'flex'} flex-col w-full lg:w-80 glass-card overflow-hidden flex-shrink-0`}>
        <div className="p-4 border-b border-light-border dark:border-dark-border/50">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-serif font-bold text-gray-900 dark:text-white">Chats</h2>
            <button onClick={() => setShowJoin(true)} className="p-2 rounded-lg bg-brand-50 dark:bg-brand-900/20 text-brand-500 hover:bg-brand-100 dark:hover:bg-brand-900/30 transition-colors">
              <Plus className="w-4 h-4" />
            </button>
          </div>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input type="text" value={searchGroup} onChange={e => setSearchGroup(e.target.value)} placeholder="Search groups..." className="input-field pl-9 py-2 text-sm" />
          </div>
        </div>
        <div className="flex-1 overflow-y-auto">
          {groups.length === 0 && (
             <div className="p-6 text-center text-sm text-gray-500">
               Click + to create or join a chat group.
             </div>
          )}
          {filteredGroups.map(group => (
            <button
              key={group.id}
              onClick={() => setSelectedGroup(group)}
              className={`w-full text-left px-4 py-3 flex items-start gap-3 transition-colors border-b border-gray-50 dark:border-dark-border/30 ${
                selectedGroup?.id === group.id ? 'bg-brand-50 dark:bg-brand-900/10' : 'hover:bg-gray-50 dark:hover:bg-dark-hover'
              }`}
            >
              <div className="w-10 h-10 rounded-xl bg-gradient-premium flex items-center justify-center flex-shrink-0 text-white text-sm font-bold">
                <Hash className="w-4 h-4" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-gray-900 dark:text-white truncate">{group.name}</h3>
                  <span className="text-xs text-gray-400 flex-shrink-0">{formatTime(group.last_message_at)}</span>
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400 truncate mt-0.5">{group.last_message || 'No messages yet'}</p>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-xs text-gray-400 flex items-center gap-1"><Users className="w-3 h-3" /> {group.member_count}</span>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Chat Area */}
      <div className={`${selectedGroup ? 'flex' : 'hidden lg:flex'} flex-1 flex-col glass-card overflow-hidden`}>
        {selectedGroup ? (
          <>
            {/* Chat Header */}
            <div className="flex items-center gap-3 px-4 lg:px-6 py-4 border-b border-light-border dark:border-dark-border/50">
              <button onClick={() => setSelectedGroup(null)} className="lg:hidden p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-dark-hover">
                <X className="w-5 h-5 text-gray-500" />
              </button>
              <div className="w-10 h-10 rounded-xl bg-gradient-premium flex items-center justify-center text-white">
                <Hash className="w-5 h-5" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900 dark:text-white">{selectedGroup.name}</h3>
                <p className="text-xs text-gray-400">{selectedGroup.member_count} members</p>
              </div>
              <button onClick={() => copyCode(selectedGroup.join_code)} className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gray-50 dark:bg-dark-surface text-xs font-mono text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-dark-hover transition-colors">
                {copied ? <Check className="w-3 h-3 text-emerald-500" /> : <Copy className="w-3 h-3" />}
                {selectedGroup.join_code}
              </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 lg:p-6 space-y-4">
              {messages.length === 0 ? (
                <div className="text-center mt-10 text-sm text-gray-500">No messages yet. Say hi!</div>
              ) : messages.map(msg => {
                const isOwn = msg.sender_id === user?.id;
                return (
                  <div key={msg.id} className={`flex ${isOwn ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-[75%] ${isOwn ? 'order-2' : ''}`}>
                      {!isOwn && <p className="text-xs font-semibold text-brand-500 mb-1 ml-1">{msg.sender_name}</p>}
                      <div className={`px-4 py-2.5 rounded-2xl ${
                        isOwn
                          ? 'bg-brand-500 text-white rounded-tr-sm'
                          : 'bg-gray-100 dark:bg-dark-hover text-gray-800 dark:text-gray-200 rounded-tl-sm'
                      }`}>
                        {msg.type === 'file' ? (
                          <div className="flex items-center gap-2">
                            <File className="w-4 h-4" />
                            <a href={msg.file_url} target="_blank" rel="noreferrer" className="text-sm underline">{msg.content}</a>
                          </div>
                        ) : (
                          <p className="text-sm">{msg.content}</p>
                        )}
                      </div>
                      <p className={`text-xs text-gray-400 mt-1 ${isOwn ? 'text-right mr-1' : 'ml-1'}`}>
                        {formatTime(msg.created_at)}
                      </p>
                    </div>
                  </div>
                );
              })}
              <div ref={messagesEndRef} />
            </div>

            {/* Message Input */}
            <form onSubmit={sendMessage} className="px-4 lg:px-6 py-4 border-t border-light-border dark:border-dark-border/50">
              <div className="flex items-center gap-3">
                <input
                  type="text"
                  value={newMessage}
                  onChange={e => setNewMessage(e.target.value)}
                  placeholder="Type a message..."
                  className="flex-1 bg-gray-50 dark:bg-dark-surface border border-gray-200 dark:border-dark-border rounded-xl px-4 py-2.5 text-sm text-gray-900 dark:text-gray-100 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-brand-500/50 focus:border-brand-500"
                />
                <button
                  type="submit"
                  disabled={!newMessage.trim()}
                  className="p-2.5 rounded-xl bg-brand-500 text-white hover:bg-brand-600 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>
            </form>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-center p-6">
            <div>
              <div className="w-16 h-16 rounded-2xl bg-gray-100 dark:bg-dark-hover flex items-center justify-center mx-auto mb-4">
                <Hash className="w-8 h-8 text-gray-400" />
              </div>
              <h3 className="text-lg font-serif font-semibold text-gray-900 dark:text-white mb-1">Select a conversation</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">Choose a group from the sidebar to start chatting</p>
            </div>
          </div>
        )}
      </div>

      {/* Join/Create Group Modal */}
      <AnimatePresence>
        {showJoin && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[100] flex items-center justify-center p-4" onClick={() => setShowJoin(false)}>
            <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.95 }} className="bg-light-surface dark:bg-dark-card rounded-2xl border border-light-border dark:border-dark-border w-full max-w-sm p-6" onClick={e => e.stopPropagation()}>
              <div className="flex justify-between items-center mb-4">
                 <h2 className="text-xl font-serif font-bold text-gray-900 dark:text-white">Chat Group</h2>
                 <button onClick={() => setShowJoin(false)}><X className="w-5 h-5 text-gray-500"/></button>
              </div>
              
              <div className="flex bg-gray-100 dark:bg-dark-surface rounded-xl p-1 mb-4">
                  <button onClick={() => setIsCreating(false)} className={`flex-1 py-1.5 rounded-lg text-sm font-semibold transition-all ${!isCreating ? 'bg-white shadow-sm text-brand-600' : 'text-gray-500'}`}>Join</button>
                  <button onClick={() => setIsCreating(true)} className={`flex-1 py-1.5 rounded-lg text-sm font-semibold transition-all ${isCreating ? 'bg-white shadow-sm text-brand-600' : 'text-gray-500'}`}>Create</button>
              </div>

              {!isCreating ? (
                <input type="text" value={joinCode} onChange={e => setJoinCode(e.target.value)} placeholder="Enter join code (e.g., ALG2026X)" className="input-field font-mono mb-4" />
              ) : (
                <input type="text" value={groupName} onChange={e => setGroupName(e.target.value)} placeholder="Group Name" className="input-field mb-4" />
              )}
              
              <div className="flex gap-3">
                <button onClick={() => setShowJoin(false)} className="btn-secondary flex-1">Cancel</button>
                <button onClick={handleJoinOrCreate} className="btn-primary flex-1">{isCreating ? 'Create' : 'Join'}</button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
