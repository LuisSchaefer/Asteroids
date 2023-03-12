from os import path
from operator import itemgetter
import json

class Highscore:
    def __init__(self, file) -> None:
        self.data = file
        self.dir = path.dirname(__file__)
      
        with open (path.join(file), 'r') as f:
            try:
                self.highscore = json.load(f)

            except:
                self.highscore = [
                    ('none', 0)
                ]
    def checkScore (self, name, score):
       if score > self.highscore:
            self.setNewHighScore(name, score)
            return True
       else:
           return False
    
    def setNewHighScore(self, name, score):
        self.highscore.append((name, score))
        self.highscore = sorted(self.highscore, key = itemgetter(1), reverse= True)[:5]
        with open(self.data, 'w') as f:
            json.dump(self.highscore, f)

    def getHighestScore (self):
        return self.highscore[0][1]
    
    def getAllHighScores(self):
        output = str(self.highscore[0][0]) + "\t" + str(self.highscore[0][1]) + "\n" + str(self.highscore[1][0]) + "\t" + str(self.highscore[1][1]) + "\n" + str(self.highscore[2][0]) + "\t" + str(self.highscore[2][1]) + "\n" + str(self.highscore[3][0]) + "\t" + str(self.highscore[3][1]) + "\n" + str(self.highscore[4][0]) + "\t" + str(self.highscore[4][1])
        return output
            
