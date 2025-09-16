import cv2
import os
import string

def setup_directories(base_dir='SignImage48x48/'):
    """Create directory structure for storing sign language images"""
    try:
        if not os.path.exists(base_dir):
            os.mkdir(base_dir)
        
        # Create blank directory
        blank_dir = os.path.join(base_dir, 'blank')
        if not os.path.exists(blank_dir):
            os.mkdir(blank_dir)
        
        # Create A-Z directories
        for letter in string.ascii_uppercase:
            letter_dir = os.path.join(base_dir, letter)
            if not os.path.exists(letter_dir):
                os.mkdir(letter_dir)
        
        return True
    except OSError as e:
        print(f"❌ Error creating directories: {e}")
        return False

def get_file_counts(base_dir):
    """Get current file counts for all directories"""
    counts = {}
    try:
        # Count files in A-Z directories
        for letter in string.ascii_uppercase:
            letter_dir = os.path.join(base_dir, letter)
            counts[letter.lower()] = len(os.listdir(letter_dir)) if os.path.exists(letter_dir) else 0
        
        # Count blank files
        blank_dir = os.path.join(base_dir, 'blank')
        counts['blank'] = len(os.listdir(blank_dir)) if os.path.exists(blank_dir) else 0
        
        return counts
    except OSError as e:
        print(f"❌ Error reading directories: {e}")
        return {}

def save_image(frame, directory, letter, count):
    """Save the processed frame as an image"""
    try:
        filename = f"{count}.jpg"
        filepath = os.path.join(directory, letter.upper(), filename)
        if letter == 'blank':
            filepath = os.path.join(directory, 'blank', filename)
        
        cv2.imwrite(filepath, frame)
        print(f"✅ Saved {filepath}")
        return True
    except Exception as e:
        print(f"❌ Error saving image: {e}")
        return False

def main():
    directory = 'SignImage48x48/'
    print(f"Current directory: {os.getcwd()}")
    
    # Setup directories
    if not setup_directories(directory):
        return
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Camera not detected")
        return
    
    print("📹 Camera initialized successfully")
    print("Instructions:")
    print("- Press a-z to capture images for respective letters")
    print("- Press '.' (period) to capture blank images")
    print("- Press ESC to quit")
    
    # Get initial counts
    counts = get_file_counts(directory)
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to read from camera")
                break
            
            # Draw ROI rectangle
            cv2.rectangle(frame, (0, 40), (300, 300), (255, 255, 255), 2)
            
            # Show current counts on frame
            y_offset = 320
            for i, (key, count) in enumerate(counts.items()):
                if i % 9 == 0 and i > 0:  # New line every 9 items
                    y_offset += 20
                x_pos = 10 + (i % 9) * 80
                cv2.putText(frame, f"{key}:{count}", (x_pos, y_offset), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
            
            cv2.imshow("Data Collection", frame)
            
            # Extract and process ROI
            roi = frame[40:300, 0:300]
            cv2.imshow("ROI", roi)
            
            # Convert to grayscale and resize
            processed_frame = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            processed_frame = cv2.resize(processed_frame, (48, 48))
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            
            # Quit conditions
            if key == 27:  # ESC
                break
            
            # Save images based on key press
            elif key == ord('.'):  # Blank
                if save_image(processed_frame, directory, 'blank', counts['blank']):
                    counts['blank'] += 1
            
            elif key >= ord('a') and key <= ord('z'):  # Letters a-z
                letter = chr(key)
                if save_image(processed_frame, directory, letter, counts[letter]):
                    counts[letter] += 1
    
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
    
    finally:
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        print("🔒 Resources cleaned up")
        
        # Print final statistics
        print("\n📊 Final Statistics:")
        total_images = sum(counts.values())
        for key, count in sorted(counts.items()):
            print(f"{key.upper()}: {count} images")
        print(f"Total: {total_images} images")

if __name__ == "__main__":
    main()
