import os
import pygame
import random
import numpy as np
from NN import NeuralNetwork



pygame.init()

#-----------------------Global-variables--------------------------------------------------------------

global RUNING
RUNING=True
POPULATION=50
BG_COLOR=(200,125,125)
GAME_SPEED=60
GENERATION_NUMBER=0
MUTTATES=0

#----------- loading images-----------------------------------------------------------------------------------

BIRD=[pygame.image.load("assets\\Bird\\Bird1.png"),pygame.image.load("assets\\Bird\\Bird1.png")]
LARGECAC=[pygame.image.load("assets\\Cactus\\LargeCactus1.png"),pygame.image.load("assets\\Cactus\\LargeCactus2.png"),pygame.image.load("assets\\Cactus\\LargeCactus3.png")]
SMALLCAC=[pygame.image.load("assets\\Cactus\\SmallCactus1.png"),pygame.image.load("assets\\Cactus\\SmallCactus2.png"),pygame.image.load("assets\\Cactus\\SmallCactus3.png")]

DUCK=[pygame.image.load("assets\\Dino\\DinoDuck1.png"),pygame.image.load("assets\\Dino\\DinoDuck2.png")]
JUMP=pygame.image.load("assets\\Dino\\DinoJump.png")
RUN=[pygame.image.load("assets\\Dino\\DinoRun1.png"),pygame.image.load("assets\\Dino\\DinoRun2.png")]
CLOUD=pygame.image.load("assets\\Other\\Cloud.png")
GROUND=pygame.image.load("assets\\Other\\Track.png")

#----------------------window--------------------------------------------------

WINDO_W=1150
WINDO_H=600

win=pygame.display.set_mode((WINDO_W,WINDO_H))
pygame.display.set_caption("dino ai made by ramzey")



#-------------------Classes----------------------------------------------------------

class Dino():
    #static attributs
    standard_vel=8
    standard_y=300
    standard_x=50

    #Constractor
    def __init__(self) -> None:
        self.x=self.standard_x
        self.y=self.standard_y 
        self.alive=True
        self.jumping=False
        self.ducking=False
        self.running=True
        self.duck_imgs=DUCK
        self.jump_imgs=JUMP
        self.run_imgs=RUN
        self.brain=NeuralNetwork()
        self.currentimg=self.run_imgs[0]
        self.vel=self.standard_vel
        self.hitbox=pygame.Rect(self.x,self.y,self.currentimg.get_width(),self.currentimg.get_height())
        self.imgindex=0
        self.score=0
    
    #class methods
    def run(self):
        #change image by the time
        self.currentimg=self.run_imgs[self.imgindex//5]
        self.imgindex+=1
        if(self.imgindex // 5 == 2):
            self.imgindex=0
    def jump(self):
        #change image
        self.currentimg=self.jump_imgs

        #move the dino up 0.8 pixels every frame
        self.y-=self.vel*4
        self.hitbox.y=self.y
        self.vel-=0.8

        #if the dino fall in the ground again 
        if self.standard_vel < -self.vel:
            self.jumping=False
            self.running=True
            self.vel=self.standard_vel

    def duck(self):
        
        self.currentimg=self.duck_imgs[self.imgindex // 5]
        self.y=self.standard_y + 30
        self.imgindex+=1
        if self.imgindex // 5 == 2:
            self.imgindex=0     

    def move(self,obs):
        if self.running:
            self.run()
        if self.jumping:
            self.jump()
        if self.ducking:
            self.duck()


        

        #decision made by dino neural network base on inputs(the height of dino,the x position of the closest obstacle,type of obstacle)(Nnormalized)
        decision=self.brain.feedForword(self.y/WINDO_H,obs[0].x/WINDO_W,(obs[0].type-2.5)/5)
        

        if decision > 0.5 and not self.jumping:
            self.jumping=True
            self.running=False
            self.ducking=False

        keys=pygame.key.get_pressed()
        #press space to save the weights of the current dino
        if keys[pygame.K_SPACE]:
            file=open("weights1.txt","w")
            file2=open("weights2.txt","w")
            print(self.brain.weights2)
            for weight in self.brain.weights2:
                file2.write(str(weight))
                file2.write("\n")
                
            for i in self.brain.weights1:
                for weights in i:
                    file.write(str(weights)+"\n")

        
        #NOT USED CURRENTLY
        if False and not self.jumping:
            self.ducking=True
            self.running=False
            self.jumping=False
        else:
            if False and self.ducking:
                self.ducking=False
                self.running=True
                self.jumping=False
                self.y=self.standard_y
        
        
        #calculating score of dino as long as he is alive for calculating fitness
        if self.alive:
            self.score+=1

    def draw(self,win):
        #draw dino (called in draw function down)
        win.blit(self.currentimg,(self.x,self.y))



class Obstacle():
    #obstacle super class
    def __init__(self,img,type1,type2,x) -> None:
        self.x=x
        self.y=330
        self.img=img
        self.hitbox=pygame.Rect(self.x,self.y,self.img.get_width(),self.img.get_height())
        self.vel=15
        self.type=type1+type2 #system made to make obstacle type numerical input by adding first type(large or small) and the second type(type of the first type)
    def move(self):
        #moving obstacle
        self.x-=self.vel
        self.hitbox.left=self.x

    #draw obstacle   
    def draw(self,win):
        win.blit(self.img,(self.x,self.y))
        self.move()        
    
class LargeCactus(Obstacle):
    #large obstacle (subclass)
    def __init__(self,img,x) :
        #choose random type
        type=random.randint(0,2)
        super().__init__(img[type],3,type,x)
        self.y-=24

class SmallCactus(Obstacle):
    #small obstacle (subclass)
    def __init__(self, img,x) :
        type=random.randint(0,2)
        super().__init__(img[type],0,type,x)








#-----------------------------Methods------------------------------------------------------------




def draw(dinos,obstacles):
    #method draw in the window
    #-------------------------
    
    #background color and ground image
    win.fill(BG_COLOR)
    win.blit(GROUND,(0,375))

    #draw living dinos and move them base on there decisions
    for dino in dinos:
        if dino.alive:
            dino.draw(win)
        dino.move(obstacles)
    
    #draw obstacles
    for obs in obstacles:
        obs.draw(win)
    pygame.display.update()
def collide(dinos,obstacles):
    #kill lived dinos on collision

    for obs in obstacles:
        for dino in dinos:
            if(pygame.Rect.colliderect(dino.hitbox,obs.hitbox)):
                dino.alive=False
def obstaclesManger(obstacles):
    #method that generate obstacles and remove them
    #-----------------------------------------------

    obstacletype=random.randint(1,2)

    #generate new obstacle every if there is no obstacles
    if len(obstacles)==0:
        if obstacletype == 1:
            obstacles.append(LargeCactus(LARGECAC,WINDO_W))
        elif obstacletype == 2 :
            obstacles.append(SmallCactus(SMALLCAC,WINDO_W))
            
    

    #remove every obstacle is coming out of the window
    for obs in obstacles:
        if obs.x<0:
            obstacles.remove(obs)
            if obstacletype == 1:
                obstacles.append(LargeCactus(LARGECAC,WINDO_W))
            elif obstacletype == 2 :
                obstacles.append(SmallCactus(SMALLCAC,WINDO_W))


def mutate(weights1,weights2):
    for iter in range(15):
        i=random.randint(0,3)
        j=random.randint(0,9)
        weights1[i][j]=np.random.randn()
    for iter in range(3):
        z=random.randint(0,10)
        weights2[z]=np.random.randn()
def crossover(parent1,parent2):
    temp=np.zeros((4,10)) #temporary weights 
    temp2=np.zeros(11)
    for i in range(4):
        for j in range(10):
            random_parent=random.randint(1,2) #for every weight, we choose randomly from certain parent
            if random_parent == 1:
                temp[i][j]=parent1.brain.weights1[i][j]
            else :
                temp[i][j]=parent2.brain.weights1[i][j]
    for i in range(11):
        random_parent=random.randint(1,2)
        if random_parent == 1:
            temp2[i]=parent1.brain.weights2[i]
        else :
            temp2[i]=parent2.brain.weights2[i]
    return temp,temp2
def select(dinos):
    #method that's find the best dinos base to there score(fitness)

    maxscore=dinos[0]
    for dino in dinos:
        if maxscore.score < dino.score:
            maxscore=dino
    maxscore2=dinos[0]
    for dino in dinos:
        if maxscore2.score < dino.score and maxscore != dino:
            maxscore2=dino
    return maxscore,maxscore2
def GenerateNewGeneration(dinos):
    #this method will make a new population from the parents who have the best fitness 
    #--------------------------------------------------------------------------------    
    global MUTTATES
    MUTTATES=0


    parent1,parent2=select(dinos) 
    dinos.clear() #empty list from dinos

    for x in range(POPULATION):
        temp1,temp2=crossover(parent1,parent2)#get new weights from the parents

        #percentage of having mutation
        randomutation=random.randint(1,100)
        if randomutation <= 10:
            mutate(temp1,temp2)
            MUTTATES+=1

        #create new dino and set the weights for his neural network
        tempdin=Dino()
        tempdin.brain.setweights(temp1,temp2)
        dinos.append(tempdin)
def check_dead(dinos):
    i=0
    for dino in dinos:
        if not dino.alive:
            i+=1
    return i==POPULATION
def weightsreader():
    w=open("weights2.txt",'r')
    s=open("weights1.txt",'r')
    x=w.readlines()
    y=s.readlines()
    weights1=np.array([float(i.strip()) for i in x])
    weights2=np.array([float(i.strip()) for i in y]).reshape(4,10)
    return weights1,weights2

def infos():
    os.system("cls")
    print("Generation number:",GENERATION_NUMBER)
    print("Current speed:",GAME_SPEED)
    print("how manny mutate dinos in this generation",MUTTATES)
def inputsReader():
    global GAME_SPEED
    keys=pygame.key.get_pressed()
    if keys[pygame.K_UP] and GAME_SPEED!=120:
        GAME_SPEED+=10
        infos()
    if keys[pygame.K_DOWN] and GAME_SPEED!=30:
        GAME_SPEED-=10
        infos

#-----------------------------------------------Main---------------------------------------------------------------


def main(dinos,obstacles):
    global RUNING
    clock=pygame.time.Clock()
    
    #making first population
    for i in range(POPULATION):
        dinos.append(Dino())

    


    #game loop
    while RUNING:
       
        #game speed
        clock.tick(GAME_SPEED)
        
        #quit game if game closed
        events=pygame.event.get()
        for e in events:
            if e.type==pygame.QUIT:
                RUNING=False
                quit()

        #calling methods(for mor infos look in the method)
        obstaclesManger(obstacles)
        draw(dinos,obstacles)
        collide(dinos,obstacles)
        inputsReader()

        #if all dinos are dead break game loop 
        if check_dead(dinos):
            break
       

        

        
while True:
    obstacles=[]
    dinos=[]
    infos()
    main(dinos,obstacles)
    GenerateNewGeneration(dinos)
    GENERATION_NUMBER+=1
    events=pygame.event.get()
    











