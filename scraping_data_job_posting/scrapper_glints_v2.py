from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
import time
import pandas as pd
from save_dataframe import save_csv_with_timestamp

def run_glints_scraper2():
    CHROMEDRIVER_PATH = "D:/Aries/PROJECT/data_scraping/chromedriver-win64/chromedriver.exe"
    TARGET_URL = "https://glints.com/id/login"

    try:
        driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH)
    except WebDriverException as e:
        print("❌ Gagal inisialisasi webdriver:", e)
        return

    wait = WebDriverWait(driver, 10)

    try:
        driver.get(TARGET_URL)
        time.sleep(5)
        driver.find_element(By.XPATH, '//span[contains(text(), "Masuk dengan Email")]').click()

        email_box = driver.find_element(By.XPATH, "//input[@aria-label='Alamat email']")
        pw_box = driver.find_element(By.XPATH, "//input[@aria-label='Kata sandi']")
        email_box.send_keys("YOUR_EMAIL_HERE")
        pw_box.send_keys("YOUR_PASSWORD_HERE")
        email_box.send_keys(Keys.RETURN)
        pw_box.send_keys(Keys.RETURN)
        time.sleep(8)
    except Exception as e:
        print("❌ Gagal login ke Glints:", e)
        # driver.quit()
        return

    try:
        driver.get("https://glints.com/id/opportunities/jobs/")
        time.sleep(8)

        input_box = driver.find_element(By.CSS_SELECTOR, 'input[data-cy="search_bar_job_title"]')
        input_box.send_keys("Graphic Design")
        input_box.send_keys(Keys.RETURN)
        time.sleep(5)
    except Exception as e:
        print("❌ Gagal membuka halaman pencarian:", e)
        # driver.quit()
        return
    
    job_data = []

    try:
        job_cards = driver.find_elements(By.CSS_SELECTOR, 'h2 a.CompactOpportunityCardsc__JobCardTitleNoStyleAnchor-sc-dkg8my-12')
        print(f"Jumlah job ditemukan: {len(job_cards)}")
        base_url = "https://glints.com"
        
        job_urls = []
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


        for i, link in enumerate(job_urls[:5]):
            try:
                driver.execute_script(f"window.open('{link}', '_blank');")
                time.sleep(2)
                driver.switch_to.window(driver.window_handles[1])

                job_title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1[aria-label="Job Title"]'))).text
                company = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/id/companies/']"))).text

                try:
                    alamat = driver.find_element(By.XPATH, "//div[contains(@class, 'AddressWrapper')]//p").text
                except NoSuchElementException:
                    alamat = "Tidak Tersedia"

                try:
                    salary = driver.find_element(By.XPATH, "//span[contains(@class, 'BasicSalary')]").text
                except NoSuchElementException:
                    salary = "Tidak Tersedia"

                try:
                    emp_type = driver.find_element(By.XPATH, "(//div[@class='TopFoldsc__JobOverViewInfo-sc-1fbktg5-9 larqhx'])[2]").text
                except:
                    emp_type = "Tidak Tersedia"

                try:
                    level_exp = driver.find_element(By.XPATH, "//div[contains(text(), 'tahun pengalaman')]").text
                except:
                    level_exp = "Tidak Tersedia"

                try:
                    provinsi = driver.find_element(By.XPATH, "(//label[@class='BreadcrumbStyle__BreadcrumbItemWrapper-sc-eq3cq-0 dgcIRu aries-breadcrumb-item'])[3]").text
                    kota = driver.find_element(By.XPATH, "(//label[@class='BreadcrumbStyle__BreadcrumbItemWrapper-sc-eq3cq-0 dgcIRu aries-breadcrumb-item'])[4]").text
                except:
                    provinsi = kota = "Tidak Tersedia"

                try:
                    container = driver.find_element(By.XPATH, "(//div[@class = 'Skillssc__TagContainer-sc-1h7ic4i-4 cSakwS'])")
                    skills = [p.text for p in container.find_elements(By.TAG_NAME, "p")]
                except:
                    skills = []

                job_data.append({
                    "Job Title": job_title,
                    "Company": company,
                    "Location": alamat,
                    "Salary": salary,
                    "Employee Type": emp_type,
                    "Level of Experience": level_exp,
                    "Province": provinsi,
                    "City": kota,
                    "Skill": skills,
                    "Link": link
                })

                print(f"✅ Berhasil scrape: {job_title} di {company}")
            except TimeoutException:
                print(f"⏰ Timeout scraping: {link}")
            except Exception as e:
                print(f"❌ Gagal scraping dari {link}: {e}")
            finally:
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

    except Exception as e:
        print("❌ Error saat scraping halaman:", e)
        # break
    
    df = pd.DataFrame(job_data)
    save_csv_with_timestamp(df, folder='D:/Aries/PROJECT/scraping_data_job_posting/data/glints', prefix='raw_data')
    print("\n✅ Scraping Glints selesai dan file disimpan.")
    driver.quit()

    # Tahan program supaya browser tidak langsung tertutup
    input("✅ Scraping selesai. Tekan Enter untuk menutup browser...")

    driver.quit()
