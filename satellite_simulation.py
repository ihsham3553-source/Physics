from vpython import *
Web VPython 3.2

# ==========================================
# 3D Dynamics: Ultra-Sharp "Needle" Orbit
# ==========================================

# 1. VISUAL SETUP
scene = canvas(title="Ultra-Sharp Eccentric Orbit", width=900, height=550, 
               background=color.black, align='left')
scene.lights = []
scene.ambient = color.gray(0.2)
distant_light(direction=vec(1, 0.5, 0.5), color=color.white)

# Cosmic Background
for i in range(150):
    sphere(pos=vec.random()*2.5e8, radius=5e5, color=color.white, emissive=True)

# --- GRAPH SETUP ---
energy_graph = graph(width=900, height=250, title="System Energy (J) vs Time",
                     xtitle="Time (s)", ytitle="Energy",
                     background=color.black, fast=True) 
k_curve = gcurve(color=color.red, label="Kinetic")
p_curve = gcurve(color=color.blue, label="Potential")
total_curve = gcurve(color=color.green, label="Total Energy")

# 2. PHYSICS CONSTANTS
G = 6.674e-11        
M_earth = 5.972e24    
R_earth = 6.371e6    
m_sat = 1500.0       

# 3. CREATE THE EARTH (Textured)
earth = sphere(pos=vec(0,0,0), radius=R_earth, texture=textures.earth, shininess=0.3)
atmosphere = sphere(pos=vec(0,0,0), radius=R_earth*1.03, color=color.cyan, opacity=0.1)

# 4. CREATE THE SATELLITE
body = box(pos=vec(0,0,0), size=vec(1.2e6, 1.2e6, 1.2e6), color=color.gray(0.7), shininess=1)
panel1 = box(pos=vec(1.8e6, 0, 0), size=vec(2.4e6, 0.8e6, 0.1e6), color=vec(0.2, 0.5, 1))
panel2 = box(pos=vec(-1.8e6, 0, 0), size=vec(2.4e6, 0.8e6, 0.1e6), color=vec(0.2, 0.5, 1))

sat_shape = compound([body, panel1, panel2], make_trail=True, 
                     trail_color=color.yellow, trail_type="curve", 
                     trail_radius=6e4, retain=2500) 

# 5. INITIAL KINEMATICS (Tuned for Sharpness)
# Lowering the velocity at a high altitude creates a "plunging" effect
alt = 7.5e7 
sat_shape.pos = vec(R_earth + alt, 0, 0)
sat_shape.v = vec(0, 1600, 200) # Reduced from 2100 for a sharper dive

telemetry = label(pixel_pos=True, pos=vec(20, 100, 0), text='', 
                  height=14, color=color.white, box=False, align='left')

# 6. SIMULATION LOOP
t = 0
base_dt = 400 

while True:
    rate(200)
    
    r_vec = sat_shape.pos - earth.pos
    r_mag = mag(r_vec)
    
    # ENHANCED ADAPTIVE TIME STEP
    # Sharp orbits need extreme precision at periapsis (closest point)
    # We use a power of the ratio to make dt drop even faster as it nears Earth
    dt = base_dt * ((r_mag / (R_earth * 12))**1.5)
    if dt < 5: dt = 5 # Extremely high precision floor for the "Sharp" turn
    
    # Gravity Calculation
    a_scalar = (G * M_earth) / (r_mag**2)
    a_vec = -a_scalar * norm(r_vec)
    
    # Integration
    sat_shape.v += a_vec * dt
    sat_shape.pos += sat_shape.v * dt
    
    # Orientation
    sat_shape.axis = norm(sat_shape.v)
    
    # Energy Plotting
    v_mag = mag(sat_shape.v)
    ke_val = 0.5 * m_sat * (v_mag**2)
    pe_val = -G * M_earth * m_sat / r_mag
    total_e = ke_val + pe_val
    
    k_curve.plot(t, ke_val)
    p_curve.plot(t, pe_val)
    total_curve.plot(t, total_e)
    
    # Telemetry
    msg = "Speed: {0} km/s\nAltitude: {1}k km\nOrbit: Ultra-Eccentric"
    telemetry.text = msg.format(round(v_mag/1000, 2), 
                                round((r_mag - R_earth)/1000, 0))
    
    # Dynamic Camera (Documentary Style)
    cam_angle = t * 0.3e-5
    dist = 1.6e8
    scene.camera.pos = vec(dist * cos(cam_angle), dist * 0.4, dist * sin(cam_angle))
    scene.camera.axis = -scene.camera.pos
    
    t += dt
    
    if r_mag < R_earth:
        telemetry.text = "IMPACT DETECTED"
        telemetry.color = color.red
        break
