# 🔍 Job Posting Scraper for Indonesia
A web scraping project to collect job postings from **Glints**, **LinkedIn**, and **JobStreet** for Indonesian job seekers. 

🎯 **Goal**: Help job seekers in Indonesia find job listings from multiple platforms in one place — cleaned, combined, and ready for analysis.

## 🧰 Tools & Technologies
- 🐍 Python
- 🕷 Selenium
- 🧮 Pandas
- 📊 Looker Studio (for dashboard)
- 💻 Visual Studio Code

## 📁 Folder Structure
scraping_data_job_posting/
├── data/
│   ├── glints/                 # CSV hasil scraping dari Glints
│   ├── jobstreet/              # CSV hasil scraping dari JobStreet
│   ├── linkedin/               # CSV hasil scraping dari LinkedIn
│   ├── glints_cleaning.py      # File cleaning untuk data Glints
│   ├── jobstreet_cleaning.py   # File cleaning untuk data JobStreet
│   └── linkedin_cleaning.py    # File cleaning untuk data LinkedIn
│
├── main.py                    # Menjalankan proses scraping semua situs
├── cleaning_main.py           # Menjalankan cleaning dan gabungkan semua data
└── README.md                  # Dokumentasi proyek



## 🚀 How to Run

1. Clone repo-nya:
   ```bash
   git clone https://github.com/username/scraping_data_job_posting.git
   cd scraping_data_job_posting
2. pip install -r requirements.txt
3. Jalankan scraper: python main.py
4. Jalankan cleaning dan penggabungan data: python cleaning_main.py


---

### 6. Hasil Output

Kalau kamu punya dashboard, tampilkan link-nya. Misal:

```markdown
## 📊 Dashboard Example

Lihat dashboard hasil data ini di: (https://lookerstudio.google.com/u/0/reporting/4587abe8-7a1f-4ea9-af75-3b87d3c607e0/page/p_p59trqssrd)

## 👨‍💻 About Me

Made with ❤️ by **Muhammad Aries Ramadhan**  
🔗 (https://www.linkedin.com/in/muhammad-aries/)  
📧 mhmmd.aries15@gmail.com
