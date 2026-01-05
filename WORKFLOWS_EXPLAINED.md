# 🔄 NDNC Automation Workflows - Complete Guide

## 📋 Overview

There are TWO distinct workflows:
1. **Review Pending** - Download from dashboard, then verify
2. **Open** - Upload files from folder, then verify

---

## 🔄 Workflow 1: Review Pending

### **Phase 1: Download Files from Dashboard**

```
Login → All Complaints → Filter "Review Pending" → 
Click Download button → All files saved to review_pending/
```

**Steps:**
1. Login to dashboard (enter OTP once)
2. Go to All Complaints page
3. Click status dropdown (shows "All Statuses")
4. Select "Review Pending"
5. Click bulk "Download" button
6. All Review Pending files download to `/Users/shraddha.s/Downloads/NDNC/review_pending/`

### **Phase 2: Process Each Downloaded File**

For each file in `review_pending/` folder:

```
Extract phone from filename → Extract date from file content → 
Search in dashboard → Find matching complaint → 
Click complaint → Download document (for verification) → 
Verify: date in URL = date in file (±6 months) → 
Verify: phone in document content → 
Click Verify button → Move to processed_review/
```

**Steps:**
1. Extract phone number from filename (e.g., `9479760361`)
2. Extract date from file content using OCR (e.g., `18-Dec-2025`)
3. Search for phone in All Complaints
4. Find row with matching date (within 6 months)
5. Click on complaint row
6. Click on document preview
7. Click Download button (opens new tab)
8. Extract date from URL
9. **Verify:**
   - ✅ URL date = file date (±6 months)
   - ✅ Phone number present in document content
10. Close new tab, return to main tab
11. If verified: Click Verify button
12. Move file to `processed_review/` folder

**Result Folder:** `/Users/shraddha.s/Downloads/NDNC/processed_review/`

---

## 🔄 Workflow 2: Open Complaints

### **Watchdog Mode (Recommended)**

```
Start watchdog → Monitor open/ folder → 
New file detected → Extract phone & date → 
Search in dashboard → Upload file → Verify → Move to processed/
```

**Steps:**
1. Start watchdog: `python3 watch_open_folder.py`
2. Login once (enter OTP)
3. Watchdog monitors `/Users/shraddha.s/Downloads/NDNC/open/`
4. When you drop a file:
   - Extract phone from filename
   - Extract date from file content (OCR)
   - Search for phone in All Complaints
   - Find row with matching date
   - Click complaint row
   - Click Upload button
   - Select file from `open/` folder
   - Check consent checkbox
   - Click Upload
   - Click on uploaded document
   - Click Verify button
   - Move to `/Users/shraddha.s/Downloads/NDNC/processed/`

**Result Folder:** `/Users/shraddha.s/Downloads/NDNC/processed/`

---

## 📁 Folder Structure

```
Downloads/NDNC/
├── review_pending/      # Downloaded from dashboard (Phase 1)
│   └── (files deleted after processing)
│
├── open/               # You place files here manually
│   └── (files deleted after processing)
│
├── processed_review/   # Review Pending files after verification
│   └── [FINAL LOCATION - Review Pending]
│
└── processed/          # Open files after upload & verification
    └── [FINAL LOCATION - Open]
```

---

## 🎯 Key Differences

| Aspect | Review Pending | Open |
|--------|---------------|------|
| **Source** | Dashboard download | Manual file placement |
| **Action** | Download → Verify | Upload → Verify |
| **Input Folder** | `review_pending/` | `open/` |
| **Output Folder** | `processed_review/` | `processed/` |
| **Verification** | Download doc again | Just verify upload |
| **Mode** | One-time batch | Watchdog (continuous) |

---

## 🚀 How to Run

### **Review Pending (One-time):**
```bash
cd /Users/shraddha.s/Desktop/watchdog_automation

# Download from dashboard + verify all
python3 complete_ndnc_automation.py review_pending
```

### **Open (Watchdog - Recommended):**
```bash
cd /Users/shraddha.s/Desktop/watchdog_automation

# Start watchdog (runs continuously)
python3 watch_open_folder.py
```

### **Both (Sequential):**
```bash
cd /Users/shraddha.s/Desktop/watchdog_automation

# Run Review Pending, then Open, then Watchdog
./run_all_workflows.sh
```

---

## 📊 Complete Flow Diagram

### **Review Pending:**
```
┌──────────────────────┐
│  Login to Dashboard  │
└──────────┬───────────┘
           │
           ↓
┌──────────────────────┐
│  All Complaints Page │
└──────────┬───────────┘
           │
           ↓
┌──────────────────────┐
│  Filter: Review      │
│  Pending             │
└──────────┬───────────┘
           │
           ↓
┌──────────────────────┐
│  Click Download      │
│  (Bulk)              │
└──────────┬───────────┘
           │
           ↓
┌──────────────────────┐
│  Files saved to      │
│  review_pending/     │
└──────────┬───────────┘
           │
           ↓
┌──────────────────────┐
│  For Each File:      │
│  • Extract phone     │
│  • Extract date      │
│  • Search dashboard  │
│  • Download doc      │
│  • Verify date+phone │
│  • Click Verify      │
│  • Move to           │
│    processed_review/ │
└──────────────────────┘
```

### **Open:**
```
┌──────────────────────┐
│  Drop file in open/  │
└──────────┬───────────┘
           │
           ↓
┌──────────────────────┐
│  Watchdog Detects    │
└──────────┬───────────┘
           │
           ↓
┌──────────────────────┐
│  Extract phone+date  │
└──────────┬───────────┘
           │
           ↓
┌──────────────────────┐
│  Search in Dashboard │
└──────────┬───────────┘
           │
           ↓
┌──────────────────────┐
│  Find Match by Date  │
└──────────┬───────────┘
           │
           ↓
┌──────────────────────┐
│  Upload File         │
└──────────┬───────────┘
           │
           ↓
┌──────────────────────┐
│  Click Verify        │
└──────────┬───────────┘
           │
           ↓
┌──────────────────────┐
│  Move to processed/  │
└──────────────────────┘
```

---

## ✅ What You'll See

### **Review Pending Output:**
```
======================================================================
🔄 REVIEW PENDING WORKFLOW
======================================================================

→ Step 1: Downloading Review Pending files from dashboard...
   → Looking for status dropdown button...
   → Found status filter: 'All Statuses'
   → Looking for Review Pending option...
   → Selecting Review Pending...
   ✓ Filtered by Review Pending
   
   → Looking for bulk Download button...
   → Found bulk Download button
   → Clicking to download all complaints...
   → Found 15 downloaded file(s)
   ✓ Moved: 9479760361_18-Dec-2025_Call1.pdf
   ✓ Moved: 8802125308_18-Dec-2025_Call1.pdf
   ...

📥 Downloaded 15 files via bulk download

→ Step 2: Processing downloaded files...
✓ Found 15 file(s) to process

============================================================
📄 Processing Review Pending: 9479760361_18-Dec-2025_Call1.pdf
============================================================
✓ Phone from filename: 9479760361

   → Extracting data from file content...
   ✓ Found phone: 9479760361
   ✓ Found date: 18-Dec-2025

   → Searching for: 9479760361
   ✓ Search executed

   → Looking for complaint with date: December 18, 2025
   → Scanning complaint rows...
   → Found 1 complaint(s) in search results
     Checking row 1: Portal Date = December 18, 2025
     ✓ Exact date match!
   ✓ Found matching complaint! Clicking row 1

   → Downloading document from complaint...
   → Document opened in new tab
   → URL: https://...18-Dec-2025...
   
   → Verifying document...
   ✓ Date verified (0 days difference)
   ✓ Phone number verified in document
   
   → Clicking Verify button...
   ✅ Document verified successfully!
   
   → Moved to processed_review: 9479760361_18-Dec-2025_Call1.pdf

✅ Successfully processed: 9479760361_18-Dec-2025_Call1.pdf

[Repeats for each file...]

======================================================================
📊 REVIEW PENDING RESULTS
======================================================================
Total: 15
✓ Success: 14
✗ Failed: 1
======================================================================
```

### **Open Watchdog Output:**
```
======================================================================
🔍 NDNC Open Folder Watchdog
======================================================================

✓ Browser ready! Watching for files...

[2025-01-05 14:30:45] 📄 New PDF detected: 9834877489_17-Dec-2025.pdf
[2025-01-05 14:30:50] 
============================================================
🚀 Processing 1 new file(s)
============================================================

============================================================
📄 Processing Open: 9834877489_17-Dec-2025.pdf
============================================================
✓ Phone from filename: 9834877489

   → Extracting data from file content...
   ✓ Found date: 17-Dec-2025

   → Searching for: 9834877489
   ✓ Search executed

   → Looking for complaint with date: December 17, 2025
   ✓ Found matching complaint!

   → Uploading document...
   ✓ Document uploaded!

   → Looking for uploaded document...
   → Clicking Verify button...
   ✅ Document verified successfully!

   → Moved to processed: 9834877489_17-Dec-2025.pdf

✅ Successfully processed: 9834877489_17-Dec-2025.pdf

============================================================
✓ Processing complete. Watching for new files...
============================================================
```

---

## 💡 Usage Tips

1. **Review Pending:** Run once per day/batch
2. **Open Watchdog:** Keep running all day
3. **OTP:** Enter only once at start
4. **Browser:** Stays open between files
5. **Folders:** Check processed folders to verify completion

---

## 🎯 Summary

✅ **Review Pending:** `Dashboard download → verify → processed_review/`
✅ **Open:** `Upload from open/ → verify → processed/`
✅ **Persistent browser:** No repeated OTP
✅ **Auto-archive:** Files moved after processing
✅ **Complete verification:** Date + phone number checks

