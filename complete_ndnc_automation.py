"""
Complete NDNC Automation - Review Pending & Open Complaints
Handles both workflows with proper verification and file management
"""

import os
import re
import time
import shutil
import PyPDF2
import pytesseract
import openpyxl
from pathlib import Path
from datetime import datetime, timedelta
from PIL import Image
from pdf2image import convert_from_path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class NDNCCompleteAutomation:
    def __init__(self, email: str):
        """Initialize NDNC automation"""
        self.email = email
        self.base_url = "https://dashboard.ndnc.exotel.com"
        self.driver = None
        
        # Setup folders
        self.ndnc_folder = Path.home() / "Downloads" / "NDNC"
        self.review_pending_folder = self.ndnc_folder / "review_pending"
        self.open_folder = self.ndnc_folder / "open"
        self.processed_folder = self.ndnc_folder / "processed"
        self.processed_review_folder = self.ndnc_folder / "processed_review"
        
        # Create folders
        for folder in [self.review_pending_folder, self.open_folder, self.processed_folder, self.processed_review_folder]:
            folder.mkdir(parents=True, exist_ok=True)
    
    def start_browser(self):
        """Start browser with download preferences"""
        print("→ Starting Chrome browser...")
        options = webdriver.ChromeOptions()
        
        # Set download directory
        prefs = {
            "download.default_directory": str(self.ndnc_folder),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        options.add_experimental_option("prefs", prefs)
        
        self.driver = webdriver.Chrome(options=options)
        time.sleep(2)
        self.driver.maximize_window()
        time.sleep(1)
        print("✓ Browser started and ready")
    
    def login(self):
        """Login to NDNC dashboard"""
        try:
            print(f"\n→ Navigating to login page...")
            self.driver.get(f"{self.base_url}/login")
            time.sleep(3)
            
            print(f"→ Entering email: {self.email}")
            wait = WebDriverWait(self.driver, 15)
            email_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"]')))
            
            # Type email slowly like a human (don't use .clear())
            for char in self.email:
                email_input.send_keys(char)
                time.sleep(0.1)
            
            # Wait before clicking
            time.sleep(1)
            
            print(f"→ Clicking Continue button...")
            continue_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            continue_button.click()
            
            print(f"\n{'='*70}")
            print(f"⏳ PLEASE ENTER OTP IN THE BROWSER WINDOW")
            print(f"   Waiting for you to enter OTP...")
            print(f"   (Timeout: 5 minutes)")
            print(f"{'='*70}\n")
            
            # Wait for navigation to dashboard (indicating successful login)
            try:
                WebDriverWait(self.driver, 300).until(
                    EC.url_contains("/dashboard")
                )
                print("✓ Login successful!")
                time.sleep(5)
                
                # Wait for dashboard page to fully load
                print("   → Waiting for dashboard to fully load...")
                wait = WebDriverWait(self.driver, 30)
                
                # Wait for dashboard elements to appear
                try:
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'nav, header, a[href*="complaints"]')))
                    print("   ✓ Dashboard elements loaded")
                except:
                    print("   ⚠️  Dashboard elements not found, but continuing...")
                
                time.sleep(3)
                
                # Verify we're actually logged in by checking URL
                current_url = self.driver.current_url
                print(f"   → Current URL: {current_url}")
                
                if "login" in current_url:
                    print("✗ Still on login page - OTP may have failed")
                    return False
                
                # Try clicking on dashboard link if available
                try:
                    dashboard_link = self.driver.find_element(By.CSS_SELECTOR, 'a[href="/dashboard"]')
                    dashboard_link.click()
                    time.sleep(3)
                    print("   ✓ Navigated to main dashboard")
                except:
                    print("   ⚠️  Dashboard link not found, proceeding anyway...")
                
                print("   ✓ Session verified - ready to proceed")
                time.sleep(2)
                return True
                
            except TimeoutException:
                print("✗ Login timeout - please ensure OTP was entered")
                return False
                
        except Exception as e:
            print(f"✗ Login error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def navigate_to_all_complaints(self):
        """Navigate to All Complaints page"""
        try:
            print("\n→ Navigating to All Complaints...")
            
            # First check current URL
            current_url = self.driver.current_url
            print(f"   → Current URL: {current_url}")
            
            # If already on all-complaints, no need to navigate
            if "all-complaints" in current_url:
                print("   ✓ Already on All Complaints page")
                return True
            
            # Navigate to All Complaints
            print(f"   → Going to: {self.base_url}/all-complaints")
            self.driver.get(f"{self.base_url}/all-complaints")
            time.sleep(5)
            
            # Wait for page to fully load
            print("   → Waiting for page to load...")
            wait = WebDriverWait(self.driver, 20)
            
            # Try to find either table or search input
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table tbody tr')))
                print("   ✓ Table loaded")
            except:
                try:
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder*="Search"]')))
                    print("   ✓ Search field loaded")
                except:
                    print("   ⚠️  Page elements not found, but continuing...")
            
            time.sleep(2)
            
            # Verify we're on the right page
            final_url = self.driver.current_url
            print(f"   → Final URL: {final_url}")
            
            if "all-complaints" in final_url or "dashboard" in final_url:
                print("✓ Successfully on All Complaints page")
                return True
            else:
                print(f"✗ Not on expected page: {final_url}")
                return False
                
        except Exception as e:
            print(f"✗ Navigation error: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Check if we need to login again
            current_url = self.driver.current_url
            if "login" in current_url:
                print(f"⚠️  Browser redirected to login page - session may have expired")
            
            return False
    
    def extract_phone_from_filename(self, filename: str) -> str:
        """Extract phone number from filename"""
        # Try patterns: 9479760361_1135047815_18-Dec-2025_Call1.pdf
        match = re.search(r'(\d{10})', filename)
        if match:
            return match.group(1)
        return None
    
    def convert_date_format(self, date_str: str) -> str:
        """Convert date from DD-Mon-YYYY to Month DD, YYYY format"""
        try:
            date_obj = datetime.strptime(date_str, '%d-%b-%Y')
            return date_obj.strftime('%B %d, %Y')
        except:
            try:
                date_obj = datetime.strptime(date_str, '%d-%m-%Y')
                return date_obj.strftime('%B %d, %Y')
            except:
                return date_str
    
    def extract_data_from_file(self, file_path: Path) -> dict:
        """Extract phone number and date from file content using OCR"""
        try:
            print(f"\n   → Extracting data from file content...")
            text = ""
            
            # Read file based on type
            if file_path.suffix.lower() == '.png':
                image = Image.open(file_path)
                text = pytesseract.image_to_string(image)
            else:
                # Try text extraction first
                try:
                    with open(file_path, 'rb') as f:
                        pdf_reader = PyPDF2.PdfReader(f)
                        for page in pdf_reader.pages:
                            text += page.extract_text()
                except:
                    pass
                
                # Use OCR if needed
                if len(text.strip()) < 50:
                    images = convert_from_path(str(file_path), dpi=300)
                    for image in images:
                        text += pytesseract.image_to_string(image)
            
            # Extract phone number (10 digits)
            phone_match = re.search(r'(\d{10})', text)
            phone = phone_match.group(1) if phone_match else None
            
            # Extract date (DD-Mon-YYYY format)
            date_patterns = [
                r'(\d{1,2}[-/]\w{3,9}[-/]\d{4})',  # 18-Dec-2025
                r'(\d{1,2}[-/]\d{1,2}[-/]\d{4})',   # 18-12-2025
            ]
            
            date = None
            for pattern in date_patterns:
                date_match = re.search(pattern, text)
                if date_match:
                    date = date_match.group(1)
                    break
            
            # Also try to extract from filename if not in content
            if not date:
                filename_date = re.search(r'(\d{1,2}-\w{3}-\d{4})', file_path.name)
                if filename_date:
                    date = filename_date.group(1)
            
            if phone:
                print(f"   ✓ Found phone: {phone}")
            if date:
                print(f"   ✓ Found date: {date}")
            
            return {
                'phone': phone,
                'date': date,
                'text': text
            }
            
        except Exception as e:
            print(f"   ✗ Extraction error: {str(e)}")
            return {'phone': None, 'date': None, 'text': ''}
    
    def search_complaint(self, phone_number: str) -> bool:
        """Search for complaint by phone number"""
        try:
            print(f"\n   → Searching for: {phone_number}")
            
            wait = WebDriverWait(self.driver, 15)
            
            # Find search input - use the correct selector
            print(f"   → Locating search field...")
            search_input = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[placeholder*="Search by number"]')
            ))
            time.sleep(1)
            
            # Clear and type phone number slowly
            search_input.clear()
            time.sleep(0.5)
            
            print(f"   → Entering phone number...")
            for digit in phone_number:
                search_input.send_keys(digit)
                time.sleep(0.1)
            
            # Wait for search results to load (no search button, auto-searches)
            time.sleep(3)
            
            print(f"   ✓ Search executed, results loading...")
            time.sleep(2)
            return True
            
        except Exception as e:
            print(f"   ✗ Search error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def find_and_click_complaint(self, expected_date: str) -> bool:
        """Find complaint matching date and click it"""
        try:
            # Convert date to portal format (Month DD, YYYY)
            target_date = self.convert_date_format(expected_date)
            
            try:
                expected_date_obj = datetime.strptime(expected_date, '%d-%b-%Y')
            except:
                try:
                    expected_date_obj = datetime.strptime(expected_date, '%d-%m-%Y')
                except:
                    print(f"   ✗ Could not parse date: {expected_date}")
                    return False
            
            print(f"\n   → Looking for complaint with date: {target_date}")
            time.sleep(2)
            
            # Get today's date
            today = datetime.now()
            six_months_ago = today - timedelta(days=183)
            
            print(f"   → Scanning complaint rows...")
            time.sleep(1)
            
            # Find all complaint rows - CORRECT SELECTOR
            rows = self.driver.find_elements(By.CSS_SELECTOR, 'div.flex.w-full.border-t')
            print(f"   → Found {len(rows)} complaint(s) in search results")
            
            if len(rows) == 0:
                print(f"   ✗ No complaint rows found")
                return False
            
            # Iterate through rows to find matching date
            for i, row in enumerate(rows):
                try:
                    # Get all columns in the row - CORRECT SELECTOR
                    columns = row.find_elements(By.CSS_SELECTOR, 'div.p-3')
                    
                    # The "Date of Call/SMS" column should be at index 4 (5th column)
                    if len(columns) >= 5:
                        date_column = columns[4]
                        portal_date_text = date_column.text.strip()
                        
                        print(f"     Checking row {i+1}: Portal Date = {portal_date_text}, File Date = {target_date}")
                        
                        # Check if dates match or are within 6 months
                        try:
                            portal_date = datetime.strptime(portal_date_text, '%B %d, %Y')
                            date_diff = abs((portal_date - expected_date_obj).days)
                            
                            if date_diff <= 183 and portal_date >= six_months_ago:
                                if date_diff == 0:
                                    print(f"     ✓ Exact date match!")
                                else:
                                    print(f"     ✓ Date within range ({date_diff} days difference)")
                                
                                print(f"   ✓ Found matching complaint! Clicking row {i+1}")
                                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", row)
                                time.sleep(1)
                                
                                # Use JavaScript click to avoid interception
                                self.driver.execute_script("arguments[0].click();", row)
                                time.sleep(3)
                                return True
                        except:
                            continue
                            
                except:
                    continue
            
            print(f"   ✗ No matching complaint found within date range")
            return False
            
        except Exception as e:
            print(f"   ✗ Error finding complaint: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def download_document_from_complaint(self) -> str:
        """Click on uploaded document to download it, return downloaded file path"""
        try:
            print(f"\n   → Starting download and verification process...")
            
            wait = WebDriverWait(self.driver, 15)
            time.sleep(2)
            
            # Step 1: Click on the uploaded document preview - CORRECT SELECTOR
            print(f"   → Looking for uploaded document preview...")
            
            # The file preview has lucide-file-text SVG
            document_preview = wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//div[contains(@class, "flex items-center")]//svg[contains(@class, "lucide-file-text")]//ancestor::div[contains(@class, "flex items-center")][1]')
            ))
            
            print(f"   → Found document preview")
            print(f"   → Clicking on document preview...")
            document_preview.click()
            time.sleep(2)
            
            # Step 2: Click the Download button - CORRECT SELECTOR
            print(f"   → Looking for Download button...")
            
            download_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//button[.//svg[contains(@class, "lucide-download")] and contains(., "Download")]')
            ))
            
            print(f"   → Found Download button")
            
            # Store current tab handle
            main_tab = self.driver.current_window_handle
            print(f"   → Current tab handle: {main_tab[:10]}...")
            
            print(f"   → Clicking Download button...")
            download_button.click()
            time.sleep(3)
            
            # Step 3: Switch to new tab
            print(f"   → Checking for new tab...")
            all_tabs = self.driver.window_handles
            
            if len(all_tabs) > 1:
                # Switch to the new tab (last one)
                new_tab = [tab for tab in all_tabs if tab != main_tab][0]
                self.driver.switch_to.window(new_tab)
                print(f"   ✓ Switched to new tab")
                
                # Step 4: Get URL and extract date
                current_url = self.driver.current_url
                print(f"   → URL: {current_url}")
                
                # Return info
                return {
                    'url': current_url,
                    'main_window': main_tab,
                    'new_window': new_tab
                }
            else:
                print(f"   ⚠️  No new tab opened")
                return None
            
        except Exception as e:
            print(f"   ✗ Download error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def verify_document_match(self, url: str, expected_phone: str, expected_date: str, file_text: str) -> bool:
        """Verify document URL date matches and phone number is in file"""
        try:
            print(f"\n   → Verifying document...")
            
            # Extract date from URL
            url_date_match = re.search(r'(\d{2})-([A-Za-z]{3})-(\d{4})', url)
            if url_date_match:
                url_date_str = f"{url_date_match.group(1)}-{url_date_match.group(2)}-{url_date_match.group(3)}"
                print(f"   → URL date: {url_date_str}")
                
                # Parse dates
                try:
                    url_date = datetime.strptime(url_date_str, '%d-%b-%Y')
                    expected_date_obj = datetime.strptime(expected_date, '%d-%b-%Y')
                except:
                    try:
                        expected_date_obj = datetime.strptime(expected_date, '%d-%m-%Y')
                    except:
                        print(f"   ✗ Could not parse dates")
                        return False
                
                # Check date match (within 6 months)
                date_diff = abs((url_date - expected_date_obj).days)
                if date_diff > 183:
                    print(f"   ✗ Date mismatch: {date_diff} days difference")
                    return False
                
                print(f"   ✓ Date verified ({date_diff} days difference)")
            
            # Check phone number in file text
            clean_text = re.sub(r'[^0-9]', '', file_text)
            if expected_phone in clean_text or f"91{expected_phone}" in clean_text:
                print(f"   ✓ Phone number verified in document")
                return True
            else:
                print(f"   ✗ Phone number NOT found in document")
                return False
                
        except Exception as e:
            print(f"   ✗ Verification error: {str(e)}")
            return False
    
    def check_complaint_status(self) -> str:
        """Check if complaint status is Review Pending or Open"""
        try:
            print(f"\n   → Checking complaint status...")
            time.sleep(2)
            
            wait = WebDriverWait(self.driver, 15)
            
            # Look for status element - CORRECT SELECTOR from HTML
            # Status has colored dot and text: "Review Pending" (amber) or "Open" (blue)
            try:
                status_element = wait.until(EC.presence_of_element_located(
                    (By.XPATH, '//div[contains(@class, "flex items-center")]//span[contains(@class, "text-amber-500") or contains(@class, "text-blue-500")]//following-sibling::span')
                ))
                status_text = status_element.text.strip()
                print(f"   ✓ Status found: {status_text}")
                return status_text.lower()
            except:
                # Try alternative selector
                try:
                    status_element = self.driver.find_element(By.XPATH,
                        '//span[text()="Status"]//ancestor::div[1]//following-sibling::div//span[@class="truncate"]')
                    status_text = status_element.text.strip()
                    print(f"   ✓ Status found: {status_text}")
                    return status_text.lower()
                except:
                    print(f"   ✗ Could not determine status")
                    return "unknown"
                    
        except Exception as e:
            print(f"   ✗ Error checking status: {str(e)}")
            return "unknown"
    
    def click_verify_button(self) -> bool:
        """Click the Verify button - used for OPEN status after upload"""
        try:
            print(f"\n   → Starting document verification...")
            
            # Wait for upload to complete and page to refresh
            time.sleep(3)
            
            wait = WebDriverWait(self.driver, 15)
            
            # Step 1: Click on the uploaded document - CORRECT SELECTOR
            print(f"   → Looking for uploaded document...")
            
            uploaded_doc = wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//div[contains(@class, "flex items-center")]//svg[contains(@class, "lucide-file-text")]//ancestor::div[contains(@class, "flex items-center")][1]')
            ))
            
            print(f"   → Found uploaded document")
            print(f"   → Clicking on uploaded document...")
            uploaded_doc.click()
            time.sleep(2)
            print(f"   ✓ Document opened")
            
            # Step 2: Click the Verify button - CORRECT SELECTOR from HTML
            print(f"   → Looking for Verify button...")
            
            verify_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//button[contains(@class, "bg-emerald-600")]//svg[contains(@class, "lucide-check")]//parent::button')
            ))
            
            print(f"   → Found Verify button (green with check icon)")
            print(f"   → Clicking Verify button...")
            verify_button.click()
            time.sleep(2)
            print(f"   ✓ Verify button clicked")
            
            # Step 3: Click the "Verify Document" confirmation button if it appears
            print(f"   → Looking for Verify Document confirmation...")
            try:
                verify_doc_button = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, '//button[@data-slot="button" and (text()="Verify Document" or text()="Confirm")]')
                ))
                
                print(f"   → Found confirmation button")
                print(f"   → Clicking Verify Document...")
                verify_doc_button.click()
                time.sleep(3)
            except:
                # May not always appear
                print(f"   → No confirmation needed")
            
            print(f"   ✅ Document verified successfully!")
            return True
            
        except Exception as e:
            print(f"✗ Error verifying document: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def upload_document(self, file_path: Path) -> bool:
        """Upload document from local file"""
        try:
            print(f"\n   → Uploading document: {file_path.name}")
            
            wait = WebDriverWait(self.driver, 15)
            time.sleep(2)
            
            # Step 1: Click Upload button - CORRECT SELECTOR from HTML
            print(f"   → Looking for Upload button...")
            upload_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//div[@class="flex items-center gap-2"]//button[.//svg[contains(@class, "lucide-upload")] and .//span[text()="Upload"]]')
            ))
            
            print(f"   → Found Upload button")
            print(f"   → Clicking Upload button...")
            upload_button.click()
            time.sleep(2)
            
            # Step 2: Click "Select File" button - CORRECT SELECTOR from HTML
            print(f"   → Looking for Select File button...")
            select_file_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//button[@data-slot="button" and text()="Select File"]')
            ))
            
            print(f"   → Clicking Select File...")
            select_file_button.click()
            time.sleep(1)
            
            # Step 3: Find file input
            print(f"   → Looking for file input element...")
            file_input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]'))
            )
            
            # Step 4: Send file path
            print(f"   → Uploading file: {file_path.name}")
            file_input.send_keys(str(file_path))
            time.sleep(3)
            print(f"   ✓ File selected successfully")
            
            # Step 5: Check consent checkbox - CORRECT SELECTOR from HTML
            print(f"   → Looking for consent checkbox...")
            consent_checkbox = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'button[type="button"][role="checkbox"]#consent')
            ))
            
            print(f"   → Clicking consent checkbox...")
            consent_checkbox.click()
            time.sleep(2)
            print(f"   ✓ Consent checkbox checked")
            
            # Step 6: Click final Upload button - CORRECT SELECTOR from HTML
            print(f"   → Looking for final Upload button...")
            final_upload_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//button[@data-slot="button" and text()="Upload"]')
            ))
            
            print(f"   → Clicking final Upload button...")
            final_upload_button.click()
            time.sleep(4)
            
            print(f"   ✓ Document uploaded successfully!")
            return True
            
        except Exception as e:
            print(f"✗ Error uploading document: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def process_review_pending_file(self, file_path: Path) -> bool:
        """Process a single Review Pending file (already downloaded from dashboard)"""
        try:
            print(f"\n{'='*60}")
            print(f"📄 Processing Review Pending: {file_path.name}")
            print(f"{'='*60}")
            
            # Extract phone from filename
            phone = self.extract_phone_from_filename(file_path.name)
            if not phone:
                print(f"✗ No phone number in filename")
                return False
            
            print(f"✓ Phone from filename: {phone}")
            
            # Extract data from file content
            file_data = self.extract_data_from_file(file_path)
            if not file_data['date']:
                print(f"✗ Could not extract date from file")
                return False
            
            expected_date = file_data['date']
            file_text = file_data['text']
            
            # Navigate to All Complaints
            self.navigate_to_all_complaints()
            
            # Search for phone number
            if not self.search_complaint(phone):
                # Move to processed_review anyway
                self.move_file_to_processed_review(file_path)
                return False
            
            # Find and click matching complaint
            if not self.find_and_click_complaint(expected_date):
                # Move to processed_review anyway
                self.move_file_to_processed_review(file_path)
                return False
            
            # Download document from complaint (for verification)
            download_info = self.download_document_from_complaint()
            if not download_info:
                # Move to processed_review anyway
                self.move_file_to_processed_review(file_path)
                return False
            
            # Verify document
            verified = self.verify_document_match(
                download_info['url'],
                phone,
                expected_date,
                file_text
            )
            
            # Close download tab and return to main
            self.driver.close()
            self.driver.switch_to.window(download_info['main_window'])
            time.sleep(1)
            
            if not verified:
                print(f"✗ Document verification failed")
                self.move_file_to_processed_review(file_path)
                return False
            
            # Click Verify button
            if not self.click_verify_button_review_pending():
                self.move_file_to_processed_review(file_path)
                return False
            
            # Move to processed_review folder
            self.move_file_to_processed_review(file_path)
            
            print(f"\n✅ Successfully processed: {file_path.name}")
            return True
            
        except Exception as e:
            print(f"\n✗ Processing error: {str(e)}")
            import traceback
            traceback.print_exc()
            # Move to processed_review anyway
            self.move_file_to_processed_review(file_path)
            return False
    
    def move_file_to_processed_review(self, file_path: Path) -> bool:
        """Move file to processed_review folder"""
        try:
            dest_path = self.processed_review_folder / file_path.name
            if dest_path.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                dest_path = self.processed_review_folder / f"{file_path.stem}_{timestamp}{file_path.suffix}"
            
            shutil.move(str(file_path), str(dest_path))
            print(f"   → Moved to processed_review: {file_path.name}")
            return True
        except Exception as e:
            print(f"   ⚠️  Could not move file: {str(e)}")
            return False
    
    def click_verify_button_review_pending(self) -> bool:
        """Click Verify button for Review Pending (no upload, just verify)"""
        try:
            print(f"\n   → Looking for Verify button...")
            
            wait = WebDriverWait(self.driver, 15)
            time.sleep(2)
            
            # Find Verify button - CORRECT SELECTOR
            verify_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//button[contains(@class, "bg-emerald-600")]//svg[contains(@class, "lucide-check")]//parent::button')
            ))
            
            print(f"   → Found Verify button (green with check icon)")
            print(f"   → Clicking Verify button...")
            verify_button.click()
            time.sleep(3)
            
            print(f"   ✅ Document verified successfully!")
            return True
            
        except Exception as e:
            print(f"✗ Error clicking verify: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def process_open_file(self, file_path: Path) -> bool:
        """Process a single Open complaint file"""
        try:
            print(f"\n{'='*60}")
            print(f"📄 Processing Open: {file_path.name}")
            print(f"{'='*60}")
            
            # Extract phone from filename
            phone = self.extract_phone_from_filename(file_path.name)
            if not phone:
                print(f"✗ No phone number in filename")
                return False
            
            print(f"✓ Phone from filename: {phone}")
            
            # Extract data from file content
            file_data = self.extract_data_from_file(file_path)
            if not file_data['date']:
                print(f"✗ Could not extract date from file")
                return False
            
            expected_date = file_data['date']
            
            # Navigate to All Complaints
            self.navigate_to_all_complaints()
            
            # Search for phone number
            if not self.search_complaint(phone):
                return False
            
            # Find and click matching complaint
            if not self.find_and_click_complaint(expected_date):
                return False
            
            # Upload document
            if not self.upload_document(file_path):
                return False
            
            # Click Verify button
            if not self.click_verify_button():
                return False
            
            # Move to processed folder
            processed_path = self.processed_folder / file_path.name
            if processed_path.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                processed_path = self.processed_folder / f"{file_path.stem}_{timestamp}{file_path.suffix}"
            
            shutil.move(str(file_path), str(processed_path))
            print(f"   → Moved to processed: {processed_path.name}")
            
            print(f"\n✅ Successfully processed: {file_path.name}")
            return True
            
        except Exception as e:
            print(f"\n✗ Processing error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def process_excel_and_download_files(self, excel_path: Path) -> int:
        """Process Excel file and download files from Document Link column"""
        try:
            print(f"\n   → Processing Excel file: {excel_path.name}")
            
            # Read Excel file
            workbook = openpyxl.load_workbook(excel_path)
            sheet = workbook.active
            
            print(f"   → Reading Excel data...")
            
            # Columns: T (20) = Document Link, C (3) = Complainer No, G (7) = Date of call/sms
            total_rows = sheet.max_row - 1  # Exclude header
            print(f"   → Found {total_rows} rows\n")
            
            downloaded_count = 0
            
            for row_idx in range(2, sheet.max_row + 1):  # Start from row 2 (skip header)
                try:
                    # Get data from columns
                    complainer_no = sheet.cell(row_idx, 3).value  # Column C
                    date_of_call = sheet.cell(row_idx, 7).value   # Column G
                    doc_link_cell = sheet.cell(row_idx, 20)       # Column T
                    
                    # Get download link (hyperlink or cell value)
                    download_link = doc_link_cell.hyperlink.target if doc_link_cell.hyperlink else doc_link_cell.value
                    
                    if not download_link or download_link in ['Download Here', None, '']:
                        print(f"   Row {row_idx-1}: No valid download link, skipping...")
                        continue
                    
                    print(f"   Row {row_idx-1}: {complainer_no} ({date_of_call})")
                    print(f"      → Downloading: {download_link[:60]}...")
                    
                    # Navigate directly to the download link
                    # This will trigger download in current tab
                    self.driver.get(download_link)
                    time.sleep(4)
                    
                    # Wait for file to download
                    time.sleep(3)
                    
                    # Find the downloaded file - files download to self.ndnc_folder
                    pdf_files = list(self.ndnc_folder.glob("*.pdf")) + list(self.ndnc_folder.glob("*.png"))
                    
                    # Exclude files already in subfolders
                    pdf_files = [f for f in pdf_files if f.parent == self.ndnc_folder]
                    
                    if pdf_files:
                        latest_file = max(pdf_files, key=lambda x: x.stat().st_mtime)
                        
                        # Check if recently downloaded (within last 10 seconds)
                        if (time.time() - latest_file.stat().st_mtime) < 10:
                            # File already has correct name from dashboard, just move it
                            dest_path = self.review_pending_folder / latest_file.name
                            if dest_path.exists():
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                dest_path = self.review_pending_folder / f"{latest_file.stem}_{timestamp}{latest_file.suffix}"
                            
                            shutil.move(str(latest_file), str(dest_path))
                            print(f"      ✓ Downloaded: {latest_file.name}")
                            downloaded_count += 1
                        else:
                            print(f"      ⚠️  No recent download found")
                    
                except Exception as e:
                    print(f"   ⚠️  Error downloading row {row_idx-1}: {str(e)}")
                    continue
            
            # Delete Excel file after processing
            try:
                excel_path.unlink()
                print(f"\n   → Deleted Excel file")
            except:
                pass
            
            return downloaded_count
            
        except Exception as e:
            print(f"   ✗ Error processing Excel: {str(e)}")
            import traceback
            traceback.print_exc()
            return 0
    
    def download_review_pending_files_from_dashboard(self) -> int:
        """Download all Review Pending documents from dashboard"""
        try:
            print(f"\n{'='*70}")
            print(f"📥 DOWNLOADING REVIEW PENDING FILES FROM DASHBOARD")
            print(f"{'='*70}\n")
            
            # Navigate to All Complaints
            self.navigate_to_all_complaints()
            
            # Filter by Review Pending status
            print(f"→ Filtering by 'Review Pending' status...")
            wait = WebDriverWait(self.driver, 15)
            time.sleep(3)
            
            # Try to find and click status filter dropdown
            try:
                print(f"   → Looking for status dropdown button...")
                status_filter_button = wait.until(EC.presence_of_element_located(
                    (By.XPATH, '//button[@role="combobox"][@data-slot="select-trigger"]')
                ))
                
                # Get current selection text
                current_status = None
                try:
                    current_status_element = status_filter_button.find_element(By.CSS_SELECTOR, 'span[data-slot="select-value"]')
                    current_status = current_status_element.text.strip()
                    print(f"   → Current filter: '{current_status}'")
                except:
                    print(f"   → Found status filter button")
                
                # Check if already filtered by Review Pending
                if current_status and "Review Pending" in current_status:
                    print(f"   ✓ Already filtered by Review Pending")
                else:
                    # Scroll button into view
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", status_filter_button)
                    time.sleep(1)
                    
                    # Click using JavaScript to avoid interception
                    print(f"   → Opening status dropdown...")
                    self.driver.execute_script("arguments[0].click();", status_filter_button)
                    time.sleep(2)
                    
                    # Select "Review Pending" from dropdown
                    print(f"   → Looking for Review Pending option...")
                    review_pending_option = wait.until(EC.element_to_be_clickable(
                        (By.XPATH, '//div[@role="option"]//span[text()="Review Pending"]')
                    ))
                    print(f"   → Selecting Review Pending...")
                    self.driver.execute_script("arguments[0].click();", review_pending_option)
                    time.sleep(4)
                    print(f"   ✓ Filtered by Review Pending")
                    
            except Exception as e:
                print(f"   ⚠️  Could not filter by status: {str(e)}")
                print(f"   Showing all complaints instead")
            
            # Wait for page to load after filtering
            time.sleep(3)
            
            # Get all complaint rows using correct selector
            rows = self.driver.find_elements(By.CSS_SELECTOR, 'div.flex.w-full.border-t')
            total_complaints = len(rows)
            print(f"✓ Found {total_complaints} Review Pending complaints\n")
            
            if total_complaints == 0:
                print(f"⚠️  No Review Pending complaints found")
                return 0
            
            # Click bulk Download button to download Excel
            try:
                print(f"→ Looking for bulk Download button...")
                
                # EXACT SELECTOR from HTML
                bulk_download_btn = wait.until(EC.presence_of_element_located(
                    (By.XPATH, '//button[@data-slot="tooltip-trigger" and contains(@class, "bg-primary")]//span[text()="Download"]//parent::button')
                ))
                print(f"   → Found bulk Download button")
                
                # Scroll into view and click using JavaScript
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", bulk_download_btn)
                time.sleep(1)
                
                print(f"   → Clicking to download Excel...")
                self.driver.execute_script("arguments[0].click();", bulk_download_btn)
                time.sleep(8)
                
                # Wait for Excel file to download
                print(f"   → Waiting for Excel file to download...")
                downloads_folder = Path.home() / "Downloads"
                excel_file = None
                
                # Wait up to 60 seconds for Excel file
                for i in range(60):
                    excel_files = list(downloads_folder.glob("complaints*.xlsx")) + list(downloads_folder.glob("complaints*.xls"))
                    if excel_files:
                        latest_excel = max(excel_files, key=lambda x: x.stat().st_mtime)
                        # Check if downloaded in last 60 seconds
                        if (time.time() - latest_excel.stat().st_mtime) < 60:
                            excel_file = latest_excel
                            break
                    
                    if i % 5 == 0:
                        print(f"      Waiting... ({i}s)")
                    time.sleep(1)
                
                if not excel_file:
                    print(f"   ⚠️  No recent Excel download detected")
                    print(f"   → Checking for existing Excel files...")
                    
                    # Look for most recent complaints file
                    excel_files = list(downloads_folder.glob("complaints*.xlsx"))
                    if excel_files:
                        excel_file = max(excel_files, key=lambda x: x.stat().st_mtime)
                        print(f"   → Found existing Excel: {excel_file.name}")
                        print(f"   → Using this file (may contain old data)")
                    else:
                        print(f"   ✗ No Excel file found")
                        raise Exception("Excel download failed")
                
                print(f"   ✓ Excel downloaded: {excel_file.name}")
                
                # Process Excel file to download individual documents
                downloaded_count = self.process_excel_and_download_files(excel_file)
                
                print(f"\n{'='*70}")
                print(f"📥 Downloaded {downloaded_count} files from Excel")
                print(f"{'='*70}\n")
                
                return downloaded_count
                
            except Exception as e:
                print(f"   ✗ Bulk download failed: {str(e)}")
                import traceback
                traceback.print_exc()
                return 0
            
            # If bulk download failed, download individually
            downloaded_count = 0
            
            for idx, row in enumerate(rows, 1):
                try:
                    print(f"   Processing complaint {idx}/{total_complaints}...")
                    
                    # Get phone and date from row before clicking
                    phone = None
                    date = None
                    
                    try:
                        columns = row.find_elements(By.CSS_SELECTOR, 'div.p-3')
                        
                        # Get date from column 4 (5th column - Date of Call/SMS)
                        if len(columns) >= 5:
                            date_column = columns[4]
                            date_text = date_column.text.strip()
                            # Format: "December 17, 2025" -> convert to "17-Dec-2025"
                            try:
                                date_obj = datetime.strptime(date_text, '%B %d, %Y')
                                date = date_obj.strftime('%d-%b-%Y')
                            except:
                                pass
                        
                        # Get phone from the row (usually column 1 or 2)
                        for col in columns:
                            col_text = col.text.strip()
                            phone_match = re.search(r'(\d{10})', col_text)
                            if phone_match:
                                phone = phone_match.group(1)
                                break
                    except:
                        pass
                    
                    # Click on the row to open complaint details
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", row)
                    time.sleep(1)
                    
                    # Use JavaScript click to avoid interception
                    self.driver.execute_script("arguments[0].click();", row)
                    time.sleep(3)
                    
                    # Try to find and download document
                    try:
                        # Find file preview element - CORRECT SELECTOR from HTML
                        doc_preview = wait.until(EC.element_to_be_clickable(
                            (By.XPATH, '//div[contains(@class, "flex items-center")]//svg[contains(@class, "lucide-file-text")]//ancestor::div[contains(@class, "flex items-center")]')
                        ))
                        
                        print(f"   → Found document preview")
                        
                        # Get filename from the preview if possible
                        try:
                            filename_element = self.driver.find_element(By.CSS_SELECTOR, 'div.font-medium.text-sm.truncate')
                            original_filename = filename_element.text.strip()
                            print(f"   → Original filename: {original_filename}")
                            
                            # Extract phone from filename if not found yet
                            if not phone:
                                phone_match = re.search(r'(\d{10})', original_filename)
                                if phone_match:
                                    phone = phone_match.group(1)
                            
                            # Extract date from filename if not found yet
                            if not date:
                                date_match = re.search(r'(\d{1,2}-\w{3}-\d{4})', original_filename)
                                if date_match:
                                    date = date_match.group(1)
                        except:
                            pass
                        
                        # Click on document preview
                        print(f"   → Clicking on document...")
                        doc_preview.click()
                        time.sleep(2)
                        
                        # Find and click Download button - CORRECT SELECTOR from HTML
                        download_btn = wait.until(EC.element_to_be_clickable(
                            (By.XPATH, '//button[.//svg[contains(@class, "lucide-download")] and contains(., "Download")]')
                        ))
                        
                        # Store main window
                        main_window = self.driver.current_window_handle
                        
                        print(f"   → Clicking Download button...")
                        download_btn.click()
                        time.sleep(4)
                        
                        # Check if new tab opened and close it
                        all_windows = self.driver.window_handles
                        for window in all_windows:
                            if window != main_window:
                                self.driver.switch_to.window(window)
                                self.driver.close()
                        self.driver.switch_to.window(main_window)
                        time.sleep(1)
                        
                        # Generate filename
                        if phone and date:
                            filename = f"{phone}_{date}_Call1.pdf"
                        else:
                            filename = f"review_pending_{idx}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                        
                        # Wait for download and move to review_pending folder
                        time.sleep(3)
                        downloads_folder = Path.home() / "Downloads"
                        
                        # Find latest downloaded file
                        pdf_files = list(downloads_folder.glob("*.pdf")) + list(downloads_folder.glob("*.png"))
                        if pdf_files:
                            latest_file = max(pdf_files, key=lambda x: x.stat().st_mtime)
                            
                            # Check if file was just downloaded (within last 10 seconds)
                            if (time.time() - latest_file.stat().st_mtime) < 10:
                                dest_path = self.review_pending_folder / filename
                                shutil.move(str(latest_file), str(dest_path))
                                print(f"   ✓ Downloaded: {filename}")
                                downloaded_count += 1
                            else:
                                print(f"   ⚠️  No recent download found")
                        
                    except Exception as e:
                        print(f"   ⚠️  Could not download document: {str(e)}")
                        import traceback
                        traceback.print_exc()
                    
                    # Go back to All Complaints
                    print(f"   → Returning to All Complaints...")
                    self.navigate_to_all_complaints()
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"   ✗ Error processing complaint {idx}: {str(e)}")
                    continue
            
            print(f"\n{'='*70}")
            print(f"📥 Downloaded {downloaded_count} files to {self.review_pending_folder}")
            print(f"{'='*70}\n")
            
            return downloaded_count
            
        except Exception as e:
            print(f"\n✗ Download error: {str(e)}")
            import traceback
            traceback.print_exc()
            return 0
    
    def run_review_pending_workflow(self):
        """Process all Review Pending files"""
        print(f"\n{'='*70}")
        print(f"🔄 REVIEW PENDING WORKFLOW")
        print(f"{'='*70}\n")
        
        # STEP 1: Download all Review Pending files from dashboard
        print(f"→ Step 1: Downloading Review Pending files from dashboard...")
        downloaded_count = self.download_review_pending_files_from_dashboard()
        
        if downloaded_count == 0:
            print(f"⚠️  No files downloaded, checking existing files...")
        
        # STEP 2: Process all files in review_pending folder
        print(f"\n→ Step 2: Processing downloaded files...")
        
        # Get all PDF/PNG files
        files = list(self.review_pending_folder.glob("*.pdf")) + \
                list(self.review_pending_folder.glob("*.png"))
        
        if not files:
            print(f"✗ No files found in {self.review_pending_folder}")
            return
        
        print(f"✓ Found {len(files)} file(s) to process\n")
        
        results = {'success': 0, 'failed': 0}
        
        for file_path in files:
            success = self.process_review_pending_file(file_path)
            if success:
                results['success'] += 1
            else:
                results['failed'] += 1
            
            # Return to All Complaints for next file
            time.sleep(2)
        
        print(f"\n{'='*70}")
        print(f"📊 REVIEW PENDING RESULTS")
        print(f"{'='*70}")
        print(f"Total: {len(files)}")
        print(f"✓ Success: {results['success']}")
        print(f"✗ Failed: {results['failed']}")
        print(f"{'='*70}\n")
    
    def run_open_workflow(self):
        """Process all Open files"""
        print(f"\n{'='*70}")
        print(f"🔄 OPEN COMPLAINTS WORKFLOW")
        print(f"{'='*70}\n")
        
        # Get all PDF/PNG files
        files = list(self.open_folder.glob("*.pdf")) + \
                list(self.open_folder.glob("*.png"))
        
        if not files:
            print(f"✗ No files found in {self.open_folder}")
            return
        
        print(f"✓ Found {len(files)} file(s) to process\n")
        
        results = {'success': 0, 'failed': 0}
        
        for file_path in files:
            success = self.process_open_file(file_path)
            if success:
                results['success'] += 1
            else:
                results['failed'] += 1
            
            # Return to All Complaints for next file
            time.sleep(2)
        
        print(f"\n{'='*70}")
        print(f"📊 OPEN COMPLAINTS RESULTS")
        print(f"{'='*70}")
        print(f"Total: {len(files)}")
        print(f"✓ Success: {results['success']}")
        print(f"✗ Failed: {results['failed']}")
        print(f"{'='*70}\n")
    
    def run(self, workflow_type='both'):
        """Run the automation"""
        try:
            # Start browser and login
            self.start_browser()
            
            if not self.login():
                print("✗ Login failed")
                return
            
            # Run workflows
            if workflow_type in ['review_pending', 'both']:
                self.run_review_pending_workflow()
            
            if workflow_type in ['open', 'both']:
                self.run_open_workflow()
            
            print(f"\n✅ Automation completed!")
            print(f"Press Enter to close browser...")
            input()
            
        except Exception as e:
            print(f"\n✗ Fatal error: {str(e)}")
            import traceback
            traceback.print_exc()
        
        finally:
            if self.driver:
                self.driver.quit()


def main():
    """Main entry point"""
    import sys
    
    print(f"\n{'='*70}")
    print(f"🤖 NDNC Complete Automation")
    print(f"{'='*70}\n")
    
    EMAIL = "shraddha.s@exotel.com"
    
    # Check for command line argument
    if len(sys.argv) > 1:
        workflow = sys.argv[1]
    else:
        print("Select workflow:")
        print("1. Review Pending only")
        print("2. Open complaints only")
        print("3. Both (default)")
        
        choice = input("\nEnter choice (1/2/3): ").strip() or '3'
        
        workflow_map = {
            '1': 'review_pending',
            '2': 'open',
            '3': 'both'
        }
        
        workflow = workflow_map.get(choice, 'both')
    
    automation = NDNCCompleteAutomation(email=EMAIL)
    automation.run(workflow_type=workflow)


if __name__ == "__main__":
    main()

