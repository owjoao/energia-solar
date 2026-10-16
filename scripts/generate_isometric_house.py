"""
Script Blender 5.x: Casa Isométrica Estilizada com Texturas PBR Hiper-Realistas
Aplica:
- Texturas PBR reais de Madeira (Albedo, Normal e Roughness)
- Texturas PBR de Telhado Cerâmico Terracota com ondulações reais
- Texturas PBR de Células Fotovoltaicas TOPCon com Barramentos Prateados
- Texturas PBR de Reboco Stucco Arquitetônico
- Texturas PBR de Gramado Tropical Esmeralda
- Smart UV Mapping em todas as peças
- Render com iluminação de estúdio de alta definição
- Exportação GLB com texturas PBR embutidas
"""

import bpy
import bmesh
import math
import os

TEXTURES_DIR = r"f:\Nova pasta\site\energia-solar\assets\3d\textures"

def clean_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for obj in bpy.data.objects:
        bpy.data.objects.remove(obj, do_unlink=True)
    for mat in bpy.data.materials:
        bpy.data.materials.remove(mat, do_unlink=True)
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh, do_unlink=True)
    for img in bpy.data.images:
        bpy.data.images.remove(img, do_unlink=True)

def create_pbr_material(name, albedo_file, normal_file=None, rough_file=None, fallback_color=(0.8, 0.8, 0.8, 1.0), metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    
    bsdf.inputs['Metallic'].default_value = metallic

    # Albedo
    albedo_path = os.path.join(TEXTURES_DIR, albedo_file) if albedo_file else None
    if albedo_path and os.path.exists(albedo_path):
        img_alb = bpy.data.images.load(albedo_path)
        tex_alb = nodes.new('ShaderNodeTexImage')
        tex_alb.image = img_alb
        links.new(tex_alb.outputs['Color'], bsdf.inputs['Base Color'])
    else:
        bsdf.inputs['Base Color'].default_value = fallback_color

    # Normal Map
    normal_path = os.path.join(TEXTURES_DIR, normal_file) if normal_file else None
    if normal_path and os.path.exists(normal_path):
        img_norm = bpy.data.images.load(normal_path)
        img_norm.colorspace_settings.name = 'Non-Color'
        tex_norm = nodes.new('ShaderNodeTexImage')
        tex_norm.image = img_norm
        
        node_norm = nodes.new('ShaderNodeNormalMap')
        node_norm.inputs['Strength'].default_value = 1.8
        links.new(tex_norm.outputs['Color'], node_norm.inputs['Color'])
        links.new(node_norm.outputs['Normal'], bsdf.inputs['Normal'])

    # Roughness Map
    rough_path = os.path.join(TEXTURES_DIR, rough_file) if rough_file else None
    if rough_path and os.path.exists(rough_path):
        img_rough = bpy.data.images.load(rough_path)
        img_rough.colorspace_settings.name = 'Non-Color'
        tex_rough = nodes.new('ShaderNodeTexImage')
        tex_rough.image = img_rough
        links.new(tex_rough.outputs['Color'], bsdf.inputs['Roughness'])
    else:
        bsdf.inputs['Roughness'].default_value = 0.45

    return mat

def create_simple_mat(name, color, roughness=0.5, metallic=0.0, emission_color=None, emission_strength=1.0):
    mat = bpy.data.materials.new(name=name)
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = color
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Metallic'].default_value = metallic
        if emission_color and 'Emission Color' in bsdf.inputs:
            bsdf.inputs['Emission Color'].default_value = emission_color
            bsdf.inputs['Emission Strength'].default_value = emission_strength
    return mat

def add_bevel_and_uv(obj, width=0.02, segments=3):
    bev = obj.modifiers.new(name="Bevel", type='BEVEL')
    bev.width = width
    bev.segments = segments
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(35)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.shade_smooth()
    
    # Gera coordenadas UV inteligentes para texturas PBR se assentarem com perfeição
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')

def build_scene():
    clean_scene()
    
    # -------------------------------------------------------------
    # 1. MATERIAIS PBR REALISTAS
    # -------------------------------------------------------------
    mat_wood_pbr = create_pbr_material("Mat_Wood_PBR", "wood_albedo.png", "wood_normal.png", "wood_rough.png", (0.85, 0.45, 0.12, 1.0))
    mat_roof_pbr = create_pbr_material("Mat_Roof_PBR", "roof_albedo.png", "roof_normal.png", "roof_rough.png", (0.84, 0.18, 0.05, 1.0))
    mat_solar_pbr = create_pbr_material("Mat_Solar_PBR", "solar_albedo.png", "solar_normal.png", "solar_rough.png", (0.01, 0.28, 0.88, 1.0), metallic=0.35)
    mat_grass_pbr = create_pbr_material("Mat_Grass_PBR", "grass_albedo.png", "grass_normal.png", "grass_rough.png", (0.06, 0.62, 0.15, 1.0))
    mat_wall_pbr = create_pbr_material("Mat_Wall_PBR", "stucco_albedo.png", "stucco_normal.png", "stucco_rough.png", (0.98, 0.98, 0.96, 1.0))

    # Materiais complementares
    mat_podium = create_simple_mat("Mat_Podium", (0.97, 0.97, 0.98, 1.0), roughness=0.35)
    mat_glass_warm = create_simple_mat("Mat_GlassWarm", (1.0, 0.84, 0.25, 1.0), roughness=0.05, emission_color=(1.0, 0.84, 0.25, 1.0), emission_strength=3.0)
    mat_solar_frame = create_simple_mat("Mat_SolarFrame", (0.92, 0.94, 0.98, 1.0), roughness=0.12, metallic=0.9)
    mat_solar_rails = create_simple_mat("Mat_SolarRails", (0.80, 0.82, 0.88, 1.0), roughness=0.15, metallic=0.9)
    mat_leaf = create_simple_mat("Mat_Leaf", (0.04, 0.48, 0.14, 1.0), roughness=0.3)
    mat_stone = create_simple_mat("Mat_Stone", (0.90, 0.92, 0.94, 1.0), roughness=0.4)
    mat_brass = create_simple_mat("Mat_Brass", (1.0, 0.80, 0.10, 1.0), roughness=0.15, metallic=0.95)
    mat_flower_red = create_simple_mat("Mat_FlowerRed", (0.95, 0.08, 0.12, 1.0), roughness=0.3)
    mat_flower_yellow = create_simple_mat("Mat_FlowerYellow", (1.0, 0.85, 0.05, 1.0), roughness=0.3)

    # Inversor
    mat_inverter_body = create_simple_mat("Mat_InverterBody", (0.96, 0.97, 0.99, 1.0), roughness=0.2)
    mat_inverter_screen = create_simple_mat("Mat_InverterScreen", (0.05, 0.07, 0.10, 1.0), roughness=0.1)
    mat_led_green = create_simple_mat("Mat_LedGreen", (0.05, 1.0, 0.2, 1.0), roughness=0.1, emission_color=(0.05, 1.0, 0.2, 1.0), emission_strength=5.0)

    # -------------------------------------------------------------
    # 2. BASE DO DIORAMA
    # -------------------------------------------------------------
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, -0.2))
    base = bpy.context.active_object
    base.name = "Diorama_Base"
    base.scale = (5.6, 5.6, 0.4)
    base.data.materials.append(mat_podium)
    add_bevel_and_uv(base, width=0.08, segments=4)

    # Jardim com Textura PBR de Gramado Tropical
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-1.3, 0.2, 0.05))
    garden = bpy.context.active_object
    garden.name = "Garden_Patch"
    garden.scale = (2.4, 4.8, 0.1)
    garden.data.materials.append(mat_grass_pbr)
    add_bevel_and_uv(garden, width=0.04, segments=3)

    # Deck de Madeira com Textura PBR Real (veios, ranhuras e verniz)
    deck_start_x = -0.05
    num_planks = 12
    plank_width = 0.22
    for i in range(num_planks):
        py = -2.2 + (i * (plank_width + 0.015))
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1.25, py, 0.06))
        plank = bpy.context.active_object
        plank.name = f"Deck_Plank_{i}"
        plank.scale = (2.4, plank_width, 0.08)
        plank.data.materials.append(mat_wood_pbr)
        add_bevel_and_uv(plank, width=0.012, segments=2)

    # -------------------------------------------------------------
    # 3. CORPO DA CASA COM TEXTURA PBR DE REBOCO STUCCO
    # -------------------------------------------------------------
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.7, 0.4, 1.25))
    house = bpy.context.active_object
    house.name = "House_Body"
    house.scale = (3.2, 3.0, 2.3)
    house.data.materials.append(mat_wall_pbr)
    add_bevel_and_uv(house, width=0.035, segments=3)

    # Rodapé externo da casa em madeira PBR
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.7, 0.4, 0.16))
    baseboard = bpy.context.active_object
    baseboard.name = "House_Baseboard"
    baseboard.scale = (3.28, 3.08, 0.16)
    baseboard.data.materials.append(mat_wood_pbr)
    add_bevel_and_uv(baseboard, width=0.015, segments=2)

    # -------------------------------------------------------------
    # 4. PORTA & JANELA NÓRDICA
    # -------------------------------------------------------------
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1.35, -1.11, 0.95))
    door_frame = bpy.context.active_object
    door_frame.scale = (0.95, 0.1, 1.7)
    door_frame.data.materials.append(mat_wood_pbr)
    add_bevel_and_uv(door_frame, width=0.015, segments=2)

    # Folha da porta
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1.35, -1.13, 0.95))
    door = bpy.context.active_object
    door.scale = (0.82, 0.06, 1.58)
    door.data.materials.append(mat_wood_pbr)
    add_bevel_and_uv(door, width=0.015, segments=2)

    # Maçaneta de ouro
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.045, location=(1.68, -1.18, 0.95))
    knob = bpy.context.active_object
    knob.data.materials.append(mat_brass)

    # Capacho de entrada
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1.35, -1.5, 0.11))
    mat_rug = create_simple_mat("Mat_Rug", (0.80, 0.55, 0.25, 1.0), roughness=0.8)
    rug = bpy.context.active_object
    rug.scale = (0.9, 0.5, 0.03)
    rug.data.materials.append(mat_rug)
    add_bevel_and_uv(rug, width=0.01, segments=2)

    # JANELA FRONTAL COM MOLDURA VAZADA REAL & VIDRO ILUMINADO
    # Vidro de fundo (grande e translúcido emitindo luz quente aconchegante)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.15, -1.11, 1.35))
    win_glass = bpy.context.active_object
    win_glass.scale = (1.20, 0.04, 1.10)
    win_glass.data.materials.append(mat_glass_warm)
    add_bevel_and_uv(win_glass, width=0.005, segments=1)

    # 4 Perfis de moldura de madeira ao redor do vidro
    # Topo
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.15, -1.14, 1.90))
    wf_top = bpy.context.active_object
    wf_top.scale = (1.28, 0.08, 0.08)
    wf_top.data.materials.append(mat_wood_pbr)
    add_bevel_and_uv(wf_top, width=0.01, segments=2)

    # Base
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.15, -1.14, 0.80))
    wf_bot = bpy.context.active_object
    wf_bot.scale = (1.28, 0.08, 0.08)
    wf_bot.data.materials.append(mat_wood_pbr)
    add_bevel_and_uv(wf_bot, width=0.01, segments=2)

    # Lateral Esquerda
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.75, -1.14, 1.35))
    wf_left = bpy.context.active_object
    wf_left.scale = (0.08, 0.08, 1.18)
    wf_left.data.materials.append(mat_wood_pbr)
    add_bevel_and_uv(wf_left, width=0.01, segments=2)

    # Lateral Direita
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.45, -1.14, 1.35))
    wf_right = bpy.context.active_object
    wf_right.scale = (0.08, 0.08, 1.18)
    wf_right.data.materials.append(mat_wood_pbr)
    add_bevel_and_uv(wf_right, width=0.01, segments=2)

    # Cruz interna do caixilho
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.15, -1.14, 1.35))
    win_cross_v = bpy.context.active_object
    win_cross_v.scale = (0.04, 0.05, 1.10)
    win_cross_v.data.materials.append(mat_wood_pbr)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.15, -1.14, 1.35))
    win_cross_h = bpy.context.active_object
    win_cross_h.scale = (1.20, 0.05, 0.04)
    win_cross_h.data.materials.append(mat_wood_pbr)

    # Parapeito em madeira com vasinhos de terracota
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.15, -1.19, 0.74))
    sill = bpy.context.active_object
    sill.scale = (1.35, 0.16, 0.08)
    sill.data.materials.append(mat_wood_pbr)
    add_bevel_and_uv(sill, width=0.012, segments=2)

    # Vasinhos fofos de terracota no parapeito
    mat_terracotta = create_simple_mat("Mat_Pot", (0.90, 0.22, 0.06, 1.0), roughness=0.4)
    for idx, (vx, vy, vscale) in enumerate([
        (-0.45, -1.19, 0.09),
        (-0.15, -1.19, 0.075),
        (0.15, -1.19, 0.10)
    ]):
        bpy.ops.mesh.primitive_cylinder_add(radius=vscale, depth=vscale*1.4, location=(vx, vy, 0.85))
        pot = bpy.context.active_object
        pot.data.materials.append(mat_terracotta)
        add_bevel_and_uv(pot, width=0.008, segments=2)

        bpy.ops.mesh.primitive_uv_sphere_add(radius=vscale*1.1, location=(vx, vy, 0.85 + (vscale*0.9)))
        plant = bpy.context.active_object
        plant.scale = (1.0, 1.0, 0.85)
        plant.data.materials.append(mat_leaf)

    # -------------------------------------------------------------
    # 5. TELHADO COM TEXTURA PBR REAL DE TELHA CERÂMICA
    # -------------------------------------------------------------
    roof_angle = math.radians(28)

    # Água frontal (onde os painéis solares se fixam)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.7, -0.38, 2.80))
    roof_front = bpy.context.active_object
    roof_front.name = "Roof_Front_Slope"
    roof_front.rotation_euler = (roof_angle, 0, 0)
    roof_front.scale = (3.6, 2.3, 0.12)
    roof_front.data.materials.append(mat_roof_pbr)
    add_bevel_and_uv(roof_front, width=0.025, segments=3)

    # Água traseira
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.7, 1.18, 2.80))
    roof_back = bpy.context.active_object
    roof_back.name = "Roof_Back_Slope"
    roof_back.rotation_euler = (-roof_angle, 0, 0)
    roof_back.scale = (3.6, 2.3, 0.12)
    roof_back.data.materials.append(mat_roof_pbr)
    add_bevel_and_uv(roof_back, width=0.025, segments=3)

    # Cumeeira
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.7, 0.4, 3.35))
    ridge = bpy.context.active_object
    ridge.scale = (3.65, 0.22, 0.16)
    ridge.data.materials.append(mat_wood_pbr)
    add_bevel_and_uv(ridge, width=0.02, segments=2)

    # Chaminé
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1.9, 0.9, 3.3))
    chimney = bpy.context.active_object
    chimney.scale = (0.55, 0.55, 1.0)
    chimney.data.materials.append(mat_roof_pbr)
    add_bevel_and_uv(chimney, width=0.025, segments=2)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1.9, 0.9, 3.82))
    chimney_cap = bpy.context.active_object
    chimney_cap.scale = (0.65, 0.65, 0.08)
    chimney_cap.data.materials.append(mat_wood_pbr)
    add_bevel_and_uv(chimney_cap, width=0.015, segments=2)

    # -------------------------------------------------------------
    # 6. TRILHOS E PAINÉIS SOLARES COLADOS COM PRECISÃO NO TELHADO
    # -------------------------------------------------------------
    # Cálculo geométrico perpendicular à inclinação de 28° do telhado:
    # Superfície superior do telhado:
    sin_a = math.sin(roof_angle)
    cos_a = math.cos(roof_angle)
    
    # Trilhos apoiados diretamente sobre a telha
    rail_offset = 0.06 + 0.02 # meia-espessura do telhado + meia-espessura do trilho
    rail_y = -0.38 - rail_offset * sin_a
    rail_z = 2.80 + rail_offset * cos_a

    for tx in [-0.4, 0.4, 1.2]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(tx, rail_y, rail_z))
        rail = bpy.context.active_object
        rail.name = f"Solar_Rail_{tx}"
        rail.rotation_euler = (roof_angle, 0, 0)
        rail.scale = (0.05, 1.8, 0.04)
        rail.data.materials.append(mat_solar_rails)

    # Painel Solar Assembly apoiado exatamente sobre os trilhos de alumínio
    panel_offset = 0.06 + 0.04 + 0.025 # telhado + trilho + meia-espessura do painel
    panel_y = -0.38 - panel_offset * sin_a
    panel_z = 2.80 + panel_offset * cos_a

    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0.4, panel_y, panel_z))
    solar_assembly = bpy.context.active_object
    solar_assembly.name = "Solar_Panel_Assembly"
    solar_assembly.rotation_euler = (roof_angle, 0, 0)

    # Atualiza a matriz de mundo do pai para calcular o parent_inverse correto
    bpy.context.view_layer.update()
    inv_parent = solar_assembly.matrix_world.inverted()

    for p_idx, px_offset in enumerate([-0.55, 0.55]):
        # Moldura metálica chanfrada apoiada no trilho
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.4 + px_offset, panel_y, panel_z))
        p_frame = bpy.context.active_object
        p_frame.name = f"Panel_Frame_{p_idx}"
        p_frame.rotation_euler = (roof_angle, 0, 0)
        p_frame.scale = (1.05, 1.5, 0.05)
        p_frame.data.materials.append(mat_solar_frame)
        add_bevel_and_uv(p_frame, width=0.012, segments=2)
        
        # Parentesco perfeito mantendo a transformação global intacta
        p_frame.parent = solar_assembly
        p_frame.matrix_parent_inverse = inv_parent

        # Células fotovoltaicas monocristalinas assentadas milimetricamente na moldura
        cell_offset = panel_offset + 0.015
        cell_y = -0.38 - cell_offset * sin_a
        cell_z = 2.80 + cell_offset * cos_a
        
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.4 + px_offset, cell_y, cell_z))
        p_cells = bpy.context.active_object
        p_cells.name = f"Panel_Cells_{p_idx}"
        p_cells.rotation_euler = (roof_angle, 0, 0)
        p_cells.scale = (0.98, 1.42, 0.02)
        p_cells.data.materials.append(mat_solar_pbr)
        p_cells.parent = solar_assembly
        p_cells.matrix_parent_inverse = inv_parent

    # -------------------------------------------------------------
    # 6.1 ANIMAÇÃO NATIVA POR KEYFRAMES: DESCIDA HELICOIDAL AERODINÂMICA
    # -------------------------------------------------------------
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 120
    bpy.context.scene.render.fps = 24

    rest_loc = (0.4, panel_y, panel_z)
    rest_rot = (roof_angle, 0.0, 0.0)

    # Gera keyframes de aproximação espiral com desaceleração logarítmica
    for f in range(1, 121, 2):
        p = (f - 1) / 119.0
        remaining = 1.0 - p
        
        cur_radius = 2.6 * (remaining ** 1.35)
        spiral_angle = remaining * (2.8 * 2.0 * math.pi)
        cur_h = remaining * 4.2
        
        cur_x = rest_loc[0] + math.cos(spiral_angle) * cur_radius
        cur_y = rest_loc[1] + math.sin(spiral_angle) * cur_radius
        cur_z = rest_loc[2] + cur_h
        
        # Pitch, Roll e Yaw aerodinâmicos suavizando até zero
        cur_rot_x = rest_rot[0] + remaining * math.sin(spiral_angle * 0.7) * math.radians(28)
        cur_rot_y = rest_rot[1] + remaining * spiral_angle * 0.22
        cur_rot_z = rest_rot[2] + remaining * math.cos(spiral_angle * 0.5) * math.radians(22)
        
        solar_assembly.location = (cur_x, cur_y, cur_z)
        solar_assembly.rotation_euler = (cur_rot_x, cur_rot_y, cur_rot_z)
        solar_assembly.keyframe_insert("location", frame=f)
        solar_assembly.keyframe_insert("rotation_euler", frame=f)

    # Frame 120: Garante repouso 100% COLADO no telhado
    solar_assembly.location = rest_loc
    solar_assembly.rotation_euler = rest_rot
    solar_assembly.keyframe_insert("location", frame=120)
    solar_assembly.keyframe_insert("rotation_euler", frame=120)
    
    # Define a cena no frame 120 para o render estático e preview
    bpy.context.scene.frame_set(120)

    # -------------------------------------------------------------
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(2.32, 0.6, 1.35))
    inverter = bpy.context.active_object
    inverter.name = "Solar_Inverter"
    inverter.scale = (0.08, 0.55, 0.75)
    inverter.data.materials.append(mat_inverter_body)
    add_bevel_and_uv(inverter, width=0.015, segments=2)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(2.37, 0.6, 1.45))
    inv_scr = bpy.context.active_object
    inv_scr.scale = (0.02, 0.35, 0.22)
    inv_scr.data.materials.append(mat_inverter_screen)
    inv_scr.parent = inverter

    bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.02, location=(2.37, 0.72, 1.25))
    inv_led = bpy.context.active_object
    inv_led.rotation_euler = (0, math.radians(90), 0)
    inv_led.data.materials.append(mat_led_green)
    inv_led.parent = inverter

    # -------------------------------------------------------------
    # 8. ELEMENTOS DECORATIVOS: ÁRVORE, ARBUSTOS, SEIXOS & FLORES
    # -------------------------------------------------------------
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.8, location=(-1.6, 1.0, 0.45))
    trunk = bpy.context.active_object
    trunk.data.materials.append(mat_wood_pbr)
    add_bevel_and_uv(trunk, width=0.01, segments=2)

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.6, location=(-1.6, 1.0, 1.15))
    fol1 = bpy.context.active_object
    fol1.scale = (1.0, 1.0, 1.2)
    fol1.data.materials.append(mat_leaf)
    add_bevel_and_uv(fol1, width=0.02, segments=2)

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.45, location=(-1.45, 1.2, 1.55))
    fol2 = bpy.context.active_object
    fol2.data.materials.append(mat_grass_pbr)

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.28, location=(-0.3, -1.8, 0.22))
    bush1 = bpy.context.active_object
    bush1.data.materials.append(mat_grass_pbr)
    add_bevel_and_uv(bush1, width=0.015, segments=2)

    # Flores coloridas no gramado
    for fl_x, fl_y, fl_col in [
        (-0.9, -1.2, mat_flower_red),
        (-0.75, -1.0, mat_flower_yellow),
        (-1.1, -1.4, mat_flower_yellow),
        (-1.4, -0.8, mat_flower_red),
        (-1.6, -0.1, mat_flower_yellow),
        (-0.8, 0.4, mat_flower_red),
    ]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.065, location=(fl_x, fl_y, 0.14))
        fl = bpy.context.active_object
        fl.scale = (1.0, 1.0, 0.8)
        fl.data.materials.append(fl_col)

    # -------------------------------------------------------------
    # 9. ILUMINAÇÃO ESTÚDIO QUENTE DE ALTA DEFINIÇÃO
    # -------------------------------------------------------------
    sun = bpy.data.lights.new(name="Sun_Key", type='SUN')
    sun.energy = 6.2
    sun.color = (1.0, 0.93, 0.83)
    sun.angle = math.radians(10)
    sun_obj = bpy.data.objects.new(name="Sun_Key", object_data=sun)
    bpy.context.collection.objects.link(sun_obj)
    sun_obj.rotation_euler = (math.radians(52), math.radians(12), math.radians(-38))

    fill = bpy.data.lights.new(name="Fill_Sky", type='SUN')
    fill.energy = 1.8
    fill.color = (0.72, 0.85, 1.0)
    fill.angle = math.radians(20)
    fill_obj = bpy.data.objects.new(name="Fill_Sky", object_data=fill)
    bpy.context.collection.objects.link(fill_obj)
    fill_obj.rotation_euler = (math.radians(35), math.radians(-25), math.radians(145))

    rim = bpy.data.lights.new(name="Rim_Light", type='SUN')
    rim.energy = 2.5
    rim.color = (1.0, 0.95, 0.85)
    rim.angle = math.radians(15)
    rim_obj = bpy.data.objects.new(name="Rim_Light", object_data=rim)
    bpy.context.collection.objects.link(rim_obj)
    rim_obj.rotation_euler = (math.radians(-40), 0, math.radians(180))

    # -------------------------------------------------------------
    # 10. CÂMERA ISOMÉTRICA CENTRALIZADA
    # -------------------------------------------------------------
    cam_data = bpy.data.cameras.new(name="Isometric_Camera")
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = 8.4
    cam_obj = bpy.data.objects.new(name="Isometric_Camera", object_data=cam_data)
    bpy.context.collection.objects.link(cam_obj)
    
    cam_dist = 16.0
    cam_obj.location = (cam_dist + 0.2, -cam_dist, cam_dist * 0.95 + 1.2)
    cam_obj.rotation_euler = (math.radians(54.736), 0, math.radians(45))
    bpy.context.scene.camera = cam_obj

    # Fundo escuro estúdio
    world = bpy.data.worlds.new("PBR_World")
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs['Color'].default_value = (0.12, 0.13, 0.16, 1.0)
        bg_node.inputs['Strength'].default_value = 1.0
    bpy.context.scene.world = world

    bpy.context.scene.render.resolution_x = 1600
    bpy.context.scene.render.resolution_y = 1600
    bpy.context.scene.render.resolution_percentage = 100

    bpy.context.scene.view_settings.view_transform = 'AgX' if 'AgX' in [i.name for i in bpy.context.scene.view_settings.bl_rna.properties['view_transform'].enum_items] else 'Filmic'
    bpy.context.scene.view_settings.look = 'Very High Contrast'

    print("[+] Cena PBR com texturas realistas construída com sucesso!")

def export_assets(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    
    blend_path = os.path.join(output_dir, "casa_isometrica.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[+] .blend salvo: {blend_path}")

    render_path = os.path.join(output_dir, "casa_isometrica_preview.png")
    bpy.context.scene.render.filepath = render_path
    bpy.ops.render.render(write_still=True)
    print(f"[+] Render PNG salvo: {render_path}")

    glb_path = os.path.join(output_dir, "casa_isometrica.glb")
    bpy.ops.export_scene.gltf(
        filepath=glb_path,
        export_format='GLB',
        use_selection=False,
        export_apply=False,
        export_animations=True,
        export_image_format='AUTO'
    )
    print(f"[+] Modelo .glb com texturas PBR e animação embutida exportado: {glb_path}")

if __name__ == "__main__":
    out_dir = r"f:\Nova pasta\site\energia-solar\assets\3d"
    build_scene()
    export_assets(out_dir)
