### Steps to run the testbeds

1.Run mininet to create topo
    ```$ sudo python lb1in2out.py```

2.Install static rules

    ```$ ./ovs_config.sh``` 

3.Start controller
    
    ```$ ryu-manager controller.py```

4.At mininet open up two terminals at h1 and h2, respectively
    ``` $mininet> xterm h1 h2 ```

5.Run traffic generator and sink at h1 and h2 (10 flows e.g.), respectively
    ``` (h2) $ ./flow-sink.sh 10 ```
    ``` (h1) $ ./flowgen.sh 10 ``` 
