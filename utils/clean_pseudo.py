import sys
import glob


def write_output(o_file, units):
    with open(o_file, "w") as output_file:
        output_file.write(" ".join(units) + '\n')


def read_input(i_file):
    with open(i_file,"r") as units_file:
            units = []
            for unit in units_file:
                unit = unit.strip("\n").split(" ")[2]
                units.append(unit)
    return units


def main():
    input_files = glob.glob(sys.argv[1] + "*")
    for i_file in input_files:
        units = read_input(i_file)
        write_output(i_file + ".clean", units)


if __name__ == '__main__':
    main()