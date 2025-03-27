import sqlite3 from 'sqlite3';
import { open, Database } from 'sqlite';
import path from 'path';

let db: Database | null = null;

export async function getDb() {
    if (db) {
        return db;
    }
    const dbPath = path.join(process.cwd(), 'db/arrest_reports.db');

    console.log(dbPath);

    db = await open({
        filename: dbPath,
        driver: sqlite3.Database
    });

    // Create the table if it doesn't exist
    await db.exec(`
    CREATE TABLE IF NOT EXISTS arrest_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_id INTEGER NOT NULL,
        case_number TEXT NOT NULL,
        incident_datetime TIMESTAMP,
        offense TEXT,
        charge_type TEXT,
        location TEXT,
        arrestee_name TEXT,
        arrestee_date_of_birth DATE,
        arrestee_gender TEXT,
        arrestee_race TEXT,
        arrestee_address TEXT,
        latitude DECIMAL,
        longitude DECIMAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )`);

    return db;
}

export async function closeDb() {
    if (db) {
        await db.close();
        db = null;
    }
} 