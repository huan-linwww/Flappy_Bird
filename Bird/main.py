import pygame
import sys
import random
import json

Screen_x = 576
Screen_y = 1024
pipe_list = []
can_score = True
username = ""


# 处理排行
def savescore(username, score):
    file = open("score.json", 'r')

    try:
        data = json.load(file)
    except json.decoder.JSONDecodeError:
        data = {}
    if username in data.keys():
        if data[username] <= score:
            data[username] = score
    else:
        data[username] = score
    file.close()
    file = open("score.json", 'w')
    json.dump(data, file)
    file.close()


def getscore():
    file = open("score.json", 'r')
    data = json.load(file)
    '''
    
    print(type(data))
    print(data)
    '''
    sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
    file.close()
    if len(sorted_data) >= 3:
        return sorted_data[:3]
    else:
        return sorted_data[0:]


def inputUI(screen):
    font = pygame.font.Font(None, 32)
    clock = pygame.time.Clock()
    input_box = pygame.Rect(250, 400, 140, 32)
    color_inactive = (221, 174, 255)
    color_active = (251, 73, 255)
    color = color_inactive
    active = False
    text = ''
    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                # 如果鼠标点到输入框内
                if input_box.collidepoint(event.pos):
                    # 激活输入框
                    active = not active
                else:
                    active = False
                # 随着输入框的激活改变边框的颜色
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        return text
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        screen.fill((127, 255, 212))
        # 生成一个新的surface对象并在上面渲染文本
        txt_surface = font.render(text, True, color)
        txt_please = font.render('Input Username:', True, color)
        # 如果字符串太长 则增加输入框的长度
        width = max(200, txt_surface.get_width() + 10)
        input_box.w = width
        # 绘制文字
        screen.blit(txt_please, (input_box.x - 180, input_box.y + 5))
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        # 绘制输入框
        pygame.draw.rect(screen, color, input_box, 2)
        # 显示图像
        pygame.display.flip()
        clock.tick(30)


class Bird(object):

    def __init__(self):
        self.Surface = pygame.image.load("Bird.png")
        self.birdRect = self.Surface.get_rect(center=(Screen_x / 6, Screen_y / 2))
        # 定义鸟的3种状态
        self.birdStatus = [pygame.image.load("Bird.png"),
                           pygame.image.load("Bird.png"),
                           pygame.image.load("Dead.png")]
        self.status = 0  # 默认飞行坐标
        self.movement = 0

        self.gravity = 0.4  # 向下加速度
        self.dead = False

    def birdUpdate(self):
        # 更新鸟的运动状态
        if not (self.dead):
            # Bird
            self.movement += self.gravity  # 完成对重力的计算

            self.birdRect.centery += self.movement
            screen.blit(self.Surface, self.birdRect)

    def jump(self):
        self.movement = 0
        self.movement -= 10

    def renew(self):
        self.birdRect = self.Surface.get_rect(center=(Screen_x / 6, Screen_y / 2))
        self.movement = 0


class Pipeline(object):

    def __init__(self):
        self.Surface = pygame.transform.scale2x(pygame.image.load("pipe-green.png"))

        self.wallx = 400  # 管道所在X轴坐标

        self.pipehigh = [400, 600, 800]

    def create_Pipe(self):
        random_high = random.choice(self.pipehigh)
        bottom_pipe = self.Surface.get_rect(midtop=(700, random_high))
        top_pipe = self.Surface.get_rect(midbottom=(700, random_high - Screen_y * 1 / 3))
        return bottom_pipe, top_pipe


def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= Screen_x / 20
    visible_pipes = [pipe for pipe in pipes if pipe.right > -50]
    return visible_pipes


def draw_pipes(pipes):
    for pipe in pipes:
        if pipe.bottom >= Screen_y:
            screen.blit(Pipeline.Surface, pipe)
        else:
            flip_pipe = pygame.transform.flip(Pipeline.Surface, False, True)
            screen.blit(flip_pipe, pipe)


def pipe_score_check():
    global score, can_score

    if pipe_list:
        for pipe in pipe_list:
            if 95 < pipe.centerx < 105 and can_score:
                score += 1
                score_sound.play()
                can_score = False
            if pipe.centerx < 0:
                can_score = True


def score_display():
    color = (255, 255, 255)
    score_surface = game_font.render(f'Your Score: {int(score)}', True, (255, 255, 255))
    score_rect = score_surface.get_rect(center=(288, 60))
    screen.blit(score_surface, score_rect)
    topscore = getscore()
    print(topscore)
    cur_font1 = pygame.font.SysFont("宋体", 80)
    cur_font2 = pygame.font.SysFont("宋体", 80)
    text_fmt1 = cur_font1.render('1  ' + '----    0', False, color)
    text_fmt2 = cur_font2.render('2  ' + '----    0', False, color)
    text_fmt3 = cur_font2.render('3  ' + '----    0', False, color)
    print(topscore[0][0])
    if len(topscore) >= 1:
        text_fmt1 = cur_font1.render('1  ' + topscore[0][0] + '    ' + str(topscore[0][1]), False, color)
        if len(topscore) >= 2:
            text_fmt2 = cur_font2.render('2  ' + topscore[1][0] + '    ' + str(topscore[1][1]), False, color)
            if len(topscore) >= 3:
                text_fmt3 = cur_font2.render('3  ' + topscore[2][0] + '    ' + str(topscore[2][1]), False, color)

    screen.blit(text_fmt1, (Screen_x / 4, 130))
    screen.blit(text_fmt2, (Screen_x / 4, 200))
    screen.blit(text_fmt3, (Screen_x / 4, 270))


def createMap():
    global pipe_list
    screen.fill((255, 255, 255))  # 填充颜色
    screen.blit(background, (0, 0))  # 填入到背景
    # 显示管道
    pipe_list = move_pipes(pipe_list)
    draw_pipes(pipe_list)
    ''' screen.blit(Pipeline.pineUp, (Pipeline.wallx, -300))  # 上管道坐标位置
    screen.blit(Pipeline.pineDown, (Pipeline.wallx, 500))  # 下管道坐标位置
    Pipeline.updatePipeline()  # 移动管道'''

    # 显示小鸟
    if Bird.dead:  # 撞管道的状态
        Bird.status = 2
    elif Bird.jump:  # 飞行状态
        Bird.status = 1

    screen.blit(Bird.birdStatus[Bird.status], Bird.birdRect)
    pipe_score_check()
    pygame.display.update()  # 更新显示


def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= 5
    visible_pipes = [pipe for pipe in pipes if pipe.right > -50]
    return visible_pipes


def checkDead(pipes):
    global can_score
    # 检测小鸟与上下方管子是否碰撞
    for pipe in pipes:
        if Bird.birdRect.colliderect(pipe):
            death_sound.play()
            can_score = True
            Bird.dead = True

    # 检测小鸟是否飞出边界
    if not 0 < Bird.birdRect[1] < height:
        Bird.dead = True
        can_score = True
    return Bird.dead


if __name__ == '__main__':

    pygame.init()
    pygame.font.init()
    score = 0
    pygame.display.set_caption("MY Flappy bird")  # 设置窗口标题
    font = pygame.font.SysFont(None, 50)
    size = width, height = Screen_x, Screen_y  # 设置窗口
    screen = pygame.display.set_mode(size)  # 显示窗口
    icon = pygame.image.load("Bird.png")  # 修改窗口默认图标
    pygame.display.set_icon(icon)

    clock = pygame.time.Clock()  # 设置时钟

    username = inputUI(screen)

    Bird = Bird()  # 实例化鸟类

    Pipeline = Pipeline()  # 实例化管道类
    SPAWNPIPE = pygame.USEREVENT
    # 创建pipe的速度
    pygame.time.set_timer(SPAWNPIPE, 1200)
    game_over_surface = pygame.transform.scale2x(pygame.image.load('message.png').convert_alpha())
    game_over_rect = game_over_surface.get_rect(center=(288, (Screen_y * 3 / 5)))
    background = pygame.image.load("bg_6.png")  # 加载背景图片
    background = pygame.transform.scale2x(background)
    flap_sound = pygame.mixer.Sound('sound/sfx_wing.wav')
    death_sound = pygame.mixer.Sound('sound/sfx_hit.wav')
    score_sound = pygame.mixer.Sound('sound/sfx_point.wav')
    score_sound_countdown = 100
    game_font = pygame.font.SysFont("Arial", 50)
    # gamestart = False

    while True:
        clock.tick(120)
        # 轮询事件
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not Bird.dead:
                    Bird.jump()
                if event.key == pygame.K_SPACE and Bird.dead:
                    Bird.dead = False
                    Bird.renew()
                    score = 0

            if event.type == SPAWNPIPE:
                pipe_list.extend(Pipeline.create_Pipe())

        Bird.birdUpdate()

        if checkDead(pipe_list):  # 检测小鸟生命状态

            screen.blit(game_over_surface, game_over_rect)
            pipe_list.clear()
            savescore(username, score)
            score_display()
            pygame.display.update()  # 更新显示

        else:

            createMap()  # 创建地图
    pygame.QUIT()  # 退出
