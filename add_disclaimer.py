import os
import sys
import argparse
from PIL import Image, ImageDraw, ImageFont

def process_images(input_dir, output_dir, disclaimer_text, version, ref_date, font_size=24, margin=10, position='bottom-right', padding=5):
    """
    Crawls through input_dir, processes each image to add a disclaimer, 
    and saves the output to output_dir.
    """
    os.makedirs(output_dir, exist_ok=True)
        
    full_disclaimer = f"{disclaimer_text} | Version: {version} | Ref Date: {ref_date}"
    
    # Try to load a default TrueType font, otherwise fallback to default PIL font
    try:
        # This is a common path for Arial on Windows
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    processed_count = 0
    error_count = 0

    valid_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff'}

    # First, collect all image files to calculate total for the progress bar
    image_files = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in valid_extensions:
                image_files.append((root, file))

    total_files = len(image_files)
    if total_files == 0:
        print("No valid images found in the input directory.")
        return

    print(f"Found {total_files} images. Starting processing...")
    print("Press Ctrl+C at any time to cancel execution.")

    try:
        for i, (root, file) in enumerate(image_files):
            input_path = os.path.join(root, file)
            
            # Maintain relative structure for output if there are subdirectories
            rel_path = os.path.relpath(root, input_dir)
            out_root = os.path.join(output_dir, rel_path)
            os.makedirs(out_root, exist_ok=True)
                
            output_path = os.path.join(out_root, file)
            
            try:
                with Image.open(input_path) as img:
                    # Convert to RGB if necessary (e.g. for some PNGs/GIFs)
                    if img.mode not in ('RGB', 'RGBA'):
                        img = img.convert('RGBA')
                        
                    # Create a drawing context
                    draw = ImageDraw.Draw(img)
                    
                    # Get text bounding box to calculate placement
                    # Fallback for older PIL versions
                    if hasattr(draw, 'textbbox'):
                        bbox = draw.textbbox((0, 0), full_disclaimer, font=font)
                        text_width = bbox[2] - bbox[0]
                        text_height = bbox[3] - bbox[1]
                    else:
                        text_width, text_height = draw.textsize(full_disclaimer, font=font)
                    
                    # Calculate position based on user argument
                    if position == 'top-left':
                        x, y = margin, margin
                    elif position == 'top-right':
                        x, y = img.width - text_width - margin, margin
                    elif position == 'top-center':
                        x, y = (img.width - text_width) // 2, margin
                    elif position == 'bottom-left':
                        x, y = margin, img.height - text_height - margin
                    elif position == 'bottom-center':
                        x, y = (img.width - text_width) // 2, img.height - text_height - margin
                    else: # default to bottom-right
                        x, y = img.width - text_width - margin, img.height - text_height - margin
                        
                    # Ensure x and y are not negative
                    x = max(0, x)
                    y = max(0, y)
                    
                    # Add a semi-transparent black background behind the text for readability
                    bg_bbox = [x - padding, y - padding, x + text_width + padding, y + text_height + padding]
                    
                    # If image has alpha channel, we can use an overlay
                    if img.mode == 'RGBA':
                        overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
                        overlay_draw = ImageDraw.Draw(overlay)
                        overlay_draw.rectangle(bg_bbox, fill=(0, 0, 0, 128))
                        overlay_draw.text((x, y), full_disclaimer, font=font, fill=(255, 255, 255, 255))
                        img = Image.alpha_composite(img, overlay)
                    else:
                        draw.rectangle(bg_bbox, fill=(0, 0, 0))
                        draw.text((x, y), full_disclaimer, font=font, fill=(255, 255, 255))
                        
                    # Save the image
                    img.save(output_path)
                    processed_count += 1
                    
            except Exception as e:
                # We print errors on a new line so it doesn't mess up the progress bar
                print(f"\nFailed to process {file}: {e}")
                error_count += 1

            # Update progress bar
            progress = (i + 1) / total_files
            bar_length = 40
            block = int(round(bar_length * progress))
            text = f"\rProgress: [{'#' * block + '-' * (bar_length - block)}] {int(progress * 100)}% ({i + 1}/{total_files})"
            sys.stdout.write(text)
            sys.stdout.flush()
            
    except KeyboardInterrupt:
        print("\n\nExecution cancelled by user (Ctrl+C).")

    print("\n" + "-" * 30)
    print(f"Summary: Processed {processed_count} images successfully. {error_count} errors.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Add disclaimer overlay to images.")
    parser.add_argument('--input_dir', required=True, help="Directory containing input images.")
    parser.add_argument('--output_dir', required=True, help="Directory to save processed images.")
    parser.add_argument('--text', default="IAS Species Map", help="Main disclaimer text.")
    parser.add_argument('--version', default="1.0", help="Version number to display.")
    parser.add_argument('--date', default="2026-04-30", help="Reference date to display.")
    parser.add_argument('--fontsize', type=int, default=18, help="Font size for the overlay text.")
    parser.add_argument('--padding', type=int, default=5, help="Inner padding around the text background.")
    parser.add_argument('--position', default="bottom-right", 
                        choices=['top-left', 'top-right', 'top-center', 'bottom-left', 'bottom-right', 'bottom-center'],
                        help="Position of the text overlay on the image.")
    
    args = parser.parse_args()
    
    process_images(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        disclaimer_text=args.text,
        version=args.version,
        ref_date=args.date,
        font_size=args.fontsize,
        position=args.position,
        padding=args.padding
    )
