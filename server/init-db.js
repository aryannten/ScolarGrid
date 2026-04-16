require('dotenv').config();
const mysql = require('mysql2/promise');
const fs = require('fs');
const path = require('path');

async function initializeDatabase() {
  console.log('Connecting to MySQL instance...');
  try {
    const connection = await mysql.createConnection({
      host: process.env.DB_HOST || '127.0.0.1',
      user: process.env.DB_USER || 'root',
      password: process.env.DB_PASSWORD || '',
      multipleStatements: true
    });

    console.log('✅ Connected to MySQL. Reading schema.sql...');
    let schemaSQL = fs.readFileSync(path.join(__dirname, 'schema.sql'), 'utf-8');

    // Remove DELIMITER commands as mysql2 doesn't support/need them
    schemaSQL = schemaSQL.replace(/DELIMITER \/\//g, '').replace(/\/\//g, '').replace(/DELIMITER ;/g, '');

    console.log('Executing schema...');
    await connection.query(schemaSQL);

    console.log('✅ Database schema and seed data successfully initialized!');
    await connection.end();
  } catch (error) {
    console.error('❌ Failed to initialize database:', error.message);
    if (error.code === 'ECONNREFUSED') {
      console.error('Help: Ensure your MySQL server (e.g. XAMPP) is running on your machine.');
    }
  }
}

initializeDatabase();
