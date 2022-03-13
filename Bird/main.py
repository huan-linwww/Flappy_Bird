import pygame
import sys
import random

Screen_x = 576
Screen_y = 1024
pipe_list = []
can_score = True


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
    score_surface = game_font.render(f'Score: {int(score)}', True, (255, 255, 255))
    score_rect = score_surface.get_rect(center=(288, 100))
    screen.blit(score_surface, score_rect)





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


def getResult():
    final_text1 = "Game Over"
    final_text2 = "Your final score is :  " + str(score)
    ft1_font = pygame.font.SysFont("Arial", 70)  # 设置第一行文字字体
    ft1_surf = font.render(final_text1, 1, (242, 3, 36))  # 设置第一行文字颜色
    ft2_font = pygame.font.SysFont("Arial", 50)  # 设置第二行文字字体
    ft2_surf = font.render(final_text2, 1, (253, 177, 6))  # 设置第二行文字颜色
    # 设置两行文字显示位置
    screen.blit(ft1_surf, [screen.get_width() / 2 - ft1_surf.get_width() / 2, 100])
    screen.blit(ft2_surf, [screen.get_width() / 2 - ft2_surf.get_width() / 2, 200])
    # 更新整个待显示的Surface对象到屏幕上
    pygame.display.flip()


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
    Bird = Bird()  # 实例化鸟类

    Pipeline = Pipeline()  # 实例化管道类
    SPAWNPIPE = pygame.USEREVENT
    # 创建pipe的速度
    pygame.time.set_timer(SPAWNPIPE, 1200)
    game_over_surface = pygame.transform.scale2x(pygame.image.load('message.png').convert_alpha())
    game_over_rect = game_over_surface.get_rect(center=(288, 512))
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
                print(len(pipe_list))
        Bird.birdUpdate()

        if checkDead(pipe_list):  # 检测小鸟生命状态

            screen.blit(game_over_surface, game_over_rect)
            pipe_list.clear()
            score_display()
            pygame.display.update()  # 更新显示

        else:


            createMap()  # 创建地图
    pygame.QUIT()  # 退出
