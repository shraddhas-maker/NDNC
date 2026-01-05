"""
NDNC Complaint Verification - Excel-Based Workflow
This script:
1. Logs into dashboard
2. Downloads Review Pending complaints as Excel
3. Downloads Open complaints as Excel
4. Processes each Excel file to download PDFs from column T
5. Runs automation on downloaded PDFs
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


class NDNCExcelWorkflow:
    def __init__(self, email: str, download_dir: str):
        """
        Initialize the NDNC Excel workflow
        
        Args:
            email: Email address for login
            download_dir: Directory where files will be downloaded
        """
        self.email = email
        self.download_dir = Path(download_dir)
        self.ndnc_folder = self.download_dir / "NDNC"
        self.base_url = "https://dashboard.ndnc.exotel.com"
        self.driver = None
        
        # Create NDNC folder if it doesn't exist
        self.ndnc_folder.mkdir(exist_ok=True)
        
        print(f"✓ NDNC folder: {self.ndnc_folder}")
    
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
                (By.XPATH, '//button[@role="combobox"]//span[contains(text(), "Review Pending") or contains(text(), "open")]'),
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
            
            # Select the desired status
            option_xpath = f'//div[@role="option"]//span[text()="{status}"]'
            option = wait.until(EC.element_to_be_clickable((By.XPATH, option_xpath)))
            option.click()
            time.sleep(2)
            
            print(f"✓ Selected status: {status}")
            return True
            
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
                (By.XPATH, '//button[contains(., "Download")]'),
            ]
            
            download_button = None
            for selector_type, selector_value in download_selectors:
                try:
                    download_button = wait.until(EC.element_to_be_clickable((selector_type, selector_value)))
                    break
                except:
                    continue
            
            if not download_button:
                print("✗ Could not find Download button")
                return False
            
            download_button.click()
            print("✓ Download button clicked")
            
            # Wait for download to complete
            print("⏳ Waiting for download to complete (10 seconds)...")
            time.sleep(10)
            
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
    
    def process_excel_file(self, excel_path: Path):
        """
        Process Excel file and download PDFs from column T
        
        Args:
            excel_path: Path to the Excel file
        """
        try:
            print(f"\n{'='*60}")
            print(f"📊 PROCESSING EXCEL FILE: {excel_path.name}")
            print(f"{'='*60}")
            
            # Read Excel file
            print(f"→ Reading Excel file...")
            df = pd.read_excel(excel_path)
            
            print(f"✓ Found {len(df)} rows")
            print(f"✓ Columns: {list(df.columns)}")
            
            # Find column T (might be named differently)
            # Common names: "Document URL", "Document", "URL", or just column index 19 (T is 20th column, index 19)
            url_column = None
            
            # Try to find URL column by name
            for col in df.columns:
                if 'url' in str(col).lower() or 'document' in str(col).lower() or 'link' in str(col).lower():
                    url_column = col
                    break
            
            # If not found by name, try column T (index 19)
            if url_column is None and len(df.columns) > 19:
                url_column = df.columns[19]
            
            if url_column is None:
                print(f"✗ Could not find URL column in Excel file")
                print(f"   Please check the Excel file structure")
                return 0
            
            print(f"✓ Using URL column: '{url_column}'")
            
            # Find contact number column - try multiple possible names
            contact_column = None
            possible_contact_columns = [
                'Complainer No',  # Exact match first
                'Telemarketer No',  # Alternative
            ]
            
            for col_name in possible_contact_columns:
                if col_name in df.columns:
                    contact_column = col_name
                    break
            
            # If not found by exact name, search for patterns
            if contact_column is None:
                for col in df.columns:
                    if 'complain' in str(col).lower() or 'contact' in str(col).lower() or 'phone' in str(col).lower():
                        contact_column = col
                        break
            
            if contact_column is None:
                print(f"✗ Could not find contact number column")
                print(f"   Available columns: {list(df.columns)}")
                return 0
            
            print(f"✓ Using contact column: '{contact_column}'")
            
            # Process each row
            downloaded_count = 0
            for idx, row in df.iterrows():
                try:
                    url = row[url_column]
                    
                    if pd.isna(url) or not url or str(url).strip() == '':
                        print(f"  Row {idx+1}: No URL found, skipping")
                        continue
                    
                    # Get contact number from row
                    contact_number = str(row[contact_column])
                    
                    if pd.isna(contact_number) or contact_number == 'nan':
                        print(f"  Row {idx+1}: No contact number found, skipping")
                        continue
                    
                    # Clean contact number (remove spaces, +91, etc.)
                    contact_number = ''.join(filter(str.isdigit, contact_number))[-10:]
                    
                    print(f"\n  Row {idx+1}: Contact {contact_number}")
                    print(f"    URL: {url[:80]}...")
                    
                    # Download the PDF
                    success = self.download_pdf_from_url(url, contact_number)
                    if success:
                        downloaded_count += 1
                    
                except Exception as e:
                    print(f"  Row {idx+1}: Error - {str(e)}")
                    continue
            
            print(f"\n✓ Downloaded {downloaded_count} PDFs from {len(df)} rows")
            return downloaded_count
            
        except Exception as e:
            print(f"✗ Error processing Excel: {str(e)}")
            import traceback
            traceback.print_exc()
            return 0
    
    def download_pdf_from_url(self, url: str, contact_number: str) -> bool:
        """
        Download PDF from URL and save to NDNC folder
        
        Args:
            url: URL to download from
            contact_number: Contact number for filename
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{contact_number}_{timestamp}.pdf"
            filepath = self.ndnc_folder / filename
            
            # Download file
            print(f"    → Downloading to {filename}...")
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                print(f"    ✓ Downloaded successfully")
                return True
            else:
                print(f"    ✗ Download failed (Status: {response.status_code})")
                return False
                
        except Exception as e:
            print(f"    ✗ Download error: {str(e)}")
            return False
    
    def run(self):
        """Main execution flow"""
        try:
            print(f"\n{'='*60}")
            print(f"🤖 NDNC EXCEL-BASED WORKFLOW")
            print(f"{'='*60}")
            print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Email: {self.email}")
            print(f"Download Directory: {self.download_dir}")
            print(f"NDNC Folder: {self.ndnc_folder}")
            print(f"{'='*60}\n")
            
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
            print(f"\n{'='*60}")
            print(f"📥 DOWNLOADING REVIEW PENDING COMPLAINTS")
            print(f"{'='*60}")
            
            if self.select_status_filter("Review Pending"):
                if self.click_download_button():
                    review_pending_file = self.get_latest_excel_file()
                    if review_pending_file:
                        self.process_excel_file(review_pending_file)
            
            # Process Open complaints
            print(f"\n{'='*60}")
            print(f"📥 DOWNLOADING OPEN COMPLAINTS")
            print(f"{'='*60}")
            
            if self.select_status_filter("open"):
                if self.click_download_button():
                    open_file = self.get_latest_excel_file()
                    if open_file:
                        self.process_excel_file(open_file)
            
            print(f"\n{'='*60}")
            print(f"✅ EXCEL PROCESSING COMPLETE!")
            print(f"{'='*60}")
            print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"\n📁 All PDFs downloaded to: {self.ndnc_folder}")
            print(f"{'='*60}\n")
            
            print(f"Browser will remain open for review.")
            print(f"Press Enter to close browser and exit...")
            input()
            
        except Exception as e:
            print(f"\n{'='*60}")
            print(f"❌ FATAL ERROR")
            print(f"{'='*60}")
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
    
    workflow = NDNCExcelWorkflow(email=EMAIL, download_dir=DOWNLOAD_DIR)
    workflow.run()


if __name__ == "__main__":
    main()