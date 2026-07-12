import os

def generate():
    board_colors = {
        'default': {
            'light': '#f0d9b5',
            'dark': '#b58863'
        },
        'neon': {
            'light': '#2a2b3d',
            'dark': '#1a1b26'
        },
        'wood': {
            'light': '#f4d0a4',
            'dark': '#b77b4c'
        },
        'cyberpunk': {
            'light': '#122538',
            'dark': '#0b1621'
        }
    }

    themes = {
        'default': {
            'white': {}, # default theme doesn't need color changes, just background injection
            'black': {}
        },
        'neon': {
            'white': {
                '#fff': '#00ffff',
                '#bba38a': '#008b8b',
                'stroke="#323232"': 'stroke="#00ffff"'
            },
            'black': {
                '#796c60': '#ff00ff',
                '#4b403b': '#8b008b',
                'stroke="#1e1e1e"': 'stroke="#ff00ff"'
            }
        },
        'wood': {
            'white': {
                '#fff': '#f5deb3',
                '#bba38a': '#d2b48c',
                'stroke="#323232"': 'stroke="#8b5a2b"'
            },
            'black': {
                '#796c60': '#8b4513',
                '#4b403b': '#3e2723',
                'stroke="#1e1e1e"': 'stroke="#1a0f0a"'
            }
        },
        'cyberpunk': {
            'white': {
                '#fff': '#ffff00',
                '#bba38a': '#ccaa00',
                'stroke="#323232"': 'stroke="#00ffff"'
            },
            'black': {
                '#796c60': '#1a0033',
                '#4b403b': '#4b0082',
                'stroke="#1e1e1e"': 'stroke="#ff00ff"'
            }
        }
    }

    base_dirs = ['white', 'black']
    
    for theme_name, colors in themes.items():
        theme_colors = board_colors[theme_name]
        
        # 1. Generate empty squares
        dest_theme_dir = os.path.join('img', 'themes', theme_name)
        os.makedirs(dest_theme_dir, exist_ok=True)
        
        for sq_type in ['light', 'dark']:
            blank_content = f'<svg xmlns="http://www.w3.org/2000/svg" width="50" height="50"><rect width="50" height="50" fill="{theme_colors[sq_type]}"/></svg>'
            with open(os.path.join(dest_theme_dir, f'blank_{sq_type}.svg'), 'w', encoding='utf-8') as f:
                f.write(blank_content)
        
        # 2. Generate piece SVGs with background injected
        for color_dir in base_dirs:
            src_dir = os.path.join('img', color_dir)
            dest_dir = os.path.join(dest_theme_dir, color_dir)
            os.makedirs(dest_dir, exist_ok=True)
            
            replacement_map = colors[color_dir]
            
            for file_name in os.listdir(src_dir):
                if file_name.endswith('.svg'):
                    src_file = os.path.join(src_dir, file_name)
                    
                    with open(src_file, 'r', encoding='utf-8') as f:
                        base_content = f.read()
                        
                    # Apply color replacements for the theme
                    for orig, rep in replacement_map.items():
                        base_content = base_content.replace(orig, rep)
                    
                    # Create a version for light and dark squares
                    for sq_type in ['light', 'dark']:
                        # Inject rect right after opening <svg ...> tag
                        idx = base_content.find('>')
                        if idx != -1:
                            rect_str = f'<rect width="50" height="50" fill="{theme_colors[sq_type]}"/>'
                            injected_content = base_content[:idx+1] + rect_str + base_content[idx+1:]
                        else:
                            injected_content = base_content
                            
                        dest_file_name = file_name.replace('.svg', f'_{sq_type}.svg')
                        dest_file = os.path.join(dest_dir, dest_file_name)
                        
                        with open(dest_file, 'w', encoding='utf-8') as f:
                            f.write(injected_content)
                            
    print("Theme assets with integrated board backgrounds generated successfully!")

if __name__ == '__main__':
    generate()
