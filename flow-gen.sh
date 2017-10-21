# usage ./flowgen <flow number>

for i in `seq 1 $1`;    # generate <flow number> udp flows to, port range 5001 ~ 5000+<flow number>
do
    iperf -c 10.0.0.2 -p $(($i+5000)) -u -b 10m -l 1000 &
done


