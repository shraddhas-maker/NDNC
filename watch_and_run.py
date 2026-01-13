"""
NDNC Watchdog Automation
Monitors the NDNC folder for new PDF files and automatically processes them
"""

import os
import time
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class Config:
    """Configuration for watchdog automation"""
    # Directory to monitor for new PDF files
    WATCH_DIRECTORY = "/Users/shraddha.s/Downloads/NDNC"
    
    # Script to run when new files are detected
    AUTOMATION_SCRIPT = "/Users/shraddha.s/Desktop/watchdog_automation/ndnc_automation.py"
    
    # Python virtual environment
    VENV_PYTHON = "/Users/shraddha.s/Desktop/watchdog_automation/venv/bin/python3"
    
    # Delay before processing (seconds) - to ensure file is fully copied
    PROCESSING_DELAY = 5
    
    # Log file
    LOG_FILE = "/Users/shraddha.s/Desktop/watchdog_automation/watchdog.log"


class PDFWatchdog(FileSystemEventHandler):
    """Handles PDF file creation events"""
    
    def __init__(self):
        self.processing = False
        self.pending_files = set()
        self.processed_files = set()  # Track files we've already queued
        self.lock = threading.Lock()
        self.processing_timer = None
        self.automation = None  # Persistent automation instance
        self.browser_ready = False
    
    def on_created(self, event):
        """Called when a new file is created"""
        if event.is_directory:
            return
        
        if event.src_path.endswith(('.pdf', '.png', '.jpg', '.jpeg')):
            with self.lock:
                # Check if we've already queued this file
                if event.src_path in self.processed_files:
                    return  # Already queued, ignore duplicate event
                
                if event.src_path.endswith('.pdf'):
                    file_type = "PDF"
                elif event.src_path.endswith('.png'):
                    file_type = "PNG"
                else:
                    file_type = "JPEG"
                self.log(f"📄 New {file_type} detected: {os.path.basename(event.src_path)}")
                
                self.pending_files.add(event.src_path)
                self.processed_files.add(event.src_path)  # Mark as queued
                
                # Cancel existing timer if any
                if self.processing_timer:
                    self.processing_timer.cancel()
                
                # Start a new timer to process files (debounce multiple events)
                self.processing_timer = threading.Timer(Config.PROCESSING_DELAY, self.trigger_processing)
                self.processing_timer.start()
    
    def on_modified(self, event):
        """Called when a file is modified (useful for large file transfers)"""
        # Ignore modify events - they're too noisy and cause duplicates
        pass
    
    def trigger_processing(self):
        """Trigger file processing after debounce delay"""
        with self.lock:
            if not self.processing and self.pending_files:
                threading.Thread(target=self.process_files, daemon=True).start()
    
    def process_files(self):
        """Process all pending files using persistent browser session"""
        with self.lock:
            if not self.pending_files:
                return
            
            self.processing = True
            files_to_process = len(self.pending_files)
        
        self.log(f"\n{'='*60}")
        self.log(f"🚀 Processing {files_to_process} new file(s)")
        self.log(f"{'='*60}\n")
        
        try:
            # Import here to avoid circular dependency
            import sys
            sys.path.insert(0, os.path.dirname(Config.AUTOMATION_SCRIPT))
            from ndnc_automation import NDNCAutomation
            
            # Initialize automation on first run
            if self.automation is None:
                self.log(f"→ First run: Initializing browser and logging in...")
                self.automation = NDNCAutomation(
                    email="shraddha.s@exotel.com",
                    pdf_directory="/Users/shraddha.s/Downloads/NDNC"
                )
                
                # Start browser and login
                self.automation.start_browser()
                if not self.automation.login():
                    self.log(f"❌ Login failed!")
                    self.automation = None
                    return
                
                if not self.automation.navigate_to_complaints():
                    self.log(f"❌ Navigation failed!")
                    self.automation.driver.quit()
                    self.automation = None
                    return
                
                self.browser_ready = True
                self.log(f"✅ Browser ready! Will process files without reopening...\n")
            
            # Process files with existing session
            if self.browser_ready:
                self.log(f"→ Processing files with existing browser session...")
                self.automation.process_all_files()
                self.log(f"✅ Files processed successfully!")
            
        except Exception as e:
            self.log(f"❌ Error during automation: {str(e)}")
            import traceback
            self.log(traceback.format_exc())
            
            # Reset automation on error
            if self.automation and self.automation.driver:
                try:
                    self.automation.driver.quit()
                except:
                    pass
            self.automation = None
            self.browser_ready = False
        
        finally:
            with self.lock:
                self.pending_files.clear()
                # Don't clear processed_files - keep track to avoid reprocessing
                # But remove after a timeout to allow reprocessing if needed
                threading.Timer(60, self.cleanup_processed_tracker).start()
                self.processing = False
            
            self.log(f"\n{'='*60}")
            self.log(f"✓ Processing complete. Browser still open. Watching for new files...")
            self.log(f"{'='*60}\n")
    
    def cleanup_processed_tracker(self):
        """Clean up processed files tracker after 60 seconds"""
        with self.lock:
            self.processed_files.clear()
    
    def cleanup(self):
        """Cleanup resources including browser"""
        self.log(f"\n→ Cleaning up resources...")
        if self.automation and self.automation.driver:
            try:
                self.log(f"→ Closing browser...")
                self.automation.driver.quit()
                self.log(f"✓ Browser closed")
            except Exception as e:
                self.log(f"⚠ Error closing browser: {e}")
        self.automation = None
        self.browser_ready = False
    
    def log(self, message):
        """Log message to console and file"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        
        # Print to console
        print(log_message)
        
        # Write to log file
        try:
            with open(Config.LOG_FILE, 'a') as f:
                f.write(log_message + '\n')
        except Exception as e:
            print(f"Warning: Could not write to log file: {e}")


def ensure_directories():
    """Ensure required directories exist"""
    watch_dir = Path(Config.WATCH_DIRECTORY)
    if not watch_dir.exists():
        watch_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created watch directory: {Config.WATCH_DIRECTORY}")
    
    log_dir = Path(Config.LOG_FILE).parent
    if not log_dir.exists():
        log_dir.mkdir(parents=True, exist_ok=True)


def main():
    """Main entry point"""
    print(f"\n{'='*60}")
    print(f"🔍 NDNC PDF Watchdog Automation")
    print(f"{'='*60}\n")
    
    # Ensure directories exist
    ensure_directories()
    
    print(f"📁 Monitoring directory: {Config.WATCH_DIRECTORY}")
    print(f"📜 Log file: {Config.LOG_FILE}")
    print(f"⚙️  Automation script: {Config.AUTOMATION_SCRIPT}")
    print(f"\n{'='*60}")
    print(f"✅ Watchdog is now active!")
    print(f"   Drop PDF files into the monitored folder to auto-process")
    print(f"   Press Ctrl+C to stop")
    print(f"{'='*60}\n")
    
    # Create event handler and observer
    event_handler = PDFWatchdog()
    observer = Observer()
    observer.schedule(event_handler, Config.WATCH_DIRECTORY, recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n\n{'='*60}")
        print(f"🛑 Stopping watchdog...")
        print(f"{'='*60}\n")
        observer.stop()
        event_handler.cleanup()
    
    observer.join()
    print("✓ Watchdog stopped successfully")


if __name__ == "__main__":
    main()

