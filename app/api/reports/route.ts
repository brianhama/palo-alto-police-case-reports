import { NextResponse } from 'next/server';
import { getDb } from '@/lib/db';

export async function GET(request: Request) {
    try {
        
        const db = await getDb();
        
        let query = 'SELECT * FROM arrest_reports';
       
        const reports = await db.all(query);

        return NextResponse.json({
            data: reports
        });
    } catch (error) {
        console.error('Error fetching reports:', error);
        return NextResponse.json(
            { error: 'Internal Server Error' },
            { status: 500 }
        );
    }
} 