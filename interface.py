import tkinter as tk;
from tkinter import scrolledtext
import sys as sys;
import assembler;
import asm_ref;
import gen;
import os;

wnd = tk.Tk();
wnd.title("HaruASM");
wnd.geometry("500x400+50+50");
wnd.resizable(False, False)
wnd.iconbitmap("haru.ico");

code_name = tk.StringVar();


def add_element(arg_element, row, col, arg_stk, arg_padx, arg_pady):
    arg_element.grid(column=col, row=row, sticky=arg_stk, padx=arg_padx, pady=arg_pady)

wnd.columnconfigure(0, weight=1)
wnd.columnconfigure(1, weight=3)

lbl_code = tk.Label(wnd, text="ASM Code");
add_element(lbl_code, 0, 0, tk.W, 2, 2);

txt_code = tk.scrolledtext.ScrolledText(wnd, width=32, height=12);
add_element(txt_code, 1, 0, tk.EW, 5, 5);

#scroll1 = tk.Scrollbar(wnd, orient="vertical", command=txt_code.yview);
#add_element(scroll1, 1, 1, tk.NS, 2, 2);
#txt_code['yscrollcommand'] = scroll1.set;



lbl_code2 = tk.Label(wnd, text="ASM Bytes");
add_element(lbl_code2, 0, 2, tk.W, 2, 2);

txt_code2 = tk.scrolledtext.ScrolledText(wnd, width=16, height=12);
add_element(txt_code2, 1, 2, tk.EW, 5, 5);

#scroll2 = tk.Scrollbar(wnd, orient="vertical", command=txt_code2.yview);
#add_element(scroll2, 1, 3, tk.NS, 2, 2);
#txt_code2['yscrollcommand'] = scroll2.set;

def to_bytes():
    code_txt = txt_code.get('1.0', 'end');
    if code_txt:
        compiles = assembler.assemble(code_txt);
        txt = "";
        txt = "".join(gen.hex_format(op) for routine in compiles for inst_list in routine[:-1] for inst in inst_list for op in inst)
        txt_code2.delete('1.0', 'end');
        txt_code2.insert('1.0', txt);

        
def to_code():
    code_txt = txt_code2.get('1.0', 'end');
    cmds = assembler.disassemble(code_txt)[0];
    txt = "\n".join(cmds)
    txt_code.delete('1.0', 'end');
    txt_code.insert('1.0', txt);

def save_code():
    tmp_name = code_name.get();
    if not (tmp_name == ""):
        with open(tmp_name + ".txt", "w") as file:
            file.write(txt_code.get('1.0', 'end')[:-1]);

btn_to_asm = tk.Button(wnd, text="To Bytes", command=to_bytes);
add_element(btn_to_asm, 3, 0, tk.EW, 2, 2);

btn_to_code = tk.Button(wnd, text="To Code", command=to_code);
add_element(btn_to_code, 3, 2, tk.EW, 2, 2);

btn_save_asm = tk.Button(wnd, text="Save Code", command=save_code);
add_element(btn_save_asm, 4, 0, tk.EW, 2, 2);

lbl_save = tk.Label(wnd, text="Filename: ");
add_element(lbl_save, 4, 1, tk.W, 2, 2);

ent = tk.Entry(wnd, textvariable=code_name);
add_element(ent, 4, 2, tk.EW, 4, 2);

class ConsoleText (tk.Text):
    # A Text widget that can display console output and error

    def __init__ (self, master, **kwargs):
        # Initialize the Text widget with some default options
        super ().__init__ (master, **kwargs)
        self.configure(state="disabled", bg="white", fg="black");
        self["width"] = 60;
        self["height"] = 8;

    def write (self, text):
        # Insert the text into the Text widget
        self.configure (state="normal")
        self.insert ("end", text)
        self.configure (state="disabled")
        self.see ("end") # Scroll to the end

    def flush (self):
        # Do nothing
        pass
    
console = ConsoleText(wnd);
console.grid(row=5, column=0, columnspan=3, padx=(10, 10), pady=(10, 10));

sys.stdout = console;
sys.stderr = console;

wnd.mainloop();