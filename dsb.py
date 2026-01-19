import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pydsb import PyDSB
import imgkit
import shutil
import os

class DSBPlanExtractor:
    CLASS_MAP = {
        51: "5a",
        52: "5b",
        53: "5c",
        61: "6a",
        62: "6b",
        63: "6c",
        71: "7a",
        72: "7b",
        73: "7c",
        81: "8a",
        82: "8b",
        83: "8c",
        91: "9a",
        92: "9b",
        93: "9c",
        101: "10a",
        102: "10b",
        103: "10c",
        11: "EF  Einführungsphase",
        12: "Q1  Qualifikationsphase I",
        13: "Q2  Qualifikationsphase II",
        # Add more when you know the exact labels
    }

    file_list = []

    def __init__(self, school_id: str, username: str):
        self.dsb = PyDSB(school_id, username)

    def extract_class_block(self, html: str, class_number: int) -> str | None:
        """
        Extract the HTML block for a specific class number from the provided HTML.
        Returns the extracted HTML as a string, or None if no data found or errors.
        """
        if class_number not in self.CLASS_MAP:
            print(f"❌ Class number {class_number} not mapped to a known section.")
            return None

        soup = BeautifulSoup(html, "html.parser")

        date_div = soup.find("div", class_="mon_title")
        if not date_div:
            print("❌ Date not found.")
            return None

        full_date_text = date_div.get_text(strip=True)
        date_part = full_date_text.split()[0]

        try:
            date_obj = datetime.strptime(date_part, "%d.%m.%Y").date()
            safe_date = date_obj.strftime("%Y-%m-%d")
        except ValueError:
            safe_date = date_part.replace('.', '-')

        class_label = self.CLASS_MAP[class_number]

        table = soup.find("table", class_="mon_list")
        rows = table.find_all("tr") if table else []

        capturing = False
        captured_rows = []
        header_row_html = ""

        for row in rows:
            if row.find("th"):
                header_row_html = str(row)

            header_cell = row.find("td", class_="list inline_header")
            if header_cell:
                label = header_cell.get_text(strip=True)
                if label.startswith(class_label):
                    capturing = True
                    captured_rows.append(str(row))
                    continue
                elif capturing:
                    break
            elif capturing:
                captured_rows.append(str(row))

        if not captured_rows:
            print(f"ℹ️ No data found for class {class_number} ({class_label}) on {date_part}.")
            return None

        html_output = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <title>Vertretungsplan {class_label} – {full_date_text}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .mon_title {{ 
                    font-weight: bold; 
                    font-size: 120%; 
                    margin-bottom: 10px; 
                    text-align: center; 
                }}
                table {{
                    border-collapse: collapse; 
                    width: 80%; 
                    margin: 0 auto;
                    font-size: 14px;
                }}
                th, td {{
                    border: 1px solid #ccc; 
                    padding: 8px; 
                    text-align: center;
                }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
            </style>
        </head>
        <body>
            <div class="mon_title">{full_date_text}</div>
            <table>
                {header_row_html}
                {''.join(captured_rows)}
            </table>
        </body>
        </html>
        """

        filename = f"subst_{class_label.split()[0]}_{safe_date}.html".replace(" ", "_")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_output.strip())

        print(f"✅ File created: {filename}")
        return filename

    def fetch_and_extract(self, class_number: int):
        """
        Fetch plans from DSB and extract the HTML block for the given class_number.
        Processes all plans except those with title 'stat. HTML 2'.
        """
        self.cleanse()
        plans = self.dsb.get_plans()
        filtered = [p for p in plans if p['title'] != "stat. HTML 2"]

        for plan in filtered:
            r = requests.get(plan['url'])
            if r.ok:
                self.extract_class_block(r.text, class_number)
            else:
                print(f"❌ Failed to fetch URL: {plan['url']}")
        self.convert2png()
    
    def cleanse(self):
        for root, dirs, files in os.walk(os.getcwd()):
            for file in files:
                if file.endswith('.html'):
                    if file.startswith('subst_'):
                        print(f'removing file: {file}')
                        os.remove(file)


    def convert2png(self):
        backup_folder = "backup"
        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)
        print('-'*50)
        for root, dirs, files in os.walk(os.getcwd()):
            for file in files:
                if file.endswith('.html'):
                    self.file_list.append(file)
                    #filename = os.path.splitext(str(file))[0]+'.jpg'
                    imgkit.from_file(str(file), f'images/{os.path.splitext(str(file))[0]}.jpg')
    
    def get_all(self):
        all_classes = [51, 52, 53, 61, 62, 63, 71, 72, 73, 81, 82, 83, 91, 92, 93, 101, 102, 103, 11, 12, 13]#
        for c in all_classes:
            self.fetch_and_extract(c)
    
    def backup(self):
        backup_folder = "backup"
        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)
        
        for file in os.listdir("images"):
            if file.endswith(".jpg"):
                # Extract the date from the filename (assuming format like 'subst_8b_2025-11-24.jpg')
                try:
                    date_str = file.split("_")[-1].split(".")[0]  # Extract '2025-11-24'
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    date_folder = os.path.join(backup_folder, date_obj.strftime("%Y-%m-%d"))
                    
                    if not os.path.exists(date_folder):
                        os.makedirs(date_folder)
                    shutil.move(os.path.join("images", file), os.path.join(date_folder, file))
                except ValueError:
                    return False
        return True


#extractor = DSBPlanExtractor(exampleID,exampleUSER)
#all_classes = [51, 52, 53, 61, 62, 63, 71, 72, 73, 81, 82, 83, 91, 92, 93, 101, 102, 103, 11, 12, 13]
#for c in all_classes:
#    extractor.fetch_and_extract(c)
#extractor.convert2png()
#extractor.cleanse()
#extractor.get_all()