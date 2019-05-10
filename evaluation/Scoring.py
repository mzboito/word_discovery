# -*- coding: utf-8 -*-


class Sentences:
    def __init__(self, gold, segmentation):
        assert len(gold) == len(segmentation)
        self.sentences = [Sentence(gold[i], segmentation[i]) for i in range(len(gold))]
    
    def boundary_score(self):
        correct = 0.0
        totalSeg = 0.0
        totalGold = 0.0
        for sentence in self.sentences:
            correct += sentence.boundary_hits() 
            totalSeg += Sentence.boundary_count(sentence.segmentation)
            totalGold += Sentence.boundary_count(sentence.gold)
        print("boundary")
        print(correct, totalSeg, totalGold)
        return [correct, totalSeg, totalGold] 

    def tokens_score(self):
        correct = 0.0
        totalSeg = 0.0
        totalGold = 0.0
        for sentence in self.sentences:
            correct += sentence.token_hits()
            totalSeg += Sentence.token_count(sentence.segmentation)
            totalGold += Sentence.token_count(sentence.gold)
        print("tokens")
        print(correct, totalSeg, totalGold)
        return [correct, totalSeg, totalGold] 
    
    def types_score(self):
        seg, gold = Sentences.get_types(self.sentences)
        correct = len(Sentences.intersection(seg, gold)) * 1.0
        totalSeg = len(seg) *1.0
        totalGold = len(gold) *1.0
        print("types")
        print(correct, totalSeg, totalGold)
        return [correct, totalSeg, totalGold] 


    @staticmethod
    def intersection(lst1, lst2):
        return [t for t in lst1 if t in lst2]

    @staticmethod
    def get_types(lst):
        gold = list()
        seg = list()
        for sentence in lst:
            gold += sentence.get_tokens(sentence.gold)
            seg += sentence.get_tokens(sentence.segmentation)
        return list(set(seg)), list(set(gold))
    


class Sentence:
    def __init__(self, gold, segmentation):
        self.gold = list()
        self.segmentation = list()
        self.parse(gold,segmentation)
    
    def parse(self, s1, s2):
        s1_unseg = s1.replace(" ","")
        s2_unseg = s2.replace(" ","")
        assert len(s1_unseg) == len(s2_unseg)
        self.gold = self.create_list(s1, s1_unseg) #gold
        self.segmentation = self.create_list(s2, s2_unseg)
        assert len(self.gold) == len(self.segmentation)
        for i in range(len(self.gold)):
            self.gold[i].alignedChar = self.segmentation[i]

    def create_list(self, s, s_unseg):
        index = 0
        order = 1
        chars_list = list()
        for i in range(len(s_unseg)):
            assert s_unseg[i] == s[index]
            if ((index + 1) < len(s)) and s[index+1] == " ": #if the next thing is a boundary
                chars_list += [Character(s_unseg[i], True, order)] #add last token in the char list
                order += 1 #next id
                index += 2 #jumps the boundary
            else:
                chars_list += [Character(s_unseg[i], False, order)]
                index+=1
        return chars_list 

    def token_hits(self): #from pierre's code
        hits = 0
        left_boundary = True
        for i in range(len(self.gold)):
            if self.gold[i].boundary and self.segmentation[i].boundary:
                if left_boundary:
                    hits += 1
                left_boundary = True
            elif (self.gold[i].boundary and not self.segmentation[i].boundary) or (not self.gold[i].boundary and self.segmentation[i].boundary):
                left_boundary = False
        if left_boundary:
            hits += 1
        return hits

    def boundary_hits(self):
        return sum(1 for element in self.gold if element.boundary and element.alignedChar.boundary)


    def _to_string(self, lst):
        return "".join([char.string if not char.boundary else char.string + " " for char in lst])
    @staticmethod
    def token_count(lst):
        return len(Sentence.get_tokens(lst))

    @staticmethod
    def boundary_count(lst):
        return sum(1 for element in lst if element.boundary)

    @staticmethod
    def get_tokens(lst):
        tokens = [""]
        for char in lst:
            tokens[-1] += char.string
            if char.boundary: #last one from a token
                tokens.append("")
        return tokens

class Character:
    def __init__(self, character, boundaryChar, order):
        self.string = character
        self.alignedChar = None #alignment character
        self.boundary = boundaryChar #boolean, if the character is the token last element
        self.order = order #id for finding the tokens (e.g. word1 = 1, word2 = 2)


