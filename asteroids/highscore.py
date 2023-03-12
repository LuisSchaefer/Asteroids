from os import path


class Highscore:
    def __init__(self, file) -> None:
        self.data = file
        self.dir = path.dirname(__file__)
        with open(path.join(self.dir, file), 'r') as f:
            try:
                self.highscore = int(f.read())
            except:
                self.highscore = 0
      
    def checkScore (self, score):
       if score > self.highscore:
            self.setNewHighScore(score)
            return True
       else:
           return False
    
    def setNewHighScore(self, score):
            self.highscore = score
            with open(path.join(self.dir, self.data), 'w') as f:
                f.write(str(score))

    def getHighScore (self):
        return self.highscore
