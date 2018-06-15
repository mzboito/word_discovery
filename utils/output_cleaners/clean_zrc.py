import sys

class Evaluation:
    def __init__(self, name, precision, recall, fscore):
        self.name = name
        self.precision = precision
        self.recall = recall
        self.fscore = fscore

class Metric:
    def __init__(self, name, mean, std, m_min, m_max):
        self.name = name
        self.mean = mean
        self.std = std
        self.min = m_min
        self.max = m_max
    
    def format(self):
        self.mean = self.mean * 100
        self.min = self.min * 100
        self.max = self.max * 100

def clean_line(s_line):
    while("  " in s_line):
        s_line = s_line.replace("  "," ")
    return s_line.split(" ")

def parse_metrics(m_list, index, name):
    info = []
    for j in range(0, 3):
        segment = clean_line(m_list[index+j])
        m = Metric(segment[0], float(segment[1]), float(segment[2]), float(segment[3]), float(segment[4]))
        m.format()
        info.append(m)
    return Evaluation(name, info[0], info[1], info[2])

def parse_boundary(boundary_file):
    lines = [line.strip() for line in open(boundary_file, "r")]
    for i in range(len(lines)):
        if lines[i] == "boundary total":
            return parse_metrics(lines, i+6,"Boundary")
    return None

def parse_t(t_file):
    evals = []
    lines = [line.strip() for line in open(t_file, "r")]
    for i in range(len(lines)):
        if lines[i] == "token total":
            evals.append(parse_metrics(lines, i+6, "Token"))
        elif lines[i] == "type total":
            evals.append(parse_metrics(lines, i+6, "Type"))
            return evals
    return None

def parse_files(boundary_file, t_file):
    t_out = parse_t(t_file)
    b_out = parse_boundary(boundary_file)
    return [t_out[0], t_out[1], b_out]

def write_output(output_prefix, output_list):
    with open(output_prefix, "w") as output_file:
        output_file.write("Evaluation\tP\tR\tF\n")
        print "Evaluation\tP\tR\tF"
        for evalu in output_list:
            output_file.write("%s\t%2.2f\t%2.2f\t%2.2f\n" % (evalu.name, evalu.precision.mean, evalu.recall.mean, evalu.fscore.mean))
            print "%s\t%2.2f\t%2.2f\t%2.2f" % (evalu.name, evalu.precision.mean, evalu.recall.mean, evalu.fscore.mean)

def main():
    '''if len(sys.argv) < 4:
        print "USAGE: python clean_zrc.py BOUNDARY TOKEN-TYPE output-prefix\n"
    '''
    boundary_file = "boundary"#sys.argv[1]
    t_file = "token_type"#sys.argv[2]
    output_prefix = "RESULTS"#sys.argv[3]

    output_list = parse_files(boundary_file, t_file)
    write_output(output_prefix, output_list)


if __name__ == '__main__':
    main()