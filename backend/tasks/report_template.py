from fpdf import FPDF
import pandas as pd
import os
from datetime import datetime
# Color scheme for professional look
COLORS = {
    'primary': (41, 128, 185),      # Blue
    'secondary': (52, 73, 94),      # Dark gray
    'accent': (231, 76, 60),        # Red
    'light_gray': (236, 240, 241),  # Light gray
    'white': (255, 255, 255),       # White
    'text_dark': (44, 62, 80),      # Dark text
    'text_light': (127, 140, 141)   # Light text
}
FPS = 1

def frame_to_seconds(frame_name, fps=1):
    try:
        frame_number = int(frame_name.replace("frame_", "").replace("_result", ""))
        return round(frame_number / fps, 2)
    except Exception:
        return 0

class EnhancedPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=False)  # Disable auto page break for manual control
        
    def header(self):
        # Professional header with logo space and title
        self.set_fill_color(*COLORS['primary'])
        self.rect(0, 0, 210, 25, 'F')
        
        # Title
        self.set_font("Arial", "B", 16)
        self.set_text_color(255, 255, 255)
        self.set_y(8)
        self.cell(0, 10, "NBA BROADCAST BRAND VISIBILITY REPORT", 0, 1, "C")
        
        # Subtitle
        self.set_font("Arial", "", 10)
        self.set_text_color(200, 200, 200)
        self.cell(0, 6, f"Generated on {datetime.now().strftime('%B %d, %Y')}", 0, 1, "C")
        
        # Reset text color
        self.set_text_color(*COLORS['text_dark'])
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(*COLORS['text_light'])
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

    def check_page_break(self, height_needed):
        """Check if we need a page break for the given height"""
        if self.get_y() + height_needed > 280:  # Page height - margin
            self.add_page()
            return True
        return False

    def create_section_header(self, title, color=None):
        """Create a professional section header"""
        if color is None:
            color = COLORS['secondary']
        
        self.check_page_break(15)  # Check if header fits
        
        self.ln(5)
        self.set_fill_color(*color)
        self.set_text_color(255, 255, 255)
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, f"  {title}", 0, 1, "L", 1)
        self.set_text_color(*COLORS['text_dark'])
        self.ln(3)

    def create_info_box(self, title, content, color=None):
        """Create an information box with border"""
        if color is None:
            color = COLORS['light_gray']
        
        # Calculate needed height
        lines = content.split('\n')
        needed_height = 8 + (len(lines) * 5) + 5  # Header + content + padding
        self.check_page_break(needed_height)
            
        self.set_fill_color(*color)
        self.set_draw_color(*COLORS['secondary'])
        self.rect(self.get_x(), self.get_y(), 190, 8, 'FD')
        
        self.set_font("Arial", "B", 10)
        # Clean title text
        clean_title = title.encode('latin-1', errors='ignore').decode('latin-1')
        self.cell(190, 8, f"  {clean_title}", 0, 1, "L")
        
        self.set_font("Arial", "", 9)
        self.set_x(self.get_x() + 5)
        # Clean content text
        clean_content = content.encode('latin-1', errors='ignore').decode('latin-1')
        self.multi_cell(180, 5, clean_content)
        self.ln(2)

    def create_styled_table(self, headers, data, col_widths=None):
        """Create a professionally styled table"""
        if col_widths is None:
            col_widths = [190 // len(headers)] * len(headers)
        
        # Calculate needed height
        needed_height = 8 + (len(data) * 7) + 5  # Header + rows + margin
        self.check_page_break(needed_height)
        
        # Header row
        self.set_fill_color(*COLORS['secondary'])
        self.set_text_color(255, 255, 255)
        self.set_font("Arial", "B", 10)
        
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 8, header, 1, 0, "C", 1)
        self.ln()
        
        # Data rows
        self.set_text_color(*COLORS['text_dark'])
        self.set_font("Arial", "", 9)
        
        for i, row in enumerate(data):
            # Alternate row colors
            if i % 2 == 0:
                self.set_fill_color(*COLORS['light_gray'])
                fill = True
            else:
                self.set_fill_color(255, 255, 255)
                fill = True
            
            for j, cell in enumerate(row):
                align = "R" if j > 0 else "L"  # Right align numbers, left align text
                # Clean cell content to remove non-latin characters
                clean_cell = str(cell).encode('latin-1', errors='ignore').decode('latin-1')
                self.cell(col_widths[j], 7, clean_cell, 1, 0, align, fill)
            self.ln()
        
        self.ln(5)

    def add_key_metrics_summary(self, df_totals, tot_col):
        """Add a key metrics summary box"""
        top_brand = df_totals.iloc[0]
        total_frames = len(df_totals)
        avg_score = df_totals[tot_col].mean()
        
        metrics_text = f"""
Total Brands Analyzed: {total_frames}
Top Performing Brand: {top_brand['Brand']} (Score: {round(top_brand[tot_col], 2)})
Average Visibility Score: {round(avg_score, 2)}
Analysis Duration: 200 seconds (estimated)
        """.strip()
        
        self.create_info_box("KEY METRICS", metrics_text, COLORS['accent'])

    def add_methodology_section(self):
        """Add detailed methodology section"""
        methodology_text = """
This analysis uses advanced OCR (Optical Character Recognition) technology to detect brand mentions in video frames extracted from NBA broadcast footage.

Frame Processing: Video frames are extracted at 1 FPS and processed using PaddleOCR for text detection.

Brand Detection: A hybrid approach combining exact matches and fuzzy string matching identifies brand appearances with high accuracy.

Scoring System: Each detection receives a confidence score based on OCR accuracy and string similarity, providing quantitative visibility metrics.

Data Validation: All detections are cross-referenced against known brand variants to minimize false positives.
        """.strip()
        
        self.create_info_box("METHODOLOGY", methodology_text)

    def add_brand_analysis_page(self, brand, frame_texts, max_frame, min_frame, max_count, min_count):
        """Add a complete brand analysis on a single page"""
        self.add_page()
        self.create_section_header(f"{brand.upper()} - DETAILED ANALYSIS", COLORS['secondary'])
        
        # Performance summary table
        summary_data = [
            ["Peak Frame", f"{max_frame} ({frame_to_seconds(max_frame)}s)" if max_frame else "N/A", str(max_count)],
            ["Lowest Frame", f"{min_frame} ({frame_to_seconds(min_frame)}s)" if min_frame else "N/A", str(min_count) if min_frame else "N/A"]
        ]
        
        self.create_styled_table(["Metric", "Frame (Time)", "Detection Count"], summary_data, [50, 90, 50])
        
        # Calculate remaining space for content
        current_y = self.get_y()
        available_space = 280 - current_y  # Page height - current position
        
        # Prioritize peak frame analysis if space is limited
        frames_to_analyze = []
        if max_frame:
            frames_to_analyze.append(("PEAK VISIBILITY", max_frame))
        if min_frame and available_space > 120:  # Only add if sufficient space
            frames_to_analyze.append(("LOWEST VISIBILITY", min_frame))
        
        for label, frame in frames_to_analyze:
            if not frame:
                continue
            
            # Check if we have enough space for this section (header + image + text ~100mm)
            if self.get_y() + 100 > 280:
                break  # Skip if not enough space
                
            # Create subsection header
            self.ln(3)
            self.set_fill_color(*COLORS['light_gray'])
            self.set_text_color(*COLORS['text_dark'])
            self.set_font("Arial", "B", 10)
            self.cell(0, 8, f"  {label} FRAME ANALYSIS", 0, 1, "L", 1)
            self.ln(2)
            
            # Add image if exists and fits
            img = find_frame_image(frame)
            if img and os.path.exists(img):
                # Calculate image size to fit available space
                remaining_space = 280 - self.get_y() - 30  # Leave space for text
                img_height = min(60, remaining_space)  # Limit image height
                img_width = img_height * 1.5  # Maintain aspect ratio
                
                if img_width > 170:  # Max width constraint
                    img_width = 170
                    img_height = img_width / 1.5
                
                if self.get_y() + img_height < 270:  # Check if image fits
                    self.image(img, x=20, w=img_width, h=img_height)
                    self.ln(5)
            
            # Add detected text (compact format)
            matches = [line for line in frame_texts.get(frame, []) 
                      if any(kw in line.lower() for kw in BRAND_KEYWORDS.get(brand, []))]
            
            if matches and self.get_y() < 260:  # Only add if space available
                self.set_font("Arial", "B", 9)
                self.cell(0, 5, "Detected Text:", ln=1)
                self.set_font("Arial", "", 8)  # Smaller font for compact display
                
                # Limit matches to fit remaining space
                max_matches = min(2, len(matches))
                for match in matches[:max_matches]:
                    if self.get_y() > 270:  # Stop if running out of space
                        break
                    self.cell(5, 4, "-", 0, 0)
                    clean_match = match[:80].encode('latin-1', errors='ignore').decode('latin-1')  # Truncate long text
                    self.cell(0, 4, clean_match, 0, 1)
                
                if len(matches) > max_matches:
                    self.set_font("Arial", "I", 8)
                    self.cell(0, 4, f"... and {len(matches) - max_matches} more detections", 0, 1)
