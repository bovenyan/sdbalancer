# usage at h2 ./flow-sink <flow number>

for i in `seq 1 $1`;    # generate <flow number> udp flows to, port range 5001 ~ 5000+<flow number>
do
    iperf -s -u -p $(($i+5000)) &
done

sleep 1
read -n 1 -s -r -p "Press any key to continue"

pkill iperf
