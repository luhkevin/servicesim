python simserver.py -n alpha -p 8000 &
python simserver.py -n gamma -p 8001 &
python simserver.py -n kappa -p 8002 &
python simserver.py -n iota -p 8003 &

python simserver.py -n controller -p 8080 -c tests/simple.json -i tests/simple-inv &
