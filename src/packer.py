import random
import string
import os
from src.opcodes import *



def alg_xor(text_bytes: bytes, key_bytes: bytes) -> bytes:
    encrypted = bytearray()
    for i, byte in enumerate(text_bytes):
        key_byte = key_bytes[i % len(key_bytes)]
        encrypted.append(byte ^ key_byte)
    return bytes(encrypted)

def alg_add(text_bytes: bytes, key_bytes: bytes) -> bytes:
    encrypted = bytearray()
    for i, byte in enumerate(text_bytes):
        key_byte = key_bytes[i % len(key_bytes)]
        encrypted.append((byte + key_byte) % 256)
    return bytes(encrypted)

def alg_reverse_xor(text_bytes: bytes, key_bytes: bytes) -> bytes:
    rev = text_bytes[::-1]
    return alg_xor(rev, key_bytes)

def lua_mini_obfuscate(source: str) -> str:
    import re
    source = re.sub(r'--\[\[.*?\]\]', '', source, flags=re.DOTALL)
    source = re.sub(r'--.*', '', source)
    renames = {
        'bxor': '_X',
        'decode_constants': '_D',
        'engine_factory': '_F',
        'bytecode': '_B',
        'opcodes': '_O',
        'session_key': '_K',
        'rolling_key': '_RK',
        'gBits32': '_G32',
        'Instructions': '_INS',
        'Constants': '_CON',
        'Stack': '_STK',
        'PC': '_P',
        'Handlers': '_H',
        'inst': '_I',
        'inst_len': '_IL',
        'mut_op': '_M',
        'true_op_int': '_TO',
        'opcode_name': '_ON',
        'handler': '_HA',
        'op_name': '_OPN',
        'op_id': '_OID'
    }
    
    for old, new in renames.items():
        source = re.sub(rf'\b{old}\b', new, source)
        
  
    source = re.sub(r'\n\s*\n', '\n', source)
    return source.strip()

def pack_script(input_source: str, print_lunar_func) -> str:
    print_lunar_func("[+] Generating Session Key...")
    session_seed = random.randint(1000, 9999)
    session_key = random.randint(1, 255)
    
    print_lunar_func("[+] Intercepting Abstract Syntax Tree...")
    op_codes_pool = list(range(1, 256))
    random.shuffle(op_codes_pool)
    
    op_map = {}
    for op in OP_LIST:
        op_map[op] = op_codes_pool.pop()
        
    constants = []
    instructions = []
    
    rk = [session_key]
    def add_constant(val_bytes: bytes) -> int:
        eb = bytearray()
        for b in val_bytes:
            enc_b = b ^ rk[0]
            eb.append(enc_b)
            rk[0] = (rk[0] + enc_b) % 256 
        val_bytes = bytes(eb)
        
        constants.append(val_bytes)
        return len(constants)
        
    print_lunar_func("[+] Adding Junk")
    decoy_keys = [
        b"sk-proj-T19x8A92BcdEfGhIjKlMnOpQrStUvWxYz",
        b"ghp_849AbCdEfGhIjKlMnOpQrStUvWxYz012345",
        b"https://discord.com/api/webhooks/123456789/AbCdEfGhIjKlMnOpQrStUvWxYz",
        b"AKIAIOSFODNN7EXAMPLE"
    ]
    for key in decoy_keys:
        add_constant(key) 
        
    def insert_junk(volume='low'):
        counts = {
            'low': (1, 3),
            'medium': (5, 10),
            'high': (15, 30)
        }
        low, high = counts.get(volume, (1, 3))
        num_trash = random.randint(low, high)
        instructions.append([op_map[OP_JMP], 0, 0, 0, num_trash])
        for _ in range(num_trash):
            instructions.append([op_map[OP_TRASH], random.randint(0,255), session_key, random.randint(0,255), 0])
            
    insert_junk('low')
    empty_idx = add_constant(b"")
    instructions.append([op_map[OP_LOADSTR], 0, 0, 0, empty_idx])

    print_lunar_func("[+] Translating Instructions and Chunking Memory...")
    raw_bytes = input_source.encode('utf-8')
    chunk_size = random.randint(60, 100)
    chunks = [raw_bytes[i:i+chunk_size] for i in range(0, len(raw_bytes), chunk_size)]
    
    print_lunar_func(f"[+] Applying Multi-Layer Cypher over {len(chunks)} blocks...")
    for chunk in chunks:
        key_str = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        key_bytes = key_str.encode('utf-8')
        
        encrypted = alg_xor(chunk, key_bytes)
        op = OP_XOR
        
        enc_idx = add_constant(encrypted)
        key_idx = add_constant(key_bytes)
        
        instructions.append([op_map[OP_LOADSTR], 1, 0, 0, enc_idx])
        instructions.append([op_map[OP_LOADSTR], 2, 0, 0, key_idx])
        instructions.append([op_map[op], 3, 1, 2, 0])
        instructions.append([op_map[OP_CONCAT], 0, 0, 3, 0])
        
        if random.random() > 0.8:
            insert_junk('low')
        
    print_lunar_func("[+] Finalizing execution trace layout...")
    instructions.append([op_map[OP_ENV], 4, 0, 0, 0])
    instructions.append([op_map[OP_LOADSTRING], 5, 4, 0, 0])
    instructions.append([op_map[OP_CALL], 5, 0, 0, 0])
    instructions.append([op_map[OP_HALT], 0, 0, 0, 0])
    
    bytecode_bytes = bytearray()
    
    def write32(num):
        bytecode_bytes.extend(num.to_bytes(4, 'big'))
        
    def write16(num):
        bytecode_bytes.extend((num & 0xFFFF).to_bytes(2, 'big'))

    def write8(num):
        bytecode_bytes.append(num & 0xFF)
        
    print_lunar_func("[+] Serializing dynamic bytecodes & evolving opcodes...")
    write32(len(instructions))
    write32(session_seed)
    
    for pc, inst in enumerate(instructions):
        true_op = inst[0]
        mutated_op = true_op ^ session_key
        write8(mutated_op)
        
        write8(inst[1])  A
        Bx = inst[4]
        if Bx > 0:
            write8((Bx >> 8) & 0xFF) # B
            write8(Bx & 0xFF)        # C
        else:
            write8(inst[2]) # B
            write8(inst[3]) # C
            
    write32(len(constants))
    for val_bytes in constants:
        write32(len(val_bytes))
        bytecode_bytes.extend(val_bytes)
        
    watermark = b"LUNAR_V2_SECURE_PAYLOAD_PATCHED_BY_ANTIGRAVITY"
    bytecode_bytes.extend(watermark)

    calc_sum = sum(bytecode_bytes) % 4294967296
    write32(calc_sum)
        
    def format_byte(b):
        return f"\\{b:03d}"
        
    lua_bytecode_str = "".join(format_byte(b) for b in bytecode_bytes)
    
    raw_url = "https://raw.githubusercontent.com/skidma/engineering/refs/heads/main/engine.lua"
    obfuscated_url = "".join(f"\\{ord(c):03d}" for c in raw_url)

    k_offset = random.randint(100, 500)
    k_expr = f"({session_key + k_offset} - {k_offset})"

    engine_path = os.path.join('src', 'module', 'engine.lua')
    with open(engine_path, 'r', encoding='utf-8') as f:
        engine_source = f.read()
    
    engine_source = lua_mini_obfuscate(engine_source)

    NEW_TEMPLATE = """\
local _K = """ + k_expr + """
local _S = """ + str(session_seed) + """
local _O = {
    OP_MOVE = {{OP_MOVE}},
    OP_LOADSTR = {{OP_LOADSTR}},
    OP_XOR = {{OP_XOR}},
    OP_CONCAT = {{OP_CONCAT}},
    OP_ENV = {{OP_ENV}},
    OP_LOADSTRING = {{OP_LOADSTRING}},
    OP_CALL = {{OP_CALL}},
    OP_HALT = {{OP_HALT}},
    OP_JMP = {{OP_JMP}},
    OP_TRASH = {{OP_TRASH}},
    OP_ADD = {{OP_ADD}},
    OP_REVXOR = {{OP_REVXOR}}
}
local _F = (function()
""" + engine_source + """
end)()()
local _B = "{{BYTECODE}}"
local _ok, _err = pcall(_F, _B, _O, _K)
if not _ok then warn("L_ERR: " .. tostring(_err)) end
"""
    print_lunar_func("[+] Packing Payload...")
    template = NEW_TEMPLATE.replace('{{BYTECODE}}', lua_bytecode_str)
    for op_name, op_int in op_map.items():
        template = template.replace(f'{{{{{op_name}}}}}', f'{op_int}')
        
    return template
