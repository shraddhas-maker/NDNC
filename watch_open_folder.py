"""
Watchdog for Open Complaints Folder
Monitors Downloads/NDNC/open/ and automatically processes new files
"""

import os
import time
import threading
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class OpenFolderWatchdog(FileSystemEventHandler):
    """Handles new file detection in Open folder"""
    
    def __init__(self, automation):
        self.automation = automation
        self.processing = False
        self.pending_files = set()
        self.processed_files = set()
        self.lock = threading.Lock()
        self.processing_timer = None
    
    def on_created(self, event):
        """Called when a new file is created"""
        if event.is_directory:
            return
        
        if event.src_path.endswith(('.pdf', '.png')):
            with self.lock:
                # Check if already queued
                if event.src_path in self.processed_files:
                    return
                
                file_type = "PDF" if event.src_path.endswith('.pdf') else "PNG"
                self.log(f"📄 New {file_type} detected: {os.path.basename(event.src_path)}")
                
                self.pending_files.add(event.src_path)
                self.processed_files.add(event.src_path)
                
                # Cancel existing timer
                if self.processing_timer:
                    self.processing_timer.cancel()
                
                # Start timer to process (debounce)
                self.processing_timer = threading.Timer(5, self.trigger_processing)
                self.processing_timer.start()
    
    def trigger_processing(self):
        """Trigger file processing"""
        with self.lock:
            if not self.processing and self.pending_files:
                threading.Thread(target=self.process_files, daemon=True).start()
    
    def process_files(self):
        """Process all pending files"""
        with self.lock:
            if not self.pending_files:
                return
            
            self.processing = True
            files_to_process = list(self.pending_files)
        
        self.log(f"\n{'='*60}")
        self.log(f"🚀 Processing {len(files_to_process)} new file(s)")
        self.log(f"{'='*60}\n")
        
        try:
            for file_path_str in files_to_process:
                file_path = Path(file_path_str)
                if file_path.exists():
                    self.automation.process_open_file(file_path)
                    time.sleep(2)  # Wait before next file
        
        except Exception as e:
            self.log(f"❌ Error during processing: {str(e)}")
            import traceback
            traceback.print_exc()
        
        finally:
            with self.lock:
                self.pending_files.clear()
                # Clear processed tracker after 60 seconds
                threading.Timer(60, self.cleanup_tracker).start()
                self.processing = False
            
            self.log(f"\n{'='*60}")
            self.log(f"✓ Processing complete. Watching for new files...")
            self.log(f"{'='*60}\n")
    
    def cleanup_tracker(self):
        """Clean up processed files tracker"""
        with self.lock:
            self.processed_files.clear()
    
    def log(self, message):
        """Log message"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {message}")


def main():
    """Main entry point for watchdog"""
    from complete_ndnc_automation import NDNCCompleteAutomation
    
    print(f"\n{'='*70}")
    print(f"🔍 NDNC Open Folder Watchdog")
    print(f"{'='*70}\n")
    
    EMAIL = "shraddha.s@exotel.com"
    WATCH_FOLDER = Path.home() / "Downloads" / "NDNC" / "open"
    
    # Ensure folder exists
    WATCH_FOLDER.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Monitoring: {WATCH_FOLDER}")
    print(f"📧 Email: {EMAIL}")
    print(f"\n{'='*70}")
    print(f"✅ Watchdog is active!")
    print(f"   Drop PDF/PNG files into the open folder to auto-process")
    print(f"   Press Ctrl+C to stop")
    print(f"{'='*70}\n")
    
    # Initialize automation (browser will start on first file)
    automation = NDNCCompleteAutomation(email=EMAIL)
    
    # Initialize browser session
    print("→ Starting browser session...")
    automation.start_browser()
    
    if not automation.login():
        print("✗ Login failed. Exiting...")
        return
    
    print("✓ Browser ready! Watching for files...\n")
    
    # Create event handler and observer
    event_handler = OpenFolderWatchdog(automation)
    observer = Observer()
    observer.schedule(event_handler, str(WATCH_FOLDER), recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n\n{'='*70}")
        print(f"🛑 Stopping watchdog...")
        print(f"{'='*70}\n")
        observer.stop()
        
        # Close browser
        if automation.driver:
            automation.driver.quit()
            print("✓ Browser closed")
    
    observer.join()
    print("✓ Watchdog stopped successfully")


if __name__ == "__main__":
    main()

