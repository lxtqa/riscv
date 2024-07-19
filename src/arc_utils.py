def has_arcwords(text):
    for keyword in ["arm64","Arm64","ARM64","arm32","Arm32","ARM32","arm","Arm","ARM", \
                    "x64","X64", \
                    "riscv64","Riscv64","RISCV64","riscv32","Riscv32","RISCV32","riscv","Riscv","RISCV",\
                    "s390","S390",\
                    "ia32","Ia32","IA32",\
                    "ppc64","Ppc64","PPC64","ppc32","Ppc32","PPC32","ppc","Ppc","PPC",\
                    "mips64","Mips64","MIPS64","mips32","Mips32","MIPS32","mips","Mips","MIPS",\
                    "loong64","Loong64","LOONG64","loong32","Loong32","LOONG32","loong","Loong","LOONG"]:
        if keyword in text:
            if keyword == "arm" and "harmony" in text:
                pass
            else:
                return keyword
    return None

def remove_arcwords(text):
    for keyword in ["arm64","Arm64","ARM64","arm32","Arm32","ARM32","arm","Arm","ARM", \
                    "x64","X64", \
                    "riscv64","Riscv64","RISCV64","riscv32","Riscv32","RISCV32","riscv","Riscv","RISCV",\
                    "s390","S390",\
                    "ia32","Ia32","IA32",\
                    "ppc64","Ppc64","PPC64","ppc32","Ppc32","PPC32","ppc","Ppc","PPC",\
                    "mips64","Mips64","MIPS64","mips32","Mips32","MIPS32","mips","Mips","MIPS",\
                    "loong64","Loong64","LOONG64","loong32","Loong32","LOONG32","loong","Loong","LOONG"]:
        text = text.replace(keyword, '')
    return text