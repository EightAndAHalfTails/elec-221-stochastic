import random
import timeit
from collections import defaultdict
ITER = 1000

class Circuit:
  def __init__(self, i=[], o=[], g=dict()):
    self.inputs = i # list of strings containing input node names
    self.outputs = o # list of strings containing output node names
    self.gates = g # dictionary keyed by output of all gates in the circuit
  def printout(self):
    print "inputs", self.inputs
    print "outputs", self.outputs
    print "gates:"
    [x.printout() for x in self.gates.values()]

class Gate:
  def __init__(self, name, op, ins, out):
    self.name = name
    self.operation = op
    self.inputs = ins
    self.output = out
  def printout(self):
    print "name: {}, op: {}, {} -> {}".format(self.name, self.operation, self.inputs, self.output)

def parse(filename):
  gates = dict()
  with open(filename) as f:
    for l in f.readlines():
      l = l.replace('\n', '')
      if l == "":
        continue
      if l[:2] == "//":
        continue
      command = l.split(" ")[0].lower()
      if command == "module":
        pass
      elif command == "input":
        inputs = l.replace("input ", "")
        inputs = inputs.replace(';', '').replace(" ", "") # strip the semicolon and whitespace
        inputs = inputs.split(',') #extract input tokens
      elif command == "output":
        outputs = l.replace("output ", "")
        outputs = outputs.replace(';', '').replace(" ", "") # strip the semicolon and whitespace
        outputs = outputs.split(',') #extract output tokens
      elif command == "wire":
        pass
      elif command in ["nand", "and", "or", "nor", "xor", "xnor", "not"]:
        #print l
        connections = l.split('(')[1].replace(" ", "").replace(");", "").split(',')
        out = connections[0]
        ins = connections[1:]
        name = l.split(" ")[1]
        gates[out] = Gate(name, command, ins, out)
      else:
        pass
        #print "cannot parse line: " + l
  return Circuit(inputs, outputs, gates)

def evaluate(node, circuit, inputval):
  if node in circuit.inputs:
    return inputval[node]
  #circuit.printout()
  #print node
  gate = circuit.gates[node] #find gate whose output is node. O(1)
  inputs = [evaluate(i, circuit, inputval) for i in gate.inputs] # get values at input
  if gate.operation == "and":
    return all(inputs)
  elif gate.operation == "nand":
    return not all(inputs)
  elif gate.operation == "or":
    return any(inputs)
  if gate.operation == "nor":
    return not any(inputs)
  elif gate.operation == "xor":
    # true if no. of Trues is odd
    return inputs.count(True)%2 == 1
  elif gate.operation == "xnor":
    # true if all inputs are the same
    return all(inputs) or not any(inputs)
    #return inputs.count(True) == 0 or inputs.count(False) == 0
  elif gate.operation == "not":
    return not inputs[0]
  else:
    print "Error at gate", gate.name
    return False

def getVNFaulty(circuit): #appends each gate in the circuit with an xor gate
  faulty_gates = dict()
  error_ins = []
  for ideal_gate in circuit.gates.values():
    intermed_node = ideal_gate.name + "__inter__"
    faulty_gate = Gate(name = ideal_gate.name,
                       op = ideal_gate.operation,
                       ins = ideal_gate.inputs,
                       out = intermed_node)
    error_name = ideal_gate.name + " VNE"
    xor_gate = Gate(name = error_name,
                    op = "xor",
                    ins = [intermed_node, error_name],
                    out = ideal_gate.output)
    error_ins.append(error_name)
    faulty_gates[faulty_gate.output] = faulty_gate
    faulty_gates[xor_gate.output] = xor_gate
  faulty_circuit = Circuit(circuit.inputs + error_ins, circuit.outputs, faulty_gates)
  return faulty_circuit

def exhaust(circuit):
  inputval = dict()
  for iteration in range(2**len(circuit.inputs)):
    input_vector = [(iteration>>i)&1 for i in xrange(len(circuit.inputs)-1,-1,-1)]
    for i in range(len(circuit.inputs)):
      inputval[circuit.inputs[i]] = input_vector[i]==1
    print input_vector, [evaluate(n, circuit, inputval) for n in circuit.outputs]

def getNonBernoulliSequences(circuit):
  inputval = dict()
  for input_node in circuit.inputs:
    prob = 0.5 #float(raw_input("Enter probability of {}: ".format(input_node)))
    num_ones = int(prob*ITER)
    non_ber = [True]*num_ones + [False]*(ITER-num_ones)
    random.shuffle(non_ber)
    inputval[input_node] = non_ber
  return inputval

def findReliabilities(filename):
  ideal = parse(filename)
  faulty = getVNFaulty(ideal)
  inputval = getNonBernoulliSequences(faulty)
  outputs_same = defaultdict(list)
  for i in range(ITER):
    inputvec = {x:inputval[x][i] for x in inputval.keys()}
    for output_node in ideal.outputs:
      ideal_output = evaluate(output_node, ideal, inputvec)
      faulty_output = evaluate(output_node, faulty, inputvec)
      outputs_same[output_node].append(ideal_output == faulty_output)
  for n, v in outputs_same.iteritems():
    pass
    #print "reliability of {} is {}".format(n, 1.0*v.count(True)/ITER)
  # Complexity = O(ITER * len(circuit.outputs) * len(circuit.gates))

reps = 1
#time = timeit.timeit('findReliabilities("C:\Users\Eight_000\Desktop\c17.v")', setup = "from __main__ import findReliabilities", number = reps)/reps
time = timeit.timeit('findReliabilities("C:\Users\Eight_000\Desktop\c432.v")', setup = "from __main__ import findReliabilities", number = reps)/reps
print time
