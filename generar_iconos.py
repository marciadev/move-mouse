from PIL import Image, ImageDraw
import os

def generar_assets(logo_path, bg_color="#F39C12"):
    folders = ["Assets", "Package/Assets"]
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
        if not os.path.exists(os.path.join(folder, "Promotional")):
            os.makedirs(os.path.join(folder, "Promotional"))
    
    logo = Image.open(logo_path).convert("RGBA")
    
    # Definición de iconos y sus escalas recomendadas por Microsoft
    # (Nombre base, Ancho base, Alto base, [Escalas])
    assets_config = [
        ("SmallTile", 71, 71, [100, 125, 150, 200, 400]),
        ("Square150x150Logo", 150, 150, [100, 125, 150, 200, 400]),
        ("LargeTile", 310, 310, [100, 125, 150, 200, 400]),
        ("Square44x44Logo", 44, 44, [100, 125, 150, 200, 400]),
        ("StoreLogo", 50, 50, [100, 125, 150, 200, 400]),
        ("BadgeLogo", 24, 24, [100, 125, 150, 200, 400]),
    ]
    
    for base_name, w, h, scales in assets_config:
        for scale in scales:
            sw = int(w * (scale / 100))
            sh = int(h * (scale / 100))
            
            padding = int(sw * 0.1)
            icon_size = (sw - padding * 2, sh - padding * 2)
            
            icon_resized = logo.resize(icon_size, Image.Resampling.LANCZOS)
            canvas = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
            canvas.paste(icon_resized, (padding, padding), icon_resized)
            
            filename = f"{base_name}.scale-{scale}.png"
            # También guardamos la versión sin escala como fallback
            if scale == 100:
                for folder in folders:
                    canvas.save(os.path.join(folder, f"{base_name}.png"))
            
            for folder in folders:
                canvas.save(os.path.join(folder, filename))

    # Wide310x150Logo (Rectangular)
    wide_scales = [100, 125, 150, 200, 400]
    for scale in wide_scales:
        sw, sh = int(310 * (scale/100)), int(150 * (scale/100))
        wide_canvas = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
        
        logo_h = int(sh * 0.8)
        aspect = logo.width / logo.height
        logo_w = int(logo_h * aspect)
        
        logo_resized = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
        wide_canvas.paste(logo_resized, ((sw - logo_w)//2, (sh - logo_h)//2), logo_resized)
        
        for folder in folders:
            wide_canvas.save(os.path.join(folder, f"Wide310x150Logo.scale-{scale}.png"))
            if scale == 100:
                wide_canvas.save(os.path.join(folder, "Wide310x150Logo.png"))

    # SplashScreen (Fondo sólido)
    splash_scales = [100, 125, 150, 200, 400]
    for scale in splash_scales:
        sw, sh = int(620 * (scale/100)), int(300 * (scale/100))
        splash_canvas = Image.new("RGBA", (sw, sh), bg_color)
        
        logo_h = int(sh * 0.5)
        aspect = logo.width / logo.height
        logo_w = int(logo_h * aspect)
        
        logo_resized = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
        splash_canvas.paste(logo_resized, ((sw - logo_w)//2, (sh - logo_h)//2), logo_resized)
        
        for folder in folders:
            splash_canvas.save(os.path.join(folder, f"SplashScreen.scale-{scale}.png"))
            if scale == 100:
                splash_canvas.save(os.path.join(folder, "SplashScreen.png"))

    print("✅ ¡Nuevos assets con escalas generados en Assets/ y Package/Assets/!")

if __name__ == "__main__":
    generar_assets("logo.png")
