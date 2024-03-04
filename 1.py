import re

# 示例字符串
text = "This is some text (with, a comma), a  ) and another (example, here)"


# 使用sub()函数进行替换
replaced_text = re.sub(re.compile(r',\s*\)(?=\s*)'), ')', text)

print(replaced_text)
