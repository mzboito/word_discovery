import argparse, sys, glob

import soft2hard, utils
from praatio import tgio
from pprint import pprint
import wave
import contextlib


def create_textgrid_obj(textgrid_list):
    new_dict = dict()
    keys = ["ORT"] #, "KAN", "MAU"]
    for key in keys:
        new_dict[key] = tgio.TextgridTier(key, [], 0.0, textgrid_list[-1].end)
        new_dict[key].tierType = tgio.INTERVAL_TIER

    for element in textgrid_list: 
        for key in keys:
            new_dict[key].entryList.append(element)
        '''try:
            phonetic = element.phonetic
            phones_list = element.phones_list
        except AttributeError:
            phonetic = element.interval
            phones_list = [element.interval]'''
    
        '''new_dict["KAN"].entryList.append(phonetic)
        new_dict["MAU"].entryList += phones_list'''

    textgrid_obj = tgio.Textgrid()
    for key in keys:
        textgrid_obj.addTier(new_dict[key])
    return textgrid_obj

def get_audio_duration(f_name):
    with contextlib.closing(wave.open(f_name,'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
            return duration

def fix_header(matrix):
    if len(matrix[0]) < len(matrix[1]):
        matrix[0].append("</S>")

def extract(args):
    f_names = glob.glob(args.matrices_folder+"/*.txt")
    textgrids = list()
    for f_name in f_names:
        matrix = utils.read_matrix_file(f_name)
        fix_header(matrix)
        id = f_name.split("/")[-1]
        print(id)
        f_name = args.audio_folder + "/" + id.replace(".txt",".wav")
        duration = get_audio_duration(f_name)
        ratio = duration/((len(matrix)-1)*0.01)

        discovered_frames, aligned_chars, _, _ = soft2hard.get_distributions(matrix, eos=False)
        assert len(discovered_frames) == len(aligned_chars)
        init = 0

        frames = list()
        for i in range(len(discovered_frames)):
            end = init + len(discovered_frames[i])
            a = tgio.Interval((init*0.01)*ratio, (end*0.01)*ratio, "".join(aligned_chars[i]))
            frames.append(a)
            #print((init*0.01)*ratio, (end*0.01)*ratio, aligned_chars[i])
            init = end
        obj = create_textgrid_obj(frames)
        textgrids.append((id, obj))
    
    for f_name, obj in textgrids:
        output_file = args.output_folder + "/" + f_name.replace(".txt",".TextGrid")
        obj.save(output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--matrices-folder', type=str, nargs='?', help='folder containing the attention matrices')
    parser.add_argument('--audio-folder', type=str, nargs='?', help='folder containing the audios')
    parser.add_argument('--output-folder', type=str, nargs='?', help='folder saving the textgrids')
    args = parser.parse_args()
    extract(args)