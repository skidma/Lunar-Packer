-- you shouldn't be here

local bxor = bit32 and bit32.bxor or function(a, b)
    local p, c = 1, 0
    while a > 0 and b > 0 do
        local ra, rb = a % 2, b % 2
        if ra ~= rb then c = c + p end
        a, b, p = (a - ra) / 2, (b - rb) / 2, p * 2
    end
    if a < b then a = b end
    while a > 0 do
        local ra = a % 2
        if ra > 0 then c = c + p end
        a, p = (a - ra) / 2, p * 2
    end
    return c
end

local function decode_constants(bytecode, pos, count, session_key)
    local constants = {}
    local rolling_key = session_key
    for i = 1, count do
        local b1, b2, b3, b4 = string.byte(bytecode, pos, pos + 3)
        if not b1 or not b2 or not b3 or not b4 then break end
        local len = (b1 * 16777216) + (b2 * 65536) + (b3 * 256) + b4
        pos = pos + 4
        local raw = string.sub(bytecode, pos, pos + len - 1)
        pos = pos + len
        local decrypted = {}
        for j = 1, #raw do
            local byte = string.byte(raw, j, j)
            decrypted[j] = string.char(bxor(byte, rolling_key))
            rolling_key = (rolling_key + (byte or 0)) % 256
        end
        constants[i] = table.concat(decrypted)
    end
    return constants, pos
end

local function engine_factory()
    return function(bytecode, opcodes, session_key)
        local stored_checksum = (string.byte(bytecode, #bytecode-3) * 16777216) +
                                (string.byte(bytecode, #bytecode-2) * 65536) +
                                (string.byte(bytecode, #bytecode-1) * 256) +
                                string.byte(bytecode, #bytecode)
        local calc_sum = 0
        for i = 1, #bytecode - 4 do
            calc_sum = (calc_sum + string.byte(bytecode, i)) % 4294967296
        end
        if calc_sum ~= stored_checksum then
            error("L_INTEG_0x2")
        end
        local pos = 1
        local function gBits32()
            local b1, b2, b3, b4 = string.byte(bytecode, pos, pos + 3)
            if not b1 then return 0 end
            pos = pos + 4
            return (b1 * 16777216) + (b2 * 65536) + (b3 * 256) + b4
        end
        local inst_len = gBits32()
        local session_seed = gBits32()
        local Instructions = {}
        for i = 1, inst_len do
            local mut_op = string.byte(bytecode, pos, pos)
            local A = string.byte(bytecode, pos + 1, pos + 1)
            local B = string.byte(bytecode, pos + 2, pos + 2)
            local C = string.byte(bytecode, pos + 3, pos + 3)
            pos = pos + 4
            if not mut_op then break end
            local true_op_int = bxor(mut_op, session_key)
            local opcode_name
            for name, id in pairs(opcodes) do
                if id == true_op_int then
                    opcode_name = name
                    break
                end
            end
            Instructions[i] = {opcode_name, A, B, C, (B * 256) + C}
        end
        local const_count = gBits32()
        local Constants, last_pos = decode_constants(bytecode, pos, const_count, session_key)
        local Stack = {}
        local PC = 1
        local Handlers = {
            [opcodes.OP_MOVE] = function(inst)
                Stack[inst[2]] = Stack[inst[3]]
            end,
            [opcodes.OP_LOADSTR] = function(inst)
                Stack[inst[2]] = Constants[inst[5]]
            end,
            [opcodes.OP_CONCAT] = function(inst)
                local a, b = Stack[inst[3]], Stack[inst[4]]
                Stack[inst[2]] = tostring(a or "") .. tostring(b or "")
            end,
            [opcodes.OP_XOR] = function(inst)
                local data = Stack[inst[3]]
                local key = Stack[inst[4]]
                if not data or not key then return end
                local result = {}
                for i = 1, #data do
                    local k_byte = string.byte(key, (i-1) % #key + 1)
                    result[i] = string.char(bxor(string.byte(data, i), k_byte))
                end
                Stack[inst[2]] = table.concat(result)
            end,
            [opcodes.OP_ADD] = function(inst)
                local data = Stack[inst[3]]
                local key = Stack[inst[4]]
                if not data or not key then return end
                local result = {}
                for i = 1, #data do
                    local k_byte = string.byte(key, (i-1) % #key + 1)
                    result[i] = string.char((string.byte(data, i) + k_byte) % 256)
                end
                Stack[inst[2]] = table.concat(result)
            end,
            [opcodes.OP_REVXOR] = function(inst)
                local data = Stack[inst[3]]
                local key = Stack[inst[4]]
                if not data or not key then return end
                local result = {}
                local len = #data
                for i = 1, len do
                    local k_byte = string.byte(key, (i-1) % #key + 1)
                    result[len - i + 1] = string.char(bxor(string.byte(data, i), k_byte))
                end
                Stack[inst[2]] = table.concat(result)
            end,
            [opcodes.OP_ENV] = function(inst)
                Stack[inst[2]] = (getgenv and getgenv().loadstring) or (getfenv and getfenv().loadstring) or loadstring
            end,
            [opcodes.OP_LOADSTRING] = function(inst)
                local loader = Stack[inst[3]]
                local source = Stack[inst[2]] or Stack[0] or ""
                if type(loader) == "function" then
                    local s, res = pcall(loader, source, "@Lunar_V1.0.0")
                    if s then
                        Stack[inst[2]] = res
                    else
                        print("Lunar: Compilation Error:", res)
                    end
                else
                    print("Lunar: Loader Error (Nil/Invalid)")
                end
            end,
            [opcodes.OP_CALL] = function(inst)
                local func = Stack[inst[2]]
                if type(func) == "function" then
                    local s, e = pcall(func)
                    if not s then
                        print("Lunar Payload Error:", e)
                    end
                end
            end,
            [opcodes.OP_JMP] = function(inst)
                PC = PC + inst[5]
            end,
            [opcodes.OP_HALT] = function(inst)
                PC = inst_len + 1
            end,
            [opcodes.OP_TRASH] = function(inst)
            end
        }
        while PC <= inst_len do
            local inst = Instructions[PC]
            if not inst then break end
            local op_name = inst[1]
            local op_id = opcodes[op_name]
            local handler = Handlers[op_id]
            if handler then
                handler(inst)
            end
            PC = PC + 1
        end
    end
end

return engine_factory
