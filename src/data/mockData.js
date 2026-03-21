export const USERS = [
  { id:1, name:'Arjun Sharma', role:'student', av:'AS', color:'#6366f1' },
  { id:2, name:'Priya Nair',   role:'student', av:'PN', color:'#ec4899' },
  { id:3, name:'Prof. Mehta',  role:'teacher', av:'PM', color:'#f59e0b' },
  { id:4, name:'Rahul Desai',  role:'student', av:'RD', color:'#10b981' },
]

export const CHATS = [
  { id:'ch-cs301', name:'Data Structures',   code:'CS301', icon:'🌳', color:'#6366f1', lastMsg:"I'll post a solved example tonight 🙌",          time:'09:21', unread:3, members:42 },
  { id:'ch-cs302', name:'Operating Systems', code:'CS302', icon:'⚙️', color:'#ec4899', lastMsg:'Deadlock section cleared up after re-reading',   time:'10:06', unread:1, members:38 },
  { id:'ch-cs303', name:'DBMS',              code:'CS303', icon:'🗄️', color:'#f59e0b', lastMsg:"I'll cover BCNF in Friday's class.",             time:'11:05', unread:0, members:40 },
  { id:'ch-cs304', name:'Computer Networks', code:'CS304', icon:'🌐', color:'#10b981', lastMsg:'Anyone want to do a group study for CN lab?',     time:'14:10', unread:2, members:35 },
]

export const MESSAGES = {
  'ch-cs301': [
    { id:1,  sid:2, text:"Hey! Did anyone get the Data Structures notes?",              time:'09:12' },
    { id:2,  sid:1, text:"Yes! I uploaded them just now 📚",                            time:'09:13' },
    { id:3,  sid:3, text:"Good morning everyone. Please review Chapter 5 before Friday.",time:'09:15' },
    { id:4,  sid:4, text:"Prof, will there be questions from linked lists?",             time:'09:17' },
    { id:5,  sid:3, text:"Yes, focus on insertion and deletion operations.",             time:'09:18' },
    { id:6,  sid:2, text:"Thanks! The AVL tree section is tricky 😅",                   time:'09:20' },
    { id:7,  sid:1, text:"I'll post a solved example tonight 🙌",                       time:'09:21' },
  ],
  'ch-cs302': [
    { id:8,  sid:3, text:"Has everyone finished the scheduling algorithms assignment?",  time:'10:00' },
    { id:9,  sid:1, text:"Working on it — Round Robin with I/O bursts is tricky",       time:'10:05' },
    { id:10, sid:2, text:"Same 😭 Deadlock section cleared up after re-reading notes",  time:'10:06' },
  ],
  'ch-cs303': [
    { id:11, sid:4, text:"Can someone explain BCNF vs 3NF with an example?",            time:'11:00' },
    { id:12, sid:1, text:"BCNF is stricter — every determinant must be a candidate key",time:'11:03' },
    { id:13, sid:3, text:"Good explanation Arjun. I'll cover this in Friday's class.",  time:'11:05' },
  ],
  'ch-cs304': [
    { id:14, sid:2, text:"The subnetting practice problems are really helpful!",         time:'14:00' },
    { id:15, sid:4, text:"Agreed! Anyone want to do a group study for the CN lab?",     time:'14:10' },
  ],
}

export const NOTES = [
  {
    id:1, title:'Data Structures – Complete Guide', subject:'CS301',
    desc:'Covers arrays, linked lists, trees, graphs with examples and complexity analysis.',
    uid:1, date:'Mar 10, 2026', ftype:'PDF', dl:142,
    ratings:[5,4,5,5,4,5,3,5], myRating:0,
    comments:[
      { uid:2, text:'This is so well organized! Saved my exam prep 🙌', time:'2 days ago' },
      { uid:4, text:'Please add more on AVL trees',                     time:'1 day ago' },
      { uid:3, text:'Excellent work Arjun. Very comprehensive.',        time:'5 hrs ago' },
    ],
  },
  {
    id:2, title:'Operating Systems – Process Management', subject:'CS302',
    desc:'Scheduling algorithms, deadlocks, memory management explained with diagrams.',
    uid:3, date:'Mar 9, 2026', ftype:'PDF', dl:98,
    ratings:[5,5,4,5,5], myRating:5,
    comments:[
      { uid:1, text:"Prof's notes are always the best 🔥", time:'3 days ago' },
      { uid:2, text:'The deadlock section is very clear',  time:'2 days ago' },
    ],
  },
  {
    id:3, title:'DBMS – SQL & Normalization', subject:'CS303',
    desc:'Full SQL reference + 1NF, 2NF, 3NF with worked examples from past papers.',
    uid:4, date:'Mar 8, 2026', ftype:'DOC', dl:76,
    ratings:[4,3,4,4], myRating:4,
    comments:[{ uid:1, text:'The normalization examples are 🔥', time:'4 days ago' }],
  },
  {
    id:4, title:'Computer Networks – Layer 1–4', subject:'CS304',
    desc:'OSI model, TCP/IP, subnetting, routing protocols with visual diagrams.',
    uid:2, date:'Mar 7, 2026', ftype:'PPT', dl:55,
    ratings:[4,5,4], myRating:0, comments:[],
  },
  {
    id:5, title:'Mathematics – Integration Techniques', subject:'MA201',
    desc:'All integration methods: substitution, parts, partial fractions with 50+ examples.',
    uid:1, date:'Mar 6, 2026', ftype:'PDF', dl:88,
    ratings:[5,5,5,4,5], myRating:0,
    comments:[{ uid:2, text:'Finally notes that explain substitution properly!', time:'5 days ago' }],
  },
]

export const AUTO_REPLIES = [
  'Got it! 👍', 'Sure, no problem!', 'Let me check and get back to you.',
  'Sounds good!', "I'll upload the notes soon 📚", 'Great question!',
  'Thanks for sharing!', 'Makes sense!', 'I agree 100%', 'Will do! 🙌',
]
