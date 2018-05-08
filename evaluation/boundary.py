# -*- coding: utf-8 -*-

class Sentences:
    def __init__(self, gold, segmentation):
        self.sentences = []
        self.parse(gold, segmentation)
    
    def parse(self, gold, segmentation):
        assert len(gold) == len(segmentation)
        for i in range(0,len(gold)):
            s = Sentence(gold[i], segmentation[i])
            self.sentences.append(s)
    
    def boundary_score(self):
        correct = 0
        totalSeg = 0
        totalGold = 0 
        for sentence in self.sentences:
            correct += sentence.boundary_score()
            totalSeg += sentence.boundary_count(sentence.segmentation)
            totalGold += sentence.boundary_count(sentence.gold)
        return [correct, totalSeg, totalGold]    

class Sentence:
    def __init__(self, gold, segmentation):
        self.gold = []
        self.segmentation = [] 
        self.parse(gold,segmentation)
    
    def parse(self, s1, s2):
        s1_unseg = s1.replace(" ","")
        s2_unseg = s2.replace(" ","")
        assert len(s1_unseg) == len(s2_unseg)

        self.gold = self.create_list(s1, s1_unseg)
        self.segmentation = self.create_list(s2, s2_unseg)

        assert len(self.gold) != len(self.segmentation)
        self.create_alignment() 
        
    def create_list(self, s, s_unseg):
        index = 0
        order = 1
        s_list = []
        for i in range(0,len(s_unseg)):
            assert s_unseg[i] == s[index]
            if index +1 < len(s) and s[index+1] == " ": #if the next thing is a boundary
                t = Token(s_unseg[i], True, order)
                order+=1
                index+=2 #keeps aligned
            else:
                t = Token(s_unseg[i], False, order)
                index+=1
            s_list.append(t)
        return s_list
    
    def create_alignment(self):
        for i in range(0,len(self.gold)):
            self.gold[i].alignedToken = self.segmentation[i]
            self.segmentation[i].alignedToken = self.gold[i]

    def boundary_score(self):
        score = 0
        for i in range(0,len(self.gold)):
            if self.gold[i].boundary and self.segmentation[i].boundary:
                score+=1
        return score
    
    def boundary_count(self, s1):
        score = 0
        for i in range(0, len(s1)):
            if s1[i].boundary:
                score+=1
        return score

class Token:
    def __init__(self, token, boundary, order):
        self.token = token
        self.alignedToken = None #this receives a pointer (not being used for the moment)
        self.boundary = boundary #boolean
        self.order = order #id for finding the tokens (e.g. word1 = 1, word2 = 2)

def main():
    pass

if __name__ == '__main__':
    main()