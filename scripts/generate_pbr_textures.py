"""
Gerador Autônomo de Texturas PBR Hiper-Realistas (Albedo, Normal Map, Roughness)
Gera:
1. Madeira Carvalho/Deck (Veios, nós, chanfros e relevo de tábuas)
2. Telhas Cerâmicas Terracota (Linhas de telhas, sobreposição, argila cozida)
3. Painel Solar TOPCon Monocristalino (Wafers de silício, barramentos de prata, grade anti-reflexo)
4. Reboco Stucco Arquitetônico (Micro-relevo de argamassa fina)
5. Gramado Tropical (Lâminas de relva e textura orgânica)
"""

import os
import numpy as np
from PIL import Image, ImageFilter

def normalize(arr):
    min_v, max_v = arr.min(), arr.max()
    if max_v - min_v > 1e-5:
        return (arr - min_v) / (max_v - min_v)
    return arr

def height_to_normal(height_map, strength=2.0):
    """Converte um mapa de altura (grayscale 0-1) em um Normal Map no espaço tangente (RGB)"""
    h, w = height_map.shape
    # Gradientes Sobel
    gy, gx = np.gradient(height_map * strength)
    
    # Vetores normais: (-gx, -gy, 1) normalizados
    norm_x = -gx
    norm_y = -gy
    norm_z = np.ones_like(height_map)
    
    length = np.sqrt(norm_x**2 + norm_y**2 + norm_z**2) + 1e-6
    nx = norm_x / length
    ny = norm_y / length
    nz = norm_z / length
    
    # Mapeia [-1, 1] para [0, 255]
    r = ((nx + 1.0) * 0.5 * 255).astype(np.uint8)
    g = ((ny + 1.0) * 0.5 * 255).astype(np.uint8)
    b = ((nz + 1.0) * 0.5 * 255).astype(np.uint8)
    
    return np.dstack([r, g, b])

def generate_wood_textures(out_dir, size=1024):
    print("[*] Gerando texturas PBR de Madeira...")
    # Cria tábuas verticais com chanfro
    num_planks = 8
    plank_width = size / num_planks
    
    y = np.linspace(0, 10, size)
    x = np.linspace(0, 80, size)
    xv, yv = np.meshgrid(x, y)
    
    # Ruído de veios esticados
    noise1 = np.sin(yv * 15.0 + np.sin(xv * 0.8) * 4.0) * 0.5 + 0.5
    noise2 = np.sin(yv * 45.0 + np.cos(xv * 1.5) * 6.0) * 0.25 + 0.25
    grain = normalize(noise1 * 0.7 + noise2 * 0.3)
    
    # Sulcos / Ranhuras entre as réguas
    seams = np.zeros((size, size))
    for i in range(num_planks):
        px = int(i * plank_width)
        w_px = max(2, int(size * 0.008))
        seams[:, max(0, px - w_px):min(size, px + w_px)] = 1.0
    
    # Altura com chanfro
    height = grain * 0.4 - seams * 0.6
    height = normalize(height)
    
    # Albedo: Tons quentes de carvalho mel / âmbar rico
    # Base: #C9681E -> RGB [201, 104, 30] a #E89138 -> [232, 145, 56]
    base_r = 195 + grain * 45 - seams * 90
    base_g = 105 + grain * 40 - seams * 70
    base_b = 30 + grain * 25 - seams * 20
    
    # Variação sutil por régua
    for i in range(num_planks):
        x_start = int(i * plank_width)
        x_end = int((i + 1) * plank_width)
        shift = ((i % 3) - 1) * 8
        base_r[:, x_start:x_end] += shift
        base_g[:, x_start:x_end] += shift * 0.7
    
    albedo = np.dstack([
        np.clip(base_r, 0, 255).astype(np.uint8),
        np.clip(base_g, 0, 255).astype(np.uint8),
        np.clip(base_b, 0, 255).astype(np.uint8)
    ])
    
    # Roughness
    rough = (0.35 + grain * 0.25 + seams * 0.35) * 255
    rough = np.clip(rough, 0, 255).astype(np.uint8)
    
    # Normal Map
    normal = height_to_normal(height, strength=4.0)
    
    Image.fromarray(albedo).save(os.path.join(out_dir, "wood_albedo.png"))
    Image.fromarray(normal).save(os.path.join(out_dir, "wood_normal.png"))
    Image.fromarray(rough).save(os.path.join(out_dir, "wood_rough.png"))
    print("[+] Texturas de Madeira PBR criadas com sucesso.")

def generate_roof_textures(out_dir, size=1024):
    print("[*] Gerando texturas PBR de Telhado Cerâmico...")
    num_tiles_x = 10
    num_tiles_y = 14
    
    x = np.linspace(0, num_tiles_x, size)
    y = np.linspace(0, num_tiles_y, size)
    xv, yv = np.meshgrid(x, y)
    
    # Curvatura cilíndrica de cada telha cerâmica
    wave_x = np.sin((xv % 1.0) * np.pi) ** 0.8
    # Sobreposição escalonada (step overlap) no eixo Y
    step_y = (yv % 1.0)
    
    height = wave_x * 0.7 + step_y * 0.3
    # Micro rugosidade de argila cozida
    micro_clay = np.random.uniform(-0.03, 0.03, (size, size))
    height = normalize(height + micro_clay)
    
    # Albedo: Vermelho Terracota Solar Vibrante (#D33F17 e #E85B28)
    base_r = 195 + wave_x * 40 - (1 - step_y) * 45
    base_g = 55 + wave_x * 25 - (1 - step_y) * 20
    base_b = 18 + wave_x * 12 - (1 - step_y) * 10
    
    albedo = np.dstack([
        np.clip(base_r, 0, 255).astype(np.uint8),
        np.clip(base_g, 0, 255).astype(np.uint8),
        np.clip(base_b, 0, 255).astype(np.uint8)
    ])
    
    rough = np.clip((0.35 + (1 - wave_x) * 0.2) * 255, 0, 255).astype(np.uint8)
    normal = height_to_normal(height, strength=5.0)
    
    Image.fromarray(albedo).save(os.path.join(out_dir, "roof_albedo.png"))
    Image.fromarray(normal).save(os.path.join(out_dir, "roof_normal.png"))
    Image.fromarray(rough).save(os.path.join(out_dir, "roof_rough.png"))
    print("[+] Texturas de Telhado PBR criadas com sucesso.")

def generate_solar_textures(out_dir, size=1024):
    print("[*] Gerando texturas PBR de Painel Solar TOPCon...")
    # Grade de 6x10 células solares monocristalinas
    cells_x = 6
    cells_y = 10
    
    # Imagem base: Azul Safira Antirreflexo profundo
    albedo = np.zeros((size, size, 3), dtype=np.uint8)
    albedo[:, :, 0] = 8   # R
    albedo[:, :, 1] = 55  # G
    albedo[:, :, 2] = 175 # B (Azul elétrico vivo fotovoltaico)
    
    height = np.ones((size, size)) * 0.5
    rough = np.ones((size, size), dtype=np.uint8) * 20 # Vidro polido ultra liso (0.08)
    
    cell_w = size / cells_x
    cell_h = size / cells_y
    
    # Linhas de separação entre células (fendas pretas/brancas)
    for cx in range(cells_x + 1):
        x_pos = int(cx * cell_w)
        x_min, x_max = max(0, x_pos - 2), min(size, x_pos + 2)
        albedo[:, x_min:x_max] = [20, 25, 35] # Fenda entre células
        height[:, x_min:x_max] = 0.2
        rough[:, x_min:x_max] = 80
        
    for cy in range(cells_y + 1):
        y_pos = int(cy * cell_h)
        y_min, y_max = max(0, y_pos - 2), min(size, y_pos + 2)
        albedo[y_min:y_max, :] = [20, 25, 35]
        height[y_min:y_max, :] = 0.2
        rough[y_min:y_max, :] = 80

    # Barramentos prateados (Busbars verticais) - 3 por célula
    for cx in range(cells_x):
        for b in range(1, 4):
            bx = int(cx * cell_w + (b * cell_w / 4))
            albedo[:, max(0, bx - 1):min(size, bx + 2)] = [225, 240, 255] # Prata metálico
            height[:, max(0, bx - 1):min(size, bx + 2)] = 0.7
            rough[:, max(0, bx - 1):min(size, bx + 2)] = 30

    # Grid de micro-linhas horizontais metálicas finas
    for fy in range(0, size, 16):
        albedo[fy:fy+1, :] = [180, 210, 245]
        
    normal = height_to_normal(height, strength=2.5)
    
    Image.fromarray(albedo).save(os.path.join(out_dir, "solar_albedo.png"))
    Image.fromarray(normal).save(os.path.join(out_dir, "solar_normal.png"))
    Image.fromarray(rough).save(os.path.join(out_dir, "solar_rough.png"))
    print("[+] Texturas de Painel Solar PBR criadas com sucesso.")

def generate_grass_textures(out_dir, size=1024):
    print("[*] Gerando texturas PBR de Gramado Tropical...")
    # Ruído orgânico multicamada
    np.random.seed(42)
    base_noise = np.random.uniform(0, 1, (size, size))
    # Suaviza para simular tufos de relva
    img_noise = Image.fromarray((base_noise * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(radius=2))
    smooth_noise = np.array(img_noise) / 255.0
    
    # Albedo: Verde Esmeralda Tropical Rico com nuances de clorofila
    r = 20 + smooth_noise * 40
    g = 145 + smooth_noise * 60
    b = 35 + smooth_noise * 45
    
    albedo = np.dstack([
        np.clip(r, 0, 255).astype(np.uint8),
        np.clip(g, 0, 255).astype(np.uint8),
        np.clip(b, 0, 255).astype(np.uint8)
    ])
    
    rough = np.clip((0.45 + smooth_noise * 0.25) * 255, 0, 255).astype(np.uint8)
    normal = height_to_normal(smooth_noise, strength=3.0)
    
    Image.fromarray(albedo).save(os.path.join(out_dir, "grass_albedo.png"))
    Image.fromarray(normal).save(os.path.join(out_dir, "grass_normal.png"))
    Image.fromarray(rough).save(os.path.join(out_dir, "grass_rough.png"))
    print("[+] Texturas de Gramado PBR criadas com sucesso.")

def generate_stucco_textures(out_dir, size=1024):
    print("[*] Gerando texturas PBR de Reboco Stucco...")
    noise = np.random.uniform(0, 1, (size, size))
    img_n = Image.fromarray((noise * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(radius=1))
    stucco = np.array(img_n) / 255.0
    
    # Albedo: Branco Marfim Quente e limpo com micro-nuances
    r = 245 + stucco * 10
    g = 244 + stucco * 10
    b = 240 + stucco * 10
    
    albedo = np.dstack([
        np.clip(r, 0, 255).astype(np.uint8),
        np.clip(g, 0, 255).astype(np.uint8),
        np.clip(b, 0, 255).astype(np.uint8)
    ])
    
    rough = np.clip((0.55 + stucco * 0.15) * 255, 0, 255).astype(np.uint8)
    normal = height_to_normal(stucco, strength=1.8)
    
    Image.fromarray(albedo).save(os.path.join(out_dir, "stucco_albedo.png"))
    Image.fromarray(normal).save(os.path.join(out_dir, "stucco_normal.png"))
    Image.fromarray(rough).save(os.path.join(out_dir, "stucco_rough.png"))
    print("[+] Texturas de Stucco PBR criadas com sucesso.")

if __name__ == "__main__":
    out = r"f:\Nova pasta\site\energia-solar\assets\3d\textures"
    os.makedirs(out, exist_ok=True)
    generate_wood_textures(out)
    generate_roof_textures(out)
    generate_solar_textures(out)
    generate_grass_textures(out)
    generate_stucco_textures(out)
    print("\n[+] TODAS AS TEXTURAS PBR FORAM GERADAS COM SUCESSO EM:", out)
