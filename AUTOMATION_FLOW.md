# 🤖 NDNC Automation Flow - Detailed Context

## Overview
This document explains exactly what happens during the automation process so you can track progress.

---

## 🔄 Complete Automation Flow

### **Phase 1: Initialization**
```
→ Starting browser
→ Opening Chrome in automated mode
✓ Browser started
```

### **Phase 2: Login**
```
→ Logging in to NDNC dashboard
→ Navigating to: https://dashboard.ndnc.exotel.com
→ Entering email: shraddha.s@exotel.com
→ Clicking Sign In
→ Waiting for OTP screen
→ OTP prompt appears - WAITING FOR MANUAL OTP ENTRY
→ After OTP: Waiting for dashboard to load
✓ Login successful
```

### **Phase 3: Navigation**
```
→ Navigating to complaints page
→ Opening: https://dashboard.ndnc.exotel.com/all-complaints
→ Waiting for page to load
✓ Navigation successful
```

### **Phase 4: File Processing**

#### 4.1 Directory Check
```
📂 CHECKING DIRECTORY FOR NEW FILES
→ Directory: /Users/shraddha.s/Downloads/NDNC
→ Processed folder: /Users/shraddha.s/Downloads/NDNC/processed

→ Found X PDF file(s)
   • file1.pdf
   • file2.pdf

→ Found Y PNG file(s)
   • image1.png
   • image2.png

📝 STARTING PROCESSING
Total files to process: X+Y
```

**Important:** If no files are found:
```
✗ No new PDF or PNG files found in main directory
  All files are already in the processed folder
  To reprocess a file, move it from processed/ back to main folder
```

#### 4.2 Processing Each File
For each file, the automation follows these steps:

```
────────────────────────────────────────────────────────────
📄 FILE 1/5: verification_CRM-123_9080758775.pdf
────────────────────────────────────────────────────────────

→ Step 1: Extracting data from file...
  ├─ Using OCR (if needed)
  ├─ Searching for contact number
  ├─ Searching for date of call
  └─ Extracting from filename if not in content
  
  ✓ Parsed file: Contact=9080758775, Date=18-Nov-2024
  
→ Step 2: Searching for complaint in dashboard...
  ├─ Contact Number: 9080758775
  ├─ Date of Call: 18-Nov-2024
  ├─ Entering search term
  ├─ Clicking search button
  ├─ Waiting for results
  ├─ Converting date format: November 18, 2024
  ├─ Checking date range (within 6 months)
  └─ Looking for matching complaint row
  
  ✓ Found matching complaint!
  
→ Step 3: Checking complaint status...
  ├─ Clicking on complaint
  ├─ Waiting for details page to load
  ├─ Reading status field
  └─ Status: OPEN (or REVIEW PENDING)

  ───── IF STATUS = "OPEN" ─────
  
  → Step 4: Status is 'OPEN' - proceeding with document upload...
    ├─ Locating file in Downloads/NDNC folder
    ├─ Found file to upload: verification_CRM-123_9080758775.pdf
    ├─ Looking for Upload button
    ├─ Clicking Upload button
    ├─ Finding file input element
    ├─ Uploading file
    ├─ Checking consent checkbox
    ├─ Clicking final Upload button
    └─ ✓ Document uploaded successfully!
  
  → Step 5: Verifying uploaded document...
    ├─ Looking for uploaded document preview
    ├─ Clicking on document
    ├─ Looking for Verify button
    ├─ Clicking Verify button
    ├─ Looking for Verify Document button
    ├─ Clicking Verify Document button
    └─ ✓ Document verified successfully!
  
  ✅ SUCCESS: Processed and verified verification_CRM-123_9080758775.pdf
  → Moved to processed folder
  
  ───── IF STATUS = "REVIEW PENDING" ─────
  
  → Step 4: Status is 'REVIEW PENDING' - verifying existing document...
    ├─ Looking for uploaded document preview
    ├─ Clicking on document
    ├─ Looking for Download button
    ├─ Clicking Download button
    ├─ New tab opens with document URL
    ├─ Extracting date from URL
    ├─ Comparing dates (URL date vs file date)
    ├─ Date validation: PASS (within 6 months)
    ├─ Closing preview tab
    ├─ Looking for Verify button
    ├─ Clicking Verify button
    └─ ✓ Document verified successfully!
  
  ✅ SUCCESS: Verified verification_CRM-123_9080758775.pdf
  → Moved to processed folder

→ Returning to All Complaints page...
⏳ Waiting 3 seconds before processing next file...

[Process repeats for next file...]
```

### **Phase 5: Completion**
```
────────────────────────────────────────────────────────────
✅ PROCESSING COMPLETE
────────────────────────────────────────────────────────────
📊 Summary:
   Total files processed: 5
   ✓ Successful: 4
   ✗ Failed: 1

📁 All processed files moved to:
   /Users/shraddha.s/Downloads/NDNC/processed
────────────────────────────────────────────────────────────

✅ AUTOMATION COMPLETED!
End Time: 2025-12-30 17:45:23

Browser window will remain open for review.
Press Enter to close the browser and exit...
```

---

## ❌ Common Failure Scenarios

### 1. No Number Found in File
```
✗ No number present in the proof: verification_unknown.pdf
  Skipping this file and moving to next...
→ Moved to processed folder
```

### 2. No Date Found in File
```
✗ Could not extract date_of_call from verification_9080758775.pdf
  PDF content preview: [first 200 chars]...
→ Moved to processed folder
```

### 3. Complaint Not Found in Dashboard
```
✗ No complaints found matching: 9080758775
❌ FAILED: Could not find/match complaint in dashboard
→ Moved to processed folder
```

### 4. Date Mismatch
```
✗ Date validation failed
  URL date: December 18, 2024
  File date: November 18, 2024
  Portal date is MORE than 6 months before file date
❌ FAILED: Could not verify document
→ Moved to processed folder
```

### 5. Upload/Verify Button Not Found
```
✗ Could not find Upload button
❌ FAILED: Could not upload document
→ Moved to processed folder
```

---

## 🎯 Key Tracking Points

### What To Watch For:

1. **OTP Entry Point**
   - Automation pauses and waits for you to enter OTP
   - Continue after OTP is entered

2. **File Count**
   - Shows how many files found before processing
   - If 0 files, check if they're already in `processed/` folder

3. **Step Numbers**
   - Step 1: Data extraction from file
   - Step 2: Search in dashboard
   - Step 3: Check status
   - Step 4: Upload/Verify based on status
   - Step 5: Final verification (if uploaded)

4. **Success/Failure Indicators**
   - ✓ or ✅ = Success
   - ✗ or ❌ = Failure
   - ⚠️ = Warning/Unknown

5. **File Movement**
   - "→ Moved to processed folder" confirms file was archived
   - Prevents reprocessing same files

---

## 📝 Log File Location

Detailed logs are saved to:
```
/Users/shraddha.s/Desktop/watchdog_automation/watchdog.log
```

View logs in real-time:
```bash
tail -f /Users/shraddha.s/Desktop/watchdog_automation/watchdog.log
```

---

## 🔍 Troubleshooting

### If automation does nothing:
1. Check if files are in main folder (not in `processed/`)
2. Look for message: "No new PDF or PNG files found"
3. Move files from `processed/` back to main folder to reprocess

### If automation gets stuck:
1. Check terminal for last message
2. Look for OTP prompt (requires manual entry)
3. Check if browser is waiting for page load
4. Review log file for errors

### If files keep failing:
1. Check file format (OCR quality)
2. Verify contact number is in file/filename
3. Verify date is in correct format
4. Check if complaint exists in dashboard

---

## 💡 Tips

- **Keep terminal visible** to track progress
- **Don't close browser** during automation
- **Be ready for OTP** when automation starts
- **Check processed folder** to see completed files
- **Review logs** if something goes wrong

