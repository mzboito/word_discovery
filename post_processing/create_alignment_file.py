import sys, codecs, glob
import utils
from segment import get_soft2hard_parser
from soft2hard import get_distributions
'''
je sais lire la langue mbochi ||| phn6 phn35 phn24 phn57 phn22 phn55 phn48 phn27 phn31 phn35 phn6 phn55 phn8 phn44 phn30 phn41
becomes
0-0 2-1 0-2 0-3 1-4 4-5 1-6 3-7 2-8 2-9 0-10 4-11 5-12 5-13 5-14 5-15
'''



def create_aligned_sequence(src_index, tgt_index):
    assert len(src_index) == len(tgt_index)
    alignments = []
    for i in range(len(src_index)): #words
        s_i = src_index[i]
        for t_i in tgt_index[i]: #list of phones
            #for t_i in segmentation: #index of every phone
            a = str(s_i)+"-"+str(t_i)
            alignments.append(a)
    return alignments


def run(args):
    sentencesPaths = glob.glob(args.matrices_prefix+"*.txt") 
    if args.individual_files and args.output_folder: #segmentation in individual files (with ID)
        files_output_list = utils.read_file(args.individual_files)
        folder = args.output_folder if args.output_folder[-1] == '/' else args.output_folder + '/'
        silence_dict = utils.read_lab_files(args.silence) if args.silence else None
        assert len(files_output_list) == len(sentencesPaths)

        for index in range(1, len(sentencesPaths)+1):
            file_path = utils.get_path(index, sentencesPaths, transformer=args.transformer, pervasive=args.pervasive)
            sentence_id = files_output_list[index-1].split("/")[-1]
            sil_list = silence_dict[sentence_id] if args.silence else None
            matrix = utils.read_matrix_file(file_path)
            discovered_words, discovered_translation, tgt_order, src_order = get_distributions(matrix, args.target, lab_lst=sil_list)
            tgt_order = tgt_order[:-1] #removes </S>
            src_order = src_order[:-1]
            final_line = create_aligned_sequence(src_order, tgt_order)
            file_name = sentence_id + ".align" 
            utils.write_output(" ".join(final_line), folder + file_name)
    
    elif args.output_folder: #segmentation in individual files (without ID)
        folder = args.output_folder if args.output_folder[-1] == '/' else args.output_folder + '/'
        silence_dict = utils.read_lab_files(args.silence) if args.silence else None
        for sentencePath in sentencesPaths:
            sentence_id = ".".join(sentencePath.split("/")[-1].split(".")[:-1])
            sil_list = silence_dict[sentence_id] if args.silence else None
            matrix = utils.read_matrix_file(sentencePath)
            discovered_words, discovered_translation, tgt_order, src_order = get_distributions(matrix, args.target, lab_lst=sil_list)
            tgt_order = tgt_order[:-1] #removes </S>
            src_order = src_order[:-1]
            final_line = create_aligned_sequence(src_order, tgt_order)
            file_name = sentencePath.split("/")[-1] + ".align"
            utils.write_output(" ".join(final_line), folder + file_name)

    
if __name__ == "__main__":
    parser = get_soft2hard_parser()
    args = parser.parse_args()
    if len(sys.argv) < 3 or not args.matrices_prefix:
        parser.print_help()
        sys.exit(1)
    '''if args.silence and not args.individual_files:
        raise Exception("SILENCE OPTION ONLY WORKS WITH INDIVIDUAL-FILES PARAMETER!")'''
    run(args)