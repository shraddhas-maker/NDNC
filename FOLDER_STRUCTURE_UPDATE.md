# Folder Structure Update - Separate Processing Results

## Changes Made
Created separate folder paths for successfully processed and failed/skipped review pending files to improve organization and tracking.

## New Folder Structure

```
~/Downloads/NDNC/
├── review_pending/          # Downloaded files waiting to be processed
├── open/                    # Files for "Open" status complaints
├── processed/               # Successfully processed "Open" files
├── processed_review/        # ✅ Successfully verified "Review Pending" files (NEW PURPOSE)
└── Not_verified/            # ❌ Failed/skipped "Review Pending" files (NEW FOLDER)
```

## Folder Purposes

### `review_pending/`
- **Purpose**: Downloaded files from the dashboard waiting to be processed
- **Source**: Bulk download from "Review Pending" status filter
- **Status**: Awaiting processing

### `processed_review/`
- **Purpose**: Successfully verified "Review Pending" files
- **Criteria for files moved here**:
  - ✅ Phone number found in filename
  - ✅ URL/logo authenticity check passed
  - ✅ Phone number found in document content
  - ✅ Date found in document content
  - ✅ Phone number found in dashboard
  - ✅ Matching complaint found with valid date
  - ✅ Document verification passed
  - ✅ "Verify" button clicked successfully
- **Result**: These files have been successfully processed and verified

### `Not_verified/` (NEW)
- **Purpose**: Failed or skipped "Review Pending" files
- **Criteria for files moved here**:
  - ❌ No phone number in filename
  - ❌ No URL/logo (not authentic)
  - ❌ Phone number not found in document content
  - ❌ No dates found in document content
  - ❌ Phone number not found in dashboard
  - ❌ No matching complaint found
  - ❌ Document verification failed
  - ❌ Processing exception/error occurred
- **Result**: These files require manual review or correction

## Code Changes

### 1. complete_ndnc_automation.py

#### Added New Folder
```python
self.not_verified_folder = self.ndnc_folder / "Not_verified"
```

#### New Method: `move_file_to_not_verified()`
```python
def move_file_to_not_verified(self, file_path: Path) -> bool:
    """Move file to Not_verified folder (failed verification or skipped)"""
    try:
        dest_path = self.not_verified_folder / file_path.name
        if dest_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest_path = self.not_verified_folder / f"{file_path.stem}_{timestamp}{file_path.suffix}"
        
        shutil.move(str(file_path), str(dest_path))
        print(f"   → Moved to Not_verified: {file_path.name}")
        return True
    except Exception as e:
        print(f"   ⚠️  Could not move file: {str(e)}")
        return False
```

#### Updated File Movement Logic
- **Success Case** (line 1603): `move_file_to_processed_review()` - Verified files
- **Failure Cases** (multiple locations): `move_file_to_not_verified()` - Failed files
  - Line 1504: No phone in filename
  - Line 1527: No URL/logo (not authentic)
  - Line 1532: Phone not in document
  - Line 1537: No dates in document
  - Line 1545: Phone not in dashboard
  - Line 1587: No matching complaint
  - Line 1596: Verification failed
  - Line 1614: Exception/error

### 2. process_review_pending_only.py

#### Added New Folder
```python
self.not_verified_folder = self.ndnc_folder / "Not_verified"
```

#### Updated File Movement Logic
```python
if success:
    # Successfully verified - move to processed_review
    dest_path = self.processed_review_folder / file_path.name
    # ... move file ...
    print(f"   → Moved to: processed_review/{file_path.name}")
    results['success'] += 1
else:
    # Failed or skipped - move to Not_verified
    dest_path = self.not_verified_folder / file_path.name
    # ... move file ...
    print(f"   → Moved to: Not_verified/{file_path.name}")
    results['failed'] += 1
```

## Benefits

### 1. **Clear Separation**
- Successfully processed files are easily identifiable
- Failed files are segregated for review

### 2. **Better Tracking**
- Quick count of successful vs failed verifications
- Easy to identify which files need manual attention

### 3. **Audit Trail**
- Clear history of processing results
- Failed files can be re-attempted after fixing issues

### 4. **Workflow Clarity**
- Success path: `review_pending/` → `processed_review/`
- Failure path: `review_pending/` → `Not_verified/`

## Failure Reasons

Files in `Not_verified/` may have failed for various reasons:

### Document Issues
- No recognizable URL or logo (authenticity check)
- Phone number missing or doesn't match
- No valid dates found
- Date outside 6-month range

### Portal Issues
- Phone number not found in dashboard
- No matching complaint for the phone number
- Complaint date doesn't match document date

### Technical Issues
- Processing exception or error
- OCR extraction failure
- Network/browser issues

## Next Steps for Failed Files

For files in `Not_verified/`:
1. **Manual Review**: Check the document manually
2. **Correct Issues**: Fix filename, ensure URL/logo is visible, verify dates
3. **Re-process**: Move back to `review_pending/` and re-run
4. **Archive**: If truly invalid, archive or delete

## Impact

✅ **Better Organization**: Clear separation of success vs failure  
✅ **Easy Troubleshooting**: Failed files in dedicated folder  
✅ **Improved Tracking**: Success/failure metrics clearer  
✅ **No Data Loss**: All processed files are preserved  
✅ **Backward Compatible**: Existing successful files remain in `processed_review/`

