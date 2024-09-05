import re


def has_archwords(text):
        # for keyword in ["arm64","Arm64","ARM64","arm32","Arm32","ARM32","arm","Arm","ARM", \
        #                 "x64","X64", \
        #                 "riscv64","Riscv64","RISCV64","riscv32","Riscv32","RISCV32","riscv","Riscv","RISCV",\
        #                 "s390","S390",\
        #                 "ia32","Ia32","IA32",\
        #                 "ppc64","Ppc64","PPC64","ppc32","Ppc32","PPC32","ppc","Ppc","PPC",\
        #                 "mips64","Mips64","MIPS64","mips32","Mips32","MIPS32","mips","Mips","MIPS",\
        #                 "loong64","Loong64","LOONG64","loong32","Loong32","LOONG32","loong","Loong","LOONG"]:
        for keyword in ["arm64","Arm64","ARM64"]:
            if keyword in text:
                return "arm64"
        for keyword in ["arm","Arm","ARM"]:
            if keyword in text:
                if keyword == "arm" and "harmony" in text:
                    pass
                else:
                    return "arm"
        for keyword in ["x64","X64"]:
            if keyword in text:
                return "x64"
        for keyword in ["riscv32", "Riscv32", "RISCV32"]:
            if keyword in text:
                return "riscv32"
        for keyword in ["riscv64", "Riscv64", "RISCV64"]:
            if keyword in text:
                return "riscv64"
        for keyword in ["riscv","Riscv","RISCV"] :
            if keyword in text:
                return "riscv"
        for keyword in ["s390","S390"]:
            if keyword in text:
                return "s390"
        for keyword in ["ia32","Ia32","IA32"] :
            if keyword in text:
                return "ia32"
        for keyword in ["ppc","Ppc","PPC"] :
            if keyword in text:
                return "ppc"
        for keyword in ["mips","Mips","MIPS"] :
            if keyword in text:
                return "mips"
        for keyword in ["loong","Loong","LOONG"] :
            if keyword in text:
                return "loong"
        return None


def remove_archwords(text):
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

def remove_whitespace(input_string):
    return re.sub(r'\s+', '', input_string)

def isfilepara(file1, file2):
    # 实现文件是否平行的逻辑
    return remove_whitespace(remove_archwords(file1)) == remove_whitespace(remove_archwords(file2))

def extract_name(header):
    name = re.findall(r"^.+\s+(\w*:?:?\w+)\(.*\).*{$",header)
    if name != []:
        return name[0]
    else:
        return None

def ishunkpara(hunk1, hunk2):
    if hunk1 == "" or hunk2 == "":
        return hunk1 == hunk2
    # 实现hunk是否平行的逻辑
    arc1 = has_archwords(hunk1)
    arc2 = has_archwords(hunk2)
    if arc1 and arc2:
        return remove_whitespace(remove_archwords(hunk1)) == remove_whitespace(remove_archwords(hunk2))
    elif not arc1 and not arc2:
        return remove_whitespace(hunk1) == remove_whitespace(hunk2)
    return False