#!/usr/bin/env python -W ignore::DeprecationWarning

### IMPORTS
import sys, librosa, os
sys.path.append('waveglow/')
import numpy as np
import torch

from hparams import create_hparams
from model import Tacotron2
from layers import TacotronSTFT, STFT
from audio_processing import griffin_lim
from train import load_model
from text import text_to_sequence
from denoiser import Denoiser
from data_utils import TextMelLoader, TextMelCollate
from torch.utils.data import DataLoader

from train import load_model, prepare_dataloaders
from text import text_to_sequence
import argparse

class Sentence():
    def __init__(self, alignment, id_wav, text, src_len, tgt_len, audio=None):
        self.id_wav = id_wav
        self.text = text
        self.alignment = alignment.cpu()
        self.src_len = src_len.cpu().item()
        self.tgt_len = tgt_len.cpu().item()
        self.audio = audio
    
    def print_sentence(self):
        print(self.id_wav)
        print(self.text)
        print(self.src_len, self.tgt_len)

class Corpus():
    def __init__(self):
        self.corpus = dict()

    def add_sentence(self, sentence, id):
        assert id not in self.corpus.keys()
        self.corpus[id] = sentence
    
    def get_sentence(self, id):
        return self.corpus[id]
    
    def items(self):
        return self.corpus.values()


def load_waveglow(waveglow_path):
    waveglow = torch.load(waveglow_path)['model']
    waveglow.cuda().eval()#.half()
    for k in waveglow.convinv:
        k.float()
    denoiser = Denoiser(waveglow)
    return waveglow

def write_audio(mel_outputs_postnet, waveglow, f_name, rate):
    '''
    link for audio functions:
    https://musicinformationretrieval.com/ipython_audio.html
    '''
    with torch.no_grad():
        audio = waveglow.infer(mel_outputs_postnet, sigma=0.666)
        audio = audio[0].data.cpu().numpy() 
        librosa.output.write_wav(f_name, audio,rate)

def generate_example(text, model):
    sequence = np.array(text_to_sequence(text, ['english_cleaners']))[None, :]
    sequence = torch.autograd.Variable(
    torch.from_numpy(sequence)).cuda().long()
    return model.inference(sequence)

def load_data(hparams):
    trainset = TextMelLoader(hparams.training_files, hparams)
    valset = TextMelLoader(hparams.validation_files, hparams)
    collate_fn = TextMelCollate(hparams.n_frames_per_step)
    train_loader = DataLoader(trainset, num_workers=1, shuffle=False,
                              batch_size=hparams.batch_size, pin_memory=False,
                              drop_last=True, collate_fn=collate_fn)

    val_loader = DataLoader(trainset, num_workers=1, shuffle=False,
                              batch_size=hparams.batch_size, pin_memory=False,
                              drop_last=True, collate_fn=collate_fn)
    return train_loader, val_loader, [trainset, valset], collate_fn

def write_matrices(corpus, output_folder):
    def line_to_str(tensor): #tensor -> numpy
            matrix = torch.Tensor.numpy(tensor.detach().cpu())
            values = []
            for i in range(len(matrix)):
                values += [str(matrix[i].item())]
            return "\t".join(["."] + values)

    for sentence in corpus.items():
        f_name = output_folder + "/" + sentence.id_wav.split("/")[-1].replace("wav","txt")
        with open(f_name,"w") as matrix:
            header = "\t".join("." + sentence.text) + "\n" 
            matrix.write(header)
            alignment = sentence.alignment[:sentence.tgt_len,:sentence.src_len]
            for i in range(len(alignment)):
                line = alignment[i]
                str_line = line_to_str(line)
                matrix.write(str_line + "\n")

def write_audios(corpus, output_folder):
    waveglow = load_waveglow(args.waveglow_path)
    for sentence in corpus.items():
        f_name =  "/".join([output_folder,sentence.id_wav.split("/")[-1]])
        mel_outputs_postnets = sentence.audio.unsqueeze(0)[:,:,:sentence.tgt_len] #removes padding
        write_audio(mel_outputs_postnets, waveglow, f_name, hparams.sampling_rate)

def check_folder(directory):
    #creates output directory if it doesnt exist yet
    try:
        os.stat(directory)
    except:
        os.makedirs(directory)

def write_textgrid(textgrid, sentence, output_folder):
    pass

def write_textgrids(corpus, output_folder):
    for sentence in corpus.items():
        textgrid = sentence.generate_textgrid()
        write_textgrid(textgrid, sentence, output_folder)

def generate(args):
    checkpoint_path = args.checkpoint_path
    check_folder(args.output_folder)

    #1 LOAD TACOTRON
    hparams = create_hparams()
    hparams.sampling_rate = 22050
    model = load_model(hparams)
    model.load_state_dict(torch.load(checkpoint_path)['state_dict'])
    _ = model.cuda().eval()#.half()

    if args.example: #2 GENERATE THE MEL SPECS FROM POSTNET FOR ONE EXAMPLE

        text = "I maybe went to far with my text to speech examples but I CANNOT STOP AND I WILL NOT STOP"
        mel_outputs, mel_outputs_postnet, _, alignments = generate_example(text, model)
        
        #3 LOAD WAVEGLOW
        waveglow = load_waveglow(args.waveglow_path)

        #4 SAVE THE AUDIO(s)
        audio_name = "test.wav"
        write_audio(mel_outputs_postnet, waveglow, audio_name, hparams.sampling_rate)

    else: #2 GENERATE THE MEL SPECS AND ATTENTION FROM THE TRAINING CORPUS

        hparams.batch_size = 2 #a bug in the architecture forces me to use a batch > 1 for decoding
        train_loader, val_loader, sanity_check, _ = load_data(hparams)
        train_items = sanity_check[0].audiopaths_and_text
        val_items = sanity_check[1].audiopaths_and_text

        index = 0
        corpus = Corpus()       
        counter = args.save_interval

        #MAIN LOOP
        sets = [train_loader, val_loader] if args.valid else [train_loader]
        for data_loader in sets:
            for i, batch in enumerate(data_loader):
                print("Batch number: ", i)
                x, _ = model.parse_batch(batch)
                text_padded, input_lengths, mel_padded, max_len, output_lengths = x
                _, mel_outputs_postnet, _, alignments = model(x)
                texts = [train_items[index], train_items[index+1]]
                #ids are sorted considering descending order (check data_utils.py TextMelCollate call)
                texts.sort(key=lambda x: len(x[1]), reverse=True)
                for j in range(hparams.batch_size):
                    id_w, text = texts[j][0], texts[j][1]
                    src_size, tgt_size = input_lengths[j], output_lengths[j]
                    audio = mel_outputs_postnet[j] if args.audios else None
                    sentence = Sentence(alignments[j], id_w, text, src_size, tgt_size, audio=audio)
                    corpus.add_sentence(sentence, index+j)
                index += hparams.batch_size
                counter -= 1
                #SAVING THE INFORMATION
                if counter == 0: 
                    print("Saving checkpoint! Saving ", args.save_interval, " matrices.")
                    #3 WRITING MATRICES
                    write_matrices(corpus, args.output_folder)
                    #4 GENERATING AUDIOS
                    if args.audios:
                        write_audios(corpus, args.output_folder)
                    corpus = Corpus() #wipes the information to free memory
                    counter = args.save_interval
           

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-folder', type=str, default="test", help='folder for outputing audios/matrices')
    parser.add_argument('--checkpoint-path', type=str, default="tacotron2_statedict.pt", help='tacotron model .pt')
    parser.add_argument('--waveglow-path', type=str, default="waveglow/waveglow_256channels_ljs_v2.pt", help='waveglow model .pt')
    parser.add_argument('--example', default=False, action='store_true', help='generates one single audio example, check code')
    parser.add_argument('--valid', default=False, action='store_true', help='generates the matrices for the validation set as well')
    parser.add_argument('--audios', default=False, action='store_true', help='synthesizes the audio, together with the attention matrices')
    parser.add_argument('--save-interval', type=int, default=20, help='For controlling GPU memory usage (when too large, the memory will explode)')
    #full precision: it takes 47 batches for memory to explore with a 12GB GPU on default tacotron model
    args = parser.parse_args()
    generate(args)