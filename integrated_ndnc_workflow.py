"""
Complete NDNC Workflow
1. Download Review Pending complaints Excel → Extract PDFs to NDNC/review_pending/
2. For Open complaints: Use existing automation (search from NDNC/open/ folder)
"""

import os
import time
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class NDNCCompleteWorkflow:
    def __init__(self, email: str, download_dir: str):
        """
        Initialize the complete NDNC workflow
        
        Args:
            email: Email address for login
            download_dir: Directory where files will be downloaded
        """
        self.email = email
        self.download_dir = Path(download_dir)
        self.ndnc_folder = self.download_dir / "NDNC"
        self.review_pending_folder = self.ndnc_folder / "review_pending"
        self.open_folder = self.ndnc_folder / "open"
        self.base_url = "https://dashboard.ndnc.exotel.com"
        self.driver = None
        
        # Create folders if they don't exist
        self.ndnc_folder.mkdir(exist_ok=True)
        self.review_pending_folder.mkdir(exist_ok=True)
        self.open_folder.mkdir(exist_ok=True)
        
        print(f"✓ NDNC folders created:")
        print(f"  • Review Pending: {self.review_pending_folder}")
        print(f"  • Open: {self.open_folder}")
    
    def start_browser(self):
        """Start Chrome browser with download preferences"""
        options = webdriver.ChromeOptions()
        
        # Set download directory
        prefs = {
            "download.default_directory": str(self.download_dir),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        options.add_experimental_option("prefs", prefs)
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.maximize_window()
        print("✓ Browser started")
    
    def login(self):
        """Handle the login process"""
        try:
            print(f"\n→ Navigating to login page...")
            self.driver.get(f"{self.base_url}/login")
            time.sleep(2)
            
            print(f"→ Entering email: {self.email}")
            wait = WebDriverWait(self.driver, 10)
            email_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"]')))
            
            for char in self.email:
                email_input.send_keys(char)
                time.sleep(0.1)
            
            time.sleep(0.5)
            
            print(f"→ Clicking Continue button...")
            continue_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            continue_button.click()
            
            print(f"\n⏳ PLEASE ENTER OTP IN THE BROWSER WINDOW")
            print(f"   Waiting for login to complete (180 seconds timeout)...")
            
            WebDriverWait(self.driver, 180).until(
                EC.url_contains("/dashboard")
            )
            print("✓ Login successful!")
            time.sleep(2)
            return True
                
        except Exception as e:
            print(f"✗ Login error: {str(e)}")
            return False
    
    def navigate_to_complaints(self):
        """Navigate to All Complaints page"""
        try:
            print("\n→ Navigating to All Complaints...")
            time.sleep(5)
            
            wait = WebDriverWait(self.driver, 20)
            
            # Try multiple selectors
            selectors = [
                (By.CSS_SELECTOR, 'a[href="/all-complaints"]'),
                (By.XPATH, '//a[contains(@href, "all-complaints")]'),
            ]
            
            for selector_type, selector_value in selectors:
                try:
                    button = wait.until(EC.element_to_be_clickable((selector_type, selector_value)))
                    button.click()
                    time.sleep(3)
                    print("✓ Arrived at All Complaints page")
                    return True
                except:
                    continue
            
            # Fallback: direct navigation
            self.driver.get(f"{self.base_url}/all-complaints")
            time.sleep(3)
            print("✓ Arrived at All Complaints page")
            return True
            
        except Exception as e:
            print(f"✗ Error navigating: {str(e)}")
            return False
    
    def select_status_filter(self, status: str):
        """
        Select status filter (Review Pending or open)
        
        Args:
            status: "Review Pending" or "open"
        """
        try:
            print(f"\n→ Selecting status filter: {status}")
            wait = WebDriverWait(self.driver, 10)
            
            # Click the status dropdown
            dropdown_selectors = [
                (By.XPATH, '//button[@role="combobox" and @data-slot="select-trigger"]'),
                (By.CSS_SELECTOR, 'button[role="combobox"][data-slot="select-trigger"]'),
            ]
            
            dropdown = None
            for selector_type, selector_value in dropdown_selectors:
                try:
                    dropdown = wait.until(EC.element_to_be_clickable((selector_type, selector_value)))
                    break
                except:
                    continue
            
            if not dropdown:
                print("✗ Could not find status dropdown")
                return False
            
            dropdown.click()
            time.sleep(1)
            
            # Select the desired status from dropdown options
            option_selectors = [
                (By.XPATH, f'//div[@role="option"]//span[text()="{status}"]'),
                (By.XPATH, f'//*[@role="option" and contains(., "{status}")]'),
            ]
            
            for selector_type, selector_value in option_selectors:
                try:
                    option = wait.until(EC.element_to_be_clickable((selector_type, selector_value)))
                    option.click()
                    time.sleep(2)
                    print(f"✓ Selected status: {status}")
                    return True
                except:
                    continue
            
            print(f"✗ Could not select status: {status}")
            return False
            
        except Exception as e:
            print(f"✗ Error selecting status: {str(e)}")
            return False
    
    def click_download_button(self):
        """Click the Download button to download Excel file"""
        try:
            print(f"→ Clicking Download button...")
            wait = WebDriverWait(self.driver, 10)
            
            # Find download button
            download_selectors = [
                (By.XPATH, '//button[.//svg[contains(@class, "lucide-download")] and .//span[text()="Download"]]'),
                (By.XPATH, '//button[.//span[text()="Download"]]'),
                (By.CSS_SELECTOR, 'button[data-slot="tooltip-trigger"]'),
            ]
            
            download_button = None
            for selector_type, selector_value in download_selectors:
                try:
                    download_button = wait.until(EC.element_to_be_clickable((selector_type, selector_value)))
                    # Check if this button has download icon or text
                    if 'download' in download_button.get_attribute('innerHTML').lower():
                        break
                except:
                    continue
            
            if not download_button:
                print("✗ Could not find Download button")
                return False
            
            download_button.click()
            print("✓ Download button clicked")
            
            # Wait for download to complete
            print("⏳ Waiting for download to complete (15 seconds)...")
            time.sleep(15)
            
            return True
            
        except Exception as e:
            print(f"✗ Error clicking download: {str(e)}")
            return False
    
    def get_latest_excel_file(self):
        """Get the most recently downloaded Excel file"""
        try:
            excel_files = list(self.download_dir.glob("complaints*.xlsx"))
            
            if not excel_files:
                print("✗ No Excel files found in downloads")
                return None
            
            # Get the most recent file
            latest_file = max(excel_files, key=lambda x: x.stat().st_mtime)
            print(f"✓ Found Excel file: {latest_file.name}")
            return latest_file
            
        except Exception as e:
            print(f"✗ Error finding Excel file: {str(e)}")
            return None
    
    def process_review_pending_excel(self, excel_path: Path):
        """
        Process Review Pending Excel file and download PDFs from Document Link column
        
        Args:
            excel_path: Path to the Excel file
        """
        try:
            print(f"\n{'='*60}")
            print(f"📊 PROCESSING REVIEW PENDING EXCEL")
            print(f"{'='*60}")
            
            # Read Excel file
            print(f"→ Reading Excel file: {excel_path.name}")
            df = pd.read_excel(excel_path)
            
            print(f"✓ Found {len(df)} rows")
            
            # Find Document Link column
            url_column = 'Document Link'
            if url_column not in df.columns:
                print(f"✗ 'Document Link' column not found")
                print(f"   Available columns: {list(df.columns)}")
                return 0
            
            # Find Complainer No column
            contact_column = 'Complainer No'
            if contact_column not in df.columns:
                print(f"✗ 'Complainer No' column not found")
                return 0
            
            # Find Date of call/sms column
            date_column = 'Date of call/sms'
            if date_column not in df.columns:
                print(f"⚠️  'Date of call/sms' column not found, will use timestamp")
                date_column = None
            
            print(f"✓ Using columns:")
            print(f"   • Document Link: {url_column}")
            print(f"   • Contact Number: {contact_column}")
            if date_column:
                print(f"   • Date: {date_column}")
            
            # Process each row
            downloaded_count = 0
            for idx, row in df.iterrows():
                try:
                    url = row[url_column]
                    
                    if pd.isna(url) or not url or str(url).strip() == '':
                        continue
                    
                    # Get contact number
                    contact_number = str(row[contact_column])
                    
                    if pd.isna(contact_number) or contact_number == 'nan':
                        continue
                    
                    # Clean contact number
                    contact_number = ''.join(filter(str.isdigit, contact_number))[-10:]
                    
                    if len(contact_number) != 10:
                        continue
                    
                    # Get date if available
                    date_str = None
                    if date_column:
                        try:
                            date_val = row[date_column]
                            if not pd.isna(date_val):
                                # Try to parse date
                                if isinstance(date_val, str):
                                    date_obj = pd.to_datetime(date_val)
                                else:
                                    date_obj = date_val
                                date_str = date_obj.strftime('%d-%b-%Y')
                        except:
                            pass
                    
                    print(f"\n  Row {idx+1}: {contact_number}", end='')
                    if date_str:
                        print(f" ({date_str})", end='')
                    print()
                    
                    # Download the PDF
                    success = self.download_pdf_from_url(
                        url, 
                        contact_number, 
                        date_str,
                        self.review_pending_folder
                    )
                    if success:
                        downloaded_count += 1
                    
                except Exception as e:
                    print(f"    ✗ Error: {str(e)}")
                    continue
            
            print(f"\n{'='*60}")
            print(f"✅ Downloaded {downloaded_count} PDFs from {len(df)} rows")
            print(f"📁 Saved to: {self.review_pending_folder}")
            print(f"{'='*60}")
            return downloaded_count
            
        except Exception as e:
            print(f"✗ Error processing Excel: {str(e)}")
            import traceback
            traceback.print_exc()
            return 0
    
    def download_pdf_from_url(self, url: str, contact_number: str, date_str: str, folder: Path) -> bool:
        """
        Download PDF from URL and save to specified folder
        
        Args:
            url: URL to download from
            contact_number: Contact number for filename
            date_str: Date string in DD-Mon-YYYY format (optional)
            folder: Folder to save to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate filename
            if date_str:
                filename = f"{contact_number}_{date_str}_Call1.pdf"
            else:
                timestamp = datetime.now().strftime("%d-%b-%Y")
                filename = f"{contact_number}_{timestamp}_Call1.pdf"
            
            filepath = folder / filename
            
            # Skip if already exists
            if filepath.exists():
                print(f"    ⏭️  Already exists: {filename}")
                return True
            
            # Download file
            print(f"    → Downloading: {filename}...")
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                print(f"    ✓ Saved")
                return True
            else:
                print(f"    ✗ Failed (Status: {response.status_code})")
                return False
                
        except Exception as e:
            print(f"    ✗ Error: {str(e)}")
            return False
    
    def run(self):
        """Main execution flow"""
        try:
            print(f"\n{'='*70}")
            print(f"🤖 COMPLETE NDNC WORKFLOW")
            print(f"{'='*70}")
            print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*70}\n")
            
            # Start browser
            self.start_browser()
            
            # Login
            if not self.login():
                print("\n✗ Login failed. Exiting...")
                return
            
            # Navigate to complaints
            if not self.navigate_to_complaints():
                print("\n✗ Navigation failed. Exiting...")
                return
            
            # Process Review Pending complaints
            print(f"\n{'='*70}")
            print(f"📥 PHASE 1: REVIEW PENDING COMPLAINTS")
            print(f"{'='*70}")
            
            if self.select_status_filter("Review Pending"):
                if self.click_download_button():
                    review_pending_file = self.get_latest_excel_file()
                    if review_pending_file:
                        self.process_review_pending_excel(review_pending_file)
            
            print(f"\n{'='*70}")
            print(f"✅ EXCEL PROCESSING COMPLETE!")
            print(f"{'='*70}")
            
            print(f"\n📁 Files saved to:")
            print(f"   • Review Pending: {self.review_pending_folder}")
            print(f"   • Open (manual): {self.open_folder}")
            print(f"\n💡 For OPEN complaints:")
            print(f"   Place your PDF files in: {self.open_folder}")
            print(f"   Then run the existing automation")
            
            print(f"\nPress Enter to close browser...")
            input()
            
        except Exception as e:
            print(f"\n{'='*70}")
            print(f"❌ FATAL ERROR")
            print(f"{'='*70}")
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
        
        finally:
            if self.driver:
                self.driver.quit()
                print(f"✓ Browser closed")


def main():
    """Main entry point"""
    EMAIL = "shraddha.s@exotel.com"
    DOWNLOAD_DIR = "/Users/shraddha.s/Downloads"
    
    workflow = NDNCCompleteWorkflow(email=EMAIL, download_dir=DOWNLOAD_DIR)
    workflow.run()


if __name__ == "__main__":
    main()