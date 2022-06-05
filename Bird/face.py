import cv2
import dlib
from imutils import face_utils
import numpy as np

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


# 头部姿态估计
def get_head_pose(shape):
    # 填写2D参考点的像素坐标集合
    # 17左眉左上角、21左眉右角、22右眉左上角、26右眉右角、36左眼左上角、39左眼右上角、42右眼左上角、45右眼右上角、31鼻子左上角
    # 35鼻子右上角、48嘴左上角、54嘴右上角、57嘴中央下角、8下巴角
    image_pts = np.float32([shape[17], shape[21], shape[22], shape[26], shape[36],
                            shape[39], shape[42], shape[45], shape[31], shape[35],
                            shape[48], shape[54], shape[57], shape[8]])
    # solvePnP求解旋转和平移矩阵：
    _, rvec, tvec = cv2.solvePnP(object_pts, image_pts, cam_M, distcoeffs)  # 得到旋转矩阵与平移矩阵
    rotation_mat, _ = cv2.Rodrigues(rvec)  # 通过罗德里格斯公式将旋转矩阵转换为旋转向量
    pose_mat = cv2.hconcat((rotation_mat, tvec))  # 水平拼接
    # 用decomposeProjectionMatrix将投影矩阵分解为旋转矩阵和相机矩阵
    _, _, _, _, _, _, euler_angle = cv2.decomposeProjectionMatrix(pose_mat)
    return euler_angle

def recognize():
    cap = cv2.VideoCapture(0)
    detector = dlib.get_frontal_face_detector()  # 用于检测人脸
    predictor = dlib.shape_predictor(face_landmark_path)  # 用于检测关键点
    nod_counts = 0  # 记录低头状态的时间
    while 1:
        ret, frame = cap.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # 将图像转为灰度图
            face = detector(gray, 0)
            if len(face) > 0:
                shape = predictor(gray, face[0])  # 提取关键点
                shape = face_utils.shape_to_np(shape)  # 将提取的特征点转为numpy矩阵，便于操作
                euler_angle = get_head_pose(shape)
                print(euler_angle[0][0])
            if euler_angle[0][0] > 3:  # 设置pitch的阈值为3，当大于3时视为低头状态
                nod_counts += 1
            if nod_counts > 4 and euler_angle[0][0] < 3:  # 当处于低头状态大于4帧且pitch小于3时，视为完成点头动作并归位，记录一次点头
                print('检测到点头')
                nod_counts = 0
            cv2.imshow("Head_Posture", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):  # 按q退出
                break
    cap.release()
    cv2.destroyAllWindows()


def main():
    cap = cv2.VideoCapture(0)
    detector = dlib.get_frontal_face_detector()  # 用于检测人脸
    predictor = dlib.shape_predictor(face_landmark_path)  # 用于检测关键点
    nod_counts = 0  # 记录低头状态的时间
    while 1:
        ret, frame = cap.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # 将图像转为灰度图
            face = detector(gray, 0)
            if len(face) > 0:
                shape = predictor(gray, face[0])  # 提取关键点
                shape = face_utils.shape_to_np(shape)  # 将提取的特征点转为numpy矩阵，便于操作
                euler_angle = get_head_pose(shape)
                print(euler_angle[0][0])
            if euler_angle[0][0] > 3:  # 设置pitch的阈值为3，当大于3时视为低头状态
                nod_counts += 1
            if nod_counts > 4 and euler_angle[0][0] < 3:  # 当处于低头状态大于4帧且pitch小于3时，视为完成点头动作并归位，记录一次点头
                print('检测到点头')
                nod_counts = 0
            cv2.imshow("Head_Posture", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):  # 按q退出
                break
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
