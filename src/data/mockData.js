// Mock data for ScholarGrid

export const USERS = [
  { id: '1', name: 'Dr. Anika Sharma', email: 'admin@scholargrid.com', role: 'admin', avatar: null, about: 'Platform Administrator', joinedAt: '2025-06-15' },
  { id: '2', name: 'Rohan Kapoor', email: 'rohan@student.edu', role: 'student', avatar: null, about: 'Computer Science, 3rd Year', joinedAt: '2025-08-20', score: 2450, tier: 'Gold', uploads: 23, downloads: 156 },
  { id: '3', name: 'Priya Patel', email: 'priya@student.edu', role: 'student', avatar: null, about: 'Electrical Engineering, 2nd Year', joinedAt: '2025-09-01', score: 3120, tier: 'Elite', uploads: 38, downloads: 210 },
  { id: '4', name: 'Arjun Nair', email: 'arjun@student.edu', role: 'student', avatar: null, about: 'Mathematics, 4th Year', joinedAt: '2025-07-10', score: 1890, tier: 'Silver', uploads: 15, downloads: 98 },
  { id: '5', name: 'Meera Joshi', email: 'meera@student.edu', role: 'student', avatar: null, about: 'Physics, 1st Year', joinedAt: '2026-01-05', score: 780, tier: 'Bronze', uploads: 6, downloads: 42 },
  { id: '6', name: 'Vikram Singh', email: 'vikram@student.edu', role: 'student', avatar: null, about: 'Chemistry, 3rd Year', joinedAt: '2025-10-12', score: 2100, tier: 'Gold', uploads: 20, downloads: 134 },
  { id: '7', name: 'Ananya Reddy', email: 'ananya@student.edu', role: 'student', avatar: null, about: 'Biology, 2nd Year', joinedAt: '2025-11-20', score: 1560, tier: 'Silver', uploads: 12, downloads: 87 },
  { id: '8', name: 'Karthik Menon', email: 'karthik@student.edu', role: 'student', avatar: null, about: 'Mechanical Engineering, 4th Year', joinedAt: '2025-06-30', score: 950, tier: 'Bronze', uploads: 8, downloads: 56 },
];

export const SUBJECTS = ['Computer Science', 'Mathematics', 'Physics', 'Chemistry', 'Electrical Engineering', 'Mechanical Engineering', 'Biology', 'Economics'];

export const NOTES = [
  { id: '1', title: 'Data Structures & Algorithms — Complete Notes', description: 'Comprehensive DSA notes covering arrays, linked lists, trees, graphs, DP, and sorting algorithms with examples.', subject: 'Computer Science', tags: ['DSA', 'Algorithms', 'Trees'], uploaderId: '2', uploaderName: 'Rohan Kapoor', createdAt: '2026-02-15', fileType: 'PDF', fileSize: '4.2 MB', downloads: 342, rating: 4.8, totalRatings: 45, ratings: [] },
  { id: '2', title: 'Linear Algebra — Matrices & Transformations', description: 'Detailed notes on matrix operations, eigenvalues, eigenvectors, and linear transformations.', subject: 'Mathematics', tags: ['Linear Algebra', 'Matrices'], uploaderId: '4', uploaderName: 'Arjun Nair', createdAt: '2026-01-20', fileType: 'PDF', fileSize: '2.8 MB', downloads: 218, rating: 4.5, totalRatings: 32, ratings: [] },
  { id: '3', title: 'Quantum Mechanics — Wave Functions', description: 'In-depth exploration of wave functions, Schrodinger equation, and quantum states.', subject: 'Physics', tags: ['Quantum', 'Wave Functions'], uploaderId: '3', uploaderName: 'Priya Patel', createdAt: '2026-03-01', fileType: 'PDF', fileSize: '5.1 MB', downloads: 189, rating: 4.9, totalRatings: 28, ratings: [] },
  { id: '4', title: 'Organic Chemistry — Reaction Mechanisms', description: 'Complete guide to organic reaction mechanisms with step-by-step solutions.', subject: 'Chemistry', tags: ['Organic', 'Reactions'], uploaderId: '6', uploaderName: 'Vikram Singh', createdAt: '2026-02-28', fileType: 'PPT', fileSize: '8.3 MB', downloads: 156, rating: 4.3, totalRatings: 22, ratings: [] },
  { id: '5', title: 'Circuit Analysis — AC/DC Fundamentals', description: 'Fundamentals of circuit analysis including Kirchhoff\'s laws, Thevenin theorem, and AC circuits.', subject: 'Electrical Engineering', tags: ['Circuits', 'AC/DC'], uploaderId: '3', uploaderName: 'Priya Patel', createdAt: '2026-01-15', fileType: 'PDF', fileSize: '3.6 MB', downloads: 267, rating: 4.7, totalRatings: 38, ratings: [] },
  { id: '6', title: 'Machine Learning — Neural Networks Guide', description: 'Introduction to neural networks, backpropagation, CNNs, and RNNs with Python examples.', subject: 'Computer Science', tags: ['ML', 'Neural Networks', 'Python'], uploaderId: '2', uploaderName: 'Rohan Kapoor', createdAt: '2026-03-10', fileType: 'PDF', fileSize: '6.7 MB', downloads: 421, rating: 4.9, totalRatings: 56, ratings: [] },
  { id: '7', title: 'Thermodynamics — Laws & Applications', description: 'Complete notes on all four laws of thermodynamics with real-world applications.', subject: 'Mechanical Engineering', tags: ['Thermo', 'Laws'], uploaderId: '8', uploaderName: 'Karthik Menon', createdAt: '2026-02-05', fileType: 'DOC', fileSize: '2.1 MB', downloads: 134, rating: 4.2, totalRatings: 18, ratings: [] },
  { id: '8', title: 'Molecular Biology — DNA & Protein Synthesis', description: 'Detailed guide to DNA replication, transcription, translation, and gene expression.', subject: 'Biology', tags: ['DNA', 'Genetics'], uploaderId: '7', uploaderName: 'Ananya Reddy', createdAt: '2026-03-05', fileType: 'PDF', fileSize: '3.9 MB', downloads: 98, rating: 4.6, totalRatings: 15, ratings: [] },
];

export const CHAT_GROUPS = [
  { id: '1', name: 'CS301 — Algorithm Design', description: 'Discussion group for Algorithm Design course', joinCode: 'ALG-2026-XK9', members: 45, createdBy: '1', createdAt: '2025-09-01', lastMessage: 'Has anyone solved the DP assignment?', lastMessageAt: '2026-03-21T18:30:00' },
  { id: '2', name: 'Physics Lab — Section A', description: 'Coordinate lab schedules and share experiment data', joinCode: 'PHY-2026-M3R', members: 32, createdBy: '1', createdAt: '2025-09-15', lastMessage: 'Lab report due Friday!', lastMessageAt: '2026-03-21T16:45:00' },
  { id: '3', name: 'Math Study Circle', description: 'Peer study group for advanced mathematics', joinCode: 'MTH-2026-B7J', members: 28, createdBy: '1', createdAt: '2025-10-01', lastMessage: 'Great session today on eigenvalues', lastMessageAt: '2026-03-21T14:20:00' },
  { id: '4', name: 'Campus Events & Announcements', description: 'Official announcements and event updates', joinCode: 'EVT-2026-Q2P', members: 156, createdBy: '1', createdAt: '2025-06-15', lastMessage: 'Tech fest registrations open!', lastMessageAt: '2026-03-21T12:00:00' },
  { id: '5', name: 'Project Collaboration Hub', description: 'Find teammates and collaborate on projects', joinCode: 'PRJ-2026-W5L', members: 67, createdBy: '1', createdAt: '2025-11-01', lastMessage: 'Looking for a frontend dev for our team', lastMessageAt: '2026-03-20T22:15:00' },
];

export const MESSAGES = {
  '1': [
    { id: 'm1', groupId: '1', senderId: '2', senderName: 'Rohan Kapoor', content: 'Hey everyone! Has anyone started the DP assignment yet?', timestamp: '2026-03-21T18:30:00', type: 'text' },
    { id: 'm2', groupId: '1', senderId: '4', senderName: 'Arjun Nair', content: 'Yes, I solved the first 3 problems. The knapsack variant is tricky though.', timestamp: '2026-03-21T18:32:00', type: 'text' },
    { id: 'm3', groupId: '1', senderId: '3', senderName: 'Priya Patel', content: 'I found a great resource on tabulation approach. Let me share it.', timestamp: '2026-03-21T18:35:00', type: 'text' },
    { id: 'm4', groupId: '1', senderId: '3', senderName: 'Priya Patel', content: 'dp_guide.pdf', timestamp: '2026-03-21T18:36:00', type: 'file', fileType: 'PDF', fileSize: '1.2 MB' },
    { id: 'm5', groupId: '1', senderId: '6', senderName: 'Vikram Singh', content: 'Thanks Priya! This is really helpful. The memoization vs tabulation comparison is great.', timestamp: '2026-03-21T18:40:00', type: 'text' },
    { id: 'm6', groupId: '1', senderId: '2', senderName: 'Rohan Kapoor', content: 'Has anyone solved the DP assignment?', timestamp: '2026-03-21T18:45:00', type: 'text' },
  ],
  '2': [
    { id: 'm7', groupId: '2', senderId: '5', senderName: 'Meera Joshi', content: 'Reminder: Lab report for Experiment 7 is due Friday!', timestamp: '2026-03-21T16:45:00', type: 'text' },
    { id: 'm8', groupId: '2', senderId: '7', senderName: 'Ananya Reddy', content: 'What format should we use for the graphs?', timestamp: '2026-03-21T16:50:00', type: 'text' },
  ],
};

export const COMPLAINTS = [
  { id: '1', userId: '2', userName: 'Rohan Kapoor', category: 'Technical', title: 'PDF preview not loading', description: 'When I try to preview PDF notes in the browser, it shows a blank page. Tried Chrome and Firefox.', status: 'Open', priority: 'High', createdAt: '2026-03-20T10:00:00', resolvedAt: null, adminResponse: null },
  { id: '2', userId: '5', userName: 'Meera Joshi', category: 'Content', title: 'Inappropriate content in Chemistry notes', description: 'The organic chemistry notes (ID: 4) contain some copied content without proper attribution.', status: 'In Progress', priority: 'Medium', createdAt: '2026-03-19T14:30:00', resolvedAt: null, adminResponse: 'Looking into this. Will review the flagged content.' },
  { id: '3', userId: '4', userName: 'Arjun Nair', category: 'Feature Request', title: 'Add LaTeX support in chat', description: 'It would be great to render LaTeX formulas directly in the chat for math discussions.', status: 'Open', priority: 'Low', createdAt: '2026-03-18T09:15:00', resolvedAt: null, adminResponse: null },
  { id: '4', userId: '7', userName: 'Ananya Reddy', category: 'Account', title: 'Cannot change profile picture', description: 'The upload button for profile picture does nothing when clicked. No error message displayed.', status: 'Resolved', priority: 'Medium', createdAt: '2026-03-15T11:00:00', resolvedAt: '2026-03-16T15:30:00', adminResponse: 'Fixed the file upload handler. Please clear your cache and try again.' },
  { id: '5', userId: '6', userName: 'Vikram Singh', category: 'Technical', title: 'Chat messages not syncing', description: 'Messages in the Algorithm Design group are not showing in real-time. Need to refresh to see new messages.', status: 'In Progress', priority: 'High', createdAt: '2026-03-17T16:00:00', resolvedAt: null, adminResponse: 'Investigating the WebSocket connection issue.' },
];

export const LEADERBOARD = USERS
  .filter(u => u.role === 'student')
  .sort((a, b) => (b.score || 0) - (a.score || 0))
  .map((u, i) => ({ ...u, rank: i + 1 }));

export const ACTIVITY_FEED = [
  { id: '1', type: 'upload', user: 'Rohan Kapoor', action: 'uploaded', target: 'Machine Learning — Neural Networks Guide', time: '2 hours ago' },
  { id: '2', type: 'rating', user: 'Priya Patel', action: 'rated', target: 'Data Structures & Algorithms notes', detail: '5 stars', time: '3 hours ago' },
  { id: '3', type: 'join', user: 'Meera Joshi', action: 'joined', target: 'CS301 — Algorithm Design', time: '5 hours ago' },
  { id: '4', type: 'complaint', user: 'Arjun Nair', action: 'submitted feedback:', target: 'Add LaTeX support in chat', time: '1 day ago' },
  { id: '5', type: 'download', user: 'Vikram Singh', action: 'downloaded', target: 'Circuit Analysis notes', time: '1 day ago' },
  { id: '6', type: 'resolve', user: 'Admin', action: 'resolved complaint:', target: 'Cannot change profile picture', time: '2 days ago' },
];

export const ANALYTICS = {
  totalUsers: 248,
  totalNotes: 156,
  totalDownloads: 12480,
  activeChats: 5,
  openComplaints: 3,
  resolvedComplaints: 42,
  monthlyUploads: [12, 18, 22, 15, 28, 35, 42, 38, 45, 52, 48, 56],
  monthlyUsers: [20, 35, 48, 62, 78, 95, 110, 128, 145, 168, 195, 248],
  topSubjects: [
    { subject: 'Computer Science', count: 45 },
    { subject: 'Mathematics', count: 32 },
    { subject: 'Physics', count: 28 },
    { subject: 'Electrical Engineering', count: 22 },
    { subject: 'Chemistry', count: 18 },
  ],
};

export const COMPLAINT_CATEGORIES = ['Technical', 'Content', 'Account', 'Feature Request', 'Other'];
export const PRIORITY_LEVELS = ['Low', 'Medium', 'High', 'Critical'];
export const STATUS_OPTIONS = ['Open', 'In Progress', 'Resolved', 'Closed'];
export const TIER_THRESHOLDS = { Bronze: 0, Silver: 1000, Gold: 2000, Elite: 3000 };
