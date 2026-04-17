/**
 * Pure JavaScript in-memory database with JSON file persistence.
 * No native compilation needed — works on any system.
 */
const fs = require('fs');
const path = require('path');
const bcrypt = require('bcryptjs');
const { v4: uuidv4 } = require('uuid');

const DB_FILE = path.join(__dirname, 'data.json');

// In-memory store
let store = {
  profiles: [],
  faculty_codes: [],
  groups: [],
  group_members: [],
  messages: [],
  notes: [],
  note_ratings: [],
  leaderboard_points: [],
  complaints: [],
};

// ── Load / Save ────────────────────────────────────────────
function loadFromDisk() {
  try {
    if (fs.existsSync(DB_FILE)) {
      const raw = fs.readFileSync(DB_FILE, 'utf-8');
      const parsed = JSON.parse(raw);
      Object.assign(store, parsed);
      console.log('💾 Loaded database from data.json');
      return true;
    }
  } catch (e) {
    console.error('Failed to load data.json, starting fresh:', e.message);
  }
  return false;
}

function saveToDisk() {
  try {
    fs.writeFileSync(DB_FILE, JSON.stringify(store, null, 2), 'utf-8');
  } catch (e) {
    console.error('Failed to save data.json:', e.message);
  }
}

// Auto-save every 10 seconds
setInterval(saveToDisk, 10000);

// ── Seed Data ──────────────────────────────────────────────
function seed() {
  console.log('📦 Seeding database with initial data...');

  const adminHash = bcrypt.hashSync('admin123', 10);
  const facultyHash = bcrypt.hashSync('faculty123', 10);
  const studentHash = bcrypt.hashSync('student123', 10);
  const now = new Date().toISOString();

  store.profiles = [
    { id: 'a0000000-0000-0000-0000-000000000001', email: 'admin@scholargrid.com', password_hash: adminHash, full_name: 'Super Admin User', role: 'superadmin', about: 'Platform administrator', avatar_url: null, points: 0, warnings: 0, is_banned: 0, created_at: now, updated_at: now },
    { id: 'f0000000-0000-0000-0000-000000000001', email: 'faculty@scholargrid.com', password_hash: facultyHash, full_name: 'Faculty User', role: 'faculty', about: 'Computer Science Professor', avatar_url: null, points: 0, warnings: 0, is_banned: 0, created_at: now, updated_at: now },
    { id: 's0000000-0000-0000-0000-000000000001', email: 'alice@student.com', password_hash: studentHash, full_name: 'Alice Johnson', role: 'student', about: 'Computer Science major', avatar_url: null, points: 150, warnings: 0, is_banned: 0, created_at: now, updated_at: now },
    { id: 's0000000-0000-0000-0000-000000000002', email: 'bob@student.com', password_hash: studentHash, full_name: 'Bob Smith', role: 'student', about: 'Mathematics enthusiast', avatar_url: null, points: 230, warnings: 0, is_banned: 0, created_at: now, updated_at: now },
    { id: 's0000000-0000-0000-0000-000000000003', email: 'carol@student.com', password_hash: studentHash, full_name: 'Carol Williams', role: 'student', about: 'Physics student', avatar_url: null, points: 310, warnings: 0, is_banned: 0, created_at: now, updated_at: now },
    { id: 's0000000-0000-0000-0000-000000000004', email: 'dave@student.com', password_hash: studentHash, full_name: 'Dave Brown', role: 'student', about: 'Engineering student', avatar_url: null, points: 80, warnings: 0, is_banned: 0, created_at: now, updated_at: now },
    { id: 's0000000-0000-0000-0000-000000000005', email: 'eve@student.com', password_hash: studentHash, full_name: 'Eve Davis', role: 'student', about: 'Biology researcher', avatar_url: null, points: 420, warnings: 0, is_banned: 0, created_at: now, updated_at: now },
  ];

  store.groups = [
    { id: 'g0000000-0000-0000-0000-000000000001', name: 'CS Study Group', description: 'Computer Science discussions and help', join_code: 'GRP-2026-CS1', created_by: 'a0000000-0000-0000-0000-000000000001', created_at: now },
    { id: 'g0000000-0000-0000-0000-000000000002', name: 'Math Warriors', description: 'Advanced mathematics study group', join_code: 'STD-2026-MTH', created_by: 'a0000000-0000-0000-0000-000000000001', created_at: now },
    { id: 'g0000000-0000-0000-0000-000000000003', name: 'Physics Lab', description: 'Physics experiments and theory', join_code: 'DSC-2026-PHY', created_by: 'a0000000-0000-0000-0000-000000000001', created_at: now },
  ];

  store.group_members = [
    { group_id: 'g0000000-0000-0000-0000-000000000001', user_id: 'a0000000-0000-0000-0000-000000000001', joined_at: now },
    { group_id: 'g0000000-0000-0000-0000-000000000001', user_id: 's0000000-0000-0000-0000-000000000001', joined_at: now },
    { group_id: 'g0000000-0000-0000-0000-000000000001', user_id: 's0000000-0000-0000-0000-000000000002', joined_at: now },
    { group_id: 'g0000000-0000-0000-0000-000000000002', user_id: 's0000000-0000-0000-0000-000000000002', joined_at: now },
    { group_id: 'g0000000-0000-0000-0000-000000000002', user_id: 's0000000-0000-0000-0000-000000000003', joined_at: now },
    { group_id: 'g0000000-0000-0000-0000-000000000003', user_id: 's0000000-0000-0000-0000-000000000003', joined_at: now },
    { group_id: 'g0000000-0000-0000-0000-000000000003', user_id: 's0000000-0000-0000-0000-000000000004', joined_at: now },
    { group_id: 'g0000000-0000-0000-0000-000000000003', user_id: 's0000000-0000-0000-0000-000000000005', joined_at: now },
  ];

  store.messages = [
    { id: uuidv4(), group_id: 'g0000000-0000-0000-0000-000000000001', sender_id: 's0000000-0000-0000-0000-000000000001', content: 'Hey everyone! Ready for the algorithms exam?', file_url: null, file_name: null, file_type: null, created_at: now },
    { id: uuidv4(), group_id: 'g0000000-0000-0000-0000-000000000001', sender_id: 's0000000-0000-0000-0000-000000000002', content: 'Yes! I uploaded my notes on graph traversal.', file_url: null, file_name: null, file_type: null, created_at: now },
    { id: uuidv4(), group_id: 'g0000000-0000-0000-0000-000000000002', sender_id: 's0000000-0000-0000-0000-000000000002', content: 'Can someone explain eigenvalues?', file_url: null, file_name: null, file_type: null, created_at: now },
    { id: uuidv4(), group_id: 'g0000000-0000-0000-0000-000000000002', sender_id: 's0000000-0000-0000-0000-000000000003', content: 'Sure! Think of them as the scaling factors of a matrix transformation.', file_url: null, file_name: null, file_type: null, created_at: now },
    { id: uuidv4(), group_id: 'g0000000-0000-0000-0000-000000000003', sender_id: 's0000000-0000-0000-0000-000000000004', content: 'Lab report due Friday, anyone started?', file_url: null, file_name: null, file_type: null, created_at: now },
  ];

  store.notes = [
    { id: 'n0000000-0000-0000-0000-000000000001', uploader_id: 's0000000-0000-0000-0000-000000000001', title: 'Data Structures Complete Guide', description: 'Comprehensive notes on arrays, trees, graphs, and hash tables', subject: 'Computer Science', file_url: '/uploads/notes/sample-ds.pdf', file_name: 'data-structures.pdf', file_type: 'application/pdf', file_size: 2048000, is_flagged: 0, is_approved: 1, downloads: 45, created_at: now },
    { id: 'n0000000-0000-0000-0000-000000000002', uploader_id: 's0000000-0000-0000-0000-000000000002', title: 'Linear Algebra Cheat Sheet', description: 'Quick reference for matrices, determinants, and eigenvalues', subject: 'Mathematics', file_url: '/uploads/notes/sample-la.pdf', file_name: 'linear-algebra.pdf', file_type: 'application/pdf', file_size: 1024000, is_flagged: 0, is_approved: 1, downloads: 32, created_at: now },
    { id: 'n0000000-0000-0000-0000-000000000003', uploader_id: 's0000000-0000-0000-0000-000000000003', title: 'Quantum Mechanics Basics', description: 'Introduction to wave-particle duality and Schrodinger equation', subject: 'Physics', file_url: '/uploads/notes/sample-qm.pdf', file_name: 'quantum-mechanics.pdf', file_type: 'application/pdf', file_size: 3072000, is_flagged: 0, is_approved: 1, downloads: 28, created_at: now },
    { id: 'n0000000-0000-0000-0000-000000000004', uploader_id: 's0000000-0000-0000-0000-000000000005', title: 'Cell Biology Notes', description: 'Detailed notes on cell structure, organelles, and processes', subject: 'Biology', file_url: '/uploads/notes/sample-bio.pdf', file_name: 'cell-biology.pdf', file_type: 'application/pdf', file_size: 1536000, is_flagged: 0, is_approved: 1, downloads: 19, created_at: now },
    { id: 'n0000000-0000-0000-0000-000000000005', uploader_id: 's0000000-0000-0000-0000-000000000001', title: 'Algorithm Design Patterns', description: 'Dynamic programming, greedy, divide and conquer patterns', subject: 'Computer Science', file_url: '/uploads/notes/sample-algo.pdf', file_name: 'algorithms.pdf', file_type: 'application/pdf', file_size: 2560000, is_flagged: 0, is_approved: 1, downloads: 55, created_at: now },
  ];

  store.complaints = [
    { id: uuidv4(), student_id: 's0000000-0000-0000-0000-000000000001', title: 'Cannot download notes', description: 'Getting a 404 error when trying to download uploaded notes', status: 'open', admin_reply: null, resolved_by: null, created_at: now, updated_at: now },
    { id: uuidv4(), student_id: 's0000000-0000-0000-0000-000000000004', title: 'Incorrect points calculation', description: 'My points were not updated after uploading 3 notes', status: 'in_progress', admin_reply: null, resolved_by: null, created_at: now, updated_at: now },
  ];

  store.note_ratings = [];
  store.leaderboard_points = [];
  store.faculty_codes = [];

  saveToDisk();
  console.log('✅ Database seeded successfully!');
}

// ── Initialize ─────────────────────────────────────────────
function initDb() {
  const loaded = loadFromDisk();
  if (!loaded || store.profiles.length === 0) {
    seed();
  }
  return store;
}

module.exports = { initDb, store, saveToDisk };
