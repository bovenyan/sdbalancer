# usage ./flowgen <flow number>

for i in `seq 1 $1`;    # generate <flow number> udp flows to, port range 5001 ~ 5000+<flow number>
do
    iperf -c 10.0.0.2 -p $(($i+5000)) -u -t 1000 -b 1m -l 1000 >/dev/null 2>&1 &
done

sleep 1

echo "generating " $1 "flows..."
read -n 1 -s -r -p "Press any kill to continue"

pkill iperf
