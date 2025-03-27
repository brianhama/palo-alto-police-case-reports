import sqlite3
from datetime import datetime
import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
import tabula
import os

# URL of the webpage containing the police log links
url = "https://www.cityofpaloalto.org/Departments/Police/Public-Information-Portal/Police-Report-Log"

# Fetch police log URLs
def fetch_police_log_urls():
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve the webpage, status code: {response.status_code}")
        return []
        
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a", href=True)
    
    # Extract URLs that link to police logs (PDFs)
    police_log_urls = [
        link["href"]
        for link in links
        if "pdf" in link["href"].lower() and 
           "files/assets/public/v/2/police-department/public-information-portal/police-report-log/" in link["href"].lower()
    ]
    
    # Convert relative URLs to absolute URLs
    base_url = "https://www.cityofpaloalto.org"
    return [url if url.startswith("http") else base_url + url for url in police_log_urls]

def format_name(name):
    """Format name as First Last, handling various input formats including 'Last, First'"""
    # Handle empty or None names
    if not name or str(name).lower() == 'nan' or str(name).strip() == '':
        return ''
    
    # Check if name contains a comma (Last, First format)
    if ',' in name:
        parts = name.split(',')
        if len(parts) == 2:
            name = f"{parts[1].strip()} {parts[0].strip()}"
    
    # Split name into parts and filter out empty strings
    parts = [part.strip() for part in name.split() if part.strip()]
    
    # Capitalize each part
    parts = [part.capitalize() for part in parts]
    
    # Join back together
    return ' '.join(parts)

def log_file_exists(cursor, filename):
    cursor.execute('SELECT id FROM arrest_reports_files WHERE file_name = ?', (filename,))
    return cursor.fetchone() is not None

def get_log_file_id(cursor, conn, filename):
    cursor.execute('SELECT id FROM arrest_reports_files WHERE file_name = ?', (filename,))
    file_id = cursor.fetchone()
    if file_id is not None:
        return file_id[0]
    else:
        cursor.execute('INSERT INTO arrest_reports_files (file_name) VALUES (?)', (filename,))
        conn.commit()
        return cursor.lastrowid

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file"""
    try:
        col2str = {'dtype': str}
        kwargs = {
            'output_format': 'dataframe',
            'pandas_options': col2str,
            'pages': 'all',
            'stream': True
        }
        tables = tabula.read_pdf(pdf_path, **kwargs)

        if not tables or len(tables) == 0:
            print(f"No tables found in {pdf_path}")
            return None
        
        first_tables = []
        additional_tables = []

        for table in tables:
            is_first_table = False
            for index, row in table.iterrows():
                if str(row.iloc[0]).startswith('25-') or str(row.iloc[0]).startswith('24-'):
                    is_first_table = True
                    break

            if is_first_table:
                first_tables.append(table)
            else:
                additional_tables.append(table)

        if not first_tables:
            print(f"No arrest report tables found in {pdf_path}")
            return None
            
        base_table = first_tables[0]
        for table in first_tables[1:]:
            base_table = pd.concat([base_table, table], ignore_index=True, axis=1)

        if len(additional_tables) > 0:
            additional_data = additional_tables[0]
            for table in additional_tables[1:]:
                additional_data = pd.concat([additional_data, table], ignore_index=True, axis=1)

            base_table = pd.concat([base_table, additional_data], ignore_index=True)

        return base_table.fillna('')
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return None

def init_database():
    conn = sqlite3.connect('./db/arrest_reports.db')
    cursor = conn.cursor()
    
    cursor.execute('''
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
    )
    ''')
    
    conn.commit()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS arrest_reports_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()

    return conn

def download_pdf(url, filename):
    """Download a PDF file from a URL"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def get_latitude_longitude(address):
    """Get latitude and longitude for an address using Google Maps API"""
    try:
        if not address:
            return 0, 0
        
        address = address + " Palo Alto, CA"
        address = address.replace(' ', '+')

        # Google Maps Geocoding API
        api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        url = f'https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}'

        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if 'results' in data and len(data['results']) > 0:
            location = data['results'][0]['geometry']['location']
            return location['lat'], location['lng']
        else:
            return 0, 0
    except Exception as e:
        print(f"Error getting coordinates for {address}: {e}")
        return 0, 0

def parse_log_entry(row):
    """Parse a single row from the PDF into a structured log entry"""
    log_entry = {}
    
    # Basic case information
    log_entry['case_number'] = row.iloc[0]
    log_entry['date'] = row.iloc[1]
    log_entry['time'] = row.iloc[2]

    # Determine time index based on content
    time_index = 2
    if len(row.iloc[2]) > 4:
        time_index = 1

    # Extract offense and determine charge type
    log_entry['offense'] = row.iloc[time_index + 1]

    charge_type = "Unknown"
    if "(M)" in log_entry['offense'] or "Misdemeanor" in log_entry['offense']:
        charge_type = "Misdemeanor"
    elif "(F)" in log_entry['offense'] or "Felony" in log_entry['offense']:
        charge_type = "Felony"
    elif "(V)" in log_entry['offense']:
        charge_type = "Violation"
    elif "(I)" in log_entry['offense'] or "Infraction" in log_entry['offense']:
        charge_type = "Infraction"
    log_entry['charge_type'] = charge_type

    # Extract location
    log_entry['location'] = row.iloc[time_index + 2]

    # If location is empty, try to extract it from the offense field
    if len(log_entry['location']) == 0:
        pattern = r"^(.*?)\s+((?:\.\d+|\d{1,5})\s.*|[A-Z].*/[A-Z].*|[A-Z\s]+)$"
        match = re.match(pattern, log_entry['offense'])
        if match:
            offense, location = match.groups()
            log_entry['offense'] = offense
            log_entry['location'] = location

    # Clean up location
    if log_entry['location'].startswith("."):
        log_entry['location'] = log_entry['location'][1:]

    if log_entry['location']:
        parts = []
        for part in log_entry['location'].split():
            if '/' in part:
                subparts = part.split('/')
                parts.append('/'.join(p.capitalize() for p in subparts))
            else:
                parts.append(part.capitalize())
        log_entry['location'] = ' '.join(parts)

    # Extract arrestee information
    log_entry['arrestee_name'] = row.iloc[time_index + 3] if len(row) > time_index + 3 else ''
    log_entry['arrestee_date_of_birth'] = row.iloc[time_index + 4] if len(row) > time_index + 4 else ''
    log_entry['arrestee_gender'] = row.iloc[time_index + 5] if len(row) > time_index + 5 else ''
    log_entry['arrestee_race'] = row.iloc[time_index + 6] if len(row) > time_index + 6 else ''
    log_entry['arrestee_address'] = row.iloc[time_index + 7] if len(row) > time_index + 7 else ''

    # Clean up address
    if log_entry['arrestee_address'].startswith("."):
        log_entry['arrestee_address'] = log_entry['arrestee_address'][1:]

    # Get coordinates
    latitude, longitude = get_latitude_longitude(log_entry['location'])
    log_entry['latitude'] = latitude
    log_entry['longitude'] = longitude

    return log_entry

def process_log_entries(conn, cursor, log_entries, file_id):
    """Process and store log entries in the database"""
    for log_entry in log_entries:
        try:
            # Parse date and time
            date_str = log_entry['date']
            if " " in date_str:
                parts = date_str.split(' ')
                date_str = parts[0]
                time_str = parts[1]
            else:
                time_str = log_entry['time']

            # Format time if needed
            if ":" not in time_str and len(time_str) == 4:
                time_str = time_str[:2] + ':' + time_str[2:]

            # Parse datetime based on year format
            try:
                if len(date_str.split('/')[-1]) == 2:
                    incident_datetime = datetime.strptime(f"{date_str} {time_str}", "%m/%d/%y %H:%M")
                else:
                    incident_datetime = datetime.strptime(f"{date_str} {time_str}", "%m/%d/%Y %H:%M")
            except ValueError:
                print(f"Error parsing datetime: {date_str} {time_str}")
                incident_datetime = None
            
            # Parse DOB
            dob = None
            if log_entry['arrestee_date_of_birth'] and len(str(log_entry['arrestee_date_of_birth'])) == 10:
                try:
                    dob = datetime.strptime(str(log_entry['arrestee_date_of_birth']), "%Y-%m-%d").date()
                except ValueError:
                    print(f"Error parsing DOB: {log_entry['arrestee_date_of_birth']}")
            
            # Format name
            formatted_name = format_name(log_entry['arrestee_name'])
            
            # Insert into database
            cursor.execute('''
            INSERT INTO arrest_reports (
                file_id, case_number, incident_datetime, offense, charge_type, location,
                arrestee_name, arrestee_date_of_birth, arrestee_gender,
                arrestee_race, arrestee_address, latitude, longitude
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                file_id,
                log_entry['case_number'],
                incident_datetime.isoformat() if incident_datetime else None,
                log_entry['offense'],
                log_entry['charge_type'],
                log_entry['location'],
                formatted_name,
                dob.isoformat() if dob else None,
                log_entry['arrestee_gender'],
                log_entry['arrestee_race'],
                log_entry['arrestee_address'],
                log_entry['latitude'],
                log_entry['longitude']
            ))
            
            conn.commit()
            print(f"Stored entry for case number: {log_entry['case_number']}")
            
        except Exception as e:
            print(f"Error storing entry: {e}")
            print(f"Entry data: {log_entry}")

def main():
    # Initialize database
    conn = init_database()
    cursor = conn.cursor()
    
    # Fetch police log URLs
    police_log_urls = fetch_police_log_urls()
    
    for log_url in police_log_urls:
        try:
            # Skip if already processed
            if log_file_exists(cursor, log_url):
                print(f"Skipping duplicate file: {log_url}")
                continue
            
            # Get file ID and download PDF
            file_id = get_log_file_id(cursor, conn, log_url)
            filename = f"log_{file_id}.pdf"
            
            print(f"Downloading {log_url}...")
            if not download_pdf(log_url, filename):
                print(f"Skipping processing for {log_url} due to download error")
                continue

            # Extract and process text
            text = extract_text_from_pdf(filename)
            if text is None:
                continue
                
            log_entries = []
            for index, row in text.iterrows():
                if str(row.iloc[0]).startswith("25-") or str(row.iloc[0]).startswith("24-"):
                    log_entry = parse_log_entry(row)
                    log_entries.append(log_entry)
                    print(f"Parsed entry: {log_entry['case_number']}")

            # Process and store entries
            process_log_entries(conn, cursor, log_entries, file_id)
            
        except Exception as e:
            print(f"Error processing {log_url}: {e}")

    conn.close()
    print("Database processing complete!")

if __name__ == "__main__":
    main()