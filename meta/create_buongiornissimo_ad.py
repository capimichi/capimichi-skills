import sys
import math
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

PROJECT_ROOT = Path(__file__).resolve().parent.parent
HERO_IMG = PROJECT_ROOT / "meta" / "assets" / "rikrestin_hero.jpeg"
OUTPUT_DIR = PROJECT_ROOT / "meta" / "assets"

def create_buongiornissimo_variant(bg_path=None, output_path=None):
    if output_path is None:
        output_path = OUTPUT_DIR / "rikrestin_buongiornissimo_ad.jpeg"

    w, h = 1080, 1080

    # 1. Base Image
    if bg_path and Path(bg_path).exists():
        base = Image.open(bg_path).convert("RGBA").resize((w, h), Image.Resampling.LANCZOS)
    else:
        # Crea sfondo radioso ad alta saturazione con gradiente solare
        base = Image.new("RGBA", (w, h), (255, 248, 220, 255))
        draw_b = ImageDraw.Draw(base)
        for y in range(h):
            # Gradiente dall'oro/arancio caldo in alto al verde natura rigoglioso in basso
            r = int(255 - (y / h) * 180)
            g = int(210 + math.sin(y / h * 2) * 40 - (y / h) * 120)
            b = int(120 - (y / h) * 90)
            draw_b.line([(0, y), (w, y)], fill=(max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)), 255))

    # Boost saturazione e calore generale
    enhancer = ImageEnhance.Color(base)
    base = enhancer.enhance(1.35)
    bright = ImageEnhance.Brightness(base)
    base = bright.enhance(1.05)

    # 2. Carica e prepara il prodotto Rikrestin Hero
    prod = Image.open(HERO_IMG).convert("RGBA")
    
    # Se usiamo il background generato, isoliamo/sfumiamo il prodotto al centro
    # Altrimenti usiamo il riquadro centrale con un bagliore dorato
    prod = prod.resize((820, 820), Image.Resampling.LANCZOS)
    
    # Crea una maschera ellittica sfumata per inserire il prodotto con un'aura di luce
    mask = Image.new("L", (820, 820), 0)
    draw_m = ImageDraw.Draw(mask)
    draw_m.ellipse([30, 30, 790, 790], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(35))

    # Glow dorato dietro al prodotto
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw_g = ImageDraw.Draw(glow)
    cx_prod, cy_prod = 540, 520
    for rad in range(460, 200, -20):
        alpha = int((460 - rad) * 0.45)
        draw_g.ellipse([cx_prod - rad, cy_prod - rad, cx_prod + rad, cy_prod + rad], fill=(255, 230, 110, alpha))
    glow = glow.filter(ImageFilter.GaussianBlur(40))
    base = Image.alpha_composite(base, glow)

    # Incolla il prodotto con la maschera sfumata
    prod_pos = (540 - 410, 520 - 410)
    base.paste(prod, prod_pos, mask)

    # 3. Layer Grafico / Overlay Buongiornissimo
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Raggi di sole dall'angolo in alto a sinistra
    sun_x, sun_y = 60, 60
    for angle_deg in range(0, 90, 4):
        rad = math.radians(angle_deg)
        length = 1300
        x2 = sun_x + length * math.cos(rad)
        y2 = sun_y + length * math.sin(rad)
        draw.line([(sun_x, sun_y), (x2, y2)], fill=(255, 255, 210, 28), width=16)

    # Font
    font_brush = "/System/Library/Fonts/Supplemental/Brush Script.ttf"
    font_arial_bold = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
    font_georgia_bold = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"

    f_buongiorno = ImageFont.truetype(font_brush, 95)
    f_sub_buongiorno = ImageFont.truetype(font_georgia_bold, 30)
    
    f_badge_super = ImageFont.truetype(font_arial_bold, 22)
    f_badge_price = ImageFont.truetype(font_arial_bold, 56)
    f_badge_qty = ImageFont.truetype(font_arial_bold, 24)

    f_bottom_title = ImageFont.truetype(font_arial_bold, 30)
    f_bottom_sub = ImageFont.truetype(font_arial_bold, 21)

    # 4. Header "Buongiornissimo" caldo ed emozionale
    # Banner superiore con curvatura e bordo oro lucido
    header_box = [30, 20, w - 30, 155]
    # Sfondo rosso rubino caldo / bordeaux festoso tipico delle cartoline
    draw.rounded_rectangle(header_box, radius=22, fill=(185, 25, 40, 245), outline=(255, 220, 80, 255), width=4)

    # Testo "☀️ Buongiorno di Cuore! 🌸" in Brush Script dorato con ombra
    t_main = "☀️ Un Buongiorno Pieno di Vita! 🌸"
    # Ombra testo
    bb_m = draw.textbbox((0, 0), t_main, font=f_buongiorno)
    w_m = bb_m[2] - bb_m[0]
    draw.text(((w - w_m) / 2 + 2, 28 + 2), t_main, fill=(60, 10, 15, 200), font=f_buongiorno)
    # Testo dorato luminoso
    draw.text(((w - w_m) / 2, 28), t_main, fill=(255, 245, 170), font=f_buongiorno)

    t_sub = "Dona nuova forza, densità e volume ai tuoi capelli ogni mattina 🌿"
    bb_s = draw.textbbox((0, 0), t_sub, font=f_sub_buongiorno)
    w_s = bb_s[2] - bb_s[0]
    draw.text(((w - w_s) / 2, 108), t_sub, fill=(255, 255, 255), font=f_sub_buongiorno)

    # 5. Bollino Solare "Offerta Straordinaria" a forma di sole/cuore
    bx, by, br = 920, 260, 115
    # Effetto bagliore esterno
    draw.ellipse([bx - br - 10, by - br - 10, bx + br + 10, by + br + 10], fill=(255, 215, 0, 120))
    # Cerchio oro caldo
    draw.ellipse([bx - br, by - br, bx + br, by + br], fill=(255, 185, 0, 250), outline=(255, 255, 255, 255), width=5)
    # Cuoricino rosso centrale o cerchio interno
    draw.ellipse([bx - br + 12, by - br + 12, bx + br - 12, by + br - 12], fill=(210, 20, 30, 245))

    p_top = "PROMO DEL GIORNO"
    p_mid = "49,99€"
    p_bot = "2 FLACONI"
    p_free = "Spedizione Gratis!"

    bp_t = draw.textbbox((0, 0), p_top, font=f_badge_super)
    draw.text((bx - (bp_t[2] - bp_t[0]) / 2, by - 70), p_top, fill=(255, 240, 140), font=f_badge_super)

    bp_m = draw.textbbox((0, 0), p_mid, font=f_badge_price)
    draw.text((bx - (bp_m[2] - bp_m[0]) / 2, by - 35), p_mid, fill=(255, 255, 255), font=f_badge_price)

    bp_b = draw.textbbox((0, 0), p_bot, font=f_badge_qty)
    draw.text((bx - (bp_b[2] - bp_b[0]) / 2, by + 26), p_bot, fill=(255, 240, 140), font=f_badge_qty)

    # Nastrone o targhetta "100% Naturale" a sinistra
    tag_box = [30, 200, 320, 255]
    draw.rounded_rectangle(tag_box, radius=15, fill=(25, 125, 45, 240), outline=(255, 220, 80, 255), width=3)
    f_tag = ImageFont.truetype(font_arial_bold, 22)
    t_tag = "🌿 100% NATURALE"
    bb_tag = draw.textbbox((0, 0), t_tag, font=f_tag)
    draw.text((30 + (290 - (bb_tag[2] - bb_tag[0])) / 2, 214), t_tag, fill=(255, 255, 255), font=f_tag)

    tag_box2 = [30, 265, 340, 320]
    draw.rounded_rectangle(tag_box2, radius=15, fill=(20, 80, 140, 240), outline=(255, 220, 80, 255), width=3)
    t_tag2 = "✨ SERENOA & FIENO"
    bb_tag2 = draw.textbbox((0, 0), t_tag2, font=f_tag)
    draw.text((30 + (310 - (bb_tag2[2] - bb_tag2[0])) / 2, 279), t_tag2, fill=(255, 255, 255), font=f_tag)

    # 6. Banner Inferiore Ultra-Rassicurante per Over 50
    # Massima enfasi su: NESSUN PAGAMENTO ANTICIPATO, PAGA AL POSTINO / CORRIERE IN CONTANTI
    bot_box = [25, 915, w - 25, 1055]
    draw.rounded_rectangle(bot_box, radius=20, fill=(15, 25, 35, 248), outline=(255, 215, 0, 255), width=4)

    # Colonna Sinistra
    draw.text((50, 930), "📦 NESSUN PAGAMENTO ONLINE", fill=(255, 215, 0), font=f_bottom_title)
    draw.text((50, 972), "Paghi comodamente in contanti alla consegna", fill=(255, 255, 255), font=f_bottom_sub)
    draw.text((50, 1005), "✅ Consegna veloce e discreta a casa tua in tutta Italia", fill=(190, 245, 190), font=ImageFont.truetype(font_arial_bold, 18))

    # Divisore
    draw.line([(680, 930), (680, 1040)], fill=(255, 215, 0, 160), width=3)

    # Colonna Destra (Bollino Garanzia)
    f_gar = ImageFont.truetype(font_arial_bold, 24)
    draw.text((710, 940), "🚚 SPEDIZIONE", fill=(80, 245, 130), font=f_gar)
    draw.text((710, 975), "GRATUITA!", fill=(80, 245, 130), font=ImageFont.truetype(font_arial_bold, 36))
    draw.text((710, 1018), "in 24/48 Ore", fill=(230, 230, 230), font=ImageFont.truetype(font_arial_bold, 18))

    # Unisci tutto
    final = Image.alpha_composite(base, overlay)
    final_rgb = final.convert("RGB")
    final_rgb.save(output_path, quality=96)
    print("Grafica Buongiornissimo generata con successo in:", output_path)
    return output_path

if __name__ == "__main__":
    create_buongiornissimo_variant()
