import os
import sys
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BG_PATH = Path(os.environ.get("BG_PATH", PROJECT_ROOT / "meta" / "assets" / "buongiornissimo_bg.jpg"))
HERO_PATH = PROJECT_ROOT / "meta" / "assets" / "rikrestin_hero.jpeg"
OUTPUT_PATH = PROJECT_ROOT / "meta" / "assets" / "rikrestin_ad_buongiornissimo.jpeg"

def build():
    w, h = 1080, 1080

    # 1. Carica lo sfondo toscano radioso
    bg = Image.open(BG_PATH).convert("RGBA").resize((w, h), Image.Resampling.LANCZOS)

    # 2. Prepara il ritaglio delle bottiglie con sfumatura radiale perfetta
    hero = Image.open(HERO_PATH).convert("RGBA")
    # Ritaglio centrato attorno alle bottiglie
    crop = hero.crop((460, 520, 1580, 1780))
    pw, ph = 470, 530
    prod = crop.resize((pw, ph), Image.Resampling.LANCZOS)

    # Maschera ellittica/sfumata avanzata senza bordi netti
    p_mask = Image.new("L", (pw, ph), 0)
    draw_pm = ImageDraw.Draw(p_mask)
    # Ellisse centrale piena
    draw_pm.ellipse([30, 20, pw - 30, ph - 15], fill=255)
    # Sfoca fortemente per una transizione eterea e naturale sul tavolo
    p_mask = p_mask.filter(ImageFilter.GaussianBlur(28))

    # Glow dorato dietro le bottiglie
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw_g = ImageDraw.Draw(glow)
    gx, gy = 540, 580
    for rad in range(300, 120, -25):
        a = int((300 - rad) * 0.38)
        draw_g.ellipse([gx - rad, gy - rad, gx + rad, gy + rad], fill=(255, 235, 120, a))
    glow = glow.filter(ImageFilter.GaussianBlur(30))
    bg = Image.alpha_composite(bg, glow)

    # Incolla le bottiglie centrate
    bg.paste(prod, (540 - pw // 2, 350), p_mask)

    # 3. Layer Grafica & Testi Emozionali Buongiornissimo
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    font_brush = "/System/Library/Fonts/Supplemental/Brush Script.ttf"
    font_bold = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
    font_georgia = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"

    f_title_script = ImageFont.truetype(font_brush, 96)
    f_sub_title = ImageFont.truetype(font_georgia, 26)

    f_badge_mini = ImageFont.truetype(font_bold, 18)
    f_badge_price = ImageFont.truetype(font_bold, 54)
    f_badge_sub = ImageFont.truetype(font_bold, 22)

    f_bot_title = ImageFont.truetype(font_bold, 30)
    f_bot_sub = ImageFont.truetype(font_bold, 21)

    # --- A. HEADER BUONGIORNISSIMO ---
    # Box curvo rosso bordeaux/rubino con doppia cornice dorata
    head_box = [30, 20, w - 30, 160]
    draw.rounded_rectangle(head_box, radius=22, fill=(175, 20, 35, 245), outline=(255, 220, 70, 255), width=4)

    t_main = "Un Buongiorno di Cuore e di Sole!"
    bb_m = draw.textbbox((0, 0), t_main, font=f_title_script)
    wm = bb_m[2] - bb_m[0]
    # Ombra scura
    draw.text(((w - wm) / 2 + 2, 28 + 2), t_main, fill=(50, 5, 10, 230), font=f_title_script)
    # Testo oro caldo brillante
    draw.text(((w - wm) / 2, 28), t_main, fill=(255, 248, 165), font=f_title_script)

    t_sub = "Per capelli forti, sani, folti e luminosi ogni mattina"
    bb_s = draw.textbbox((0, 0), t_sub, font=f_sub_title)
    ws = bb_s[2] - bb_s[0]
    draw.text(((w - ws) / 2, 115), t_sub, fill=(255, 255, 255), font=f_sub_title)

    # --- B. BOLLINO PROMO DEL GIORNO (Top Right) ---
    bx, by, br = 920, 275, 115
    # Effetto bagliore esterno solare
    draw.ellipse([bx - br - 12, by - br - 12, bx + br + 12, by + br + 12], fill=(255, 215, 0, 140))
    # Bordo oro lucido
    draw.ellipse([bx - br, by - br, bx + br, by + br], fill=(255, 190, 0, 255), outline=(255, 255, 255, 255), width=4)
    # Cerchio interno rosso caldo
    draw.ellipse([bx - br + 10, by - br + 10, bx + br - 10, by + br - 10], fill=(215, 20, 30, 250))

    p1 = "OFFERTA SPECIALE"
    p2 = "49,99€"
    p3 = "2 FLACONI"

    bp1 = draw.textbbox((0, 0), p1, font=f_badge_mini)
    draw.text((bx - (bp1[2] - bp1[0]) / 2, by - 66), p1, fill=(255, 240, 140), font=f_badge_mini)

    bp2 = draw.textbbox((0, 0), p2, font=f_badge_price)
    draw.text((bx - (bp2[2] - bp2[0]) / 2, by - 34), p2, fill=(255, 255, 255), font=f_badge_price)

    bp3 = draw.textbbox((0, 0), p3, font=f_badge_sub)
    draw.text((bx - (bp3[2] - bp3[0]) / 2, by + 28), p3, fill=(255, 240, 140), font=f_badge_sub)

    # --- C. PICCOLE ETICHETTE A SINISTRA (Fiducia & Ingredienti) ---
    f_pill = ImageFont.truetype(font_bold, 21)
    # Pill 1: 100% Naturale
    draw.rounded_rectangle([30, 210, 320, 265], radius=15, fill=(20, 120, 40, 245), outline=(255, 220, 80, 255), width=3)
    draw.text((50, 224), "* 100% NATURALE *", fill=(255, 255, 255), font=f_pill)

    # Pill 2: Serenoa Repens
    draw.rounded_rectangle([30, 280, 340, 335], radius=15, fill=(15, 80, 145, 245), outline=(255, 220, 80, 255), width=3)
    draw.text((45, 294), "* SERENOA REPENS *", fill=(255, 255, 255), font=f_pill)

    # --- D. FOOTER RASSICURANTE PER ANZIANI / OVER 50 ---
    bot_box = [30, 915, w - 30, 1055]
    draw.rounded_rectangle(bot_box, radius=20, fill=(16, 26, 36, 250), outline=(255, 215, 0, 255), width=4)

    # Colonna Sinistra
    draw.text((55, 930), "NESSUN PAGAMENTO ONLINE", fill=(255, 215, 0), font=f_bot_title)
    draw.text((55, 972), "Paghi comodamente in contanti al corriere alla consegna", fill=(255, 255, 255), font=f_bot_sub)
    draw.text((55, 1008), "* Nessuna carta richiesta • Consegna comoda a casa tua", fill=(185, 245, 185), font=ImageFont.truetype(font_bold, 18))

    # Divisore verticale
    draw.line([(700, 930), (700, 1040)], fill=(255, 215, 0, 180), width=3)

    # Colonna Destra
    f_sped = ImageFont.truetype(font_bold, 22)
    f_sped_huge = ImageFont.truetype(font_bold, 36)
    draw.text((725, 938), "SPEDIZIONE", fill=(80, 245, 130), font=f_sped)
    draw.text((725, 972), "GRATIS!", fill=(80, 245, 130), font=f_sped_huge)
    draw.text((725, 1016), "in 24/48 Ore", fill=(220, 220, 220), font=ImageFont.truetype(font_bold, 18))

    # 4. Salva la composizione finale
    final = Image.alpha_composite(bg, overlay)
    final_rgb = final.convert("RGB")
    final_rgb.save(OUTPUT_PATH, quality=96)
    print("Masterpiece Buongiornissimo creato con successo in:", OUTPUT_PATH)

if __name__ == "__main__":
    build()
