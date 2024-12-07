def rgb_to_hsl(r, g, b):
    r /= 255.0
    g /= 255.0
    b /= 255.0
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    l = (max_c + min_c) / 2
    if max_c == min_c:
        h = s = 0
    else:
        d = max_c - min_c
        s = d / (2 - max_c - min_c) if l > 0.5 else d / (max_c + min_c)
        if max_c == r:
            h = (g - b) / d + (6 if g < b else 0)
        elif max_c == g:
            h = (b - r) / d + 2
        elif max_c == b:
            h = (r - g) / d + 4
        h /= 6
    return h, s, l

def hsl_to_rgb(h, s, l):
    def hue_to_rgb(p, q, t):
        if t < 0: t += 1
        if t > 1: t -= 1
        if t < 1/6: return p + (q - p) * 6 * t
        if t < 1/2: return q
        if t < 2/3: return p + (q - p) * (2/3 - t) * 6
        return p
    
    if s == 0:
        r = g = b = l
    else:
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = hue_to_rgb(p, q, h + 1/3)
        g = hue_to_rgb(p, q, h)
        b = hue_to_rgb(p, q, h - 1/3)
    
    return round(r * 255), round(g * 255), round(b * 255)

def next_color_in_wheel(rgb, n, min_saturation=0.5, min_lightness=0.5):
    r, g, b = rgb
    h, s, l = rgb_to_hsl(r, g, b)
    
    # Ensure saturation and lightness are at least the minimum values
    s = max(s, min_saturation)
    l = max(l, min_lightness)
    
    h_next = (h + 1 / n) % 1.0
    return hsl_to_rgb(h_next, s, l)

# Example Home Assistant Python script: change_light_color.py

# Get the entity_id from the script arguments
entity_id = data.get('entity_id')
num_steps = data.get('num_steps', 16)

# Fetch the current RGB state of the light
state = hass.states.get(entity_id)
attributes = state.attributes

# Extract the RGB color
rgb = attributes.get('rgb_color', [255, 182, 193])

# Calculate the next color in the wheel

next_rgb = next_color_in_wheel(rgb, num_steps)

# Call the light.turn_on service to set the new color
hass.services.call('light', 'turn_on', {
    'entity_id': entity_id,
    'rgb_color': next_rgb
})
