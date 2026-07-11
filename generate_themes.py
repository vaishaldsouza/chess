import os
import shutil

def generate():
    themes = {
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
        for color_dir in base_dirs:
            src_dir = os.path.join('img', color_dir)
            dest_dir = os.path.join('img', 'themes', theme_name, color_dir)
            os.makedirs(dest_dir, exist_ok=True)
            
            replacement_map = colors[color_dir]
            
            for file_name in os.listdir(src_dir):
                if file_name.endswith('.svg'):
                    src_file = os.path.join(src_dir, file_name)
                    dest_file = os.path.join(dest_dir, file_name)
                    
                    with open(src_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    for orig, rep in replacement_map.items():
                        content = content.replace(orig, rep)
                        
                    with open(dest_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                        
    print("Theme assets generated successfully under img/themes/")

if __name__ == '__main__':
    generate()
