"""
NDNC Complaint Verification Automation Script
This script automates the process of verifying NDNC complaints by:
1. Logging into the dashboard
2. Reading PDF files with complaint data
3. Searching and matching complaints by contact number and date
"""

import os
import re
import time
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import PyPDF2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
import pytesseract
from pdf2image import convert_from_path
from PIL import Image


class NDNCAutomation:
    def __init__(self, email: str, pdf_directory: str):
        """
        Initialize the NDNC automation
        
        Args:
            email: Email address for login
            pdf_directory: Directory containing PDF files with complaint data
        """
        self.email = email
        self.pdf_directory = Path(pdf_directory)
        self.processed_directory = self.pdf_directory / "processed"
        self.base_url = "https://dashboard.ndnc.exotel.com"
        self.driver = None
        
        # Create processed directory if it doesn't exist
        self.processed_directory.mkdir(exist_ok=True)
        
    
    def parse_pdf_file(self, pdf_path: Path) -> Dict[str, str]:
        """
        Extract contact_number and date_of_call from FILENAME
        Simple and reliable approach - uses filename data
        
        Args:
            pdf_path: Path to the PDF or PNG file
            
        Returns:
            Dictionary with 'contact_number' and 'date_of_call'
        """
        try:
            print(f"   📝 Parsing: {pdf_path.name}")
            
            contact_number = None
            date_of_call = None
            
            # ============================================================
            # STEP 1: Extract phone number from FILENAME
            # ============================================================
            print(f"\n   📱 Extracting phone number from filename...")
            
            # Pattern: Look for 10-digit numbers in filename
            # Example: 9479760361_1135047815_18-Dec-2025_Call1.pdf
            # Match any sequence of exactly 10 digits
            filename_numbers = re.findall(r'(\d{10})', pdf_path.name)
            
            if filename_numbers:
                contact_number = filename_numbers[0]
                print(f"   ✓ Phone number: {contact_number}")
                
                if len(filename_numbers) > 1:
                    print(f"      (Multiple numbers found: {filename_numbers}, using first)")
            else:
                print(f"   ✗ No 10-digit number found in filename")
                return None
            
            # ============================================================
            # STEP 2: Extract date from FILENAME
            # ============================================================
            print(f"\n   📅 Extracting date from filename...")
            
            # Pattern: DD-Mon-YYYY (e.g., 18-Dec-2025)
            filename_date_match = re.search(r'(\d{1,2})-(\w{3})-(\d{4})', pdf_path.name, re.IGNORECASE)
            
            if filename_date_match:
                day, month, year = filename_date_match.groups()
                try:
                    date_obj = datetime.strptime(f"{day}-{month}-{year}", '%d-%b-%Y')
                    date_of_call = date_obj.strftime('%d-%b-%Y')
                    print(f"   ✓ Date: {date_of_call}")
                except:
                    date_of_call = f"{day}-{month}-{year}"
                    print(f"   ✓ Date: {date_of_call} (raw format)")
            else:
                print(f"   ✗ No date found in filename (expected format: DD-Mon-YYYY)")
                return None
            
            # ============================================================
            # FINAL RESULT
            # ============================================================
            print(f"\n   ✅ Extraction successful!")
            print(f"      📱 Phone: {contact_number}")
            print(f"      📅 Date:  {date_of_call}")
            
            return {
                'contact_number': contact_number,
                'date_of_call': date_of_call,
                'filename': pdf_path.name
            }
                    
        except Exception as e:
            print(f"\n   ✗ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def verify_phone_in_file(self, pdf_path: Path, contact_number: str) -> bool:
        """
        Verify that the phone number exists in the file content
        Uses OCR to check if the number is actually present in the document
        
        Args:
            pdf_path: Path to the PDF or PNG file
            contact_number: Phone number to verify (without +91)
            
        Returns:
            True if phone number found in content, False otherwise
        """
        try:
            print(f"\n   🔍 Verifying phone number {contact_number} exists in file content...")
            
            # Read file content
            text = ""
            
            if pdf_path.suffix.lower() == '.png':
                print(f"      → Reading PNG image...")
                image = Image.open(pdf_path)
                
                # Simple OCR
                from PIL import ImageEnhance
                img = image.convert('L')
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(2.0)
                
                text = pytesseract.image_to_string(img)
            else:
                print(f"      → Reading PDF...")
                
                # Try direct text extraction
                try:
                    with open(pdf_path, 'rb') as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        for page in pdf_reader.pages:
                            text += page.extract_text()
                except:
                    pass
                
                # If no text, use OCR
                if len(text.strip()) < 50:
                    images = convert_from_path(str(pdf_path), dpi=300)
                    for image in images:
                        from PIL import ImageEnhance
                        img = image.convert('L')
                        enhancer = ImageEnhance.Contrast(img)
                        img = enhancer.enhance(2.0)
                        text += pytesseract.image_to_string(img)
            
            # Clean text - remove all spaces and special characters
            clean_text = re.sub(r'[^0-9]', '', text)
            
            # Check if phone number exists in the text
            # Look for the 10-digit number (may appear with or without +91)
            
            # Search for exact 10-digit match
            if contact_number in clean_text:
                print(f"      ✅ Phone number {contact_number} FOUND in file content!")
                return True
            
            # Also check for +91 prefix version
            plus91_version = f"91{contact_number}"
            if plus91_version in clean_text:
                print(f"      ✅ Phone number found as +91 {contact_number} in file content!")
                return True
            
            # Check individual chunks (sometimes OCR breaks numbers into parts)
            # If at least 7 consecutive digits match, consider it found
            if len(contact_number) >= 7:
                for i in range(len(contact_number) - 6):
                    chunk = contact_number[i:i+7]
                    if chunk in clean_text:
                        print(f"      ⚠️  Partial match found (7+ digits): considering as valid")
                        return True
            
            print(f"      ❌ Phone number {contact_number} NOT FOUND in file content")
            print(f"      📄 File may not contain the expected phone number")
            return False
            
        except Exception as e:
            print(f"      ⚠️  Error during verification: {str(e)}")
            print(f"      Assuming number is present (benefit of doubt)")
            return True  # In case of error, allow processing to continue
    def convert_date_format(self, date_str: str) -> str:
        """
        Convert date from format like '18-Nov-2025' to 'November 18, 2025'
        
        Args:
            date_str: Date string in format DD-Mon-YYYY
            
        Returns:
            Date string in format 'Month DD, YYYY'
        """
        try:
            # Parse the date
            date_obj = datetime.strptime(date_str, '%d-%b-%Y')
            # Format it as "Month DD, YYYY"
            return date_obj.strftime('%B %d, %Y')
        except Exception as e:
            print(f"✗ Error converting date {date_str}: {str(e)}")
            return date_str
    
    def is_date_within_range(self, file_date_str: str, portal_date_str: str) -> bool:
        """
        Check if portal date is the same or within 6 months of file date
        
        Args:
            file_date_str: Date from file in format 'DD-Mon-YYYY' or 'Month DD, YYYY'
            portal_date_str: Date from portal in format 'Month DD, YYYY'
            
        Returns:
            True if dates match or portal date is within 6 months of file date
        """
        try:
            # Parse file date (can be in DD-Mon-YYYY or Month DD, YYYY format)
            try:
                file_date = datetime.strptime(file_date_str, '%d-%b-%Y')
            except:
                file_date = datetime.strptime(file_date_str, '%B %d, %Y')
            
            # Parse portal date (Month DD, YYYY format)
            portal_date = datetime.strptime(portal_date_str, '%B %d, %Y')
            
            # Calculate the difference in days
            date_diff = abs((portal_date - file_date).days)
            
            # 6 months ≈ 183 days (30.5 days * 6)
            six_months_in_days = 183
            
            if date_diff <= six_months_in_days:
                if date_diff == 0:
                    print(f"     ✓ Exact date match!")
                else:
                    print(f"     ✓ Date within range ({date_diff} days difference)")
                return True
            else:
                print(f"     ✗ Date outside 6-month range ({date_diff} days difference)")
                return False
                
        except Exception as e:
            print(f"     ✗ Error comparing dates: {str(e)}")
            return False
    
    def start_browser(self):
        """Start the browser and create a new page"""
        options = webdriver.ChromeOptions()
        # Uncomment next line for headless mode
        # options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)
        self.driver.maximize_window()
        print("✓ Browser started")
    
    def login(self):
        """
        Handle the login process
        User will need to enter OTP manually
        """
        try:
            print(f"\n→ Navigating to login page...")
            self.driver.get(f"{self.base_url}/login")
            time.sleep(2)
            
            print(f"→ Entering email: {self.email}")
            wait = WebDriverWait(self.driver, 10)
            email_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"]')))
            
            # Type slowly like a human
            for char in self.email:
                email_input.send_keys(char)
                time.sleep(0.1)
            
            # Wait a moment to simulate human behavior
            time.sleep(0.5)
            
            print(f"→ Clicking Continue button...")
            continue_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            continue_button.click()
            
            print(f"\n⏳ PLEASE ENTER OTP IN THE BROWSER WINDOW")
            print(f"   Waiting for login to complete (180 seconds / 3 minutes timeout)...")
            
            # Wait for navigation to dashboard (indicating successful login)
            try:
                WebDriverWait(self.driver, 180).until(
                    EC.url_contains("/dashboard")
                )
                print("✓ Login successful!")
                time.sleep(2)
                return True
            except TimeoutException:
                print("✗ Login timeout - please ensure OTP was entered")
                return False
                
        except Exception as e:
            print(f"✗ Login error: {str(e)}")
            return False
    
    def navigate_to_complaints(self):
        """Navigate to the All Complaints page"""
        try:
            print("\n→ Navigating to All Complaints...")
            print("   (Waiting for page to fully load...)")
            
            # Wait longer for dashboard to fully load
            time.sleep(8)
            
            # Try multiple selectors for "All Complaints" button
            wait = WebDriverWait(self.driver, 20)
            
            all_complaints_button = None
            selectors = [
                (By.CSS_SELECTOR, 'a[href="/all-complaints"]'),
                (By.XPATH, '//a[contains(@href, "all-complaints")]'),
                (By.XPATH, '//a[contains(text(), "All Complaints")]'),
                (By.XPATH, '//button[contains(text(), "All Complaints")]'),
                (By.XPATH, '//*[contains(text(), "All Complaints")]'),
            ]
            
            for selector_type, selector_value in selectors:
                try:
                    print(f"   Trying selector: {selector_value[:50]}...")
                    all_complaints_button = wait.until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    print(f"   Found All Complaints button!")
                    break
                except Exception as e:
                    continue
            
            if not all_complaints_button:
                # Try navigating directly to the URL
                print("   Button not found, navigating directly to URL...")
                self.driver.get(f"{self.base_url}/all-complaints")
                time.sleep(5)
            else:
                all_complaints_button.click()
                time.sleep(5)
            
            print("✓ Arrived at All Complaints page")
            return True
            
        except Exception as e:
            print(f"✗ Error navigating to complaints: {str(e)}")
            return False
    
    def search_and_match_complaint(self, contact_number: str, date_of_call: str) -> bool:
        """
        Search for a complaint by contact number and match by date
        
        Args:
            contact_number: The contact number to search for
            date_of_call: The date of call in format DD-Mon-YYYY
            
        Returns:
            True if complaint was found and clicked, False otherwise
        """
        try:
            # Convert date to the format shown in the table
            target_date = self.convert_date_format(date_of_call)
            print(f"\n→ Searching for: {contact_number} with date: {target_date}")
            
            # Find the search input
            wait = WebDriverWait(self.driver, 10)
            search_input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder*="Search by number"]'))
            )
            
            # Clear and enter the contact number
            search_input.clear()
            time.sleep(0.3)
            
            # Type slowly like a human
            for char in contact_number:
                search_input.send_keys(char)
                time.sleep(0.1)
            
            # Wait for search results to load
            time.sleep(2)
            
            # Find all rows in the results table
            rows = self.driver.find_elements(By.CSS_SELECTOR, 'div.flex.w-full.border-t')
            row_count = len(rows)
            
            print(f"→ Found {row_count} result(s)")
            
            if row_count == 0:
                print(f"✗ No results found for {contact_number}")
                return False
            
            # Iterate through rows to find matching date
            for i, row in enumerate(rows):
                # Get all columns in the row
                columns = row.find_elements(By.CSS_SELECTOR, 'div.p-3')
                
                # The "Date of Call/SMS" column should be at index 4 (5th column)
                if len(columns) >= 5:
                    date_column = columns[4]
                    portal_date_text = date_column.text.strip()
                    
                    print(f"  Checking row {i+1}: Portal Date = {portal_date_text}, File Date = {target_date}")
                    
                    # Check if dates match or are within 6 months
                    if self.is_date_within_range(date_of_call, portal_date_text):
                        print(f"✓ Found matching complaint! Clicking row {i+1}")
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", row)
                        time.sleep(0.5)
                        row.click()
                        time.sleep(2)
                        return True
            
            print(f"✗ No matching date found within 6-month range for {contact_number}")
            return False
            
        except Exception as e:
            print(f"✗ Error searching complaint: {str(e)}")
            return False
    
    def upload_document(self, contact_number: str) -> bool:
        """
        Upload the document for the complaint
        
        Args:
            contact_number: The contact number to find the file
            
        Returns:
            True if document was uploaded successfully, False otherwise
        """
        try:
            print(f"\n→ Starting document upload process...")
            
            # Wait for page to load after clicking complaint
            time.sleep(3)
            
            # Step 1: Locate the file in Downloads/NDNC folder first
            downloads_path = Path.home() / "Downloads" / "NDNC"
            
            # Search for file with the contact number in its name (PDF or PNG)
            matching_pdf = list(downloads_path.glob(f"*{contact_number}*.pdf"))
            matching_png = list(downloads_path.glob(f"*{contact_number}*.png"))
            matching_files = matching_pdf + matching_png
            
            if not matching_files:
                print(f"✗ Could not find PDF or PNG file with contact number {contact_number} in {downloads_path}")
                return False
            
            file_to_upload = matching_files[0]
            print(f"→ Found file to upload: {file_to_upload.name}")
            
            # Step 2: Click the Upload button (with upload icon)
            print(f"→ Looking for Upload button...")
            wait = WebDriverWait(self.driver, 10)
            
            # Try multiple selectors for the upload button
            upload_button = None
            selectors = [
                (By.XPATH, '//button[contains(@class, "bg-primary") and .//span[text()="Upload"]]'),
                (By.XPATH, '//button[.//svg[contains(@class, "lucide-upload")]]'),
                (By.XPATH, '//button[contains(., "Upload") and .//svg]'),
                (By.XPATH, '//div[@class="flex items-center gap-2"]//button[.//span[text()="Upload"]]'),
            ]
            
            for selector_type, selector_value in selectors:
                try:
                    upload_button = wait.until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    print(f"   Found Upload button using selector: {selector_value[:60]}...")
                    break
                except:
                    continue
            
            if not upload_button:
                print(f"✗ Could not find Upload button")
                return False
            
            print(f"→ Clicking Upload button...")
            upload_button.click()
            time.sleep(2)
            
            # Step 3: Find and use the file input element directly
            print(f"→ Looking for file input element...")
            
            # Find the hidden file input element
            file_input = None
            try:
                file_input = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]'))
                )
            except:
                # If not found, try clicking "Select File" button first
                print(f"→ Trying to click Select File button...")
                try:
                    select_file_button = wait.until(
                        EC.element_to_be_clickable((By.XPATH, '//button[text()="Select File"]'))
                    )
                    # Don't actually click it, just find the file input
                    select_file_button.click()
                    time.sleep(1)
                    file_input = self.driver.find_element(By.CSS_SELECTOR, 'input[type="file"]')
                except:
                    pass
            
            if not file_input:
                print(f"✗ Could not find file input element")
                return False
            
            # Step 4: Send the file path to the input element
            print(f"→ Uploading file: {file_to_upload.name}")
            file_input.send_keys(str(file_to_upload))
            time.sleep(2)
            print(f"✓ File selected successfully")
            
            # Step 5: Check the consent checkbox
            print(f"→ Looking for consent checkbox...")
            try:
                consent_checkbox = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="button"][role="checkbox"]#consent'))
                )
                
                print(f"→ Clicking consent checkbox...")
                consent_checkbox.click()
                time.sleep(1)
                print(f"✓ Consent checkbox checked")
            except Exception as e:
                print(f"✗ Could not find/click consent checkbox: {str(e)}")
                return False
            
            # Step 6: Click the final Upload button
            print(f"→ Looking for final Upload button...")
            try:
                # This is the final upload button (not the one with icon)
                final_upload_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, '//button[@data-slot="button" and text()="Upload"]'))
                )
                
                print(f"→ Clicking final Upload button...")
                final_upload_button.click()
                time.sleep(3)
                
                print(f"✓ Document uploaded successfully!")
                return True
            except Exception as e:
                print(f"✗ Could not find/click final Upload button: {str(e)}")
                return False
            
        except Exception as e:
            print(f"✗ Error uploading document: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def verify_document(self) -> bool:
        """
        Verify the uploaded document by clicking on it and then clicking Verify button
        
        Returns:
            True if document was verified successfully, False otherwise
        """
        try:
            print(f"\n→ Starting document verification process...")
            
            # Wait for upload to complete and page to refresh
            time.sleep(3)
            
            wait = WebDriverWait(self.driver, 10)
            
            # Step 1: Click on the uploaded document
            print(f"→ Looking for uploaded document...")
            
            # Try multiple selectors for the uploaded document
            document_selectors = [
                (By.CSS_SELECTOR, 'div.bg-slate-100.h-24.w-full.rounded.flex.items-center.justify-center.overflow-hidden.cursor-pointer'),
                (By.XPATH, '//div[contains(@class, "bg-slate-100") and contains(@class, "cursor-pointer")]//svg[contains(@class, "lucide-file-text")]//ancestor::div[contains(@class, "cursor-pointer")]'),
                (By.XPATH, '//div[contains(@class, "cursor-pointer") and .//svg[contains(@class, "lucide-file-text")]]'),
            ]
            
            uploaded_doc = None
            for selector_type, selector_value in document_selectors:
                try:
                    uploaded_doc = wait.until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    print(f"   Found uploaded document")
                    break
                except:
                    continue
            
            if not uploaded_doc:
                print(f"✗ Could not find uploaded document")
                return False
            
            print(f"→ Clicking on uploaded document...")
            uploaded_doc.click()
            time.sleep(2)
            print(f"✓ Document opened")
            
            # Step 2: Click the Verify button
            print(f"→ Looking for Verify button...")
            
            # Try multiple selectors for the Verify button
            verify_selectors = [
                (By.XPATH, '//button[contains(@class, "bg-emerald-600") and contains(., "Verify")]'),
                (By.XPATH, '//button[contains(text(), "Verify") and .//svg[contains(@class, "lucide-check")]]'),
                (By.XPATH, '//button[text()="Verify"]'),
                (By.CSS_SELECTOR, 'button.bg-emerald-600'),
            ]
            
            verify_button = None
            for selector_type, selector_value in verify_selectors:
                try:
                    verify_button = wait.until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    print(f"   Found Verify button")
                    break
                except:
                    continue
            
            if not verify_button:
                print(f"✗ Could not find Verify button")
                return False
            
            print(f"→ Clicking Verify button...")
            verify_button.click()
            time.sleep(2)
            print(f"✓ Verify button clicked")
            
            # Step 3: Click the "Verify Document" button
            print(f"→ Looking for Verify Document button...")
            
            # Try multiple selectors for the Verify Document button
            verify_doc_selectors = [
                (By.XPATH, '//button[contains(@class, "bg-emerald-600") and text()="Verify Document"]'),
                (By.XPATH, '//button[contains(text(), "Verify Document")]'),
                (By.CSS_SELECTOR, 'button.bg-emerald-600[data-slot="button"]'),
            ]
            
            verify_doc_button = None
            for selector_type, selector_value in verify_doc_selectors:
                try:
                    verify_doc_button = wait.until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    print(f"   Found Verify Document button")
                    break
                except:
                    continue
            
            if not verify_doc_button:
                print(f"✗ Could not find Verify Document button")
                return False
            
            print(f"→ Clicking Verify Document button...")
            verify_doc_button.click()
            time.sleep(3)
            
            print(f"✓ Document verified successfully!")
            return True
            
        except Exception as e:
            print(f"✗ Error verifying document: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def check_complaint_status(self) -> str:
        """
        Check the status of the complaint (open vs Review Pending)
        
        Returns:
            Status string: "open" or "Review Pending" or "unknown"
        """
        try:
            print(f"\n→ Checking complaint status...")
            time.sleep(2)
            
            wait = WebDriverWait(self.driver, 10)
            
            # Look for status element
            status_selectors = [
                (By.XPATH, '//div[contains(@class, "flex items-start justify-start")]//span[@class="font-medium"]//span'),
                (By.XPATH, '//span[text()="Status:"]/following-sibling::span//span'),
                (By.XPATH, '//span[contains(text(), "Status:")]/following-sibling::*//span'),
            ]
            
            for selector_type, selector_value in status_selectors:
                try:
                    status_element = wait.until(
                        EC.presence_of_element_located((selector_type, selector_value))
                    )
                    status_text = status_element.text.strip()
                    print(f"✓ Status found: {status_text}")
                    return status_text
                except:
                    continue
            
            print(f"✗ Could not determine status")
            return "unknown"
            
        except Exception as e:
            print(f"✗ Error checking status: {str(e)}")
            return "unknown"
    
    def move_to_processed(self, file_path: Path) -> bool:
        """
        Move a processed file to the processed directory
        
        Args:
            file_path: Path to the file to move
            
        Returns:
            True if moved successfully, False otherwise
        """
        try:
            destination = self.processed_directory / file_path.name
            
            # If file already exists in processed folder, add timestamp
            if destination.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                stem = destination.stem
                suffix = destination.suffix
                destination = self.processed_directory / f"{stem}_{timestamp}{suffix}"
            
            shutil.move(str(file_path), str(destination))
            print(f"   → Moved to processed folder: {file_path.name}")
            return True
        except Exception as e:
            print(f"   ⚠ Could not move file to processed folder: {str(e)}")
            return False
    
    def extract_date_from_url(self, url: str) -> str:
        """
        Extract date from URL
        Looks for patterns like: YYYY-MMM-DD, DD-MMM-YYYY, etc.
        
        Args:
            url: The URL containing the date
            
        Returns:
            Date string in 'Month DD, YYYY' format or None
        """
        try:
            # Try multiple date patterns in URL
            patterns = [
                r'(\d{2})-([A-Za-z]{3})-(\d{4})',  # 24-Dec-2025
                r'(\d{4})-([A-Za-z]{3})-(\d{2})',  # 2025-Dec-24
                r'(\d{4})(\d{2})(\d{2})',           # 20251224
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    if len(match.groups()) == 3:
                        # Try to parse and convert to standard format
                        try:
                            # Try format: DD-Mon-YYYY
                            date_str = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
                            date_obj = datetime.strptime(date_str, '%d-%b-%Y')
                            return date_obj.strftime('%B %d, %Y')
                        except:
                            try:
                                # Try format: YYYY-Mon-DD (convert to DD-Mon-YYYY)
                                date_str = f"{match.group(3)}-{match.group(2)}-{match.group(1)}"
                                date_obj = datetime.strptime(date_str, '%d-%b-%Y')
                                return date_obj.strftime('%B %d, %Y')
                            except:
                                pass
            
            return None
            
        except Exception as e:
            print(f"✗ Error extracting date from URL: {str(e)}")
            return None
    
    def download_and_verify_existing(self, file_date_str: str) -> bool:
        """
        Download existing document, verify date, and click verify if valid
        
        Args:
            file_date_str: Date from the PDF file in format DD-Mon-YYYY
            
        Returns:
            True if verification was successful, False otherwise
        """
        try:
            print(f"\n→ Starting download and verification process...")
            
            wait = WebDriverWait(self.driver, 10)
            
            # Step 1: Click on the uploaded document preview
            print(f"→ Looking for uploaded document preview...")
            
            document_selectors = [
                (By.CSS_SELECTOR, 'div.bg-slate-100.h-24.w-full.rounded.flex.items-center.justify-center.overflow-hidden.cursor-pointer'),
                (By.XPATH, '//div[contains(@class, "bg-slate-100") and contains(@class, "cursor-pointer") and .//svg[contains(@class, "lucide-file-text")]]'),
            ]
            
            document_preview = None
            for selector_type, selector_value in document_selectors:
                try:
                    document_preview = wait.until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    print(f"   Found document preview")
                    break
                except:
                    continue
            
            if not document_preview:
                print(f"✗ Could not find document preview")
                return False
            
            print(f"→ Clicking on document preview...")
            document_preview.click()
            time.sleep(2)
            
            # Step 2: Click the Download button
            print(f"→ Looking for Download button...")
            
            download_selectors = [
                (By.XPATH, '//button[.//svg[contains(@class, "lucide-download")] and contains(., "Download")]'),
                (By.XPATH, '//button[contains(text(), "Download")]'),
                (By.CSS_SELECTOR, 'button[data-slot="button"]:has(svg.lucide-download)'),
            ]
            
            download_button = None
            for selector_type, selector_value in download_selectors:
                try:
                    download_button = wait.until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    print(f"   Found Download button")
                    break
                except:
                    continue
            
            if not download_button:
                print(f"✗ Could not find Download button")
                return False
            
            # Store current tab handle
            main_tab = self.driver.current_window_handle
            print(f"→ Current tab handle: {main_tab[:10]}...")
            
            print(f"→ Clicking Download button...")
            download_button.click()
            time.sleep(3)
            
            # Step 3: Switch to new tab
            print(f"→ Checking for new tab...")
            all_tabs = self.driver.window_handles
            
            if len(all_tabs) > 1:
                # Switch to the new tab (last one)
                new_tab = [tab for tab in all_tabs if tab != main_tab][0]
                self.driver.switch_to.window(new_tab)
                print(f"✓ Switched to new tab")
                
                # Step 4: Get URL and extract date
                current_url = self.driver.current_url
                print(f"→ URL: {current_url}")
                
                # Extract date from URL
                url_date = self.extract_date_from_url(current_url)
                
                if url_date:
                    print(f"→ Extracted date from URL: {url_date}")
                    
                    # Step 5: Compare dates (portal date should be same or within 6 months before file date)
                    if self.is_date_within_range(file_date_str, url_date):
                        print(f"✓ Date validation passed!")
                        
                        # Close the new tab
                        self.driver.close()
                        
                        # Switch back to main tab
                        self.driver.switch_to.window(main_tab)
                        print(f"✓ Switched back to main tab")
                        time.sleep(1)
                        
                        # Step 6: Click Verify button
                        print(f"→ Looking for Verify button...")
                        
                        verify_selectors = [
                            (By.XPATH, '//button[contains(@class, "bg-emerald-600") and contains(., "Verify")]'),
                            (By.XPATH, '//button[contains(text(), "Verify")]'),
                        ]
                        
                        verify_button = None
                        for selector_type, selector_value in verify_selectors:
                            try:
                                verify_button = wait.until(
                                    EC.element_to_be_clickable((selector_type, selector_value))
                                )
                                print(f"   Found Verify button")
                                break
                            except:
                                continue
                        
                        if verify_button:
                            print(f"→ Clicking Verify button...")
                            verify_button.click()
                            time.sleep(2)
                            print(f"✓ Document verified successfully!")
                            return True
                        else:
                            print(f"✗ Could not find Verify button")
                            return False
                    else:
                        print(f"✗ Date validation failed - dates are beyond 6-month range")
                        # Close the new tab
                        self.driver.close()
                        # Switch back to main tab
                        self.driver.switch_to.window(main_tab)
                        return False
                else:
                    print(f"✗ Could not extract date from URL")
                    # Close the new tab
                    self.driver.close()
                    # Switch back to main tab
                    self.driver.switch_to.window(main_tab)
                    return False
            else:
                print(f"✗ New tab did not open")
                return False
            
        except Exception as e:
            print(f"✗ Error in download and verify process: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Try to switch back to main tab if we're in a different one
            try:
                main_tabs = [handle for handle in self.driver.window_handles]
                if main_tabs:
                    self.driver.switch_to.window(main_tabs[0])
            except:
                pass
            
            return False
    
    def process_all_files(self):
        """Process all PDF and PNG files in the directory"""
        print(f"\n{'='*60}")
        print(f"📂 CHECKING DIRECTORY FOR NEW FILES")
        print(f"{'='*60}")
        print(f"→ Directory: {self.pdf_directory}")
        print(f"→ Processed folder: {self.processed_directory}")
        print(f"")
        
        # Get all PDF and PNG files
        pdf_files = list(self.pdf_directory.glob("*.pdf"))
        png_files = list(self.pdf_directory.glob("*.png"))
        all_files = pdf_files + png_files
        
        print(f"→ Found {len(pdf_files)} PDF file(s)")
        if pdf_files:
            for f in pdf_files:
                print(f"   • {f.name}")
        
        print(f"→ Found {len(png_files)} PNG file(s)")
        if png_files:
            for f in png_files:
                print(f"   • {f.name}")
        
        print(f"")
        
        if not all_files:
            print(f"✗ No new PDF or PNG files found in main directory")
            print(f"   All files are already in the processed folder")
            print(f"   To reprocess a file, move it from processed/ back to main folder")
            return
        
        print(f"\n{'='*60}")
        print(f"📝 STARTING PROCESSING")
        print(f"{'='*60}")
        print(f"Total files to process: {len(all_files)}")
        print(f"{'='*60}\n")
        
        results = {
            'success': 0,
            'failed': 0,
            'skipped_no_number': 0,
            'total': len(all_files)
        }
        
        for idx, pdf_file in enumerate(all_files, 1):
            print(f"\n{'─'*60}")
            print(f"📄 FILE {idx}/{len(all_files)}: {pdf_file.name}")
            print(f"{'─'*60}")
            
            # Parse PDF to extract data from FILENAME
            print(f"→ Step 1: Extracting data from filename...")
            complaint_data = self.parse_pdf_file(pdf_file)
            
            if not complaint_data:
                print(f"✗ Failed to extract data from filename - moving to processed folder")
                results['failed'] += 1
                self.move_to_processed(pdf_file)
                continue
            
            # Search and match the complaint
            print(f"\n→ Step 2: Searching for complaint in dashboard...")
            print(f"   Contact Number: {complaint_data['contact_number']}")
            print(f"   Date of Call: {complaint_data['date_of_call']}")
            
            success = self.search_and_match_complaint(
                complaint_data['contact_number'],
                complaint_data['date_of_call']
            )
            
            if success:
                # Check status of the complaint
                print(f"\n→ Step 3: Checking complaint status...")
                status = self.check_complaint_status()
                
                if status.lower() == "open":
                    # VERIFY PHONE NUMBER EXISTS IN FILE BEFORE UPLOADING
                    print(f"\n→ Step 4: Status is 'OPEN'")
                    print(f"→ Step 5: Verifying phone number exists in file content...")
                    
                    if not self.verify_phone_in_file(pdf_file, complaint_data['contact_number']):
                        print(f"\n⚠️  SKIPPING: Phone number not found in file content")
                        print(f"   The file may not be the correct document for this complaint")
                        results['skipped_no_number'] += 1
                        self.move_to_processed(pdf_file)
                        
                        # Navigate back to all complaints page
                        print(f"\n→ Returning to All Complaints page...")
                        self.driver.get(f"{self.base_url}/all-complaints")
                        time.sleep(3)
                        continue
                    
                    # Upload new document
                    print(f"\n→ Step 6: Phone verified! Proceeding with document upload...")
                    if self.upload_document(complaint_data['contact_number']):
                        # Verify the uploaded document
                        print(f"\n→ Step 7: Verifying uploaded document...")
                        if self.verify_document():
                            results['success'] += 1
                            print(f"\n✅ SUCCESS: Processed and verified {pdf_file.name}")
                            self.move_to_processed(pdf_file)
                        else:
                            results['failed'] += 1
                            print(f"\n❌ FAILED: Could not verify document for {pdf_file.name}")
                            self.move_to_processed(pdf_file)
                    else:
                        results['failed'] += 1
                        print(f"\n❌ FAILED: Could not upload document for {pdf_file.name}")
                        self.move_to_processed(pdf_file)
                        
                elif "review pending" in status.lower():
                    # VERIFY PHONE NUMBER EXISTS IN FILE BEFORE VERIFYING
                    print(f"\n→ Step 4: Status is 'REVIEW PENDING'")
                    print(f"→ Step 5: Verifying phone number exists in file content...")
                    
                    if not self.verify_phone_in_file(pdf_file, complaint_data['contact_number']):
                        print(f"\n⚠️  SKIPPING: Phone number not found in file content")
                        print(f"   The file may not be the correct document for this complaint")
                        results['skipped_no_number'] += 1
                        self.move_to_processed(pdf_file)
                        
                        # Navigate back to all complaints page
                        print(f"\n→ Returning to All Complaints page...")
                        self.driver.get(f"{self.base_url}/all-complaints")
                        time.sleep(3)
                        continue
                    
                    # Download and verify existing document
                    print(f"\n→ Step 6: Phone verified! Verifying existing document...")
                    if self.download_and_verify_existing(complaint_data['date_of_call']):
                        results['success'] += 1
                        print(f"\n✅ SUCCESS: Verified {pdf_file.name}")
                        self.move_to_processed(pdf_file)
                    else:
                        results['failed'] += 1
                        print(f"\n❌ FAILED: Could not verify document for {pdf_file.name}")
                        self.move_to_processed(pdf_file)
                else:
                    print(f"\n⚠️  UNKNOWN STATUS: {status} - skipping this file")
                    results['failed'] += 1
                    self.move_to_processed(pdf_file)
                
                # Navigate back to all complaints page
                print(f"\n→ Returning to All Complaints page...")
                self.driver.get(f"{self.base_url}/all-complaints")
                time.sleep(3)
                
                # Wait before processing next file
                if idx < len(all_files):
                    print(f"⏳ Waiting 3 seconds before processing next file...")
                    time.sleep(3)
            else:
                results['failed'] += 1
                print(f"\n❌ FAILED: Could not find/match complaint in dashboard")
                self.move_to_processed(pdf_file)
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"✅ PROCESSING COMPLETE")
        print(f"{'='*60}")
        print(f"📊 Summary:")
        print(f"   Total files processed: {results['total']}")
        print(f"   ✓ Successful: {results['success']}")
        print(f"   ✗ Failed: {results['failed']}")
        if results['skipped_no_number'] > 0:
            print(f"   ⚠️  Skipped (phone not in file): {results['skipped_no_number']}")
        print(f"")
        print(f"📁 All processed files moved to:")
        print(f"   {self.processed_directory}")
        print(f"{'='*60}\n")
    
    def run(self, headless=False):
        """
        Main execution method
        
        Args:
            headless: If True, runs without manual intervention (no input prompts)
        """
        try:
            print(f"\n{'='*60}")
            print(f"🤖 NDNC COMPLAINT VERIFICATION AUTOMATION")
            print(f"{'='*60}")
            print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Email: {self.email}")
            print(f"Watch Directory: {self.pdf_directory}")
            print(f"Mode: {'Headless (Watchdog)' if headless else 'Interactive'}")
            print(f"{'='*60}\n")
            
            # Start browser
            print(f"→ Phase 1: Starting browser...")
            self.start_browser()
            print(f"✓ Browser started\n")
            
            # Login
            print(f"→ Phase 2: Logging in to NDNC dashboard...")
            if not self.login():
                print("\n✗ Login failed. Exiting...")
                return
            print(f"✓ Login successful\n")
            
            # Navigate to complaints page
            print(f"→ Phase 3: Navigating to complaints page...")
            if not self.navigate_to_complaints():
                print("\n✗ Could not navigate to complaints page. Exiting...")
                return
            print(f"✓ Navigation successful\n")
            
            # Process all PDF and PNG files
            print(f"→ Phase 4: Processing files...")
            self.process_all_files()
            
            print(f"\n{'='*60}")
            print(f"✅ AUTOMATION COMPLETED!")
            print(f"{'='*60}")
            print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"")
            
            if not headless:
                print(f"Browser window will remain open for review.")
                print(f"Press Enter to close the browser and exit...")
                print(f"{'='*60}\n")
                input()
                
                # Only close browser in interactive mode
                if self.driver:
                    self.driver.quit()
                    print(f"\n✓ Browser closed")
                    print(f"✓ Automation terminated\n")
            else:
                print(f"Watchdog mode: Browser will remain open for next files...")
                print(f"{'='*60}\n")
            
        except Exception as e:
            print(f"\n{'='*60}")
            print(f"❌ FATAL ERROR")
            print(f"{'='*60}")
            print(f"Error: {str(e)}")
            print(f"{'='*60}\n")
            import traceback
            traceback.print_exc()
            
            # Only close browser on error in interactive mode
            if not headless and self.driver:
                self.driver.quit()
                print(f"\n✓ Browser closed")
                print(f"✓ Automation terminated\n")


def main():
    """Main entry point"""
    # Configuration
    EMAIL = "shraddha.s@exotel.com"
    pdf_path = "/Users/shraddha.s/Downloads/NDNC"
    
    # Check if running via watchdog (headless mode)
    headless_mode = os.environ.get('WATCHDOG_MODE') == '1'
    
    # Create and run automation
    automation = NDNCAutomation(email=EMAIL, pdf_directory=PDF_DIRECTORY)
    automation.run(headless=headless_mode)


if __name__ == "__main__":
    main()

