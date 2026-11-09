import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_IMG = PROJECT_ROOT / "meta" / "assets" / "rikrestin_hero.jpeg"
OUTPUT_IMG = PROJECT_ROOT / "meta" / "assets" / "rikrestin_ad_b_graphic.jpeg"

def create_graphic_ad():
    # Carica e lavora a 1080x1080 (standard perfetto per Meta Feed e Reels)
    im = Image.open(INPUT_IMG).convert("RGBA")
    im = im.resize((1080, 1080), Image.Resampling.LANCZOS)
    w, h = 1080, 1080

    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    font_bold = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
    font_reg = "/System/Library/Fonts/Supplemental/Arial.ttf"

    font_header_title = ImageFont.truetype(font_bold, 36)
    font_header_sub = ImageFont.truetype(font_bold, 24)
    
    font_badge_small = ImageFont.truetype(font_bold, 20)
    font_badge_huge = ImageFont.truetype(font_bold, 50)
    font_badge_sub = ImageFont.truetype(font_bold, 22)

    font_trust_title = ImageFont.truetype(font_bold, 28)
    font_trust_sub = ImageFont.truetype(font_reg, 21)

    # 1. Header Banner Superiore (Verde Bosco scuro con bordo dorato)
    # y: da 30 a 145
    header_box = [35, 30, w - 35, 140]
    draw.rounded_rectangle(header_box, radius=18, fill=(18, 55, 25, 235), outline=(220, 180, 60, 255), width=3)

    t1 = "TRATTAMENTO NATURALE ANTI-CADUTA"
    t2 = "CON SERENOA REPENS & FIENO GRECO"

    bb1 = draw.textbbox((0, 0), t1, font=font_header_title)
    w1 = bb1[2] - bb1[0]
    draw.text(((w - w1) / 2, 45), t1, fill=(255, 255, 255), font=font_header_title)

    bb2 = draw.textbbox((0, 0), t2, font=font_header_sub)
    w2 = bb2[2] - bb2[0]
    draw.text(((w - w2) / 2, 92), t2, fill=(215, 245, 215), font=font_header_sub)

    # 2. Bollino Circolare Offerta (In alto a destra, sopra le foglie)
    cx, cy, r = 930, 230, 105
    # Ombra leggera
    draw.ellipse([cx - r + 4, cy - r + 4, cx + r + 4, cy + r + 4], fill=(0, 0, 0, 90))
    # Badge rosso acceso con bordo bianco
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(210, 25, 25, 245), outline=(255, 255, 255, 255), width=4)

    p1 = "OFFERTA 2X1"
    p2 = "49,99€"
    p3 = "2 FLACONI"

    bp1 = draw.textbbox((0, 0), p1, font=font_badge_small)
    draw.text((cx - (bp1[2] - bp1[0]) / 2, cy - 60), p1, fill=(255, 235, 130), font=font_badge_small)

    bp2 = draw.textbbox((0, 0), p2, font=font_badge_huge)
    draw.text((cx - (bp2[2] - bp2[0]) / 2, cy - 26), p2, fill=(255, 255, 255), font=font_badge_huge)

    bp3 = draw.textbbox((0, 0), p3, font=font_badge_sub)
    draw.text((cx - (bp3[2] - bp3[0]) / 2, cy + 30), p3, fill=(255, 255, 255), font=font_badge_sub)

    # 3. Banner Inferiore (Contrassegno & Spedizione Gratuita)
    # y: da 930 a 1045
    bottom_box = [35, 935, w - 35, 1045]
    draw.rounded_rectangle(bottom_box, radius=18, fill=(15, 22, 28, 235), outline=(255, 204, 0, 255), width=3)

    # Colonna Sinistra: Pagamento alla Consegna
    col_left_x = 65
    b_left_1 = "PAGAMENTO ALLA CONSEGNA"
    b_left_2 = "Paghi in contanti al corriere"
    draw.text((col_left_x, 950), b_left_1, fill=(255, 215, 0), font=font_trust_title)
    draw.text((col_left_x, 990), b_left_2, fill=(230, 230, 230), font=font_trust_sub)

    # Divisore verticale
    draw.line([(550, 950), (550, 1030)], fill=(90, 105, 115, 200), width=2)

    # Colonna Destra: Spedizione Gratis
    col_right_x = 585
    b_right_1 = "SPEDIZIONE GRATIS"
    b_right_2 = "Consegna rapida in 24/48h"
    draw.text((col_right_x, 950), b_right_1, fill=(75, 225, 120), font=font_trust_title)
    draw.text((col_right_x, 990), b_right_2, fill=(230, 230, 230), font=font_trust_sub)

    # Composizione finale
    final_img = Image.alpha_composite(im, overlay)
    final_rgb = final_img.convert("RGB")
    final_rgb.save(OUTPUT_IMG, quality=95)
    print("Creatività grafica perfezionata (1080x1080) salvata in:", OUTPUT_IMG)

if __name__ == "__main__":
    create_graphic_ad()
