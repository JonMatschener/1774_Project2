# 1774_Project3

Code Modifications

To implement breaker functionality, modifications were made primarily within the Circuit and PowerFlow classes. An in_service attribute was introduced for both transmission lines and transformers, allowing each component to be dynamically enabled or disabled. Additional methods were added to the Circuit class to control breaker states:

open_line(name) / close_line(name)
open_transformer(name) / close_transformer(name)

The Ybus construction process was updated so that only in-service elements contribute to the system admittance matrix. When a breaker is opened, the corresponding element is excluded from the Ybus stamping process, effectively removing its electrical connection from the network.

A key enhancement was the addition of an island detection routine within the PowerFlow solver. This routine uses a graph traversal method (breadth-first search) to verify that all buses remain connected to the slack bus before solving. If any buses are disconnected, the solver raises an error and prevents execution. This avoids numerical instability caused by singular admittance matrices and ensures that only physically valid systems are analyzed.

How To Use The Code

1. Download all files in project.

2. Open test_case69.py, test_case69_breaker.py, test_case69,transformerbreaker.py.
   a. Run test_case69.py for normal circuit operation and results.
   b. Run test_case69_breaker.py to see operation with a transmission line breaker open.
   c. Run test_case69,transformerbreaker.py to see operation with a transformer breaker open.

3. In either breaker case, edit "c.open_line("")" with the name of a breaker or transformer to see varying results.

Example Case 1 – Normal Operation
The first test case uses the standard Case 6.9 system with all breakers closed. The network is fully connected, allowing power to flow through all transmission paths.

Expected behavior:

•	Stable voltage profile across all buses 

•	Converged Newton-Raphson solution 

•	Power flows distributed across all lines 

 
Example Case 2 – Transmission Line Breaker Open 
In the second test case, the breaker on transmission line L1 is opened. This removes the connection between Bus Five and Bus Four.
<img width="391" height="174" alt="image" src="https://github.com/user-attachments/assets/4821fd32-9286-4178-9742-2ea8b66a49f1" />


Effects:

•	Modified Ybus matrix 

•	Reduced network connectivity 

•	Redistribution of power flow 

•	Possible voltage deviations at affected buses 

Expected Output (Results Below Verified in Power World):

=== BREAKER OPEN (L1) ===

One: V=1.0000, delta=0.0000

Two: V=0.7750, delta=-19.6376

Three: V=1.0500, delta=13.6484

Four: V=1.0228, delta=11.4049

Five: V=0.9326, delta=-4.6812

Mathematically, removing the line eliminates its admittance contribution. This demonstrates how breaker operations impact system behavior and validates the simulator’s ability to model real-world switching conditions.
 
Example Case 3 – Transformer Breaker Open
In the third case, the breaker for transformer T1 is opened. This removes the connection between Bus One and Bus Five. 
 <img width="414" height="190" alt="image" src="https://github.com/user-attachments/assets/1861e96b-530d-4d80-b93c-4670247e9d27" />

The expected output from removing either transformer results in a message displaying:

“ValueError: System is islanded (not all buses connected to slack). Power flow cannot be solved.”
This is different from that of Power World because Power World automatically solves the issue and continues to run the circuit.
