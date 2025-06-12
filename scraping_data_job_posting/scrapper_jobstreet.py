from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import pandas as pd
from tqdm import tqdm
from save_dataframe import save_csv_with_timestamp
from selenium.common.exceptions import WebDriverException, SessionNotCreatedException

def run_jstreet_scraper():
    CHROMEDRIVER_PATH = "D:/Aries/PROJECT/data_scraping/chromedriver-win64/chromedriver.exe"
    TARGET_URL = "https://id.jobstreet.com/"
    
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        # options.add_argument("--headless")  # Uncomment jika ingin headless
        driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=options)
    except SessionNotCreatedException as e:
        print(f"❌ Session gagal dibuat. Periksa versi chromedriver dan Chrome: {e}")
        return
    except WebDriverException as e:
        print(f"❌ Gagal memulai WebDriver: {e}")
        return

    wait = WebDriverWait(driver, 10)

    print("🔎 Membuka halaman JobStreet...")

    try:
        driver.get(TARGET_URL)
    except WebDriverException as e:
        print(f"❌ Gagal membuka halaman: {e}")
        driver.quit()
        return

    # Isi pencarian
    try:
        search_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="keywords-input"]')))
        enter_button = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="searchButton"]')))
        time.sleep(3)
        search_input.send_keys("Graphic Design" + Keys.RETURN)
        enter_button.click()
        time.sleep(5)
        # search_input.send_keys(Keys.RETURN)
    except TimeoutException:
        print("❌ Input pencarian tidak ditemukan.")
        driver.quit()
        return
    except Exception as e:
        print(f"❌ Error saat input pencarian: {e}")
        driver.quit()
        return

    job_data = []
    max_pages = 2
    page_count = 1

    while page_count <= max_pages:
        print(f"\n📄 Scraping halaman ke-{page_count}...")

        try:
            # wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[class="_1oozmqe0 l218ib4z l218ib4x"]')))
            job_cards = driver.find_elements(By.CSS_SELECTOR, 'div._1oozmqe0.l218ib4z.l218ib4x a')
            # print(f"Jumlah job ditemukan: {len(job_cards)}")
            # print(job_cards)
        except TimeoutException:
            print("⏰ Timeout menunggu job cards.")
            break
        except WebDriverException as e:
            print(f"❌ Gagal mengambil job cards: {e}")
            break

        job_urls = []
        base_url = "https://id.jobstreet.com"

        for card in job_cards:
            try:
                link = card.get_attribute('href')
                # Periksa apakah link sudah lengkap atau perlu ditambah base_url
                if not link.startswith("http"):
                    link = base_url + link
                job_urls.append(link)
                # print(job_urls)
            except Exception as e:
                print("⚠️ Gagal ambil link:", e)

        for i, link in enumerate(tqdm(job_urls[:5], desc="Scraping Jobs.....")):
            try:
                driver.execute_script(f"window.open('{link}', '_blank');")
                time.sleep(3)
                driver.switch_to.window(driver.window_handles[1])

                job_title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1[data-automation="job-detail-title"]'))).text
                company = driver.find_element(By.CSS_SELECTOR, 'span[data-automation="advertiser-name"]').text

                try:
                    alamat = driver.find_element(By.CSS_SELECTOR, 'span[data-automation="job-detail-location"] a').text
                except:
                    alamat = "Tidak Tersedia"

                try:
                    salary = driver.find_element(By.CSS_SELECTOR, 'span[data-automation="job-detail-salary"]').text
                    if "Tambahkan" in salary:
                        salary = "Tidak Tersedia"
                except:
                    salary = "Tidak Tersedia"

                try:
                    emp_type = driver.find_element(By.CSS_SELECTOR, 'span[data-automation="job-detail-work-type"] a').text
                except:
                    emp_type = "Tidak Tersedia"

                try:
                    container = driver.find_element(By.CSS_SELECTOR, 'div[data-automation="jobAdDetails"]')
                    lists = container.find_elements(By.XPATH, './/ul | .//ol')
                    deskripsi = [li.text.strip() for lst in lists for li in lst.find_elements(By.TAG_NAME, "li")]
                    job_desc = "\n".join(deskripsi)
                except:
                    job_desc = "Tidak Tersedia"

                job_data.append({
                    "Job Title": job_title,
                    "Company": company,
                    "Location": alamat,
                    "Salary": salary,
                    "Employee Type": emp_type,
                    "Job Desc": job_desc,
                    "Link": link
                })

                print(f"✅ {job_title} - {company}")
            except Exception as e:
                print(f"❌ Gagal scraping dari {link}: {e}")
            finally:
                try:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    time.sleep(1)
                except Exception as e:
                    print(f"⚠️ Gagal menutup tab atau switch: {e}")
                    break

        # Klik tombol "Selanjutnya"
        try:
            next_button = driver.find_element(By.XPATH, '//a[.//span[text()="Selanjutnya"]]')
            driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
            next_button.click()
            page_count += 1
            time.sleep(3)
        except NoSuchElementException:
            print("📌 Tidak ada halaman selanjutnya.")
            break
        except TimeoutException:
            print("⏰ Tidak bisa menemukan tombol next.")
            break
        except Exception as e:
            print(f"⚠️ Error saat klik next: {e}")
            break

    df = pd.DataFrame(job_data)
    save_csv_with_timestamp(df, folder='D:/Aries/PROJECT/scraping_data_job_posting/data/jobstreet', prefix='raw_data')
    print("\n✅ Scraping JobStreet selesai dan file disimpan.")

    try:
        driver.quit()
    except:
        pass

