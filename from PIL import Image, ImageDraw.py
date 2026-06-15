from PIL import Image, ImageDraw

# Create a blank white image
img_width, img_height = 1600, 1200
img = Image.new("RGB", (img_width, img_height), "white")
draw = ImageDraw.Draw(img)

# Title
draw.text((20, 20), "Lean Canvas - Affordable AI-Based Wearable Safety Coat", fill="black")

# Lean Canvas sections (simplified)
sections = [
    ("Problem", "High accident risk for night/rural workers; lack of affordable smart PPE; slow emergency response"),
    ("Customer Segments", "Rural industries, construction, municipalities, logistics, disaster response"),
    ("Unique Value Proposition", "Affordable AI-powered coat with visibility, hazard detection, comfort, alerts"),
    ("Solution", "Reflective LEDs; AI hazard detection; fall detection; Peltier comfort; wireless alerts"),
    ("Channels", "Direct sales, government tenders, PPE suppliers, online B2B marketplaces"),
    ("Revenue Streams", "Product sales, bulk orders, maintenance/service contracts"),
    ("Cost Structure", "Materials, manufacturing, AI dev/testing, marketing, distribution"),
    ("Key Metrics", "Units sold, adoption rate, incident reduction, repeat orders"),
    ("Unfair Advantage", "First mover in low-cost AI PPE; AI & IoT expertise; scalable design")
]

# Grid layout
col_width = img_width // 3
row_height = img_height // 3
index = 0

for row in range(3):
    for col in range(3):
        if index < len(sections):
            title, content = sections[index]
            x = col * col_width + 10
            y = row * row_height + 60
            # Draw box
            draw.rectangle([x, y, x + col_width - 20, y + row_height - 20], outline="black", width=2)
            # Title
            draw.text((x + 5, y + 5), title, fill="black")
            # Content
            draw.multiline_text((x + 5, y + 25), content, fill="black", spacing=4)
            index += 1

# Save image
simple_lean_canvas_path = "/mnt/data/Simple_Lean_Canvas_Safety_Coat.png"
img.save(simple_lean_canvas_path)

simple_lean_canvas_path
