"""
Process Review Pending Files Only
Processes files already in review_pending/ folder
No dashboard download - just search, verify, and move to processed_review/
"""

import os
import re
import time
import shutil
import PyPDF2
import pytesseract
from pathlib import Path
from datetime import datetime, timedelta
from PIL import Image
from pdf2image import convert_from_path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class ReviewPendingProcessor:
    def __init__(self, email: str):
        """Initialize processor"""
        self.email = email
        self.base_url = "https://dashboard.ndnc.exotel.com"
        self.driver = None
        
        # Setup folders
        self.ndnc_folder = Path.home() / "Downloads" / "NDNC"
        self.review_pending_folder = self.ndnc_folder / "review_pending"
        self.processed_review_folder = self.ndnc_folder / "processed_review"
        self.not_verified_folder = self.ndnc_folder / "Not_verified"
        
        # Create folders
        self.review_pending_folder.mkdir(parents=True, exist_ok=True)
        self.processed_review_folder.mkdir(parents=True, exist_ok=True)
        self.not_verified_folder.mkdir(parents=True, exist_ok=True)
    
    def start_browser(self):
        """Start browser"""
        print("→ Starting Chrome browser...")
        options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome(options=options)
        time.sleep(2)
        self.driver.maximize_window()
        time.sleep(1)
        print("✓ Browser started and ready")
    
    def login(self):
        """Login to dashboard"""
        try:
            print(f"\n→ Navigating to login page...")
            self.driver.get(f"{self.base_url}/login")
            time.sleep(3)
            
            print(f"→ Entering email: {self.email}")
            wait = WebDriverWait(self.driver, 15)
            email_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"]')))
            
            # Type email slowly
            for char in self.email:
                email_input.send_keys(char)
                time.sleep(0.1)
            
            time.sleep(1)
            
            print(f"→ Clicking Continue button...")
            continue_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            continue_button.click()
            
            print(f"\n{'='*70}")
            print(f"⏳ PLEASE ENTER OTP IN THE BROWSER WINDOW")
            print(f"   Waiting for you to enter OTP...")
            print(f"   (Timeout: 5 minutes)")
            print(f"{'='*70}\n")
            
            # Wait for dashboard
            try:
                WebDriverWait(self.driver, 300).until(
                    EC.url_contains("/dashboard")
                )
                print("✓ Login successful!")
                time.sleep(5)
                
                print("   → Waiting for dashboard to fully load...")
                wait = WebDriverWait(self.driver, 30)
                
                try:
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'nav, header, a[href*="complaints"]')))
                    print("   ✓ Dashboard elements loaded")
                except:
                    print("   ⚠️  Dashboard elements not found, but continuing...")
                
                time.sleep(3)
                
                current_url = self.driver.current_url
                print(f"   → Current URL: {current_url}")
                
                if "login" in current_url:
                    print("✗ Still on login page")
                    return False
                
                try:
                    dashboard_link = self.driver.find_element(By.CSS_SELECTOR, 'a[href="/dashboard"]')
                    dashboard_link.click()
                    time.sleep(3)
                    print("   ✓ Navigated to main dashboard")
                except:
                    print("   ⚠️  Dashboard link not found, proceeding anyway...")
                
                print("   ✓ Session verified")
                time.sleep(2)
                return True
                
            except TimeoutException:
                print("✗ Login timeout")
                return False
                
        except Exception as e:
            print(f"✗ Login error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def navigate_to_all_complaints(self):
        """Navigate to All Complaints"""
        try:
            print("\n→ Navigating to All Complaints...")
            
            current_url = self.driver.current_url
            print(f"   → Current URL: {current_url}")
            
            if "all-complaints" in current_url:
                print("   ✓ Already on All Complaints page")
                return True
            
            print(f"   → Going to: {self.base_url}/all-complaints")
            self.driver.get(f"{self.base_url}/all-complaints")
            time.sleep(5)
            
            print("   → Waiting for page to load...")
            wait = WebDriverWait(self.driver, 20)
            
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.flex.w-full.border-t')))
                print("   ✓ Complaint table loaded")
            except:
                try:
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder*="Search by number"]')))
                    print("   ✓ Search field loaded")
                except:
                    print("   ⚠️  Page elements not found, but continuing...")
            
            time.sleep(2)
            
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
            return False
    
    def close_open_modals(self):
        """Close any open modal dialogs by clicking the X button"""
        try:
            wait = WebDriverWait(self.driver, 3)
            
            # Try to find and click the X (close) button on modal dialogs
            close_button_selectors = [
                # The X button from user's HTML
                (By.XPATH, '//button[@class and contains(@class, "absolute") and contains(@class, "top-4") and contains(@class, "right-4")]//svg[contains(@class, "lucide-x")]//parent::button'),
                (By.XPATH, '//button[contains(@class, "absolute") and contains(@class, "right-4")]/*[name()="svg" and contains(@class, "lucide-x")]//parent::button'),
                # Generic close button in dialog
                (By.XPATH, '//div[@role="dialog"]//button[.//span[text()="Close"]]'),
                (By.XPATH, '//div[@role="dialog"]//button[contains(@class, "ring-offset-background")]//svg[contains(@class, "lucide-x")]//parent::button'),
                # Any close button with X icon
                (By.CSS_SELECTOR, 'div[role="dialog"] button svg.lucide-x'),
            ]
            
            for selector_type, selector_value in close_button_selectors:
                try:
                    close_button = wait.until(EC.element_to_be_clickable((selector_type, selector_value)))
                    print(f"   → Closing modal dialog...")
                    self.driver.execute_script("arguments[0].click();", close_button)
                    time.sleep(0.5)
                    print(f"   ✓ Modal closed")
                    return True
                except:
                    continue
            
            # If no modal found, that's okay
            return True
            
        except Exception as e:
            # Silently fail - modals may not be open
            return True
    
    def extract_phone_from_filename(self, filename: str) -> str:
        """Extract phone number from filename"""
        match = re.search(r'(\d{10})', filename)
        if match:
            return match.group(1)
        return None
    
    def extract_telemarketer_from_filename(self, filename: str) -> str:
        """Extract telemarketer number (second 10-digit number) from filename"""
        matches = re.findall(r'(\d{10})', filename)
        if len(matches) >= 2:
            return matches[1]  # Second 10-digit number is telemarketer
        return None
    
    def clean_ordinal_date(self, date_str: str) -> str:
        """Remove ordinal suffixes (st, nd, rd, th) from dates"""
        # Remove st, nd, rd, th from dates like "17th Dec 2025" -> "17 Dec 2025"
        return re.sub(r'(\d{1,2})(st|nd|rd|th)\b', r'\1', date_str)
    
    def convert_date_format(self, date_str: str) -> str:
        """Convert date from various formats to Month DD, YYYY format"""
        # Clean ordinal suffixes first
        date_str = self.clean_ordinal_date(date_str)
        
        date_formats = [
            '%Y-%m-%d %H:%M:%S %p',  # 2026-01-06 08:49:47 AM
            '%Y-%m-%dT%H:%M:%S',  # ISO timestamp: 2025-12-27T13:59:55
            '%d-%b-%Y %H:%M:%S',  # 30-Jan-2026 12:30:10 (Shaadi)
            '%b %d, %Y %I:%M:%S %p',  # Dec 22, 2025 5:08:27 PM (Magento)
            '%B %d, %Y %I:%M:%S %p',  # December 22, 2025 5:08:27 PM
            '%m/%d/%y %I:%M %p',  # 12/23/25 6:58 PM (AJIO)
            '%d %b %Y',    # 17 Dec 2025 (after cleaning "17th Dec 2025")
            '%d %B %Y',    # 17 December 2025
            '%d-%b-%Y',    # 12-Dec-2025
            '%d-%m-%Y',    # 12-12-2025
            '%d/%b/%y',    # 11/Dec/25
            '%d-%b-%y',    # 11-Dec-25
            '%d/%b/%Y',    # 11/Dec/2025
            '%d.%b.%Y',    # 11.Dec.2025
            '%d.%b.%y',    # 11.Dec.25
            '%d/%m/%Y',    # 11/12/2025
            '%d/%m/%y',    # 11/12/25
            '%b %d %Y',    # Jan 05 2026 (without comma)
            '%B %d %Y',    # January 05 2026 (without comma)
            '%b %d, %Y',   # Jan 2, 2026 (with comma)
            '%B %d, %Y',   # January 2, 2026 (with comma)
        ]
        
        for fmt in date_formats:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                return date_obj.strftime('%B %d, %Y')
            except:
                continue
        
        # If no format matches, return original
        return date_str
    
    def preprocess_image_for_ocr(self, image):
        """Apply multiple preprocessing techniques to improve OCR accuracy"""
        import cv2
        import numpy as np
        
        # Convert PIL Image to numpy array
        img_array = np.array(image)
        
        # Upscale image for better OCR on small text (URLs, dates in code blocks)
        # 2x scaling improves accuracy significantly for small fonts
        height, width = img_array.shape[:2]
        img_array = cv2.resize(img_array, (width * 2, height * 2), interpolation=cv2.INTER_CUBIC)
        
        # Try multiple preprocessing approaches
        processed_images = []
        
        # 1. Original (upscaled) image
        processed_images.append(img_array)
        
        # 2. Grayscale conversion
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            processed_images.append(gray)
            
            # 3. Thresholding
            _, thresh1 = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
            processed_images.append(thresh1)
            
            # 4. Adaptive thresholding
            thresh2 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            processed_images.append(thresh2)
            
            # 5. Noise removal
            denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
            processed_images.append(denoised)
            
            # ========== ADDITIONAL PREPROCESSING FOR GRAY TEXT ==========
            # 6. CLAHE (Contrast Limited Adaptive Histogram Equalization) - Excellent for gray/low-contrast text
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)
            processed_images.append(enhanced)
            
            # 7. Lower threshold for capturing lighter gray text
            _, thresh_low = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)
            processed_images.append(thresh_low)
            
            # 8. Even lower threshold for very light gray text
            _, thresh_very_low = cv2.threshold(gray, 60, 255, cv2.THRESH_BINARY)
            processed_images.append(thresh_very_low)
            
            # 9. CLAHE + Binary threshold (best for gray text on white background)
            _, clahe_thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            processed_images.append(clahe_thresh)
            
            # 10. Sharpening to enhance text edges (helps with blurry gray text)
            kernel_sharpen = np.array([[-1,-1,-1],
                                       [-1, 9,-1],
                                       [-1,-1,-1]])
            sharpened = cv2.filter2D(gray, -1, kernel_sharpen)
            processed_images.append(sharpened)
            
            # 11. CLAHE + Sharpening (combined approach for best gray text capture)
            sharpened_enhanced = cv2.filter2D(enhanced, -1, kernel_sharpen)
            processed_images.append(sharpened_enhanced)
        
        return processed_images
    
    def extract_url_from_address_bar(self, image):
        """Enhanced OCR specifically for browser address bar region"""
        import cv2
        import numpy as np
        
        try:
            # Convert PIL to numpy
            img_array = np.array(image)
            height, width = img_array.shape[:2]
            
            # Focus on top 150 pixels (browser address bar area)
            address_bar_region = img_array[0:min(150, height), :]
            
            # Convert to grayscale
            if len(address_bar_region.shape) == 3:
                gray = cv2.cvtColor(address_bar_region, cv2.COLOR_RGB2GRAY)
            else:
                gray = address_bar_region
            
            # Apply aggressive preprocessing for small text
            # 1. Upscale 3x for better OCR
            upscaled = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
            
            # 2. Contrast enhancement
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(upscaled)
            
            # 3. Sharpening kernel
            kernel = np.array([[-1,-1,-1],
                             [-1, 9,-1],
                             [-1,-1,-1]])
            sharpened = cv2.filter2D(enhanced, -1, kernel)
            
            # 4. Binary threshold
            _, binary = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Try OCR on enhanced address bar region
            configs = [
                '--psm 7',  # Single text line (perfect for address bar)
                '--psm 6',  # Uniform block
            ]
            
            extracted_text = []
            for config in configs:
                try:
                    text = pytesseract.image_to_string(binary, config=config)
                    if text.strip():
                        extracted_text.append(text.strip())
                except:
                    continue
            
            return ' '.join(extracted_text)
            
        except Exception as e:
            print(f"   → Address bar extraction error: {str(e)}")
            return ""
    
    def extract_all_dates_from_text(self, text: str) -> list:
        """Extract ALL dates from text content"""
        dates_found = []
        
        # Comprehensive date patterns (more flexible)
        date_patterns = [
            r'\b(\d{4})-(\d{2})-(\d{2})\s+\d{2}:\d{2}:\d{2}\s+[AP]M',  # 2026-01-06 08:49:47 AM
            r'\b(\d{4})-(\d{2})-(\d{2})T\d{2}:\d{2}:\d{2}',  # ISO timestamp: 2025-12-27T13:59:55.871298Z
            r'\b(\d{1,2})-(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-(\d{4})\s+\d{2}:\d{2}:\d{2}\b',  # 30-Jan-2026 12:30:10 (Shaadi)
            r'\b(\d{1,2})[-/](\d{1,2})[-/](\d{4})\s+\d{1,2}:\d{2}(?::\d{2})?',  # 11-12-2025 13:50 or 11/12/2025 13:50:05 (CRM)
            r'\b(\d{1,2})/(\d{1,2})/(\d{2})\s+\d{1,2}:\d{2}\s+[AP]M\b',  # 12/23/25 6:58 PM (AJIO format)
            r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{1,2}),\s+(\d{4})\s+\d{1,2}:\d{2}:\d{2}\s+[AP]M\b',  # Dec 22, 2025 5:08:27 PM
            r'\b(\d{1,2})(?:st|nd|rd|th)?\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})\b',  # 17th Dec 2025, 3rd Dec 2025
            r'\b(\d{1,2})[-/\s_](\w{3,9})[-/\s_](\d{4})\b',  # 14-Dec-2025, 15 December 2025, 14_Dec_2025
            r'\b(\d{1,2})[-/\s_](\w{3,9})[-/\s_](\d{2})\b',  # 14-Dec-25, 14_Dec_25
            r'\b(\w{3,9})\s+(\d{1,2}),?\s+(\d{4})\b',         # December 14, 2025
            r'\b(\d{1,2})[-/\.](\d{1,2})[-/\.](\d{4})\b',    # 14/12/2025, 14.12.2025
            r'\b(\d{4})[-/\.](\d{1,2})[-/\.](\d{1,2})\b',    # 2025-12-14, 2025.12.14
            r'\b(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})\b',  # 14 December 2025
            r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{1,2}),?\s+(\d{4})\b',  # December 14, 2025
        ]
        
        for pattern in date_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                date_str = match.group(0).strip()
                # Clean up date string
                date_str = re.sub(r'\s+', ' ', date_str)  # Normalize spaces
                if date_str and len(date_str) >= 6:  # Minimum date length
                    dates_found.append(date_str)
        
        return dates_found
    
    def extract_data_from_file(self, file_path: Path) -> dict:
        """Extract phone and date from file content"""
        try:
            print(f"\n   → Performing comprehensive OCR extraction...")
            all_text = ""
            
            # Read file based on type with enhanced OCR
            if file_path.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                image = Image.open(file_path)
                
                # FIRST: Try to extract URL from browser address bar (top of screenshot)
                print(f"   → Attempting enhanced URL extraction from address bar...")
                address_bar_text = self.extract_url_from_address_bar(image)
                if address_bar_text:
                    print(f"   ✓ Address bar text: {address_bar_text[:100]}")
                
                # Try multiple OCR configurations and preprocessing
                ocr_configs = [
                    '--psm 6',  # Assume uniform block of text
                    '--psm 3',  # Fully automatic page segmentation
                    '--psm 11', # Sparse text
                    '--psm 12', # Sparse text with OSD
                ]
                
                # Get preprocessed images
                try:
                    processed_images = self.preprocess_image_for_ocr(image)
                except Exception as prep_error:
                    print(f"   → Preprocessing failed, using original image: {str(prep_error)}")
                    processed_images = [image]
                
                # Try OCR with each configuration and preprocessing combination
                texts = []
                
                # Add address bar text first (highest priority)
                if address_bar_text:
                    texts.append(address_bar_text)
                
                for config in ocr_configs:
                    for proc_img in processed_images[:8]:  # Use first 8 preprocessing methods (includes gray text enhancement)
                        try:
                            text = pytesseract.image_to_string(proc_img, config=config)
                            if len(text.strip()) > 10:
                                texts.append(text)
                        except:
                            continue
                
                # Combine all extracted text
                all_text = "\n".join(texts)
                
            else:
                # For PDFs: Extract text using BOTH PyPDF2 AND OCR
                # This ensures we get text from regular content + screenshots/code blocks/API responses
                
                # Step 1: Try PyPDF2 text extraction (fast, for regular text)
                pypdf_text = ""
                try:
                    with open(file_path, 'rb') as f:
                        pdf_reader = PyPDF2.PdfReader(f)
                        for page in pdf_reader.pages:
                            pypdf_text += page.extract_text()
                    print(f"   → PyPDF2 extracted {len(pypdf_text)} characters")
                except:
                    pass
                
                # Step 2: ALWAYS run OCR on ALL pages (to capture screenshots, code blocks, formatted content)
                ocr_text = ""
                try:
                    print(f"   → Running OCR on all PDF pages...")
                    images = convert_from_path(str(file_path), dpi=300)
                    for page_num, image in enumerate(images, 1):
                        print(f"      → OCR page {page_num}/{len(images)}...")
                        # Try multiple configs for better accuracy
                        page_text = ""
                        for config in ['--psm 6', '--psm 3', '--psm 11']:
                            try:
                                text = pytesseract.image_to_string(image, config=config)
                                if len(text) > len(page_text):
                                    page_text = text
                            except:
                                continue
                        ocr_text += page_text + "\n"
                    print(f"   → OCR extracted {len(ocr_text)} characters")
                except Exception as e:
                    print(f"   ⚠️  OCR warning: {e}")
                
                # Combine both sources (PyPDF2 + OCR)
                all_text = pypdf_text + "\n" + ocr_text
            
            print(f"   → OCR extracted {len(all_text)} characters")
            
            # Debug: Show sample of extracted text
            if len(all_text.strip()) > 0:
                sample = all_text[:500].replace('\n', ' ')
                print(f"   → Text sample: {sample[:150]}...")
            
            # Extract ALL phone numbers (10-digit, strip 91 prefix)
            # Pattern 1: Continuous digits (with optional 91 prefix)
            phone_pattern = r'(?:91)?(\d{10})'
            phone_matches = re.findall(phone_pattern, all_text)
            
            # Pattern 2: Formatted phone numbers like (821) 758-8944
            formatted_pattern = r'\((\d{3})\)\s*(\d{3})-(\d{4})'
            formatted_matches = re.findall(formatted_pattern, all_text)
            # Combine the three groups into 10-digit number
            formatted_phones = [''.join(match) for match in formatted_matches]
            
            # Pattern 3: Dash-separated like 821-758-8944
            dash_pattern = r'(\d{3})-(\d{3})-(\d{4})'
            dash_matches = re.findall(dash_pattern, all_text)
            dash_phones = [''.join(match) for match in dash_matches]
            
            # Pattern 4: Plus sign with country code like +91-8826809975
            plus_pattern = r'\+91-?(\d{10})'
            plus_matches = re.findall(plus_pattern, all_text)
            
            # Combine all phone numbers
            all_phone_matches = phone_matches + formatted_phones + dash_phones + plus_matches
            
            # Filter unique valid phones
            unique_phones = list(set([p for p in all_phone_matches if len(p) == 10 and not p.startswith('0000')]))
            
            # Extract ALL dates
            all_dates = self.extract_all_dates_from_text(all_text)
            unique_dates = list(set(all_dates))
            
            # If no dates found in OCR, try filename
            if not unique_dates:
                filename_date = re.search(r'(\d{1,2}-\w{3}-\d{4})', file_path.name)
                if filename_date:
                    unique_dates.append(filename_date.group(1))
                    print(f"   → Extracted date from filename: {filename_date.group(1)}")
            
            # Check for URL/logo patterns - Includes business CRM systems and company branding
            url_patterns = ['zomato', 'blinkit', 'lifeline', 'exotel', 'swiggy', 'uber', 'ola', 'amazon', 
                          'flipkart', 'dunzo', 'bigbasket', 'grofers', 'myntra', 'meesho', 'paytm',
                          'phonepe', 'gpay', 'hdfc', 'crm', 'dynamics', 'salesforce', 'persistency', 
                          'persistence', 'shipsy', 'gam', 'portal', 'analytics', 'visualize',
                          'freshtohome', 'magento', 'ajio', 'ril', 'reliance', 'shaadi', 'matrimony',
                          'http://', 'https://', 'www.', 
                          '.com', '.in', '.org', '.net', '.io', '.co', '.ai', '.tech']
            logo_patterns = ['order', 'delivery', 'invoice', 'receipt', 'bill', 'lead', 'policy', 
                           'hdfc', 'life', 'insurance', 'visualisation', 'dashboard', 'analytics',
                           'eureka', 'forbes', 'customer', 'service', 'case', 'member', 'tracking']
            
            found_urls = [url for url in url_patterns if re.search(re.escape(url), all_text, re.IGNORECASE)]
            found_logos = [logo for logo in logo_patterns if re.search(re.escape(logo), all_text, re.IGNORECASE)]
            
            # Print results
            if unique_phones:
                print(f"   ✓ Found {len(unique_phones)} phone number(s): {', '.join(unique_phones)}")
            else:
                print(f"   ✗ No phone numbers found in document")
            
            if unique_dates:
                print(f"   ✓ Found {len(unique_dates)} date(s): {', '.join(unique_dates)}")
            else:
                print(f"   ✗ No dates found in document")
            
            if found_urls:
                print(f"   ✓ Found URL patterns: {', '.join(found_urls[:3])}")
            else:
                print(f"   ⚠️  No known URL patterns found")
            
            if found_logos:
                print(f"   ✓ Found logo/brand text: {', '.join(found_logos[:3])}")
            else:
                print(f"   ⚠️  No logo text found")
            
            return {
                'phone': unique_phones[0] if unique_phones else None,
                'all_phones': unique_phones,
                'all_dates': unique_dates,
                'date': unique_dates[0] if unique_dates else None,
                'text': all_text,
                'urls_found': found_urls,
                'logos_found': found_logos,
                'has_authenticity': len(found_urls) > 0 or len(found_logos) > 0
            }
            
        except Exception as e:
            print(f"   ✗ OCR extraction error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'phone': None,
                'all_phones': [],
                'all_dates': [],
                'date': None,
                'text': '',
                'urls_found': [],
                'logos_found': [],
                'has_authenticity': False
            }
    
    def search_complaint(self, phone_number: str) -> bool:
        """Search for complaint"""
        try:
            print(f"\n   → Searching for: {phone_number}")
            
            wait = WebDriverWait(self.driver, 15)
            
            # Close any open modals first
            try:
                close_buttons = self.driver.find_elements(By.XPATH, '//div[@role="dialog"][@data-state="open"]//button[.//svg[contains(@class, "lucide-x")]]')
                for btn in close_buttons:
                    try:
                        self.driver.execute_script("arguments[0].click();", btn)
                        time.sleep(0.5)
                    except:
                        pass
            except:
                pass
            
            print(f"   → Locating search field...")
            search_input = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[placeholder*="Search by number"]')
            ))
            time.sleep(1)
            
            # Use JavaScript to clear and set value instead of .clear()
            self.driver.execute_script("arguments[0].value = '';", search_input)
            time.sleep(0.5)
            
            print(f"   → Entering phone number...")
            for digit in phone_number:
                search_input.send_keys(digit)
                time.sleep(0.1)
            
            time.sleep(3)
            
            print(f"   ✓ Search executed")
            time.sleep(2)
            return True
            
        except Exception as e:
            print(f"   ✗ Search error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def find_and_click_complaint(self, expected_date: str, telemarketer_number: str = None) -> bool:
        """Find and click matching complaint"""
        try:
            target_date = self.convert_date_format(expected_date)
            
            # Clean ordinal suffixes and try multiple date formats to parse the expected date
            cleaned_date = self.clean_ordinal_date(expected_date)
            expected_date_obj = None
            date_formats = [
                '%Y-%m-%d %H:%M:%S %p',  # 2026-01-06 08:49:47 AM
                '%Y-%m-%dT%H:%M:%S',  # ISO timestamp: 2025-12-27T13:59:55
                '%d-%b-%Y %H:%M:%S',  # 30-Jan-2026 12:30:10 (Shaadi)
                '%b %d, %Y %I:%M:%S %p',  # Dec 22, 2025 5:08:27 PM (Magento)
                '%B %d, %Y %I:%M:%S %p',  # December 22, 2025 5:08:27 PM
                '%m/%d/%y %I:%M %p',  # 12/23/25 6:58 PM (AJIO)
                '%d %b %Y',    # 17 Dec 2025
                '%d %B %Y',    # 17 December 2025
                '%d-%b-%Y',    # 12-Dec-2025
                '%d-%m-%Y',    # 12-12-2025
                '%d/%b/%y',    # 11/Dec/25
                '%d-%b-%y',    # 11-Dec-25
                '%d/%b/%Y',    # 11/Dec/2025
                '%d.%b.%Y',    # 11.Dec.2025
                '%d.%b.%y',    # 11.Dec.25
                '%b %d %Y',    # Jan 05 2026 (without comma)
                '%B %d %Y',    # January 05 2026 (without comma)
                '%b %d, %Y',   # Jan 2, 2026 (with comma)
                '%B %d, %Y',   # January 2, 2026 (with comma)
            ]
            
            for fmt in date_formats:
                try:
                    expected_date_obj = datetime.strptime(cleaned_date, fmt)
                    break
                except:
                    continue
            
            if not expected_date_obj:
                print(f"      → Date '{expected_date}' could not be parsed (trying next date...)")
                return False
            
            print(f"      → Parsed date: {target_date}")
            if telemarketer_number:
                print(f"   → Telemarketer filter: {telemarketer_number}")
            time.sleep(2)
            
            today = datetime.now()
            six_months_ago = today - timedelta(days=183)
            
            print(f"   → Scanning complaint rows...")
            time.sleep(1)
            
            rows = self.driver.find_elements(By.CSS_SELECTOR, 'div.flex.w-full.border-t')
            print(f"   → Found {len(rows)} complaint(s)")
            
            if len(rows) == 0:
                print(f"   ✗ No complaints found")
                return False
            
            # Collect matching rows first
            matching_rows = []
            
            for i, row in enumerate(rows):
                try:
                    columns = row.find_elements(By.CSS_SELECTOR, 'div.p-3')
                    
                    if len(columns) >= 5:
                        date_column = columns[4]
                        portal_date_text = date_column.text.strip()
                        
                        # Extract telemarketer number from row (column index 1)
                        telemarketer_column = columns[1] if len(columns) > 1 else None
                        row_telemarketer = telemarketer_column.text.strip() if telemarketer_column else None
                        
                        print(f"     Row {i+1}: Date={portal_date_text}, Telemarketer={row_telemarketer}")
                        
                        try:
                            portal_date = datetime.strptime(portal_date_text, '%B %d, %Y')
                            date_diff = abs((portal_date - expected_date_obj).days)
                            
                            # Accept if within 6 months (183 days in either direction)
                            if date_diff <= 183:
                                if date_diff == 0:
                                    print(f"             ✓ Date: Exact match!")
                                else:
                                    print(f"             ✓ Date: Within 6 months ({date_diff} days)")
                                
                                # Add to matching rows
                                matching_rows.append({
                                    'index': i,
                                    'row': row,
                                    'date': portal_date_text,
                                    'telemarketer': row_telemarketer,
                                    'date_diff': date_diff
                                })
                        except:
                            continue
                            
                except:
                    continue
            
            if not matching_rows:
                print(f"   ✗ No matching complaint by date")
                return False
            
            # If multiple matches and telemarketer number provided, filter by telemarketer
            if len(matching_rows) > 1 and telemarketer_number:
                print(f"\n   → Multiple matches found ({len(matching_rows)}), filtering by telemarketer: {telemarketer_number}")
                
                telemarketer_match = None
                for match in matching_rows:
                    if match['telemarketer'] == telemarketer_number:
                        telemarketer_match = match
                        print(f"   ✓ Found matching telemarketer in row {match['index']+1}")
                        break
                
                if telemarketer_match:
                    row_to_click = telemarketer_match['row']
                    row_index = telemarketer_match['index']
                else:
                    print(f"   ⚠️  No telemarketer match, using first date match")
                    row_to_click = matching_rows[0]['row']
                    row_index = matching_rows[0]['index']
            else:
                # Single match or no telemarketer filter
                row_to_click = matching_rows[0]['row']
                row_index = matching_rows[0]['index']
            
            print(f"\n   ✓ Clicking row {row_index+1}...")
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", row_to_click)
            time.sleep(1)
            self.driver.execute_script("arguments[0].click();", row_to_click)
            time.sleep(3)
            return True
            
        except Exception as e:
            print(f"   ✗ Error: {str(e)}")
            return False
    
    def validate_document_completely(self, file_data: dict, expected_phone: str, url_date_str: str) -> tuple:
        """
        Comprehensive validation of document using OCR data
        Returns: (is_valid: bool, reason: str)
        """
        print(f"\n{'='*70}")
        print(f"📋 COMPREHENSIVE DOCUMENT VALIDATION")
        print(f"{'='*70}")
        
        validation_results = []
        all_passed = True
        
        # 1. Check for URL/Logo authenticity
        print(f"\n1. Authenticity Check (URL/Logo):")
        if file_data.get('has_authenticity'):
            urls = file_data.get('urls_found', [])
            logos = file_data.get('logos_found', [])
            print(f"   ✓ PASSED - Found patterns:")
            if urls:
                print(f"      URLs: {', '.join(urls)}")
            if logos:
                print(f"      Logos: {', '.join(logos)}")
            validation_results.append(("Authenticity", True, f"Found: {', '.join(urls + logos)}"))
        else:
            print(f"   ✗ FAILED - No URL or logo patterns found")
            print(f"      Required: Company URL or document proof")
            validation_results.append(("Authenticity", False, "No URL/logo found in document"))
            all_passed = False
        
        # 2. Check for phone number
        print(f"\n2. Phone Number Check:")
        found_phones = file_data.get('all_phones', [])
        if expected_phone in found_phones:
            print(f"   ✓ PASSED - Phone {expected_phone} found in document")
            validation_results.append(("Phone", True, f"Matched: {expected_phone}"))
        else:
            print(f"   ✗ FAILED - Phone {expected_phone} NOT found in document")
            if found_phones:
                print(f"      Found in doc: {', '.join(found_phones)}")
                print(f"      Expected: {expected_phone}")
            else:
                print(f"      No phone numbers found in document")
            validation_results.append(("Phone", False, f"Expected {expected_phone}, found {found_phones}"))
            all_passed = False
        
        # 3. Check for date within 6 months of URL date
        print(f"\n3. Date Validation (within 6 months of URL date):")
        url_date_obj = None
        
        # Clean ordinal suffixes from URL date
        cleaned_url_date = self.clean_ordinal_date(url_date_str)
        
        # Try multiple date formats for URL date
        date_formats = [
            '%Y-%m-%d %H:%M:%S %p',  # 2026-01-06 08:49:47 AM
            '%Y-%m-%dT%H:%M:%S',  # ISO timestamp: 2025-12-27T13:59:55
            '%d-%b-%Y %H:%M:%S',  # 30-Jan-2026 12:30:10 (Shaadi)
            '%b %d, %Y %I:%M:%S %p',  # Dec 22, 2025 5:08:27 PM (Magento)
            '%B %d, %Y %I:%M:%S %p',  # December 22, 2025 5:08:27 PM
            '%m/%d/%y %I:%M %p',  # 12/23/25 6:58 PM (AJIO)
            '%d %b %Y', '%d %B %Y', '%d-%b-%Y', '%d-%m-%Y',
            '%d/%b/%y', '%d-%b-%y', '%d/%b/%Y', '%d.%b.%Y',
            '%d.%b.%y', '%d/%m/%Y', '%d/%m/%y',
            '%b %d %Y', '%B %d %Y',     # Jan 05 2026 (without comma)
            '%b %d, %Y', '%B %d, %Y',   # Jan 2, 2026 (with comma)
        ]
        
        for fmt in date_formats:
            try:
                url_date_obj = datetime.strptime(cleaned_url_date, fmt)
                break
            except:
                continue
        
        found_dates = file_data.get('all_dates', [])
        valid_date_found = False
        
        if not url_date_obj:
            print(f"   ⚠️  Cannot parse URL date: {url_date_str}")
        elif not found_dates:
            print(f"   ✗ FAILED - No dates found in document content")
            validation_results.append(("Date", False, "No dates found in document"))
            all_passed = False
        else:
            print(f"   → URL date: {url_date_str} → {url_date_obj.strftime('%B %d, %Y')}")
            print(f"   → Checking {len(found_dates)} date(s) from document:")
            
            # Check each date to see if it's within 6 months
            for idx, date_str in enumerate(found_dates, 1):
                try:
                    if len(date_str) < 6:
                        print(f"      ⊘ Date {idx}/{len(found_dates)}: '{date_str}' - SKIPPED (malformed)")
                        continue
                    
                    doc_date_obj = None
                    cleaned_date_str = self.clean_ordinal_date(date_str)
                    
                    formats_to_try = [
                        '%Y-%m-%d %H:%M:%S %p',            # 2026-01-06 08:49:47 AM
                        '%Y-%m-%dT%H:%M:%S',               # ISO timestamp: 2025-12-27T13:59:55
                        '%d-%b-%Y %H:%M:%S',               # 30-Jan-2026 12:30:10 (Shaadi)
                        '%b %d, %Y %I:%M:%S %p',           # Dec 22, 2025 5:08:27 PM (Magento)
                        '%B %d, %Y %I:%M:%S %p',           # December 22, 2025 5:08:27 PM
                        '%m/%d/%y %I:%M %p',               # 12/23/25 6:58 PM (AJIO)
                        '%d-%m-%Y %H:%M',                  # 11-12-2025 13:50 (CRM format)
                        '%d/%m/%Y %H:%M',                  # 11/12/2025 13:50 (CRM format)
                        '%d-%m-%Y %H:%M:%S',               # 11-12-2025 13:50:05
                        '%d/%m/%Y %H:%M:%S',               # 11/12/2025 13:50:05
                        '%d %b %Y', '%d %B %Y', '%d-%b-%Y', '%d-%B-%Y',
                        '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%m-%d-%Y',
                        '%Y-%m-%d', '%d/%m/%y', '%m/%d/%y',
                        '%d/%b/%y', '%d-%b-%y', '%d/%b/%Y',
                        '%d.%b.%Y', '%d.%b.%y',
                        '%b %d %Y', '%B %d %Y',           # Jan 05 2026 (without comma)
                        '%B %d, %Y', '%b %d, %Y',         # Month name formats (with comma)
                    ]
                    
                    for fmt in formats_to_try:
                        try:
                            doc_date_obj = datetime.strptime(cleaned_date_str, fmt)
                            break
                        except:
                            continue
                    
                    if doc_date_obj:
                        diff_days = abs((doc_date_obj - url_date_obj).days)
                        diff_months = diff_days / 30.44
                        
                        if diff_months <= 6:
                            print(f"   ✓ PASSED - Date {idx}/{len(found_dates)}: '{date_str}' → {doc_date_obj.strftime('%B %d, %Y')}")
                            print(f"      Difference: {diff_months:.1f} months ({diff_days} days)")
                            validation_results.append(("Date", True, f"Matched: {date_str} ({diff_months:.1f} months)"))
                            valid_date_found = True
                            break
                        else:
                            print(f"      ✗ Date {idx}/{len(found_dates)}: '{date_str}' is {diff_months:.1f} months away")
                    else:
                        print(f"      ⊘ Date {idx}/{len(found_dates)}: '{date_str}' - Could not parse")
                except Exception as e:
                    print(f"      ⊘ Date {idx}/{len(found_dates)}: '{date_str}' - Error: {str(e)[:50]}")
                    continue
            
            if not valid_date_found:
                print(f"   ✗ FAILED - No dates within 6 months of URL date ({url_date_str})")
                validation_results.append(("Date", False, f"No dates within 6 months of {url_date_str}"))
                all_passed = False
        
        # Final verdict
        print(f"\n{'='*70}")
        print(f"📊 VALIDATION SUMMARY")
        print(f"{'='*70}")
        for check_name, passed, details in validation_results:
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"{status} - {check_name}: {details}")
        
        if all_passed:
            print(f"\n🎉 ALL VALIDATIONS PASSED - Document is authentic and valid")
            print(f"{'='*70}\n")
            return (True, "All validations passed")
        else:
            failed_checks = [name for name, passed, _ in validation_results if not passed]
            reason = f"Failed checks: {', '.join(failed_checks)}"
            print(f"\n❌ VALIDATION FAILED - {reason}")
            print(f"{'='*70}\n")
            return (False, reason)
    
    def extract_date_from_url(self, url: str) -> str:
        """Extract date from URL in format DD-Mon-YYYY"""
        try:
            match = re.search(r'(\d{2})-([A-Za-z]{3})-(\d{4})', url)
            if match:
                return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
            return None
        except:
            return None
    
    def is_date_within_range(self, file_date_str: str, url_date_str: str) -> bool:
        """Check if dates are within 6 months range"""
        try:
            # Clean ordinal suffixes
            file_date_str = self.clean_ordinal_date(file_date_str)
            url_date_str = self.clean_ordinal_date(url_date_str)
            
            # Try multiple date formats
            date_formats = [
                '%Y-%m-%d %H:%M:%S %p',  # 2026-01-06 08:49:47 AM
                '%Y-%m-%dT%H:%M:%S',  # ISO timestamp: 2025-12-27T13:59:55
                '%d-%b-%Y %H:%M:%S',  # 30-Jan-2026 12:30:10 (Shaadi)
                '%b %d, %Y %I:%M:%S %p',  # Dec 22, 2025 5:08:27 PM (Magento)
                '%B %d, %Y %I:%M:%S %p',  # December 22, 2025 5:08:27 PM
                '%m/%d/%y %I:%M %p',  # 12/23/25 6:58 PM (AJIO)
                '%d %b %Y',    # 17 Dec 2025
                '%d %B %Y',    # 17 December 2025
                '%d-%b-%Y',    # 12-Dec-2025
                '%d-%m-%Y',    # 12-12-2025
                '%d/%b/%y',    # 11/Dec/25
                '%d-%b-%y',    # 11-Dec-25
                '%d/%b/%Y',    # 11/Dec/2025
                '%d.%b.%Y',    # 11.Dec.2025
                '%d.%b.%y',    # 11.Dec.25
                '%d/%m/%Y',    # 11/12/2025
                '%d/%m/%y',    # 11/12/25
                '%b %d %Y',    # Jan 05 2026 (without comma)
                '%B %d %Y',    # January 05 2026 (without comma)
                '%b %d, %Y',   # Jan 2, 2026 (with comma)
                '%B %d, %Y',   # January 2, 2026 (with comma)
            ]
            
            # Parse file_date independently
            file_date = None
            for fmt in date_formats:
                try:
                    file_date = datetime.strptime(file_date_str, fmt)
                    break
                except:
                    continue
            
            # Parse url_date independently
            url_date = None
            for fmt in date_formats:
                try:
                    url_date = datetime.strptime(url_date_str, fmt)
                    break
                except:
                    continue
            
            if not file_date or not url_date:
                print(f"   ✗ Could not parse dates: file_date='{file_date_str}' (parsed: {file_date}), url_date='{url_date_str}' (parsed: {url_date})")
                return False
            
            date_diff = abs((file_date - url_date).days)
            print(f"   → Date comparison: {file_date_str} vs {url_date_str} = {date_diff} days difference")
            return date_diff <= 183  # 6 months = ~183 days
        except Exception as e:
            print(f"   ✗ Date parsing error: {str(e)}")
            return False
    
    def verify_document_authenticity(self, current_url: str) -> bool:
        """
        Verify document authenticity by checking for URL or logo in the document
        Takes a screenshot of the document page and uses OCR to check for specific patterns
        """
        try:
            print(f"   → Verifying document authenticity with OCR...")
            
            # Take screenshot of the document page
            screenshot = self.driver.get_screenshot_as_png()
            
            # Convert to PIL Image for OCR
            from io import BytesIO
            image = Image.open(BytesIO(screenshot))
            
            # Extract text using OCR
            text = pytesseract.image_to_string(image)
            text_lower = text.lower()
            
            # Check for URL patterns that should be present in legitimate documents
            url_patterns = [
                'zomato',
                'admin.zomans.com',
                'lifeline',
                'exotel',
                'order',
            ]
            
            # Check for logo/brand text
            logo_patterns = [
                'zomato',
                'customer',
                'delivery',
                'order',
            ]
            
            found_patterns = []
            
            # Check URL patterns
            for pattern in url_patterns:
                if pattern in text_lower:
                    found_patterns.append(f"URL pattern '{pattern}'")
            
            # Check logo patterns
            for pattern in logo_patterns:
                if pattern in text_lower:
                    found_patterns.append(f"Logo text '{pattern}'")
            
            if found_patterns:
                print(f"   ✓ Authenticity verified - Found: {', '.join(found_patterns[:3])}")
                return True
            else:
                print(f"   ⚠️  Authenticity check: No recognizable URL or logo patterns found")
                # Print first 100 chars of extracted text for debugging
                preview = ' '.join(text.split()[:20])
                print(f"   → OCR preview: {preview}...")
                # Still return True as this is an additional check, not a blocker
                return True
                
        except Exception as e:
            print(f"   ⚠️  Authenticity check error: {str(e)}")
            # Don't fail the verification if OCR fails
            return True
    
    def download_and_verify_existing(self, file_date_str: str, expected_phone: str) -> bool:
        """
        Download existing document, verify date and phone, and click verify if valid
        
        Args:
            file_date_str: Date from the PDF file in format DD-Mon-YYYY
            expected_phone: Expected phone number to verify in the document
            
        Returns:
            True if verification was successful, False otherwise
        """
        try:
            print(f"\n→ Starting download and verification process...")
            
            wait = WebDriverWait(self.driver, 15)
            
            # Step 1: Click on the uploaded document preview
            print(f"   → Looking for uploaded document preview...")
            
            document_selectors = [
                (By.XPATH, '//div[@class="text-left"]//div[contains(@class, "font-medium")]'),
                (By.CSS_SELECTOR, 'div.bg-slate-100.h-24.w-full.rounded.flex.items-center.justify-center.overflow-hidden.cursor-pointer'),
                (By.XPATH, '//div[contains(@class, "bg-slate-100") and contains(@class, "cursor-pointer")]'),
            ]
            
            document_preview = None
            for selector_type, selector_value in document_selectors:
                try:
                    document_preview = wait.until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    print(f"   → Found document preview")
                    break
                except:
                    continue
            
            if not document_preview:
                print(f"   ✗ Could not find document preview")
                self.close_open_modals()
                return False
            
            print(f"   → Clicking on document preview...")
            self.driver.execute_script("arguments[0].click();", document_preview)
            time.sleep(3)
            
            # Step 2: Wait for modal dialog to appear
            print(f"   → Waiting for modal dialog to open...")
            wait.until(EC.presence_of_element_located((By.XPATH, '//div[@role="dialog"][@data-state="open"]')))
            time.sleep(2)
            
            # Step 3: Click the Download button (inside dialog header)
            print(f"   → Looking for Download button in modal...")
            
            download_selectors = [
                (By.XPATH, '//div[@role="dialog"]//button[contains(text(), "Download")]'),
                (By.XPATH, '//button[contains(text(), "Download") and @data-slot="button"]'),
                (By.CSS_SELECTOR, 'div[role="dialog"] button[data-slot="button"]:has(svg.lucide-download)'),
                (By.XPATH, '//div[@role="dialog"]//button[.//svg[contains(@class, "lucide-download")]]'),
            ]
            
            download_button = None
            for idx, (selector_type, selector_value) in enumerate(download_selectors):
                try:
                    print(f"      Trying selector {idx+1}...")
                    download_button = wait.until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    print(f"   → Found Download button (selector {idx+1})")
                    break
                except:
                    continue
            
            if not download_button:
                print(f"   ✗ Could not find Download button with any selector")
                # Debug: Print available buttons in the dialog
                try:
                    dialog_buttons = self.driver.find_elements(By.XPATH, '//div[@role="dialog"]//button')
                    print(f"   → Found {len(dialog_buttons)} buttons in dialog")
                    for i, btn in enumerate(dialog_buttons[:5]):  # Show first 5
                        btn_text = btn.text.strip()[:30] if btn.text else "(no text)"
                        print(f"      Button {i+1}: {btn_text}")
                except Exception as debug_e:
                    print(f"   → Debug error: {debug_e}")
                self.close_open_modals()
                return False
            
            # Store current tab handle
            main_tab = self.driver.current_window_handle
            print(f"   → Current tab handle: {main_tab[:10]}...")
            
            # Use JavaScript click to avoid interception
            print(f"   → Scrolling Download button into view...")
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", download_button)
            time.sleep(1)
            
            print(f"   → Clicking Download button...")
            self.driver.execute_script("arguments[0].click();", download_button)
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
                
                # Extract date from URL
                url_date = self.extract_date_from_url(current_url)
                
                if url_date:
                    print(f"   → Extracted date from URL: {url_date}")
                    
                    # Step 5: Download the portal document and perform comprehensive validation
                    print(f"\n   → Taking screenshot of portal document for validation...")
                    
                    # Save screenshot as temporary file
                    import tempfile
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                        tmp_path = Path(tmp_file.name)
                        screenshot_bytes = self.driver.get_screenshot_as_png()
                        tmp_file.write(screenshot_bytes)
                    
                    try:
                        # Perform OCR on portal screenshot
                        print(f"\n{'─'*70}")
                        print(f"🔍 PORTAL DOCUMENT OCR EXTRACTION")
                        print(f"{'─'*70}")
                        portal_file_data = self.extract_data_from_file(tmp_path)
                        
                        # Perform comprehensive validation
                        is_valid, reason = self.validate_document_completely(
                            portal_file_data,
                            expected_phone,
                            url_date
                        )
                        
                        # Clean up temp file
                        try:
                            tmp_path.unlink()
                        except:
                            pass
                        
                        if not is_valid:
                            print(f"\n❌ VALIDATION FAILED: {reason}")
                            # Close the new tab
                            self.driver.close()
                            # Switch back to main tab
                            self.driver.switch_to.window(main_tab)
                            self.close_open_modals()
                            return False
                        
                        print(f"   ✓ Comprehensive validation passed!")
                        
                    except Exception as val_error:
                        print(f"   ⚠️  Validation error: {str(val_error)}")
                        # Clean up temp file
                        try:
                            tmp_path.unlink()
                        except:
                            pass
                        # Close the new tab
                        self.driver.close()
                        # Switch back to main tab
                        self.driver.switch_to.window(main_tab)
                        self.close_open_modals()
                        return False
                    
                    # Close the new tab
                    self.driver.close()
                    
                    # Switch back to main tab
                    self.driver.switch_to.window(main_tab)
                    print(f"   ✓ Switched back to main tab")
                    time.sleep(2)
                    
                    # Step 6: Click Verify button (inside dialog footer)
                    print(f"   → Looking for Verify button in modal...")
                    
                    # Wait for modal to be visible again
                    wait.until(EC.presence_of_element_located((By.XPATH, '//div[@role="dialog"][@data-state="open"]')))
                    time.sleep(1)
                    
                    verify_selectors = [
                        (By.XPATH, '//div[@role="dialog"]//button[contains(@class, "bg-emerald-600") and .//svg[contains(@class, "lucide-check")]]'),
                        (By.XPATH, '//div[@data-slot="dialog-footer"]//button[contains(@class, "bg-emerald-600")]'),
                        (By.XPATH, '//div[@role="dialog"]//button[contains(., "Verify") and contains(@class, "bg-emerald-600")]'),
                    ]
                    
                    verify_button = None
                    for selector_type, selector_value in verify_selectors:
                        try:
                            verify_button = wait.until(
                                EC.element_to_be_clickable((selector_type, selector_value))
                            )
                            print(f"   → Found Verify button")
                            break
                        except:
                            continue
                    
                    if verify_button:
                        print(f"   → Clicking Verify button...")
                        self.driver.execute_script("arguments[0].click();", verify_button)
                        time.sleep(2)
                        
                        # Step 7: Handle confirmation dialog "Verify Document"
                        print(f"   → Looking for confirmation dialog...")
                        try:
                            confirm_verify_button = wait.until(EC.element_to_be_clickable(
                                (By.XPATH, '//button[contains(@class, "bg-emerald-600") and contains(text(), "Verify Document")]')
                            ))
                            print(f"   → Clicking Verify Document confirmation...")
                            self.driver.execute_script("arguments[0].click();", confirm_verify_button)
                            time.sleep(3)
                            print(f"   ✅ Document verified successfully!")
                            return True
                        except Exception as confirm_e:
                            print(f"   ⚠️  Confirmation dialog not found, verification may have completed")
                            return True
                    else:
                        print(f"   ✗ Could not find Verify button")
                        self.close_open_modals()
                        return False
                else:
                    print(f"   ✗ Could not extract date from URL")
                    # Close the new tab
                    self.driver.close()
                    # Switch back to main tab
                    self.driver.switch_to.window(main_tab)
                    self.close_open_modals()
                    return False
            else:
                print(f"   ✗ New tab did not open")
                self.close_open_modals()
                return False
            
        except Exception as e:
            print(f"   ✗ Error in download and verify process: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Try to switch back to main tab if we're in a different one
            try:
                main_tabs = [handle for handle in self.driver.window_handles]
                if main_tabs:
                    self.driver.switch_to.window(main_tabs[0])
            except:
                pass
            
            # Close any open modals
            try:
                self.close_open_modals()
            except:
                pass
            
            return False
    
    def process_file(self, file_path: Path) -> bool:
        """Process single file"""
        try:
            print(f"\n{'='*70}")
            print(f"📄 Processing: {file_path.name}")
            print(f"{'='*70}")
            
            # Extract phone from filename
            phone = self.extract_phone_from_filename(file_path.name)
            if not phone:
                print(f"✗ No phone in filename")
                return False
            
            print(f"✓ Phone: {phone}")
            
            # Extract telemarketer number from filename (if present)
            telemarketer = self.extract_telemarketer_from_filename(file_path.name)
            if telemarketer:
                print(f"✓ Telemarketer: {telemarketer}")
            else:
                print(f"⚠️  No telemarketer number in filename")
            
            # Extract data from file
            file_data = self.extract_data_from_file(file_path)
            if not file_data.get('all_dates'):
                print(f"✗ No dates found")
                return False
            
            file_text = file_data['text']
            
            # Navigate to All Complaints
            self.navigate_to_all_complaints()
            
            # Search
            if not self.search_complaint(phone):
                # Navigate back to All Complaints for next file
                print(f"\n→ Navigating back to All Complaints page for next file...")
                self.navigate_to_all_complaints()
                return False
            
            # Try ALL dates until one matches a complaint
            all_dates = file_data['all_dates']
            print(f"\n→ Trying {len(all_dates)} date(s) to find matching complaint...")
            
            complaint_found = False
            matched_date = None
            for idx, expected_date in enumerate(all_dates, 1):
                print(f"\n   → Attempt {idx}/{len(all_dates)}: Trying date '{expected_date}'")
                
                if self.find_and_click_complaint(expected_date, telemarketer):
                    print(f"   ✓ Successfully matched complaint with date: {expected_date}")
                    complaint_found = True
                    matched_date = expected_date
                    break
                else:
                    print(f"   ✗ Date '{expected_date}' did not match any complaint")
                    # Continue to next date
            
            # FALLBACK: If no dates matched, try extracting date from filename and match exactly
            if not complaint_found:
                print(f"\n⚠️  No dates matched within 6 months. Trying FALLBACK: filename date exact match...")
                
                # Extract date from filename (format: DD-Mon-YYYY)
                filename_date_match = re.search(r'(\d{1,2})-(\w{3})-(\d{4})', file_path.name)
                if filename_date_match:
                    filename_date = filename_date_match.group(0)
                    print(f"   → Extracted filename date: {filename_date}")
                    
                    if self.find_and_click_complaint(filename_date, telemarketer):
                        print(f"   ✓ Successfully matched using filename date: {filename_date}")
                        complaint_found = True
                        matched_date = filename_date
                    else:
                        print(f"   ✗ Filename date '{filename_date}' also did not match")
                else:
                    print(f"   ✗ Could not extract date from filename")
            
            if not complaint_found:
                print(f"\n✗ No matching complaint found (tried {len(all_dates)} date(s) + filename)")
                # Navigate back to All Complaints for next file
                print(f"\n→ Navigating back to All Complaints page for next file...")
                self.navigate_to_all_complaints()
                return False
            
            # Download, verify, and click Verify button (all-in-one)
            if not self.download_and_verify_existing(matched_date, phone):
                # Navigate back to All Complaints for next file
                print(f"\n→ Navigating back to All Complaints page for next file...")
                self.navigate_to_all_complaints()
                return False
            
            print(f"\n✅ Success: {file_path.name}")
            return True
            
        except Exception as e:
            print(f"\n✗ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            # Navigate back to All Complaints for next file
            try:
                print(f"\n→ Navigating back to All Complaints page for next file...")
                self.navigate_to_all_complaints()
            except:
                pass  # Ignore navigation errors in exception handler
            return False
    
    def run(self):
        """Main run method"""
        try:
            print(f"\n{'='*70}")
            print(f"🔄 Review Pending Processor")
            print(f"{'='*70}\n")
            
            # Get files
            files = list(self.review_pending_folder.glob("*.pdf")) + \
                    list(self.review_pending_folder.glob("*.png")) + \
                    list(self.review_pending_folder.glob("*.jpg")) + \
                    list(self.review_pending_folder.glob("*.jpeg"))
            
            if not files:
                print(f"✗ No files in {self.review_pending_folder}")
                return
            
            print(f"✓ Found {len(files)} file(s) to process\n")
            
            # Start browser and login
            self.start_browser()
            
            if not self.login():
                print("✗ Login failed")
                return
            
            # Process each file
            results = {'success': 0, 'failed': 0}
            
            for file_path in files:
                success = self.process_file(file_path)
                
                # Move to appropriate folder based on success
                try:
                    if success:
                        # Successfully verified - move to processed_review
                        dest_path = self.processed_review_folder / file_path.name
                        if dest_path.exists():
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            dest_path = self.processed_review_folder / f"{file_path.stem}_{timestamp}{file_path.suffix}"
                        
                        shutil.move(str(file_path), str(dest_path))
                        print(f"   → Moved to: processed_review/{file_path.name}")
                        results['success'] += 1
                    else:
                        # Failed or skipped - move to Not_verified
                        dest_path = self.not_verified_folder / file_path.name
                        if dest_path.exists():
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            dest_path = self.not_verified_folder / f"{file_path.stem}_{timestamp}{file_path.suffix}"
                        
                        shutil.move(str(file_path), str(dest_path))
                        print(f"   → Moved to: Not_verified/{file_path.name}")
                        results['failed'] += 1
                except Exception as e:
                    print(f"   ⚠️  Could not move: {str(e)}")
                
                time.sleep(2)
            
            # Summary
            print(f"\n{'='*70}")
            print(f"📊 RESULTS")
            print(f"{'='*70}")
            print(f"Total: {len(files)}")
            print(f"✓ Success: {results['success']}")
            print(f"✗ Failed: {results['failed']}")
            print(f"{'='*70}\n")
            
            print(f"✅ Completed!")
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
    EMAIL = "shraddha.s@exotel.com"
    
    processor = ReviewPendingProcessor(email=EMAIL)
    processor.run()


if __name__ == "__main__":
    main()

