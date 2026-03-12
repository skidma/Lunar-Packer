import argparse
import os
import sys

from src.packer import pack_script

if os.name == 'nt':
    os.system('title Lunar (Luau) (v1.0.0)')

def print_lunar(msg):
    blue = "\033[38;5;111m"
    white = "\033[97m"
    reset = "\033[0m"
    if msg.startswith('['):
        msg = ' ' + msg
    msg = msg.replace('[', f'{blue}[{white}').replace(']', f'{blue}]{white}').replace('+', f'{blue}+{white}').replace('-', f'{blue}-{white}')
    print(f"{white}{msg}{reset}")

def main():
    parser = argparse.ArgumentParser(description="Lunar (Luau) (v1.0.0)")
    parser.add_argument("input", help="The input .lua script to obfuscate")
    parser.add_argument("-o", "--output", help="The output path. Defines out.lua by default.", default=None)
    
    try:
        args = parser.parse_args()
    except Exception as e:
        print_lunar(f"[-] Command-line parsing error: {e}")
        sys.exit(1)
    
    input_file = args.input
    output_file = args.output
    
    os.system('cls' if os.name == 'nt' else 'clear')
    
    if not os.path.exists(input_file):
        print_lunar(f"[-] Error: Could not find input file '{input_file}'")
        sys.exit(1)
        
    if output_file is None:
        name, ext = os.path.splitext(input_file)
        ext = ext if ext else '.lua'
        output_file = f"{name}_obf{ext}"
        
    print_lunar(f"[+] Loading target payload: {input_file}")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            source = f.read()
            
        packed = pack_script(source, print_lunar)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(packed)
            
        print_lunar(f"[+] Success! Compiled securely to {os.path.basename(output_file)}")
    except IOError as e:
        print_lunar(f"[-] Initializer I/O Error: {e}")
        sys.exit(1)
    except Exception as e:
        print_lunar(f"[-] Fatal Builder Exception: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
