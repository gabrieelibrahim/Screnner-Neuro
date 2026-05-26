import cloudscraper
import json
import csv

url = "https://idx.co.id/primary/ListedCompany/GetCompanyProfiles?start=0&length=9999"

try:
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})
    
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Origin': 'https://idx.co.id',
        'Referer': 'https://idx.co.id/id/data-pasar/data-saham/daftar-saham/'
    }
    
    response = scraper.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        profiles = data.get('data', [])
        
        csv_file = r"d:\PROJECT UJI COBA\ScannerNeuro\data\idx_tickers.csv"
        
        with open(csv_file, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ticker', 'name', 'sector'])
            
            for p in profiles:
                kode = p.get('KodeEmiten', '')
                ticker = f"{kode}.JK" if kode else ''
                name = p.get('NamaEmiten', '')
                sector = p.get('Sektor', 'Unknown')
                
                if ticker:
                    writer.writerow([ticker, name, sector])
                
        print(f"Berhasil mengunduh {len(profiles)} emiten ke idx_tickers.csv")
    else:
        print(f"Gagal mengunduh: HTTP {response.status_code}")
except Exception as e:
    print(f"Error: {e}")
