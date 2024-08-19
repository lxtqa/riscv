import re


def has_arcwords(text,arch = ""):
    if arch == "":
        for keyword in ["arm","Arm","ARM", \
                        "x64","X64", \
                        "riscv","Riscv","RISCV",\
                        "s390","S390",\
                        "ia32","Ia32","IA32",\
                        "ppc","Ppc","PPC",\
                        "mips","Mips","MIPS",\
                        "loong","Loong","LOONG"]:
            if keyword in text:
                if keyword == "arm" and "harmony" in text:
                    pass
                else:
                    return keyword
        return None
    elif arch == "arm64":
        for keyword in  ["arm64","Arm64","ARM64"] :
            if keyword in text:
                return keyword
        return None
    elif arch == "arm":
        for keyword in  ["arm","Arm","ARM"] :
            if keyword in text:
                if keyword == "arm" and "harmony" in text or "arm64" in text or "Arm64" in text or "ARM64" in text:
                    pass
                return keyword
        return None
    elif arch == "x64":
        for keyword in  ["x64","X64"] :
            if keyword in text:
                return keyword
        return None
    elif arch == "riscv":
        #判断是否存在riscv64
        for keyword in  ["riscv","Riscv","RISCV"] :
            if keyword in text:
                return keyword
        return None
    elif arch == "riscv64":
        #判断是否存在riscv64
        for keyword in  ["riscv","Riscv","RISCV"] :
            if keyword in text:
                if "riscv32" in text or "Riscv32" in text or "RISCV32" in text:
                    pass
                return keyword
        return None
    elif arch == "riscv32":
        #判断是否存在riscv32
        for keyword in  ["riscv","Riscv","RISCV"] :
            if keyword in text:
                if "riscv64" in text or "Riscv64" in text or "RISCV64" in text:
                    pass
                return keyword
        return None
    elif arch == "s390":
        for keyword in  ["s390","S390"] :
            if keyword in text:
                return keyword
        return None
    elif arch == "ia32":
        for keyword in  ["ia32","Ia32","IA32"] :
            if keyword in text:
                return keyword
        return None
    elif arch == "ppc":
        for keyword in  ["ppc","Ppc","PPC"] :
            if keyword in text:
                return keyword
        return None
    elif arch == "mips":
        for keyword in  ["mips","Mips","MIPS"] :
            if keyword in text:
                return keyword
        return None
    elif arch == "loong":
        for keyword in  ["loong","Loong","LOONG"] :
            if keyword in text:
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

def remove_whitespace(input_string):
    return re.sub(r'\s+', '', input_string)

def isfilepara(file1, file2):
    # 实现文件是否平行的逻辑
    return remove_whitespace(remove_arcwords(file1)) == remove_whitespace(remove_arcwords(file2))

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
    arc1 = has_arcwords(hunk1)
    arc2 = has_arcwords(hunk2)
    if arc1 and arc2:
        return remove_whitespace(remove_arcwords(hunk1)) == remove_whitespace(remove_arcwords(hunk2))
    elif not arc1 and not arc2:
        return remove_whitespace(hunk1) == remove_whitespace(hunk2)
    return False