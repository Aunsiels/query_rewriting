for i in {1..3}
do
    python3 experiments_random.py "experiments_random_new/$(hostname)_new_$i.tsv" &
done
