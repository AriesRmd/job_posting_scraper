from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException,ElementClickInterceptedException
import time
import pandas as pd
from tqdm import tqdm
from save_dataframe import save_csv_with_timestamp
from selenium.common.exceptions import WebDriverException, SessionNotCreatedException
from selenium.webdriver.chrome.options import Options




def run_linkedin_scraper():
    CHROMEDRIVER_PATH = "D:/Aries/PROJECT/data_scraping/chromedriver-win64/chromedriver.exe"
    TARGET_URL = "https://www.linkedin.com/login"

    try:
        #untuk menghilangkan pesan [1368:6584:0428/120307.735:ERROR:socket_manager.cc(147)] Failed to resolve address for stun.l.google.com., errorcode: -105
        chrome_options = Options()
        chrome_options.add_argument("--disable-webrtc")  # Nonaktifkan WebRTC
        chrome_options.add_argument("--disable-features=WebRtcHideLocalIpsWithMdns")
        driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=chrome_options)
    except WebDriverException as e:
        print("❌ Gagal inisialisasi webdriver:", e)
        return

    wait = WebDriverWait(driver, 10)

    try:
        driver.get(TARGET_URL)
        time.sleep(2)
        email_box = driver.find_element(By.XPATH, "//input[@aria-label='Email or phone']")
        pw_box = driver.find_element(By.XPATH, "//input[@aria-label='Password']")
        email_box.send_keys("YOUR_EMAIL_HERE",Keys.RETURN)
        pw_box.send_keys("YOUR_PASSWORD_HERE",Keys.RETURN)
        time.sleep(5)
    except Exception as e:
        print("❌ Gagal login ke Linkedin:", e)
        # driver.quit()
        return

    try:
        # Menyelesaikan captcha manual dulu
        time.sleep(5)
        driver.get("https://www.linkedin.com/jobs/graphic-designer-jobs/")
        time.sleep(5)

        input_box = driver.find_element(By.XPATH, '//input[@aria-label="Search by title, skill, or company"]')
        input_box.send_keys("Graphic Design")
        input_box.send_keys(Keys.RETURN)
        time.sleep(5)
    except Exception as e:
        print("❌ Gagal membuka halaman pencarian:", e)
        driver.quit()
        return

    #---------Fungsi Untuk Melakukan Scroll------------
    def smooth_scroll_container(driver, container, scroll_step=100, pause=0.1):
        current_position = 0
        last_height = driver.execute_script("return arguments[0].scrollHeight", container)
        
        while current_position < last_height:
            # Scroll in increments
            current_position += scroll_step
            driver.execute_script("arguments[0].scrollTop = arguments[1]", container, current_position)
            
            # Wait briefly between scrolls
            time.sleep(pause)
            
            # Update container height in case content loads dynamically
            new_height = driver.execute_script("return arguments[0].scrollHeight", container)
            if new_height > last_height:
                last_height = new_height



    #---------Scrapping Data----------
    # Inisialisasi jumlah halaman
    page_number = 2  # kita mulai dari page 2 (karena page 1 sudah dibuka)
    job_data = []
    max_pages = 10
    page_count = 1
    job_urls = []

    while page_count <= max_pages:

        # Scroll to bottom of specific container
        desired_container = driver.find_element(By.XPATH, "//div[contains(@class,'aMDXzvpxGIbmbbpDRnHzKPLEHkTTIqOnVWmPuEk')]") #dirubah setiap hari, scrollnya
        # Smooth scroll version
        smooth_scroll_container(driver, desired_container)


        print(f"\n📄 Scraping halaman ke-{page_count}...")
        time.sleep(10)
        try:
            # wait.until(EC.presence_of_all_elements_located((By.XPATH, '//ul[@class="gPpnfPapJiAkDLdAWTJMxObGNHXeHhtnLg"]')))
            # container = driver.find_element(By.XPATH, '//ul[@class="gPpnfPapJiAkDLdAWTJMxObGNHXeHhtnLg"]')
            job_cards = driver.find_elements(By.XPATH, "//li[contains(@class, 'p0') and contains(@class, 'relative') and contains(@class, 'scaffold-layout__list-item')]")

            # # Cetak isi setiap li
            for index, li in enumerate(job_cards, 1):
                print(f"Item {index}: {li.text}")

        except TimeoutException:
            print("⏰ Timeout menunggu job cards.")
            break
        except WebDriverException as e:
            print(f"❌ Gagal mengambil job cards: {e}")
            break

        job_urls = []
        for card in job_cards[:5]: #Jumlah link yang di scrapping
            try:
                link = card.find_element(By.TAG_NAME, 'a').get_attribute('href')
                job_urls.append(link)
            except Exception as e:
                print("⚠️ Gagal ambil link:", e)

        print(len(job_urls))

        for link in tqdm(job_urls, desc="Scraping Jobs....."):
            try:
                driver.execute_script(f"window.open('{link}', '_blank');")
                time.sleep(3)
                driver.switch_to.window(driver.window_handles[1])

                job_title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1[class="t-24 t-bold inline"]'))).text
                company = driver.find_element(By.CSS_SELECTOR, 'div[class="job-details-jobs-unified-top-card__company-name"]').text

                try:
                    alamat = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[6]/div[3]/div[2]/div/div/main/div[2]/div[1]/div/div[1]/div/div/div/div[3]/div/span/span[1]'))).text
                except:
                    alamat = "Tidak Tersedia"

                try:
                    job_detail = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.job-details-preferences-and-skills__pill")))                   
                    # Extract text from all elements
                    job_detail_all_texts = [element.text for element in job_detail]
                    if "Tambahkan" in job_detail_all_texts:
                        job_detail_all_texts = "Tidak Tersedia"
                except:
                    job_detail_all_texts = "Tidak Tersedia"

                time.sleep(5)
                #Membuka job deskripsi
                try:
                    button = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Click to see more description"]')
                    button.click()
                    print("✅ Button clicked.")
                except NoSuchElementException:
                    print("ℹ️ Button not found, continuing...")

                try:
                    # Job Desc
                    container = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[6]/div[3]/div[2]/div/div/main/div[2]/div[1]/div/div[4]/article')))
                    lists = container.find_elements(By.XPATH, ".//span")
                    # Extract text from each span, filtering out empty/whitespace-only texts
                    all_texts = [span.text.strip() for span in lists if span.text.strip()]
                    # Join all texts with newlines for better readability
                    combined_text = "\n".join(all_texts)
                except:
                    combined_text = "Tidak Tersedia"

                job_data.append({
                    "Job Title": job_title,
                    "Company": company,
                    "Location": alamat,
                    "Job Detail": job_detail_all_texts,
                    # "Employee Type": emp_type,
                    "Job Desc": combined_text,
                    "Link": link
                })
                print(f"✅ {job_title} - {company}")
                print(f"Location: {alamat}")
                print(f"Job Details: {job_detail_all_texts}")
                print(f"Job Desc: ",combined_text)
                # print({link})
                
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
        time.sleep(5)
        try:
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//li[@data-test-pagination-page-btn='{page_number}']"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
            next_button.click()
            print(f"✅ Pindah ke halaman {page_number}")
            page_number += 1
            page_count += 1
            time.sleep(3)

        except NoSuchElementException:
            print("📌 Tidak ada halaman selanjutnya.")
            break
        except TimeoutException:
            print("⏰ Tidak bisa menemukan tombol halaman berikutnya.")
            break
        except Exception as e:
            print(f"⚠️ Error saat klik halaman berikutnya: {e}")
            break
    
    df = pd.DataFrame(job_data)
    save_csv_with_timestamp(df, folder='D:/Aries/PROJECT/scraping_data_job_posting/data/linkedin', prefix='raw_data')
    print("\n✅ Scraping Linkedin selesai dan file disimpan.")

    try:
        driver.quit()
    except:
        pass

