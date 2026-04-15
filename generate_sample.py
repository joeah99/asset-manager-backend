from PIL import Image, ImageDraw

img = Image.new('RGB', (800, 600), color=(255, 255, 255))
d = ImageDraw.Draw(img)

# Fallback font handling
try:
    from PIL import ImageFont
    # Try generic sans-serif, fallback to default if missing
    font = ImageFont.truetype("arial.ttf", 24)
except Exception:
    font = ImageFont.load_default()

# Make it look like a real invoice
d.text((50, 50), "INVOICE #99238", fill=(0,0,0), font=font)
d.text((50, 100), "Date: 2025-06-12", fill=(0,0,0), font=font)
d.text((50, 150), "Vendor: AgTech Solutions LLC", fill=(0,0,0), font=font)

d.text((50, 250), "Item Description", fill=(0,0,0), font=font)
d.text((450, 250), "Total Amount", fill=(0,0,0), font=font)
d.line([(50, 280), (600, 280)], fill=(0,0,0), width=2)

d.text((50, 300), "John Deere 8R 410 Tractor", fill=(0,0,0), font=font)
d.text((450, 300), "$420,500.00", fill=(0,0,0), font=font)

img.save('sample_invoice.png')
print("Successfully generated sample_invoice.png")
