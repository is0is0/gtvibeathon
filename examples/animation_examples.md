# Animation Examples for Voxel

## Simple Animation Prompts

### Rotating Objects
```
a collection of geometric shapes slowly rotating in space with soft lighting
```

### Floating Islands
```
floating islands with waterfalls, slowly drifting in the sky, camera circling around them
```

### Pulsing Lights
```
a dark room with neon lights pulsing in sync, objects bouncing gently to the rhythm
```

## Complex Animation Scenes

### Cyberpunk City Flythrough
```
a cyberpunk city street with neon signs, holographic ads flickering, steam rising from vents, camera flying through the scene from street level to rooftops
```

### Magical Library
```
an enchanted library with floating books opening and closing, glowing runes appearing and fading on ancient tomes, a crystal orb pulsing with light, camera slowly orbiting the scene
```

### Underwater Exploration
```
an underwater coral reef with fish swimming in schools, kelp swaying with the current, bioluminescent creatures pulsing light, camera descending from surface to sea floor
```

### Space Station
```
a space station interior with holographic displays animating with data, robotic arms assembling components, lights pulsing across control panels, camera smoothly gliding through corridors
```

### Mystical Forest
```
a mystical forest with fireflies dancing in patterns, mushrooms glowing and pulsing, mist rolling across the ground, ancient tree branches slowly swaying, camera tracking along a winding path
```

## Animation Technique Examples

### Easing Showcase
```
a series of cubes demonstrating different easing types: one bouncing elastically, one moving smoothly with ease-in-out, one pulsing with sine waves, arranged in a grid
```

### Material Animation
```
abstract geometric shapes transforming materials: one fading from rough to metallic, another changing colors through the spectrum, one pulsing emission, all rotating slowly
```

### Constraint Animation
```
a mechanical gear system where gears track each other's rotation, pistons following paths along curves, arms tracking moving targets, all working in synchronized motion
```

### Camera Choreography
```
a still life scene with dramatic camera movement: starting wide, slowly zooming in while orbiting the subject, rack focus from foreground to background, revealing details
```

## Narrative Animation Scenes

### Morning Coffee Shop
```
a cozy coffee shop at dawn: sunlight gradually increasing through windows, steam rising from coffee cups, clock hands moving, pastry display rotating slowly, camera panning across the scene
```

### Sci-Fi Laboratory Sequence
```
a high-tech lab: holographic displays cycling through data, robotic arms assembling a device, particle accelerator glowing with increasing energy, warning lights beginning to flash, camera pushing in toward the center
```

### Medieval Blacksmith
```
a blacksmith's workshop: bellows pumping air into glowing forge, hammer rising and falling (implied), sparks flying upward, metal stock glowing hot to cool, rotating tool rack, camera circling the forge
```

### Rocket Launch Countdown
```
a rocket launch pad at sunset: warning lights pulsing faster as countdown proceeds, steam venting from rocket, gantry arms retracting, support structures releasing, camera ascending from ground level to show full scene
```

## Abstract/Artistic Animations

### Procedural Motion Graphics
```
abstract geometric patterns morphing and transforming: triangles becoming hexagons, colors shifting through gradients, scales pulsing, rotations at different speeds, hypnotic synchronized motion
```

### Particle Dance
```
a field of luminous particles following invisible force fields, swirling into vortexes, dispersing and reforming, colors shifting based on velocity, camera slowly rotating around the system
```

### Crystalline Growth
```
crystals growing from a central point, branching fractally, pulsing with inner light, rotating slowly to show different facets, new crystals sprouting from existing ones, camera orbiting and zooming
```

## Animation Timing Tips

### Short Loops (2-5 seconds / 48-120 frames)
- Icon animations
- Logo reveals
- Product rotations
- Simple loops

### Medium Sequences (5-10 seconds / 120-240 frames)
- Scene reveals
- Camera moves
- Character actions
- Transitional moments

### Long Narratives (10-20 seconds / 240-480 frames)
- Story sequences
- Complex camera choreography
- Multi-stage transformations
- Environmental cycles

## Easing Guide for Different Effects

### Natural/Organic Motion
```
Use: BEZIER with EASE_IN_OUT
Example: "floating objects", "swaying trees", "breathing motion"
```

### Mechanical/Precise Motion
```
Use: LINEAR or CUBIC
Example: "gears turning", "robotic arms", "sliding doors"
```

### Bouncy/Playful Motion
```
Use: BOUNCE or ELASTIC with EASE_OUT
Example: "bouncing balls", "spring-loaded objects", "cartoon effects"
```

### Dramatic/Impact Moments
```
Use: EXPO or CIRC with EASE_IN or EASE_OUT
Example: "camera crash zoom", "impact frame", "dramatic reveals"
```

### Smooth/Cinematic Motion
```
Use: SINE or BEZIER with EASE_IN_OUT
Example: "camera dolly", "smooth transitions", "elegant movements"
```

## Multi-Object Choreography

### Synchronized Motion
```
a line of dominoes falling in sequence, each delayed slightly from the previous, camera following the wave of motion
```

### Offset Animation
```
a grid of cubes, each bouncing with a slight time offset creating a wave pattern across the grid, colors shifting as they move
```

### Call and Response
```
two objects mirroring each other's movements with a delay, one rising as the other falls, rotating in opposite directions, creating visual rhythm
```

## Advanced Techniques to Request

### Follow Path
```
"an object following a spiral path from bottom to top"
"camera tracking along a bezier curve through obstacles"
```

### Track To Constraint
```
"multiple spotlights all tracking a central moving object"
"objects rotating to always face the camera"
```

### F-Curve Modifiers
```
"a hovering object with subtle noise for organic floating motion"
"a pulsing light with cyclic modifier for infinite loop"
```

### Material Animation
```
"emission strength pulsing like a heartbeat"
"color shifting through the spectrum over time"
"transparency fading in and out"
```

### Shape Keys
```
"morphing between different forms"
"face transforming expressions"
```

## Prompt Formula for Best Results

**Template:**
```
[SCENE TYPE] with [MAIN OBJECTS] where [PRIMARY ANIMATION],
[SECONDARY ANIMATIONS], [MATERIAL/LIGHT ANIMATIONS],
camera [CAMERA MOTION], [MOOD/ATMOSPHERE]
```

**Example:**
```
A futuristic control room with holographic displays where data streams
flow upward, buttons pulse when activated, warning lights cycle through
alert states, camera slowly orbits the main console, atmospheric blue
lighting with dramatic volumetric rays
```

## Common Animation Mistakes to Avoid

❌ "make everything move" - Too chaotic
✅ "primary object rotates while secondary objects pulse gently"

❌ "animate the cube" - Too vague
✅ "cube bounces up and down with elastic easing, completing 3 bounces over 5 seconds"

❌ "camera moves around" - Undefined motion
✅ "camera orbits clockwise 180 degrees over 8 seconds with smooth ease-in-out"

## Frame Rate Considerations

- **24 fps**: Cinematic, slightly motion-blurred feel
- **30 fps**: Smooth, standard video
- **60 fps**: Ultra smooth, gaming/sports

For most Voxel animations, **24 fps** is recommended for cinematic quality.
