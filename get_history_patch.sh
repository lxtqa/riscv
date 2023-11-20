cd v8
git log > ../GitLog-origin.txt
python3 ../get_hash.py
python3 ../gen_patch.py
rm ../GitLog-origin.txt
rm ../GitHash-origin.txt
cd ..
python3 classify.py
python3 split_and_filter.py ./classified_patch