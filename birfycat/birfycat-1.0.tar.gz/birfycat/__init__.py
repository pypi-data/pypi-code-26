import random
import threading

class Cat(object):
    ihungry=0
    ihappy=0
    ihealth=0
    status=0#1-sleep 2-walk 3-play 4-feed 5-seedoctor 6-wake

    def __init__(self, ihungry=random.randint(0,100), ihappy=random.randint(0,100), ihealth=random.randint(0,100), status=random.randint(2,5)):
        self.ihungry=ihungry
        self.ihappy=ihappy
        self.ihealth=ihealth
        self.status=status
    
    def sleep(self):
        self.status=1

    def walk(self):
        self.status=2
    
    def play(self):
        self.status=3
    
    def feed(self):
        self.status=4
    
    def seedoctor(self):
        self.status=5
    
    def wake(self):
        self.status=6
        
    def hungryorfull(self):
        self.ihealth-=1

    def unhappy(self):
        self.ihealth-=1

    def disturbsleeping(self):
        self.ihappy-=4

    def getStatus(self):
        if self.status==1:
            return '我在睡觉......'
        elif self.status==2:
            return '我在散步.....'
        elif self.status==3:
            return '我在玩耍......'
        elif self.status==4:
            return '我在吃饭......'
        elif self.status==5:
            return '我在看医生......'    
        elif self.status==6:
            return '我醒着但很无聊......'

    def checkstatus(self):
        if self.ihungry < 0:
            self.ihungry=0
        elif self.ihungry > 100:
            self.ihungry=100
        if self.ihappy < 0:
            self.ihappy=0
        elif self.ihappy > 100:
            self.ihappy=100
        if self.ihealth < 0:
            self.ihealth=0
        elif self.ihealth > 100:
            self.ihealth=100

    def update(self):
        if self.status==1:
            self.ihungry+=1
        elif self.status==2:
            self.ihungry+=3
            self.ihealth+=1
        elif self.status==3:
            self.ihungry+=3
            self.ihappy+=1
        elif self.status==4:
            self.ihungry-=3
        elif self.status==5:
            self.ihealth+=4    
        elif self.status==6:
            self.ihungry+=2
            self.ihappy-=1
        if (self.ihungry>80) or (self.ihungry<20):
            self.ihealth-=2
        if (self.ihappy<20):
            self.ihealth-=1
        self.checkstatus()

    def checksleep(self):
        if self.status==1:
            if input('你确认要吵醒我吗？我在睡觉，你要是坚持吵醒我，我会不高兴的！（y表示是/其他表示不是）：')=='y':
                self.disturbsleeping()
                return True
            else:
                return False
        else:
            return True


def main():
    global hours,cat

    print('我的名字叫Tommy，一只可爱的猫咪....')
    print('你可以和我一起散步，玩耍，你也需要给我好吃的东西，带我去看病，也可以让我发呆....')
    print('Commands:')
    print('1.walk:散步')
    print('2.play:玩耍')
    print('3.feed:喂我')
    print('4.seedoctor:看医生')
    print('5.letalone:让我独自一人')
    print('6.status:查看我的状态')
    print('7.bye:不想看到我')
    
    try:
        f=open('./data','r')
        hours=int(f.readline())
        ihappy=int(f.readline())
        ihungry=int(f.readline())
        ihealth=int(f.readline())
        status=int(f.readline())
        f.close()
        cat=Cat(ihungry=ihungry,ihappy=ihappy,ihealth=ihealth,status=status)
    except Exception:
        hours=random.randint(0,23)
        cat=Cat()

        if (hours < 8) and (hours >= 0):
            cat.sleep()
    
    ticktock()

    while True:
        print()
        command = input("Command:")
        if command == "status":
            print("当前时间：%-2d点"%hours)
            print("我当前的状态：%s"%cat.getStatus())
            print('Happiness:   Sad %s%s Happy  (%03d)'%('*'*int(cat.ihappy//2),'-'*int(50-cat.ihappy//2),cat.ihappy))
            print('Hungry:     Full %s%s Hungry (%03d)'%('*'*int(cat.ihungry//2),'-'*int(50-cat.ihungry//2),cat.ihungry))
            print('Health:     Sick %s%s Healthy(%03d)'%('*'*int(cat.ihealth//2),'-'*int(50-cat.ihealth//2),cat.ihealth))
        elif command == "walk":
            if cat.checksleep():
                cat.walk()
            print(cat.getStatus())
        elif command == "play":
            if cat.checksleep():
                cat.play()
            print(cat.getStatus())
        elif command == "feed":
            if cat.checksleep():
                cat.feed()
            print(cat.getStatus())
        elif command == "seedoctor":
            if cat.checksleep():
                cat.seedoctor()
            print(cat.getStatus())
        elif command == "letalone":
            if cat.status != 1:
                cat.wake()
            print(cat.getStatus())
        elif command == "quit":
            print("Bye.....")
            timer.cancel()
            f=open('./data','w')
            f.write(str(hours)+"\n")
            f.write(str(cat.ihappy)+"\n")
            f.write(str(cat.ihungry)+"\n")
            f.write(str(cat.ihealth)+"\n")
            f.write(str(cat.status)+"\n")
            f.close()
            break
        else:
            print('我听不懂你在说什么')

def ticktock():
    global timer,hours
        
    hours+=1
    if hours>23:
        hours=0
    if hours==0:
        cat.sleep()
    if hours==8:
        cat.wake()
    cat.update()
    timer=threading.Timer(5.0,ticktock)
    timer.start()

if __name__ == "__main__":
    main()
    