
ryu-manager --observe-links simple_switch_13.py topology_discovery.py
ryu-manager my_controller.py
ovs-ofctl add-flow switch1 "table=0, priority=10, dl_type=0x0800, nw_src=10.0.0.1, nw_dst=10.0.0.2, in_port=1, actions=output:2, max-rate=3000000"
ovs-ofctl add-flow switch1 "table=0, priority=10, dl_type=0x0800, dl_src=00:00:00:00:00:01, dl_dst=00:00:00:00:00:02, in_port=1, actions=output:2, max-rate=2000000"
