import os, time, random, tempfile, requests
os.environ["PATH"] += os.pathsep + r"C:\Program Files\ffmpeg-2025-10-09-git-469aad3897-essentials_build\bin"
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pydub import AudioSegment
import whisper
from pydub import AudioSegment
import speech_recognition as sr
from pydub.utils import which

print("🎵 FFmpeg found at:", which("ffmpeg"))


def create_fake_pdf():
    pdf_path = os.path.join(tempfile.gettempdir(), "test_resume.pdf")
    try:
        c = canvas.Canvas(pdf_path, pagesize=letter)
        c.setFont("Helvetica", 12)
        c.drawString(100, 750, "Test Resume")
        c.drawString(100, 730, "Name: John Doe")
        c.drawString(100, 710, "Email: john.doe@example.com")
        c.drawString(100, 690, "Phone: 123-456-7890")
        c.drawString(100, 670, "This is a fake resume for testing purposes only.")
        c.save()
        print(f"📄 Created fake PDF at: {pdf_path}")
        return pdf_path
    except Exception as e:
        print(f"❌ Failed to create PDF: {e}")
        raise



# def alacrity_job_apply(
#     link: str,
#     wait_after_submit: int = 5,
#     keep_browser_open: bool = True,
# ):
#     resume_path = create_fake_pdf()
#     chrome_options = Options()
#     chrome_options.add_argument("--headless=new")
#     chrome_options.add_argument("--no-sandbox")
#     chrome_options.add_argument("--disable-dev-shm-usage")
#     chrome_options.add_argument(f"--user-data-dir={tempfile.mkdtemp()}")
#     chrome_options.add_argument("--disable-blink-features=AutomationControlled")
#     chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124")
#     chrome_options.add_argument("start-maximized")
#     chrome_options.add_argument("disable-infobars")
#     buster_crx_path = os.path.abspath("mpbjkejclgfgadiemmefgebjfooflfhl-3.1.0-www.Crx4Chrome.com.crx")
#     chrome_options.add_extension(buster_crx_path)
#     driver = None
#     try:
#         print(f"⏳ Initializing ChromeDriver from {ChromeDriverManager().install()}")
#         driver = webdriver.Chrome(
#             service=Service(ChromeDriverManager().install()), options=chrome_options
#         )
#     except Exception as e:
#         print(f"❌ Failed to initialize ChromeDriver: {e}")
#         try:
#             os.remove(resume_path)
#         except Exception:
#             pass
#         return False
#     try:
#         print(f"🌐 Opening browser and navigating to {link}")
#         driver.get(link)
#         wait = WebDriverWait(driver, 30)
#         print("🍪 Checking for cookie consent button...")
#         try:
#             consent_button = wait.until(
#                 EC.element_to_be_clickable(
#                     (By.CSS_SELECTOR, "button.tracking-consent-button.allow")
#                 )
#             )
#             actions = ActionChains(driver)
#             actions.move_to_element(consent_button).pause(random.uniform(0.5, 1.0)).click().perform()
#             print("✅ Clicked cookie consent 'Allow' button.")
#             time.sleep(1)
#         except Exception as e:
#             print(f"⚠️ Cookie consent button not found or not clickable: {e}. Continuing...")
#         print("⏳ Waiting for form to load...")
#         try:
#             wait.until(
#                 EC.presence_of_element_located(
#                     (By.CSS_SELECTOR, "div#resumator-application-form")
#                 )
#             )
#             print("✅ Form loaded.")
#         except Exception as e:
#             print(f"❌ Form not found: {e}")
#             return False
#         print("🖱️ Simulating human-like mouse movements...")
#         try:
#             body = driver.find_element(By.TAG_NAME, "body")
#             actions = ActionChains(driver)
#             actions.move_to_element_with_offset(body, 50, 50).pause(
#                 random.uniform(0.5, 1.5)
#             )
#             actions.move_by_offset(100, 100).pause(random.uniform(0.3, 0.8))
#             actions.move_by_offset(-50, 200).pause(random.uniform(0.4, 1.0))
#             actions.perform()
#         except Exception as e:
#             print(f"⚠️ Mouse movement simulation failed: {e}")
#         def safe_send(name, value):
#             try:
#                 el = driver.find_element(By.NAME, name)
#                 el.clear()
#                 for char in value:
#                     el.send_keys(char)
#                     time.sleep(random.uniform(0.05, 0.15))
#                 print(f"✍️ Filled field: {name}")
#             except Exception:
#                 print(f"⚠️ Field not found: {name}")
#         safe_send("resumator-firstname-value", "Muhammad")
#         safe_send("resumator-lastname-value", "Osman")
#         safe_send("resumator-email-value", "admin@gmail.com")
#         safe_send("resumator-phone-value", "1234567890")
#         safe_send("resumator-address-value", "123 Main Street")
#         safe_send("resumator-city-value", "London")
#         safe_send("resumator-state-value", "England")
#         safe_send("resumator-postal-value", "3000")
#         try:
#             upload_input = driver.find_element(By.NAME, "resumator-resume-value")
#             upload_input.send_keys(resume_path)
#             print(f"✅ Uploaded resume: {resume_path}")
#         except Exception:
#             print("⚠️ Resume upload failed. Check input name or file path.")
#         try:
#             print("🔒 Handling reCAPTCHA with Buster...")
#             wait = WebDriverWait(driver, 10)
#             captcha_iframe = wait.until(
#                 EC.frame_to_be_available_and_switch_to_it(
#                     (By.CSS_SELECTOR, "iframe[name^='a-'][src^='https://www.google.com/recaptcha/api2/anchor?']")
#                 )
#             )
#             print("🖱️ Switched to reCAPTCHA iframe.")
#             checkbox = wait.until(
#                 EC.element_to_be_clickable(
#                     (By.XPATH, "//span[@class='recaptcha-checkbox goog-inline-block recaptcha-checkbox-unchecked rc-anchor-checkbox']/div[@class='recaptcha-checkbox-checkmark']")
#                 )
#             )
#             actions = ActionChains(driver)
#             actions.move_to_element(checkbox).pause(random.uniform(0.5, 1.0)).click().perform()
#             print("✅ Clicked reCAPTCHA checkbox.")
#             driver.switch_to.default_content()
#             time.sleep(2)
#             try:
#                 audio_button = driver.find_elements(By.ID, "recaptcha-audio-button")
#                 if audio_button:
#                     print("🔊 Audio challenge detected. Triggering Buster to solve...")
#                     actions.move_to_element(audio_button[0]).pause(random.uniform(0.5, 1.0)).click().perform()
#                     print("✅ Clicked audio challenge button. Waiting for Buster to solve...")
#                     time.sleep(10)
#             except Exception as e:
#                 print(f"⚠️ Audio button check failed: {e}")
#             image_challenge = driver.find_elements(By.CSS_SELECTOR, "div.rc-imageselect")
#             if image_challenge:
#                 print("⚠️ Image challenge detected. Buster cannot solve this.")
#                 time.sleep(5)
#                 return False
#             time.sleep(3)
#             try:
#                 token = driver.find_element(By.ID, "g-recaptcha-response").get_attribute("value")
#                 if token:
#                     print("✅ reCAPTCHA token generated successfully.")
#                 else:
#                     raise Exception("reCAPTCHA token is empty; checkbox or audio challenge may not have been solved.")
#             except Exception as e:
#                 print(f"⚠️ Failed to verify reCAPTCHA token: {e}")
#                 time.sleep(5)
#                 return False
#         except Exception as e:
#             print(f"⚠️ reCAPTCHA handling failed: {e}")
#             driver.switch_to.default_content()
#             print("❌ CAPTCHA solving failed. Pausing for inspection.")
#             time.sleep(5)
#             return False
#         try:
#             print("⏳ Locating submit button...")
#             submit_btn = wait.until(
#                 EC.element_to_be_clickable(
#                     (By.CSS_SELECTOR, "a#resumator-submit-resume")
#                 )
#             )
#             ActionChains(driver).move_to_element(submit_btn).pause(
#                 random.uniform(0.5, 1.5)
#             ).click().perform()
#             print("🚀 Form submitted.")
#             time.sleep(wait_after_submit)
#             screenshot_path = os.path.join(
#                 tempfile.gettempdir(), "application_result.png"
#             )
#             driver.save_screenshot(screenshot_path)
#             print(f"📸 Screenshot saved at {screenshot_path}")
#         except Exception as e:
#             print(f"⚠️ Submit button not found: {e}. Check selector or submit manually.")
#             time.sleep(5)
#             return False
#         time.sleep(5)
#         return True
#     except Exception as e:
#         print(f"❌ Error during automation: {e}")
#         time.sleep(5)
#         return False
#     finally:
#         try:
#             if driver:
#                 driver.quit()
#                 print("🧹 Browser closed.")
#         except Exception:
#             pass
#         try:
#             os.remove(resume_path)
#             print(f"🗑️ Deleted fake PDF: {resume_path}")
#         except Exception:
#             print(f"⚠️ Could not delete fake PDF: {resume_path}")



# def alacrity_job_apply(
#     link: str,
#     wait_after_submit: int = 5,
#     keep_browser_open: bool = True,
# ):
#     resume_path = create_fake_pdf()
#     chrome_options = Options()
#     # chrome_options.add_argument("--headless=new")
#     chrome_options.add_argument("--no-sandbox")
#     chrome_options.add_argument("--disable-dev-shm-usage")
#     chrome_options.add_argument(f"--user-data-dir={tempfile.mkdtemp()}")
#     chrome_options.add_argument("--disable-blink-features=AutomationControlled")
#     chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124")
#     chrome_options.add_argument("start-maximized")
#     chrome_options.add_argument("disable-infobars")
    
#     buster_crx_path = os.path.abspath("mpbjkejclgfgadiemmefgebjfooflfhl-3.1.0-www.Crx4Chrome.com.crx")  
#     chrome_options.add_extension(buster_crx_path)

#     try:
#         print(f"⏳ Initializing ChromeDriver from {ChromeDriverManager().install()}")
#         driver = webdriver.Chrome(
#             service=Service(ChromeDriverManager().install()), options=chrome_options
#         )
#     except Exception as e:
#         print(f"❌ Failed to initialize ChromeDriver: {e}")
#         return

#     try:
#         print(f"🌐 Opening browser and navigating to {link}")
#         driver.get(link)
#         wait = WebDriverWait(driver, 30)

#         # Handle cookie consent button
#         print("🍪 Checking for cookie consent button...")
#         try:
#             consent_button = wait.until(
#                 EC.element_to_be_clickable(
#                     (By.CSS_SELECTOR, "button.tracking-consent-button.allow")
#                 )
#             )
#             actions = ActionChains(driver)
#             actions.move_to_element(consent_button).pause(random.uniform(0.5, 1.0)).click().perform()
#             print("✅ Clicked cookie consent 'Allow' button.")
#             time.sleep(1)  # Brief wait for page to stabilize
#         except Exception as e:
#             print(f"⚠️ Cookie consent button not found or not clickable: {e}. Continuing...")

#         print("⏳ Waiting for form to load...")
#         try:
#             wait.until(
#                 EC.presence_of_element_located(
#                     (By.CSS_SELECTOR, "div#resumator-application-form")
#                 )
#             )
#             print("✅ Form loaded.")
#         except Exception as e:
#             print(f"❌ Form not found: {e}")
#             return

#         print("🖱️ Simulating human-like mouse movements...")
#         try:
#             body = driver.find_element(By.TAG_NAME, "body")
#             actions = ActionChains(driver)
#             actions.move_to_element_with_offset(body, 50, 50).pause(
#                 random.uniform(0.5, 1.5)
#             )
#             actions.move_by_offset(100, 100).pause(random.uniform(0.3, 0.8))
#             actions.move_by_offset(-50, 200).pause(random.uniform(0.4, 1.0))
#             actions.perform()
#         except Exception as e:
#             print(f"⚠️ Mouse movement simulation failed: {e}")

#         def safe_send(name, value):
#             try:
#                 el = driver.find_element(By.NAME, name)
#                 el.clear()
#                 for char in value:
#                     el.send_keys(char)
#                     time.sleep(random.uniform(0.05, 0.15))
#                 print(f"✍️ Filled field: {name}")
#             except Exception:
#                 print(f"⚠️ Field not found: {name}")

#         safe_send("resumator-firstname-value", "Muhammad")
#         safe_send("resumator-lastname-value", "Osman")
#         safe_send("resumator-email-value", "admin@gmail.com")
#         safe_send("resumator-phone-value", "1234567890")
#         safe_send("resumator-address-value", "123 Main Street")
#         safe_send("resumator-city-value", "London")
#         safe_send("resumator-state-value", "England")
#         safe_send("resumator-postal-value", "3000")

#         try:
#             upload_input = driver.find_element(By.NAME, "resumator-resume-value")
#             upload_input.send_keys(resume_path)
#             print(f"✅ Uploaded resume: {resume_path}")
#         except Exception:
#             print("⚠️ Resume upload failed. Check input name or file path.")

#         try:
#             print("🔒 Handling reCAPTCHA with Buster...")
#             wait = WebDriverWait(driver, 10)
#             # Locate the reCAPTCHA iframe
#             captcha_iframe = wait.until(
#                 EC.frame_to_be_available_and_switch_to_it(
#                     (By.CSS_SELECTOR, "iframe[name^='a-'][src^='https://www.google.com/recaptcha/api2/anchor?']")
#                 )
#             )
#             print("🖱️ Switched to reCAPTCHA iframe.")

#             # Locate and click the checkbox
#             checkbox = wait.until(
#                 EC.element_to_be_clickable(
#                     (By.XPATH, "//span[@class='recaptcha-checkbox goog-inline-block recaptcha-checkbox-unchecked rc-anchor-checkbox']/div[@class='recaptcha-checkbox-checkmark']")
#                 )
#             )
#             actions = ActionChains(driver)
#             actions.move_to_element(checkbox).pause(random.uniform(0.5, 1.0)).click().perform()
#             print("✅ Clicked reCAPTCHA checkbox.")
#             driver.switch_to.default_content()

#             # Check if audio challenge is triggered and let Buster solve it
#             time.sleep(2)  # Wait for potential challenge
#             try:
#                 audio_button = driver.find_elements(By.ID, "recaptcha-audio-button")
#                 if audio_button:
#                     print("🔊 Audio challenge detected. Triggering Buster to solve...")
#                     actions.move_to_element(audio_button[0]).pause(random.uniform(0.5, 1.0)).click().perform()
#                     print("✅ Clicked audio challenge button. Waiting for Buster to solve...")
#                     time.sleep(10)  # Give Buster time to solve (adjust as needed)
#             except Exception as e:
#                 print(f"⚠️ Audio button check failed: {e}")

#             # Check for image challenge (unsupported by Buster)
#             image_challenge = driver.find_elements(By.CSS_SELECTOR, "div.rc-imageselect")
#             if image_challenge:
#                 print("⚠️ Image challenge detected. Buster cannot solve this.")
#                 if keep_browser_open:
#                     print("⏳ Browser will remain open for inspection. Press Enter to close...")
#                     input()
#                 return

#             # Verify token
#             time.sleep(3)  # Wait for token generation
#             try:
#                 token = driver.find_element(By.ID, "g-recaptcha-response").get_attribute("value")
#                 if token:
#                     print("✅ reCAPTCHA token generated successfully.")
#                 else:
#                     raise Exception("reCAPTCHA token is empty; checkbox or audio challenge may not have been solved.")
#             except Exception as e:
#                 print(f"⚠️ Failed to verify reCAPTCHA token: {e}")
#                 if keep_browser_open:
#                     print("⏳ Browser will remain open for inspection. Press Enter to close...")
#                     input()
#                 return

#         except Exception as e:
#             print(f"⚠️ reCAPTCHA handling failed: {e}")
#             driver.switch_to.default_content()
#             print("❌ CAPTCHA solving failed. Pausing for inspection.")
#             if keep_browser_open:
#                 print("⏳ Browser will remain open. Press Enter to continue or close manually...")
#                 input()
#             return

#         try:
#             print("⏳ Locating submit button...")
#             submit_btn = wait.until(
#                 EC.element_to_be_clickable(
#                     (By.CSS_SELECTOR, "a#resumator-submit-resume")
#                 )
#             )
#             ActionChains(driver).move_to_element(submit_btn).pause(
#                 random.uniform(0.5, 1.5)
#             ).click().perform()
#             print("🚀 Form submitted.")
#             time.sleep(wait_after_submit)
#             screenshot_path = os.path.join(
#                 tempfile.gettempdir(), "application_result.png"
#             )
#             driver.save_screenshot(screenshot_path)
#             print(f"📸 Screenshot saved at {screenshot_path}")
#         except Exception as e:
#             print(f"⚠️ Submit button not found: {e}. Check selector or submit manually.")
#             if keep_browser_open:
#                 print(
#                     "⏳ Browser will remain open for inspection. Press Enter to close..."
#                 )
#                 input()
#             return

#         if keep_browser_open:
#             print("⏳ Browser will remain open. Press Enter to close...")
#             input()

#     except Exception as e:
#         print(f"❌ Error during automation: {e}")
#         if keep_browser_open:
#             print("⏳ Browser will remain open. Press Enter to close...")
#             input()

#     finally:
#         driver.quit()
#         print("🧹 Browser closed.")
#         try:
#             os.remove(resume_path)
#             print(f"🗑️ Deleted fake PDF: {resume_path}")
#         except Exception:
#             print(f"⚠️ Could not delete fake PDF: {resume_path}")






def transcribe_audio_captcha(audio_path):
    try:
        recognizer = sr.Recognizer()
        sound = AudioSegment.from_mp3(audio_path)
        wav_path = audio_path.replace(".mp3", ".wav")
        sound.export(wav_path, format="wav")
        with sr.AudioFile(wav_path) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio)
        return text.strip()
    except Exception as e:
        print("audio path",audio_path)
        print("❌ Audio CAPTCHA solving failed:", e)
        return None

def solve_audio_recaptcha(driver, wait, max_attempts=5):
    try:
        wait.until(EC.frame_to_be_available_and_switch_to_it(
            (By.CSS_SELECTOR, "iframe[src*='anchor']")))
        checkbox = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "div.recaptcha-checkbox-border")))
        checkbox.click()
        driver.switch_to.default_content()
        time.sleep(2)
        wait.until(EC.frame_to_be_available_and_switch_to_it(
            (By.CSS_SELECTOR, "iframe[src*='bframe']")))
        audio_btn = wait.until(EC.element_to_be_clickable((By.ID, "recaptcha-audio-button")))
        audio_btn.click()
        time.sleep(1)
        for attempt in range(1, max_attempts + 1):
            print(f"🎧 Attempt {attempt}/{max_attempts}: downloading audio challenge...")
            audio_el = wait.until(EC.presence_of_element_located((By.TAG_NAME, "audio")))
            src = audio_el.get_attribute("src")
            if not src:
                print("❌ No audio src found, maybe verification passed.")
                driver.switch_to.default_content()
                return True
            tmp_mp3 = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
            r = requests.get(src, stream=True, timeout=15)
            with open(tmp_mp3, "wb") as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
            text = transcribe_audio_captcha(tmp_mp3)
            if not text:
                print("❌ Could not transcribe audio. Retrying with next challenge...")
                try:
                    reload_btn = wait.until(EC.element_to_be_clickable((By.ID, "recaptcha-reload-button")))
                    reload_btn.click()
                    time.sleep(2)
                    continue
                except:
                    break

            print(f"✅ Transcribed: {text}")
            input_box = wait.until(EC.presence_of_element_located((By.ID, "audio-response")))
            input_box.clear()
            for ch in text:
                input_box.send_keys(ch)
                time.sleep(0.02)
            verify_btn = driver.find_element(By.ID, "recaptcha-verify-button")
            verify_btn.click()
            time.sleep(3)
            driver.switch_to.default_content()
            time.sleep(2)
            try:
                wait.until(EC.frame_to_be_available_and_switch_to_it(
                    (By.CSS_SELECTOR, "iframe[src*='anchor']")))
                checked = driver.find_element(By.CSS_SELECTOR, "span.recaptcha-checkbox-checked")
                if checked:
                    print("✅ Audio CAPTCHA solved successfully.")
                    driver.switch_to.default_content()
                    return True
            except:
                driver.switch_to.default_content()
                wait.until(EC.frame_to_be_available_and_switch_to_it(
                    (By.CSS_SELECTOR, "iframe[src*='bframe']")))
                print("🔁 New audio challenge detected. Retrying...")
        print("❌ Failed after multiple attempts.")
        driver.switch_to.default_content()
        return False
    except Exception as e:
        driver.switch_to.default_content()
        print(f"❌ Audio CAPTCHA solving failed: {e}")
        return False


def alacrity_job_apply(link: str, wait_after_submit: int = 5):
    resume_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
    with open(resume_path, "wb") as f:
        f.write(b"%PDF-1.4 Dummy Resume PDF")
    chrome_options = Options()
    # chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"--user-data-dir={tempfile.mkdtemp()}")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("disable-infobars")

    try:
        print(f"⏳ Initializing ChromeDriver from {ChromeDriverManager().install()}")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    except Exception as e:
        print(f"❌ Failed to initialize ChromeDriver: {e}")
        return

    try:
        print(f"🌐 Opening browser and navigating to {link}")
        driver.get(link)
        wait = WebDriverWait(driver, 30)

        try:
            consent_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.tracking-consent-button.allow")))
            ActionChains(driver).move_to_element(consent_button).pause(random.uniform(0.5, 1.0)).click().perform()
            time.sleep(1)
        except:
            pass

        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div#resumator-application-form")))
        except:
            print("❌ Form not found")
            return

        def safe_send(name, value):
            try:
                el = driver.find_element(By.NAME, name)
                el.clear()
                for c in value:
                    el.send_keys(c)
                    time.sleep(random.uniform(0.05, 0.15))
            except:
                pass

        # Fill the form
        safe_send("resumator-firstname-value", "Muhammad")
        safe_send("resumator-lastname-value", "Osman")
        safe_send("resumator-email-value", "admin@gmail.com")
        safe_send("resumator-phone-value", "1234567890")
        safe_send("resumator-address-value", "123 Main Street")
        safe_send("resumator-city-value", "London")
        safe_send("resumator-state-value", "England")
        safe_send("resumator-postal-value", "3000")

        try:
            upload_input = driver.find_element(By.NAME, "resumator-resume-value")
            upload_input.send_keys(resume_path)
        except:
            pass

        print("🔒 Solving reCAPTCHA via audio challenge...")
        audio_captcha_solver = solve_audio_recaptcha(driver, wait)
        if not audio_captcha_solver:
            print("❌ CAPTCHA solving failed")
            return

        try:
            submit_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a#resumator-submit-resume")))
            ActionChains(driver).move_to_element(submit_btn).pause(random.uniform(0.5, 1.5)).click().perform()
            time.sleep(wait_after_submit)
            screenshot_path = os.path.join(tempfile.gettempdir(), "application_result.png")
            driver.save_screenshot(screenshot_path)
            print(f"📸 Screenshot saved at {screenshot_path}")
        except:
            pass

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        driver.quit()
        try:
            os.remove(resume_path)
        except:
            pass






def create_fake_pdf():
    pdf_path = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False).name
    try:
        c = canvas.Canvas(pdf_path, pagesize=letter)
        c.setFont("Helvetica", 12)
        c.drawString(100, 750, "Fake Resume - John Doe")
        c.drawString(100, 735, "Email: johndoe@example.com")
        c.drawString(100, 720, "Phone: 123-456-7890")
        c.drawString(100, 705, "Experience: 3 years in software development.")
        c.save()
        print(f"📄 Created fake PDF at: {pdf_path}")
        return pdf_path
    except Exception as e:
        print(f"❌ Failed to create PDF: {e}")
        raise

def simulate_human_interactions(driver):
    try:
        print("🖱️ Simulating human-like interactions...")
        body = driver.find_element(By.TAG_NAME, "body")
        actions = ActionChains(driver)
        actions.move_to_element_with_offset(body, 50, 50).pause(random.uniform(0.5, 1.5))
        actions.move_by_offset(100, 100).pause(random.uniform(0.3, 0.8))
        actions.move_by_offset(-50, 200).pause(random.uniform(0.4, 1.0))
        actions.move_by_offset(150, -100).pause(random.uniform(0.5, 1.2))
        driver.execute_script("window.scrollBy(0, 300);")
        time.sleep(random.uniform(0.5, 1.0))
        driver.execute_script("window.scrollBy(0, -100);")
        time.sleep(random.uniform(0.3, 0.8))
        try:
            form_elements = driver.find_elements(By.CSS_SELECTOR, "input, textarea")
            if form_elements:
                actions.move_to_element(random.choice(form_elements)).pause(random.uniform(0.5, 1.0)).perform()
        except Exception:
            pass
        actions.perform()
        print("✅ Completed human-like interactions.")
    except Exception as e:
        print(f"⚠️ Interaction simulation failed: {e}")


def crsth_job_apply(link: str, keep_browser_open: bool = True, wait_after_submit: int = 10):
    pdf_path = create_fake_pdf()
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"--user-data-dir={tempfile.mkdtemp()}")
    driver = None

    try:
        print(f"⏳ Initializing ChromeDriver from {ChromeDriverManager().install()}")
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), 
            options=chrome_options
        )
    except Exception as e:
        print(f"❌ Failed to initialize webdriver: {e}")
        return

    try:
        print(f"🌐 Opening browser and navigating to {link}")
        driver.get(link)
        wait = WebDriverWait(driver, 30)

        # ✅ Handle cookie consent
        try:
            print("🍪 Checking for cookie consent button...")
            cookie_btn = wait.until(
                EC.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    "button.cookie-consent__accept-button.atsPrimaryButton.buttonSmall.primaryButtonTextColor.primaryButtonFillColor.font-weight-bold"
                ))
            )
            actions = ActionChains(driver)
            actions.move_to_element(cookie_btn).pause(random.uniform(0.5, 1.0)).click().perform()
            print("✅ Cookie consent accepted.")
            time.sleep(2)
        except Exception as e:
            print(f"⚠️ Cookie consent button not found or already accepted: {e}")

        print("⏳ Waiting for form to load...")
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "form.quickApplyApplicationForm")))
            print("✅ Form loaded.")
        except Exception as e:
            print(f"❌ Form not found: {e}")
            return

        simulate_human_interactions(driver)

        def fill_field(name, value):
            try:
                el = driver.find_element(By.NAME, name)
                el.clear()
                actions = ActionChains(driver)
                actions.move_to_element(el).pause(random.uniform(0.3, 0.8)).click().perform()
                for char in value:
                    el.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.15))
                print(f"✍️ Filled field: {name}")
            except Exception:
                print(f"⚠️ Field not found: {name}")

        # Fill the form
        fill_field("firstName", "Muhammad")
        fill_field("lastName", "Osman")
        fill_field("email", "admin@gmail.com")
        fill_field("confirmEmail", "admin@gmail.com")
        fill_field("phone", "2349596586")

        try:
            radio = driver.find_element(By.NAME, "phone1TextMessageOptIn")
            driver.execute_script("arguments[0].click();", radio)
            print("✅ Selected radio: phone1TextMessageOptIn")
        except Exception as e:
            print(f"⚠️ Failed to select radio: {e}")

        try:
            upload_input = driver.find_element(By.NAME, "resume_desktop[]")
            upload_input.send_keys(pdf_path)
            print(f"✅ Uploaded fake resume: {pdf_path}")
        except Exception:
            print("⚠️ Resume upload failed. Check input name or file path.")

        # Check for reCAPTCHA v2 checkbox
        try:
            print("🔒 Checking for reCAPTCHA checkbox...")
            captcha_iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[title='reCAPTCHA']")))
            actions = ActionChains(driver)
            actions.move_to_element(captcha_iframe).pause(random.uniform(1.0, 2.0)).perform()
            print("🖱️ Hovered over reCAPTCHA iframe.")

            driver.switch_to.frame(captcha_iframe)
            checkbox = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.recaptcha-checkbox-border")))
            actions = ActionChains(driver)
            actions.move_to_element(checkbox).pause(random.uniform(0.5, 1.5))
            actions.move_by_offset(5, 5).pause(random.uniform(0.3, 0.8))
            actions.move_to_element(checkbox).pause(random.uniform(0.5, 1.0))
            actions.click().perform()
            print("✅ Clicked reCAPTCHA checkbox.")

            driver.switch_to.default_content()
            time.sleep(3)
            if driver.find_elements(By.CSS_SELECTOR, "div.recaptcha-checkbox-checked"):
                print("✅ CAPTCHA appears solved.")
            else:
                raise Exception("Checkbox click didn't solve CAPTCHA; likely requires image challenge.")
        except Exception as e:
            print(f"⚠️ No reCAPTCHA checkbox found or click failed: {e}. Assuming invisible CAPTCHA or no CAPTCHA.")

        # Simulate more interactions before submission
        simulate_human_interactions(driver)

        # Submit form
        try:
            print("⏳ Locating submit button...")
            submit_btn = wait.until(EC.element_to_be_clickable((By.NAME, "quickApplyApplicationSubmit")))
            actions = ActionChains(driver)
            actions.move_to_element(submit_btn).pause(random.uniform(0.5, 1.5)).click().perform()
            print("🚀 Form submitted.")
            time.sleep(wait_after_submit)
            screenshot_path = os.path.join(tempfile.gettempdir(), "application_result.png")
            driver.save_screenshot(screenshot_path)
            print(f"📸 Screenshot saved at {screenshot_path}")
        except Exception as e:
            print(f"⚠️ Submit button not found or click failed: {e}")
            if keep_browser_open:
                print("⏳ Browser will remain open for inspection. Press Enter to close...")
                input()
            return

        if keep_browser_open:
            print("⏳ Browser will remain open. Press Enter to close...")
            input()

    except Exception as e:
        print(f"❌ Error during job application: {e}")
        if keep_browser_open:
            print("⏳ Browser will remain open for inspection. Press Enter to close...")
            input()
    finally:
        if driver:
            driver.quit()
            print("🧹 Browser closed.")
        try:
            os.remove(pdf_path)
            print(f"🗑️ Deleted fake PDF: {pdf_path}")
        except Exception:
            print(f"⚠️ Could not delete fake PDF: {pdf_path}")
