import { useState }       from 'react'
import LoginScreen        from './screens/LoginScreen'
import ChatListScreen     from './screens/ChatListScreen'
import ChatRoom           from './screens/ChatRoom'
import NotesScreen        from './screens/NotesScreen'
import NoteDetail         from './screens/NoteDetail'
import UploadScreen       from './screens/UploadScreen'
import ProfileScreen      from './screens/ProfileScreen'
import BottomNav          from './components/BottomNav'
import Sidebar            from './components/Sidebar'
import Background         from './components/Background'
import { NOTES, CHATS }  from './data/mockData'
import { deepCopy }       from './utils/helpers'

export default function App() {
  const [user,       setUser]       = useState(null)
  const [tab,        setTab]        = useState('chat')
  const [activeChat, setActiveChat] = useState(null)
  const [viewNote,   setViewNote]   = useState(null)
  const [notes,      setNotes]      = useState(() => deepCopy(NOTES))
  const [chats,      setChats]      = useState(() => deepCopy(CHATS))

  const goTab = (t) => { setTab(t); setActiveChat(null); setViewNote(null) }

  const openChat = (chat) => {
    setChats(prev => prev.map(c => c.id === chat.id ? { ...c, unread: 0 } : c))
    setActiveChat(chat)
  }

  const updateNote = (updated) => {
    setNotes(prev => prev.map(n => n.id === updated.id ? updated : n))
    setViewNote(updated)
  }

  const addNote = (n) => setNotes(prev => [n, ...prev])

  const handleLogout = () => {
    setUser(null); setTab('chat'); setActiveChat(null)
    setViewNote(null); setNotes(deepCopy(NOTES)); setChats(deepCopy(CHATS))
  }

  const hideNav = (tab === 'chat' && activeChat) || (tab === 'notes' && viewNote)

  if (!user) return (
    <>
      <Background />
      <LoginScreen onLogin={setUser} />
    </>
  )

  const renderScreen = () => {
    if (tab === 'chat') {
      if (activeChat) return <ChatRoom chat={activeChat} currentUser={user} onBack={() => setActiveChat(null)} />
      return <ChatListScreen chats={chats} onOpen={openChat} />
    }
    if (tab === 'notes') {
      if (viewNote) return <NoteDetail note={viewNote} currentUser={user} onBack={() => setViewNote(null)} onUpdate={updateNote} />
      return <NotesScreen notes={notes} onViewNote={setViewNote} />
    }
    if (tab === 'upload')  return <UploadScreen  currentUser={user} onNoteAdded={addNote} />
    if (tab === 'profile') return <ProfileScreen currentUser={user} notes={notes} onLogout={handleLogout} />
  }

  return (
    <>
      <Background />
      <div className="app-shell">
        <Sidebar active={tab} onChange={goTab} />
        <div className="app-content">
          {renderScreen()}
          {!hideNav && <BottomNav active={tab} onChange={goTab} />}
        </div>
      </div>
    </>
  )
}
