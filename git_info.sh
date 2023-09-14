cd ../v8
git log > ../my_shell/GitLog-origin.txt
python3 ../my_shell/get_hash.py > ../my_shell/GitHash-origin.txt
python3 ../my_shell/gen_patch.py
rm ../my_shell/GitLog-origin.txt
rm ../my_shell/GitHash-origin.txt