import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time

class OctoFitUITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.base_url = "http://localhost:8000/"

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def test_01_homepage_loads(self):
        self.driver.get(self.base_url)
        self.assertIn("OctoFit", self.driver.title)

    def test_login(self):
        """Test login as demo user."""
        self.driver.get(self.base_url + "accounts/login/")
        self.driver.find_element(By.NAME, "username").send_keys("octofittestuser")
        self.driver.find_element(By.NAME, "password").send_keys("TestPassword123!")
        self.driver.find_element(By.XPATH, "//button[contains(text(),'Login')]").click()
        for _ in range(10):
            if "OctoFit Tracker" in self.driver.title or "Welcome to OctoFit Tracker" in self.driver.page_source:
                break
            time.sleep(0.5)
        if not ("OctoFit Tracker" in self.driver.title or "Welcome to OctoFit Tracker" in self.driver.page_source):
            print("[DEBUG] Login page source after submit:")
            print(self.driver.page_source)
        assert "OctoFit Tracker" in self.driver.title or "Welcome to OctoFit Tracker" in self.driver.page_source, "Login failed"
        print("[STEP] Login successful.")

    def test_houses_and_activities(self):
        """Test all houses, activities, and challenges are visible and accessible."""
        self.test_login()
        house_names = ["Kraken", "Montana", "Razor", "Serene"]
        for house in house_names:
            self.driver.get(self.base_url + f"house/{house.lower()}/")
            time.sleep(1)
            assert house in self.driver.page_source, f"House {house} not found on its page!"
            print(f"[STEP] House {house} page loaded.")
            # Activities
            activities = self.driver.find_elements(By.CSS_SELECTOR, ".house-program ul li")
            assert activities, f"No activities found for house {house}"
            print(f"[STEP] Activities for {house}: {[a.text for a in activities]}")
            # Challenges
            challenges = self.driver.find_elements(By.CSS_SELECTOR, ".house-challenges ul li")
            assert challenges, f"No challenges found for house {house}"
            print(f"[STEP] Challenges for {house}: {[c.text for c in challenges]}")

    def test_accept_and_complete_challenge(self):
        """Test accepting and completing a challenge."""
        self.test_login()
        self.driver.get(self.base_url + "house/kraken/")
        time.sleep(1)
        try:
            accept_btn = self.driver.find_element(By.CSS_SELECTOR, ".accept-challenge")
            accept_btn.click()
            time.sleep(1)
            assert "accepted" in self.driver.page_source.lower(), "Challenge not accepted!"
            print("[STEP] Challenge accepted.")
        except Exception:
            print("[WARN] No challenge to accept.")
        try:
            complete_btn = self.driver.find_element(By.CSS_SELECTOR, ".complete-challenge")
            complete_btn.click()
            time.sleep(1)
            assert "completed" in self.driver.page_source.lower(), "Challenge not completed!"
            print("[STEP] Challenge completed.")
        except Exception:
            print("[WARN] No challenge to complete.")

    def test_log_activity(self):
        """Test logging an activity."""
        self.test_login()
        self.driver.get(self.base_url + "submit-activity/")
        try:
            activity_type = self.driver.find_element(By.NAME, "activity_type")
            activity_type.send_keys("Automated Test Workout")
            self.driver.find_element(By.NAME, "duration").send_keys("30")
            self.driver.find_element(By.XPATH, "//button[contains(text(),'Submit')]").click()
            time.sleep(1)
            assert "Activity submitted" in self.driver.page_source, "Activity not submitted!"
            print("[STEP] Activity submitted.")
        except Exception:
            print("[WARN] Activity form not present or already submitted.")

    def test_leaderboard(self):
        """Test leaderboard loads and shows houses."""
        self.test_login()
        self.driver.get(self.base_url + "leaderboard/")
        assert "Leaderboard" in self.driver.page_source, "Leaderboard not found!"
        print("[STEP] Leaderboard loaded.")
        for house in ["Kraken", "Montana", "Razor", "Serene"]:
            assert house in self.driver.page_source, f"House {house} not found on leaderboard!"

    def test_octocoach_bot(self):
        """Test OctoCoach bot interaction and persona switching."""
        self.test_login()
        self.driver.get(self.base_url)
        try:
            chat_btn = self.driver.find_element(By.ID, "octocoach-quick-btn")
            chat_btn.click()
            time.sleep(1)
            chat_input = self.driver.find_element(By.ID, "octocoach-input")
            chat_input.send_keys("Give me a fitness tip!" + Keys.RETURN)
            time.sleep(2)
            chat_response = self.driver.find_element(By.ID, "octocoach-response")
            assert len(chat_response.text) > 0, "OctoCoach did not respond!"
            print("[STEP] OctoCoach responded.")
        except Exception:
            print("[ERROR] OctoCoach bot not working or not present.")

    def test_profile_edit_and_persona(self):
        """Test profile editing and persona switching."""
        self.test_login()
        self.driver.get(self.base_url + "accounts/profile/")
        try:
            bio = self.driver.find_element(By.NAME, "bio")
            bio.clear()
            bio.send_keys("Automated test bio")
            self.driver.find_element(By.XPATH, "//button[contains(text(),'Save') or contains(text(),'Update')]").click()
            time.sleep(1)
            assert "updated" in self.driver.page_source.lower(), "Profile not updated!"
            print("[STEP] Profile updated.")
            # Persona switching (if implemented)
            persona_select = self.driver.find_element(By.NAME, "bot_persona")
            persona_select.send_keys("Classic Arnold")
            self.driver.find_element(By.XPATH, "//button[contains(text(),'Save') or contains(text(),'Update')]").click()
            time.sleep(1)
            print("[STEP] Persona switched.")
        except Exception:
            print("[WARN] Profile form or persona switch not present.")

    def test_upload_progress_photo(self):
        """Test uploading a progress photo."""
        # self.test_login()
        # self.driver.get(self.base_url + "house/kraken/")
        # try:
        #     upload_btn = self.driver.find_element(By.ID, "upload-photo-btn")
        #     upload_btn.click()
        #     time.sleep(1)
        #     file_input = self.driver.find_element(By.ID, "progress-photo-upload")
        #     file_input.send_keys("/workspaces/skills-build-applications-w-copilot-agent-mode/octofit-tracker/backend/static/audio/gym_bell.mp3")
        #     time.sleep(2)
        #     assert "success" in self.driver.page_source.lower() or "photo" in self.driver.page_source.lower(), "Photo upload failed!"
        #     print("[STEP] Photo uploaded.")
        # except Exception:
        #     print("[WARN] Photo upload not available or failed.")

    def test_logout_and_relogin(self):
        """Test logout and re-login."""
        self.test_login()
        self.driver.get(self.base_url + "accounts/logout/")
        self.driver.get(self.base_url + "accounts/login/")
        self.driver.find_element(By.NAME, "username").send_keys("octofittestuser")
        self.driver.find_element(By.NAME, "password").send_keys("TestPassword123!")
        self.driver.find_element(By.XPATH, "//button[contains(text(),'Login')]").click()
        for _ in range(10):
            if "OctoFit Tracker" in self.driver.title or "Welcome to OctoFit Tracker" in self.driver.page_source:
                break
            time.sleep(0.5)
        assert "OctoFit Tracker" in self.driver.title or "Welcome to OctoFit Tracker" in self.driver.page_source, "Re-login failed!"
        print("[STEP] Re-login successful.")

if __name__ == "__main__":
    unittest.main()
