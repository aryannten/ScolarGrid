require('dotenv').config({ path: '../.env' });
const mysql = require('mysql2/promise');
const fs = require('fs');
const path = require('path');

async function runMigration() {
  const connection = await mysql.createConnection({
    host: process.env.DB_HOST || '127.0.0.1',
    user: process.env.DB_USER || 'root',
    password: process.env.DB_PASSWORD || '',
  });

  const dbName = process.env.DB_NAME || 'scholargrid_db';

  console.log(`Creating database ${dbName} if not exists...`);
  await connection.query(`CREATE DATABASE IF NOT EXISTS \`${dbName}\``);
  await connection.query(`USE \`${dbName}\``);

  console.log('Running schema creation...');
  const schemaPath = path.join(__dirname, 'mysql_schema.sql');
  const schemaSql = fs.readFileSync(schemaPath, 'utf8');
  
  // Split schema by ; and execute
  const statements = schemaSql.split(';').map(s => s.trim()).filter(s => s.length > 0);
  for (const stmt of statements) {
    await connection.query(stmt);
  }

  console.log('Reading data.json...');
  const dataPath = path.join(__dirname, 'data.json');
  if (!fs.existsSync(dataPath)) {
    console.log('No data.json found, skipping seeding.');
    await connection.end();
    return;
  }
  
  const rawData = fs.readFileSync(dataPath, 'utf8');
  const data = JSON.parse(rawData);

  console.log('Seeding profiles...');
  if (data.profiles && data.profiles.length > 0) {
    const profileValues = data.profiles.map(p => [
      p.id, p.email, p.password_hash, p.full_name, p.avatar_url, p.role, p.about, 
      p.points || 0, p.warnings || 0, p.is_banned || 0, 
      p.created_at, p.updated_at
    ]);
    await connection.query(`INSERT IGNORE INTO profiles (id, email, password_hash, full_name, avatar_url, role, about, points, warnings, is_banned, created_at, updated_at) VALUES ?`, [profileValues]);
  }

  console.log('Seeding groups...');
  if (data.groups && data.groups.length > 0) {
    const groupValues = data.groups.map(g => [
      g.id, g.name, g.description, g.join_code, g.created_by, g.created_at
    ]);
    await connection.query(`INSERT IGNORE INTO \`groups\` (id, name, description, join_code, created_by, created_at) VALUES ?`, [groupValues]);
  }

  console.log('Seeding group_members...');
  if (data.group_members && data.group_members.length > 0) {
    const memberValues = data.group_members.map(m => [
      m.group_id, m.user_id, m.joined_at
    ]);
    await connection.query(`INSERT IGNORE INTO group_members (group_id, user_id, joined_at) VALUES ?`, [memberValues]);
  }

  console.log('Seeding messages...');
  if (data.messages && data.messages.length > 0) {
    const messageValues = data.messages.map(m => [
      m.id, m.group_id, m.sender_id, m.content, m.file_url, m.file_name, m.file_type, m.created_at
    ]);
    await connection.query(`INSERT IGNORE INTO messages (id, group_id, sender_id, content, file_url, file_name, file_type, created_at) VALUES ?`, [messageValues]);
  }

  console.log('Seeding notes...');
  if (data.notes && data.notes.length > 0) {
    const noteValues = data.notes.map(n => [
      n.id, n.uploader_id, n.title, n.description, n.subject, n.file_url, n.file_name, n.file_type, n.file_size,
      n.is_flagged || 0, n.is_approved === undefined ? 1 : n.is_approved, n.downloads || 0, n.created_at
    ]);
    await connection.query(`INSERT IGNORE INTO notes (id, uploader_id, title, description, subject, file_url, file_name, file_type, file_size, is_flagged, is_approved, downloads, created_at) VALUES ?`, [noteValues]);
  }

  console.log('Seeding complaints...');
  if (data.complaints && data.complaints.length > 0) {
    const complaintValues = data.complaints.map(c => [
      c.id, c.student_id, c.title, c.description, c.status || 'open', c.admin_reply, c.resolved_by, c.created_at, c.updated_at
    ]);
    await connection.query(`INSERT IGNORE INTO complaints (id, student_id, title, description, status, admin_reply, resolved_by, created_at, updated_at) VALUES ?`, [complaintValues]);
  }

  // note_ratings, leaderboard_points, faculty_codes are mostly empty in JSON or simple
  console.log('Seeding leaderboard_points...');
  if (data.leaderboard_points && data.leaderboard_points.length > 0) {
    const pointsValues = data.leaderboard_points.map(p => [
      p.id, p.user_id, p.points, p.reason, p.reference_id, p.created_at
    ]);
    await connection.query(`INSERT IGNORE INTO leaderboard_points (id, user_id, points, reason, reference_id, created_at) VALUES ?`, [pointsValues]);
  }

  console.log('Seeding faculty_codes...');
  if (data.faculty_codes && data.faculty_codes.length > 0) {
    const codeValues = data.faculty_codes.map(f => [f.code, f.created_at]);
    await connection.query(`INSERT IGNORE INTO faculty_codes (code, created_at) VALUES ?`, [codeValues]);
  }

  console.log('Migration completed successfully!');
  await connection.end();
}

runMigration().catch(err => {
  console.error('Migration failed:', err);
  process.exit(1);
});
