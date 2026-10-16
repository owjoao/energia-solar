"""
Script Blender 5.x: Casa Isométrica Aconchegante (Diorama Clay/Toy Style)
Fiel à estética da referência:
- Madeira quente com ripas e chanfros suaves (bevels)
- Paredes off-white quentes com iluminação solar aconchegante
- Janelas com caixilhos escandinavos e luz interna
- Telhado estilizado com telhas/ripas e painéis solares modulares de alta precisão
- Jardim com pedrinhas, arbustos fofos e iluminação quente de arandela
"""

import bpy
import bmesh
import math
import os

def clean_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for obj in bpy.data.objects:
        bpy.data.objects.remove(obj, do_unlink=True)
    for mat in bpy.data.materials:
        bpy.data.materials.remove(mat, do_unlink=True)
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh, do_unlink=True)

def create_mat(name, color, roughness=0.5, metallic=0.0, emission_color=None, emission_strength=1.0):
    mat = bpy.data.materials.new(name=name)
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = color
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Metallic'].default_value = metallic
        if 'Subsurface Weight' in bsdf.inputs:
            bsdf.inputs['Subsurface Weight'].default_value = 0.03
        if emission_color and 'Emission Color' in bsdf.inputs:
            bsdf.inputs['Emission Color'].default_value = emission_color
            bsdf.inputs['Emission Strength'].default_value = emission_strength
    return mat

def add_bevel(obj, width=0.02, segments=3):
    bev = obj.modifiers.new(name="Bevel", type='BEVEL')
    bev.width = width
    bev.segments = segments
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(35)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.shade_smooth()

def build_scene():
    clean_scene()
    
    # -------------------------------------------------------------
    # MATERIAIS HIPER VIBRANTES E CONTRASTADOS (ESTÚDIO NINTENDO / PIXAR 3D)
    # -------------------------------------------------------------
    mat_podium = create_mat("Mat_Podium", (0.97, 0.97, 0.98, 1.0), roughness=0.35)
    mat_wood_light = create_mat("Mat_WoodLight", (0.88, 0.48, 0.12, 1.0), roughness=0.35) # Teca / Carvalho Quente Envernizado
    mat_wood_mid = create_mat("Mat_WoodMid", (0.75, 0.36, 0.08, 1.0), roughness=0.35) # Madeira âmbar saturada
    mat_wood_trim = create_mat("Mat_WoodTrim", (0.60, 0.25, 0.05, 1.0), roughness=0.38) # Cedro escuro contrastado
    mat_wall = create_mat("Mat_Wall", (0.98, 0.98, 0.96, 1.0), roughness=0.45) # Branco marfim limpo
    
    # Telhado: Vermelho Cerâmica / Telha Terracota Quente e Vívida (Contraste Máximo!)
    mat_roof_terracotta = create_mat("Mat_RoofTerra", (0.84, 0.18, 0.05, 1.0), roughness=0.35) # Telha Cerâmica Vermelha Vibrante
    mat_roof_trim = create_mat("Mat_RoofTrim", (0.92, 0.45, 0.12, 1.0), roughness=0.3)
    
    mat_glass = create_mat("Mat_Glass", (0.35, 0.70, 0.95, 1.0), roughness=0.04, metallic=0.3) # Vidro azul celeste cristalino
    mat_glass_warm = create_mat("Mat_GlassWarm", (1.0, 0.82, 0.20, 1.0), roughness=0.05, emission_color=(1.0, 0.82, 0.20, 1.0), emission_strength=3.0)
    
    # Jardim: Verde Esmeralda Tropical Rico (zero tons lavados)
    mat_grass = create_mat("Mat_Grass", (0.06, 0.62, 0.15, 1.0), roughness=0.45) # Grama esmeralda rica e viva
    mat_terracotta = create_mat("Mat_Pot", (0.90, 0.22, 0.06, 1.0), roughness=0.4)
    mat_leaf = create_mat("Mat_Leaf", (0.04, 0.45, 0.12, 1.0), roughness=0.3) # Folhas verde-bosque densas
    mat_stone = create_mat("Mat_Stone", (0.90, 0.92, 0.94, 1.0), roughness=0.4)
    mat_brass = create_mat("Mat_Brass", (1.0, 0.78, 0.10, 1.0), roughness=0.15, metallic=0.95)

    # Painel Solar: Azul Safira Fotovoltaico Puro e Luminoso
    mat_solar_frame = create_mat("Mat_SolarFrame", (0.92, 0.94, 0.98, 1.0), roughness=0.12, metallic=0.9)
    mat_solar_cells = create_mat("Mat_SolarCells", (0.01, 0.28, 0.88, 1.0), roughness=0.08, metallic=0.45) # Azul elétrico intenso
    mat_solar_lines = create_mat("Mat_SolarLines", (0.90, 0.96, 1.0, 1.0), roughness=0.1, metallic=0.7)
    mat_solar_rails = create_mat("Mat_SolarRails", (0.80, 0.82, 0.88, 1.0), roughness=0.15, metallic=0.9)

    # Cores vivas para flores no jardim
    mat_flower_red = create_mat("Mat_FlowerRed", (0.95, 0.08, 0.12, 1.0), roughness=0.3)
    mat_flower_yellow = create_mat("Mat_FlowerYellow", (1.0, 0.85, 0.05, 1.0), roughness=0.3)

    # Inversor
    mat_inverter_body = create_mat("Mat_InverterBody", (0.96, 0.97, 0.99, 1.0), roughness=0.2)
    mat_inverter_screen = create_mat("Mat_InverterScreen", (0.05, 0.07, 0.10, 1.0), roughness=0.1)
    mat_led_green = create_mat("Mat_LedGreen", (0.05, 1.0, 0.2, 1.0), roughness=0.1, emission_color=(0.05, 1.0, 0.2, 1.0), emission_strength=5.0)

    # -------------------------------------------------------------
    # 1. BASE DIORAMA (PODIUM REDONDO/CHANFRADO)
    # -------------------------------------------------------------
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, -0.2))
    base = bpy.context.active_object
    base.name = "Diorama_Base"
    base.scale = (5.6, 5.6, 0.4)
    base.data.materials.append(mat_podium)
    add_bevel(base, width=0.08, segments=4)

    # Jardim com gramado fofo
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-1.3, 0.2, 0.05))
    garden = bpy.context.active_object
    garden.name = "Garden_Patch"
    garden.scale = (2.4, 4.8, 0.1)
    garden.data.materials.append(mat_grass)
    add_bevel(garden, width=0.04, segments=3)

    # Deck de madeira com réguas individuais na frente e lateral direita
    deck_start_x = -0.05
    deck_width = 2.4
    num_planks = 12
    plank_width = 0.22
    for i in range(num_planks):
        py = -2.2 + (i * (plank_width + 0.015))
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1.25, py, 0.06))
        plank = bpy.context.active_object
        plank.name = f"Deck_Plank_{i}"
        plank.scale = (2.4, plank_width, 0.08)
        # Varia sutilmente a cor para realismo da madeira
        plank.data.materials.append(mat_wood_light if i % 2 == 0 else mat_wood_mid)
        add_bevel(plank, width=0.012, segments=2)

    # -------------------------------------------------------------
    # 2. CORPO DA CASA COM ACABAMENTO ACONCHEGANTE
    # -------------------------------------------------------------
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.7, 0.4, 1.25))
    house = bpy.context.active_object
    house.name = "House_Body"
    house.scale = (3.2, 3.0, 2.3)
    house.data.materials.append(mat_wall)
    add_bevel(house, width=0.035, segments=3)

    # Rodapé externo da casa em madeira
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.7, 0.4, 0.16))
    baseboard = bpy.context.active_object
    baseboard.name = "House_Baseboard"
    baseboard.scale = (3.28, 3.08, 0.16)
    baseboard.data.materials.append(mat_wood_trim)
    add_bevel(baseboard, width=0.015, segments=2)

    # -------------------------------------------------------------
    # 3. PORTA & ENTRADA NÓRDICA
    # -------------------------------------------------------------
    # Batente de madeira da porta
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1.35, -1.11, 0.95))
    door_frame = bpy.context.active_object
    door_frame.name = "Door_Frame"
    door_frame.scale = (0.95, 0.1, 1.7)
    door_frame.data.materials.append(mat_wood_trim)
    add_bevel(door_frame, width=0.015, segments=2)

    # Folha da porta com relevo
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1.35, -1.13, 0.95))
    door = bpy.context.active_object
    door.name = "Door_Leaf"
    door.scale = (0.82, 0.06, 1.58)
    door.data.materials.append(mat_wood_mid)
    add_bevel(door, width=0.015, segments=2)

    # Maçaneta de latão dourado
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.045, location=(1.68, -1.18, 0.95))
    knob = bpy.context.active_object
    knob.name = "Door_Knob"
    knob.data.materials.append(mat_brass)

    # Capacho de fibra de coco
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1.35, -1.5, 0.11))
    mat_rug = create_mat("Mat_Rug", (0.75, 0.60, 0.45, 1.0), roughness=0.8)
    rug = bpy.context.active_object
    rug.scale = (0.9, 0.5, 0.03)
    rug.data.materials.append(mat_rug)
    add_bevel(rug, width=0.01, segments=2)

    # -------------------------------------------------------------
    # 4. JANELA FRONTAL COM CAIXILHO ESCANDINAVO E VASOS
    # -------------------------------------------------------------
    # Batente externo
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.15, -1.11, 1.35))
    win_frame = bpy.context.active_object
    win_frame.name = "Window_Frame"
    win_frame.scale = (1.25, 0.1, 1.15)
    win_frame.data.materials.append(mat_wood_trim)
    add_bevel(win_frame, width=0.02, segments=2)

    # Vidro com iluminação suave interna
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.15, -1.12, 1.35))
    win_glass = bpy.context.active_object
    win_glass.name = "Window_Glass"
    win_glass.scale = (1.1, 0.02, 1.0)
    win_glass.data.materials.append(mat_glass_warm)

    # Caixilhos em cruz (+)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.15, -1.14, 1.35))
    win_cross_v = bpy.context.active_object
    win_cross_v.scale = (0.05, 0.03, 1.0)
    win_cross_v.data.materials.append(mat_wood_light)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.15, -1.14, 1.35))
    win_cross_h = bpy.context.active_object
    win_cross_h.scale = (1.1, 0.03, 0.05)
    win_cross_h.data.materials.append(mat_wood_light)

    # Parapeito em madeira com vasinhos de terracota
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.15, -1.20, 0.74))
    sill = bpy.context.active_object
    sill.scale = (1.35, 0.18, 0.08)
    sill.data.materials.append(mat_wood_light)
    add_bevel(sill, width=0.015, segments=2)

    # Vasinhos fofos
    for idx, (vx, vy, vscale, pcolor) in enumerate([
        (-0.45, -1.20, 0.10, mat_terracotta),
        (-0.15, -1.20, 0.08, mat_wood_mid),
        (0.15, -1.20, 0.11, mat_terracotta)
    ]):
        bpy.ops.mesh.primitive_cylinder_add(radius=vscale, depth=vscale*1.4, location=(vx, vy, 0.85))
        pot = bpy.context.active_object
        pot.data.materials.append(pcolor)
        add_bevel(pot, width=0.008, segments=2)

        # Plantinha suculenta redonda
        bpy.ops.mesh.primitive_uv_sphere_add(radius=vscale*1.1, location=(vx, vy, 0.85 + (vscale*0.9)))
        plant = bpy.context.active_object
        plant.scale = (1.0, 1.0, 0.85)
        plant.data.materials.append(mat_leaf)

    # -------------------------------------------------------------
    # 5. TELHADO ESCANDINAVO ACONCHEGANTE (DUAS ÁGUAS)
    # -------------------------------------------------------------
    roof_angle = math.radians(28)

    # Estrutura base do telhado frontal
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.7, -0.38, 2.80))
    roof_front = bpy.context.active_object
    roof_front.name = "Roof_Front_Slope"
    roof_front.rotation_euler = (roof_angle, 0, 0)
    roof_front.scale = (3.6, 2.3, 0.12)
    roof_front.data.materials.append(mat_roof_terracotta)
    add_bevel(roof_front, width=0.025, segments=3)

    # Telhado traseiro
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.7, 1.18, 2.80))
    roof_back = bpy.context.active_object
    roof_back.name = "Roof_Back_Slope"
    roof_back.rotation_euler = (-roof_angle, 0, 0)
    roof_back.scale = (3.6, 2.3, 0.12)
    roof_back.data.materials.append(mat_roof_terracotta)
    add_bevel(roof_back, width=0.025, segments=3)

    # Cumeeira de acabamento
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.7, 0.4, 3.35))
    ridge = bpy.context.active_object
    ridge.scale = (3.65, 0.22, 0.16)
    ridge.data.materials.append(mat_roof_trim)
    add_bevel(ridge, width=0.02, segments=2)

    # Chaminé fofa com tijolos terracota e topo chanfrado
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1.9, 0.9, 3.3))
    chimney = bpy.context.active_object
    chimney.scale = (0.55, 0.55, 1.0)
    chimney.data.materials.append(mat_roof_terracotta)
    add_bevel(chimney, width=0.025, segments=2)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1.9, 0.9, 3.82))
    chimney_cap = bpy.context.active_object
    chimney_cap.scale = (0.65, 0.65, 0.08)
    chimney_cap.data.materials.append(mat_roof_trim)
    add_bevel(chimney_cap, width=0.015, segments=2)

    # -------------------------------------------------------------
    # 6. ESTRUTURA DE TRILHOS E PAINÉIS SOLARES FOTOVOLTAICOS
    # -------------------------------------------------------------
    # Trilhos de alumínio instalados sobre as ripas do telhado frontal
    for tx in [-0.4, 0.4, 1.2]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(tx, -0.38, 2.90))
        rail = bpy.context.active_object
        rail.name = f"Solar_Rail_{tx}"
        rail.rotation_euler = (roof_angle, 0, 0)
        rail.scale = (0.05, 1.8, 0.04)
        rail.data.materials.append(mat_solar_rails)

    # GERAÇÃO DO CONJUNTO DE 2 PAINÉIS SOLARES DE ALTA EFICIÊNCIA
    # Objeto Pai para animação em espiral (Solar_System_Group)
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0.4, -0.38, 2.97))
    solar_assembly = bpy.context.active_object
    solar_assembly.name = "Solar_Panel_Assembly"
    solar_assembly.rotation_euler = (roof_angle, 0, 0)

    # Cria 2 módulos de painéis solares elegantes lado a lado
    for p_idx, px_offset in enumerate([-0.55, 0.55]):
        # Moldura de Alumínio
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.4 + px_offset, -0.38, 2.97))
        p_frame = bpy.context.active_object
        p_frame.name = f"Panel_Frame_{p_idx}"
        p_frame.rotation_euler = (roof_angle, 0, 0)
        p_frame.scale = (1.05, 1.5, 0.05)
        p_frame.data.materials.append(mat_solar_frame)
        add_bevel(p_frame, width=0.012, segments=2)
        p_frame.parent = solar_assembly

        # Células Fotovoltaicas (azul marinho profundo com reflexo acetinado)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.4 + px_offset, -0.38, 2.99))
        p_cells = bpy.context.active_object
        p_cells.name = f"Panel_Cells_{p_idx}"
        p_cells.rotation_euler = (roof_angle, 0, 0)
        p_cells.scale = (0.98, 1.42, 0.02)
        p_cells.data.materials.append(mat_solar_cells)
        p_cells.parent = solar_assembly

        # Linhas de barramento finas prateadas sobre as células
        for by in [-0.4, 0.0, 0.4]:
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.4 + px_offset, -0.38, 3.00))
            busbar = bpy.context.active_object
            busbar.rotation_euler = (roof_angle, 0, 0)
            # Desloca na coordenada local do telhado
            busbar.scale = (0.95, 0.015, 0.01)
            busbar.data.materials.append(mat_solar_lines)
            busbar.parent = solar_assembly

    # -------------------------------------------------------------
    # 7. INVERSOR SOLAR COMPACTO COM LED VERDE ATIVO NA LATERAL
    # -------------------------------------------------------------
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(2.32, 0.6, 1.35))
    inverter = bpy.context.active_object
    inverter.name = "Solar_Inverter"
    inverter.scale = (0.08, 0.55, 0.75)
    inverter.data.materials.append(mat_inverter_body)
    add_bevel(inverter, width=0.015, segments=2)

    # Visor digital
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(2.37, 0.6, 1.45))
    inv_scr = bpy.context.active_object
    inv_scr.scale = (0.02, 0.35, 0.22)
    inv_scr.data.materials.append(mat_inverter_screen)
    inv_scr.parent = inverter

    # Led de status verde gerando energia
    bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.02, location=(2.37, 0.72, 1.25))
    inv_led = bpy.context.active_object
    inv_led.rotation_euler = (0, math.radians(90), 0)
    inv_led.data.materials.append(mat_led_green)
    inv_led.parent = inverter

    # -------------------------------------------------------------
    # 8. JARDIM COZY (ÁRVORE ESTILIZADA, ARBUSTOS E SEIXOS)
    # -------------------------------------------------------------
    # Tronco de madeira arredondado
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.8, location=(-1.6, 1.0, 0.45))
    trunk = bpy.context.active_object
    trunk.data.materials.append(mat_wood_trim)
    add_bevel(trunk, width=0.01, segments=2)

    # Copa da árvore em esferas fofas estilo clay
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.6, location=(-1.6, 1.0, 1.15))
    fol1 = bpy.context.active_object
    fol1.scale = (1.0, 1.0, 1.2)
    fol1.data.materials.append(mat_leaf)
    add_bevel(fol1, width=0.02, segments=2)

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.45, location=(-1.45, 1.2, 1.55))
    fol2 = bpy.context.active_object
    fol2.data.materials.append(mat_grass)

    # Arbustos fofos na entrada
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.28, location=(-0.3, -1.8, 0.22))
    bush1 = bpy.context.active_object
    bush1.data.materials.append(mat_grass)
    add_bevel(bush1, width=0.015, segments=2)

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=(-0.55, -1.6, 0.18))
    bush2 = bpy.context.active_object
    bush2.data.materials.append(mat_leaf)

    # Pedrinhas de seixo no jardim
    for idx, (px, py, ps) in enumerate([
        (-1.2, -0.6, 0.18),
        (-1.5, -0.3, 0.14),
        (-1.3, 0.2, 0.22),
        (-1.7, 0.4, 0.16)
    ]):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=ps, location=(px, py, 0.12))
        stone = bpy.context.active_object
        stone.scale = (1.0, 0.85, 0.45)
        stone.data.materials.append(mat_stone)

    # Flores vibrantes estilizadas no gramado
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
    # 9. ILUMINAÇÃO DE ESTÚDIO ISOMÉTRICO (CORES VIBRANTES & CONTRASTE)
    # -------------------------------------------------------------
    # Sol Quente Dourado (Key Light)
    sun = bpy.data.lights.new(name="Sun_GoldenHour", type='SUN')
    sun.energy = 5.8
    sun.color = (1.0, 0.92, 0.82) # Luz solar intensa e rica
    sun.angle = math.radians(12) # Sombras bem definidas e nítidas
    sun_obj = bpy.data.objects.new(name="Sun_GoldenHour", object_data=sun)
    bpy.context.collection.objects.link(sun_obj)
    sun_obj.rotation_euler = (math.radians(52), math.radians(12), math.radians(-38))

    # Luz de Preenchimento Azul Vibrante (Fill Light)
    fill = bpy.data.lights.new(name="Fill_Sky", type='SUN')
    fill.energy = 1.6
    fill.color = (0.70, 0.84, 1.0)
    fill.angle = math.radians(25)
    fill_obj = bpy.data.objects.new(name="Fill_Sky", object_data=fill)
    bpy.context.collection.objects.link(fill_obj)
    fill_obj.rotation_euler = (math.radians(35), math.radians(-25), math.radians(145))

    # Luz de Borda Traseira (Rim Light quente para fazer as cores saltarem)
    rim = bpy.data.lights.new(name="Rim_Light", type='SUN')
    rim.energy = 2.4
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

    # Fundo Slate Escuro (#20232a) com alto contraste para valorizar as cores
    world = bpy.data.worlds.new("Cozy_World")
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs['Color'].default_value = (0.125, 0.135, 0.165, 1.0)
        bg_node.inputs['Strength'].default_value = 1.0
    bpy.context.scene.world = world

    # Configurações de Render
    bpy.context.scene.render.resolution_x = 1600
    bpy.context.scene.render.resolution_y = 1600
    bpy.context.scene.render.resolution_percentage = 100

    # Color Management com contraste muito alto para cores vibrantes
    bpy.context.scene.view_settings.view_transform = 'AgX' if 'AgX' in [i.name for i in bpy.context.scene.view_settings.bl_rna.properties['view_transform'].enum_items] else 'Filmic'
    bpy.context.scene.view_settings.look = 'Very High Contrast'

    print("[+] Nova Casa Isométrica Estilizada construída com sucesso!")

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
        export_apply=True
    )
    print(f"[+] Modelo .glb exportado: {glb_path}")

if __name__ == "__main__":
    out_dir = r"f:\Nova pasta\site\energia-solar\assets\3d"
    build_scene()
    export_assets(out_dir)

