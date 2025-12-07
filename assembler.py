import asm_ref;
import gen;
import os;

IMMEDIATE = 0x0; ZERO_PAGE = 0x1; ZERO_PAGE_X = 0x2;
ABSOLUTE = 0x3; ABSOLUTE_X = 0x4; ABSOLUTE_Y = 0x5;
INDIRECT_X = 0x6; INDIRECT_Y = 0x7; NA = 0x8;
INDIRECT = 0x9; ZERO_PAGE_Y = 0xa;

DO_NOTHING = 0x0; STOP = 0x1; RECURSE = 0x2; STOP_RECURSE = 0x3;
SHOW_BRANCH = 0x4;


MODE_CMD = 0x0; MODE_ARG = 0x1;
SMODE_NONE = -1;
SMODE_IMM = 0x0;
SMODE_ADR = 0x1;
SMODE_IND = 0x2;

SMODE_DADR = 0x3;
SMODE_DIMM = 0x4;
SMODE_INDJJMP = 0x5;

DTYPE_IMM = 0x0; DTYPE_ADR = 0x1; DTYPE_NONE = 0x0;

sm_map = {};
sm_map["$"] = SMODE_ADR;
sm_map["#"] = SMODE_IMM;
sm_map["("] = SMODE_IND;
sm_map["*"] = SMODE_DADR;
sm_map["@"] = SMODE_DADR;
sm_map["!"] = SMODE_DIMM;




whitespace = (" ", "\t", "\n", "\e", "\r");
whitespace2 = (" ", "\t", "\n");
valid_args = ("$", "#", "(", "*", "@");
reserved_chars = "$#()*@,.?!%^&[]+=";

hexdigits = "0123456789abcdefABCDEF";
adr_reg = "XY";

def asm_get_byte(cmd, arg_type):
    return asm_ref.asm_cmd[cmd + str(arg_type)];

def bytestr_val(arg_val):
    return int(arg_val, 16);

def disassemble(arg_txt):
    binary_data = bytes.fromhex(arg_txt.replace("\n", ""))  # Convert hex string to bytes
    cmds = []
    pos = 0
    size = len(binary_data)
    asm = asm_ref.asm
    
    def byte_read():
        nonlocal pos;
        if pos >= size:
            return -1;
        val = binary_data[pos];
        pos += 1;
        return val
    
    while pos < size:
        inst_pos = pos;
        byte = byte_read();
        if byte == -1:
            break;
        if byte in asm:
            insc = asm[byte];
            bytes_list = [byte_read() for _ in range(insc[0x2] - 1)];
            res = get_inst(asm[byte], bytes_list);
            line = res[0x0];
            res_cmd = res[0x1];
            if line == "NUL":
                break;
            cmds.append(line);
        else:
            print("Error! Read an invalid byte at pos " + hex(inst_pos) + "!");
            print("(" + hex(byte) + ")");
            break;
    return (cmds, pos);

def get_inst(insc, args):
    opcode_name = insc[0x0];
    ot = insc[0x1];
    opcode_len = insc[0x2];
    arg2 = "";
    result = DO_NOTHING;
    result_line = "";
    
    line = opcode_name;
    if (opcode_name == "NUL"):
        return ("NUL", STOP);
    if (opcode_len > 0x0):
        if (len(args) > 0x0):
            arg1 = gen.hex_format(args[0]);
            if (opcode_len == 0x3):
                arg2 = gen.hex_format(args[1]);
        if (ot == IMMEDIATE):
            line = line + " #$" + arg1;
            if (opcode_name in asm_ref.BRANCH_OPS):
                result = SHOW_BRANCH;
        elif (ot == ZERO_PAGE):
            line = line + " $" + arg1;
        elif (ot == ZERO_PAGE_X):
            line = line + " $" + arg1 + ",X";
        elif (ot == ABSOLUTE):
            line = line + " $" + arg2 + arg1;
        elif (ot == ABSOLUTE_X):
            line = line + " $" + arg2 + arg1 + ",X";
        elif (ot == ABSOLUTE_Y):
            line = line + " $" + arg2 + arg1 + ",Y";
        elif (ot == INDIRECT_X):
            line = line + " ($" + arg1 + ",X)";
        elif (ot == INDIRECT_Y):
            line = line + " ($" + arg1 + "),Y";
        elif (ot == INDIRECT):
            line = line + "($" + arg2 + arg1 + ")"
        if (opcode_name in asm_ref.END_OPS):
            result = STOP;
        return (line, result);
        
    else:
        return (line, result);

def assemble(asm_code):
    lines = asm_code.splitlines()
    all_cmds = []
    label = ""
    label_index = 0
    lst = []
    
    for line_nmb, line in enumerate(lines, start=1):
        line = line.strip()
        if not line or line.startswith("/"):
            continue
        
        pos_nmb = 0
        cmd, byte1, byte2, add_r, keyword = "", "", "", "", ""
        mode, sub_mode = MODE_CMD, SMODE_NONE
        arg_c = ""
        
        if "[" in line:
            label_start = line.index("[") + 1
            label_end = line.index("]", label_start)
            label = line[label_start:label_end]
            if lst:
                all_cmds.append((lst, label))
                label_index += 1
                lst = []
            continue
        
        for c in line:
            pos_nmb += 1
            if c == "/":
                break
            
            if mode == MODE_CMD:
                if c.isupper():
                    cmd += c
                    if len(cmd) > 2:
                        mode = MODE_ARG
                        cmd = cmd.upper()
                continue
            
            if mode == MODE_ARG:
                if c in whitespace2:
                    continue
                
                if not arg_c:
                    arg_c = c
                    if arg_c not in valid_args:
                        print(f"Error in input! Invalid argument '{arg_c}' at line {line_nmb}, pos {pos_nmb}.")
                    else:
                        sub_mode = sm_map.get(arg_c, SMODE_NONE)
                    continue
                
                if sub_mode in {SMODE_IMM, SMODE_ADR, SMODE_INDJJMP} and c in hexdigits:
                    (byte1 if len(byte1) < 2 else byte2).join(c)
                elif sub_mode in {SMODE_IND, SMODE_DADR, SMODE_DIMM}:
                    if c in adr_reg:
                        add_r = c
                    elif c not in reserved_chars:
                        keyword += c
                
        if len(cmd) > 2:
            byte = asm_get_byte(cmd, sub_mode)
            if sub_mode == SMODE_NONE:
                lst.append((byte,))
            elif sub_mode == SMODE_IMM:
                lst.append((byte, bytestr_val(byte1)))
            elif sub_mode == SMODE_ADR:
                arg1 = bytestr_val(byte1)
                arg2 = bytestr_val(byte2) if byte2 else None
                lst.append((byte, arg2, arg1) if arg2 else (byte, arg1))
            elif sub_mode == SMODE_IND:
                lst.append((byte, bytestr_val(byte1)))
            elif sub_mode == SMODE_INDJJMP:
                lst.append((byte, bytestr_val(byte2), bytestr_val(byte1)))
    
    if not label:
        label = f"default_label_{label_index}"
    all_cmds.append((lst, label))
    
    return all_cmds


