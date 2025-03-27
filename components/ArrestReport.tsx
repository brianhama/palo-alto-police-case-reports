'use client';
export interface ArrestReport {
    id: number;
    file_id: number;
    case_number: string;
    incident_datetime: string;
    offense: string;
    charge_type: string;
    location: string;
    arrestee_name: string;
    arrestee_date_of_birth: string;
    arrestee_gender: string;
    arrestee_race: string;
    arrestee_address: string;
    latitude: number;
    longitude: number;
    created_at: string;
}
