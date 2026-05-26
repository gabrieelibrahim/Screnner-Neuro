import json
import csv

try:
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    csv_file = r"d:\PROJECT UJI COBA\ScannerNeuro\data\idx_tickers.csv"
    with open(csv_file, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ticker', 'name', 'sector'])
        
        for p in data:
            kode = p.get('KodeEmiten', '')
            if kode:
                ticker = f"{kode}.JK"
                name = p.get('NamaEmiten', '')
                sector = p.get('Sektor', 'Unknown')
                writer.writerow([ticker, name, sector])
                
    print(f"Berhasil mengkonversi {len(data)} emiten.")
except Exception as e:
    print(e)
