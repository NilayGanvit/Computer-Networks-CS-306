import subprocess
import time

host1 = 'h1'
host2 = 'h2'

# run server program on host2
subprocess.Popen(['mnexec', '-a', host2, 'python', 'server.py'])

# wait for server to start up
time.sleep(1)

# run client program on host1
start_time = time.time()
num_packets = 10
rtt_sum = 0
for i in range(num_packets):
    output = subprocess.check_output(['mnexec', '-a', host1, 'python', 'client.py'])
    end_time = time.time()
    rtt = end_time - start_time
    rtt_sum += rtt
    print('Packet %d: RTT = %f' % (i+1, rtt))
    start_time = time.time()

# compute average RTT and use as estimate of link cost
link_cost = rtt_sum / num_packets
print('Link cost: %f' % link_cost)
