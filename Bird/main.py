import pygame
import sys
import random
import json
import cv2
import dlib
from face import get_head_pose
from imutils import face_utils
import numpy as np
from score import savescore, getscore

Screen_x = 576
Screen_y = 1024
pipe_list = []
can_score = True
username = ""

face_landmark_path = 'shape_predictor_68_face_landmarks.dat'  # 人脸模型路径
# 世界坐标系:3D参考点
object_pts = np.float32([[6.825897, 6.760612, 4.402142],  # 33左眉左上角
                         [1.330353, 7.122144, 6.903745],  # 29左眉右角
                         [-1.330353, 7.122144, 6.903745],  # 34右眉左角
                         [-6.825897, 6.760612, 4.402142],  # 38右眉右上角
                         [5.311432, 5.485328, 3.987654],  # 13左眼左上角
                         [1.789930, 5.393625, 4.413414],  # 17左眼右上角
                         [-1.789930, 5.393625, 4.413414],  # 25右眼左上角
                         [-5.311432, 5.485328, 3.987654],  # 21右眼右上角
                         [2.005628, 1.409845, 6.165652],  # 55鼻子左上角
                         [-2.005628, 1.409845, 6.165652],  # 49鼻子右上角
                         [2.774015, -2.080775, 5.048531],  # 43嘴左上角
                         [-2.774015, -2.080775, 5.048531],  # 39嘴右上角
                         [0.000000, -3.116408, 6.097667],  # 45嘴中央下角
                         [0.000000, -7.415691, 4.070434]])  # 6下巴角
# 添加相机内参矩阵
K = [608.43683158, 0.0, 313.54391368,
     0.0, 608.52002274, 255.73442784,
     0.0, 0.0, 1.0]
# 添加相机畸变参数
D = [-2.27397410e-01, 8.34759272e-01, 2.10685804e-03, -4.30764993e-04, -1.15198356e+00]
# 转为矩阵形式
cam_M = np.array(K).reshape(3, 3).astype(np.float32)
distcoeffs = np.array(D).reshape(5, 1).astype(np.float32)


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
    cap = cv2.VideoCapture(0)
    detector = dlib.get_frontal_face_detector()  # 用于检测人脸
    predictor = dlib.shape_predictor(face_landmark_path)  # 用于检测关键点
    nod_counts = 0  # 记录低头状态的时间

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

    MY_EVENT = pygame.USEREVENT + 1

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
        clock.tick(60)
        ret, frame = cap.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # 将图像转为灰度图
            face = detector(gray, 0)
            if len(face) > 0:
                shape = predictor(gray, face[0])  # 提取关键点
                shape = face_utils.shape_to_np(shape)  # 将提取的特征点转为numpy矩阵，便于操作
                euler_angle = get_head_pose(shape)
                # print(euler_angle[0][0])
            if euler_angle[0][0] > 3:  # 设置pitch的阈值为3，当大于3时视为低头状态
                nod_counts += 1
            if nod_counts > 4 and euler_angle[0][0] < 3:  # 当处于低头状态大于4帧且pitch小于3时，视为完成点头动作并归位，记录一次点头
                print('检测到点头')
                my_event = pygame.event.Event(MY_EVENT, {"message": "事件触发"})
                # 将这个事件加入到事件队列
                pygame.event.post(my_event)
                nod_counts = 0
            cv2.imshow("Head_Posture", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):  # 按q退出
                break

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
            if event.type == MY_EVENT:
                print("点头触发")

                if Bird.dead:
                    Bird.dead = False
                    Bird.renew()
                    score = 0
                else:
                    Bird.jump()

        Bird.birdUpdate()

        if checkDead(pipe_list):  # 检测小鸟生命状态

            screen.blit(game_over_surface, game_over_rect)
            pipe_list.clear()
            savescore(username, score)
            score_display()
            pygame.display.update()  # 更新显示

        else:

            createMap()  # 创建地图
    cap.release()
    cv2.destroyAllWindows()
    pygame.QUIT()  # 退出
