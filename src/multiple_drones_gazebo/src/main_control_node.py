#!/usr/bin/env python
import rospy
import time
import sys
from roslib import message
from geometry_msgs.msg import PoseStamped, Twist, Quaternion
from std_msgs.msg import Float64MultiArray
from visualization_msgs.msg import Marker
from sklearn.preprocessing import normalize
import numpy as np
from tf.transformations import *


# difference between poses in common frame of structure {'X': np.array([x, y, z]), 'O': np.array(quaternion)}
def pose_diff(p1, p2, k = 1.):
    q1 = p1['O'] 
    q2 = p2['O']
    diff = {'X': k * (p1['X'] - p2['X']), 'O': qq_div(quaternion_slerp(q1, q2, k), q1) }
    return diff

# quaternion rotation
def qv_rot(q, v):
    v = np.append(v, 1)
    return np.matmul(quaternion_matrix(q), v)[0:3]

# quaternion relative rotation
def qq_div(q1, q2):
    return quaternion_multiply(q2, quaternion_inverse(q1))

# flat, radial formation with center point in [0 0 0], aligned along x, facing outside
def make_formation(r_form, n):
    r = np.array([r_form, 0., 0.], dtype = np.float64)
    pos = {}
    for i in range(n):
        q_rot = quaternion_from_euler(0, 0,  - 2. * i * np.pi / n)
        pos[i] = {'X': qv_rot(q_rot, r), 'O':q_rot}
    return pos

def angle(v1, v2, acute):
    angle = np.arccos(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
    if (acute == True):
        return angle
    else:
        return 2 * np.pi - angle



class Control: 

    # callback function for pose reading
    def call_pose(self, data, arg):
        #PoseStamped
        drone_id = arg
        #p = [Point2list(data.pose.position), Quaternion2list(data.pose.orientation)]
        if not self.recv_pose[drone_id]:
            pos = data.pose.position
            ori = data.pose.orientation
            posex = np.array([pos.x, pos.y, pos.z], dtype = np.float64)
            poseo = np.array([ori.x, ori.y, ori.z, ori.w],  dtype = np.float64)
            poseo = poseo / np.linalg.norm(poseo)
            self.Pose_list[drone_id] = {'X': posex, 'O': poseo}
            self.recv_pose[drone_id] = True
            return "done receiving pose"
        return "already received"

    # callback function for kinect data reading
    def call_obst(self, data, arg):
        #PoseStamped
        drone_id = arg
        if not self.recv_obst[drone_id]:
            self.Obst_list[drone_id] = np.reshape(np.asarray(data.data, dtype = np.float64), [-1, 3])
            self.recv_obst[drone_id] = True
            return "done receiving obstacles"
        return "already received"

    # obstacles pushes evaluation, settable params: linear gain (gain) and inverted vector norm power (pow_dist)
    def col_avoid(self, gain = 1.0, pow_dist = 1.):
        # print(gain)
        margin = 0.35
        obstacle_push = {}
        obst_cnt = 10
        for i, obst_temp in self.Obst_list.items():
            try:
                gaini = gain/np.shape(obst_temp)[0]
                lens = np.linalg.norm(obst_temp, axis = 1)
                dirs = normalize(obst_temp, norm='l2')


                # idxs = np.argsort(lens)[::-1][0:obst_cnt]
                # lensi = lens[idxs]
                # dirsi = dirs[idxs,:]

                # gaini /= obst_cnt
                # pushes = gaini * dirsi * np.power(lensi, 1 - pow_dist)[:, None]
                pushes = gaini * dirs * np.power(lens - margin, 1 - pow_dist)[:, None]
                push_loc = np.sum(pushes, axis = 0)
                push_glob = qv_rot(self.Pose_list[i]['O'], push_loc)
                if np.linalg.norm(push_glob) < self.min_push:
                    push_glob = 0. * push_glob
                obstacle_push[i] = push_glob
            except:
                print('Reset: kinnect connection failed, call Michal Jarzyna')
                obstacle_push[i] = np.array([0., 0., 0.])
        return obstacle_push

    # target pull evaluation, settable parameters: linear gain (gain) and vector length power (pow_tar)
    def tar_follow(self, gain = 1., pow_tar = 1.):
        pulls = {}
        for i, pose in self.Pose_list.items():
            qL = self.virtualX[i]['O']
            direction = self.targetX['X'] + qv_rot(qL, self.formation[i]['X']) - pose['X']
            dist = np.linalg.norm(direction)
            direction /= dist
            pulls[i] = gain * direction * np.power(dist, pow_tar)
        return pulls

    # step of target movement
    def tar_update(self):
        self.targetX['X'] += self.targetV['X']*self.dT

    # step of consensus algorithm
    def update_virtual(self, push, pull):
        temp_x = self.virtualX
        temp_v = self.virtualV
        # virtual leader pose update
        for v_id in range(self.drone_count):        # for each virtual leader
            self.virtualX[v_id]  = temp_x[v_id] 
            self.virtualV[v_id]  = temp_v[v_id]
            for q_id in range(self.drone_count):    # for each drone you hear
                self.virtualX[v_id] = pose_diff(self.virtualX[v_id], pose_diff(temp_x[v_id], temp_x[q_id], self.W[v_id][q_id]))
                if not (v_id == q_id):
                    self.virtualV[v_id] = pose_diff(self.virtualV[v_id], pose_diff(temp_v[v_id], temp_v[q_id], self.W[v_id][q_id]))
                else:
                    own_o = np.array([0, 0, 0, 1], dtype = np.float64)
                    # print(push[v_id])
                    v1 = pull[v_id]
                    v2 = qv_rot(self.Pose_list[v_id]['O'], np.array([1., 0., 0.]))
                    if np.abs(angle(v1, v2, True)) > np.pi/2:
                        pull[v_id] = np.array([0., 0., 0.])
                    pp = {'X': (1/self.W[v_id][q_id]) * push[v_id] + pull[v_id], 'O': own_o}
                    self.virtualV[v_id] = pose_diff(self.virtualV[v_id], pose_diff(temp_v[v_id], pp, self.W[v_id][q_id]))
            ksi = 0.1
            ori0 = {'X': (1. - 1./ksi) * self.virtualX[v_id]['X'], 'O': np.array([0,0,0,1], dtype = np.float64)}
            self.virtualX[v_id] = pose_diff(self.virtualX[v_id], ori0, ksi)
            
            pose0 = {'X':np.array([0., 0., 0.]), 'O': np.array([0., 0., 0., 1.])}
            vdT = {'X': temp_v[v_id]['X'] * self.dT, 'O': quaternion_slerp(np.array([0., 0., 0., 1.]), temp_v[v_id]['O'], self.dT)}
            self.virtualX[v_id] = pose_diff(self.virtualX[v_id], pose_diff(pose0, vdT)) ########## *dT

            # random change in virtual lider position
            #self.virtualX[v_id]['X']+=(np.random.rand(3)-0.5)/10;

    def send_msgs(self):
        msg = Twist()
        for q_id, pub in self.Pub_list.items():
            # Pose_list - pose global
            # virtualX, virtualV - LIDER pose, velocity global
            # formation - shape
            # vi = vil + k(x_zad - x_own)
            k = 0.3    #do some PID
            qL = self.virtualX[q_id]['O']
            x_zad = self.virtualX[q_id]['X'] + qv_rot(qL, self.formation[q_id]['X'])
            # x_zad = self.virtualX[q_id]['X'] + self.formation[q_id]['X']
            # x_zad = (q_id + 1) * np.array([0, 0, 2])
            wL = euler_from_quaternion(self.virtualV[q_id]['O'])
            Vadd = np.cross(self.formation[q_id]['X'], wL)
            V = (self.virtualV[q_id]['X'] + Vadd) + k * (x_zad - self.Pose_list[q_id]['X'])
            V = qv_rot(quaternion_inverse(self.Pose_list[q_id]['O']), V)
            msg.linear.x = V[0]
            msg.linear.y = V[1]
            msg.linear.z = V[2]
            # wi = wil + k(fi_zad - fi_own)
            wil = self.virtualV[q_id]['O']
            fi_zad = quaternion_multiply(self.virtualX[q_id]['O'], self.formation[q_id]['O'])
            # fi_zad = np.array([0,0,0,1])
            fi_own = self.Pose_list[q_id]['O']
            wi = quaternion_multiply(wil, qq_div(fi_own, fi_zad))
            rwi = euler_from_quaternion(wi)
            msg.angular.x = rwi[0]
            msg.angular.y = rwi[1]
            msg.angular.z = rwi[2]
            pub.publish(msg)




    # class initialization
    def __init__(self, drone_cnt):
        
        # Control frquency
        self.rate = rospy.Rate(5)
        # time step (for controllers)
        self.dT =  float(0.2)
        # # of Quads
        self.drone_count = int(drone_cnt)
        # pose reading flags
        self.recv_pose = [False]*self.drone_count
        # kinect reading flag
        self.recv_obst = [False]*self.drone_count
        # subscribers handlers for pose reading
        self.Sub_pose_list = {}
        # subscribers handlers for kinect reading
        self.Sub_obst_list = {}
        # publishers handlers for steering
        self.Pub_list = {}
        # Quads poses Pose_list[#] = {'X':, 'O'}
        self.Pose_list = {}
        # Kinect data holder
        self.Obst_list = {}
        # consensus gains
        k_mine = 3. #3 
        k_yours = 1. # 1
        W = k_yours * np.ones([self.drone_count, self.drone_count], dtype = np.float64) + k_mine*np.eye(self.drone_count, dtype = np.float64)
        self.W_true = np.divide(W, np.sum(W, axis = 1))
        self.W = self.W_true
        
        # Radial, flat formation
        self.formation = make_formation(r_form = 2.5, n = self.drone_count)
        # lower bound for obstacles push
        self.min_push = 0.63
        # virtual leader initialization flag
        self.init_virtual_flag = False
        # virtual leader poses virtualX[#] = {'X':, 'O':}
        self.virtualX = {}
        # virtual leader velocities  virtualV[#] = {'X':, 'O':}
        self.virtualV = {}
        ################################ should target be oriented?
        # pseudo target velocity, initial forward flight
        self.targetV = {'X': np.array([0, 0, 0], dtype = np.float64), 'O': np.array([0., 0., 0., 1.], dtype = np.float64)}
        # pseudo target position
        self.targetX = {'X': np.array([0, 0, 1], dtype = np.float64), 'O': np.array([0., 0., 0., 1.], dtype = np.float64)}
        

        self.tar_pub  = rospy.Publisher('targetX', Marker, queue_size = 1)
        self.msg_tarX = Marker()
        self.msg_tarX.header.frame_id = 'world'
        self.msg_tarX.color.a = 1
        self.msg_tarX.color.r = 1
        self.msg_tarX.scale.x = 0.5
        self.msg_tarX.scale.y = 0.5
        self.msg_tarX.scale.z = 0.5
        self.msg_tarX.type = 2

        # Pose reader initialization
        for i in range(self.drone_count):
            sub_name = "drone" + str(i + 1) + "/ground_truth_to_tf/pose"
            sub = rospy.Subscriber(sub_name, PoseStamped, self.call_pose, i)
            self.Sub_pose_list[i] = sub

        # kinect reader initialization
        for i in range(self.drone_count):
            sub_name = "drone" + str(i + 1) + "/Obstacles"
            sub = rospy.Subscriber(sub_name, Float64MultiArray, self.call_obst, i)
            self.Sub_pose_list[i] = sub

        # control sender initialization
        for i in range(self.drone_count):
            pub_name = "drone" + str(i + 1) + "/cmd_vel"
            pub = rospy.Publisher(pub_name, Twist, queue_size = 1)
            self.Pub_list[i] = pub

        # Main loop
        t = time.time()
        start = 0
        dir_cnt = 0
        push_gain = 0.
        follow_gain = 0.
        start_delay = 40
        n_pol =3 
        while not rospy.is_shutdown():
            
            
            
            self.msg_tarX.pose.position.x = self.targetX['X'][0]
            self.msg_tarX.pose.position.y = self.targetX['X'][1]
            self.msg_tarX.pose.position.z = self.targetX['X'][2]

            self.tar_pub.publish(self.msg_tarX)

            # self.targetV = np.random.random([])
            # virtual leader initialization
            while not self.init_virtual_flag:
                if self.recv_pose.count(False) == 0:
                    for key, val in self.Pose_list.items():
                        self.virtualX[key] = {}
                        self.virtualX[key]['X'] = val['X'] - qv_rot(quaternion_inverse(self.formation[key]['O']), self.formation[key]['X'])
                        self.virtualX[key]['X'][2] = 3.
                        self.virtualX[key]['O'] = quaternion_inverse(self.formation[key]['O'])         ## val['O']-
                        self.virtualV[key] = {}
                        self.virtualV[key]['X'] = np.array([0., 0., 0.], dtype = np.float64)
                        self.virtualV[key]['O'] = np.array([0., 0., 0., 1.], dtype = np.float64)                        
                    self.init_virtual_flag = True

            
            if self.recv_pose.count(False) == 0 and self.recv_obst.count(False) == 0:
                # elapsed = time.time() - t
                # t = time.time()
                # print(1/elapsed)
                ## Update virtual
                if dir_cnt > 100:
                    # destroy random connection
                    # self.W = self.W_true
                    # print('Usuniete polaczenia')
                    # index_throw = np.random.randint(0,self.drone_count, size=(n_pol,2))
                    # for i in range(n_pol):
                    #     if (index_throw[i][0]!=index_throw[i][1]):
                    #         self.W[index_throw[i][0],index_throw[i][1]] = 0
                    #         print(index_throw[i])
                    #  
                    # print('------------')
                    self.targetV['X'][0] = np.random.rand()-0.5
                    self.targetV['X'][1] = np.random.rand()-0.5
                    dir_cnt = 0
                self.tar_update()
                push_gain = 0. if start < start_delay else 0.0 #2.1
                follow_gain = 0. if start < start_delay else 1.0
                push = self.col_avoid(gain = -push_gain, pow_dist = 1.5)
                # print('--------push:')
                # print(push[0])
                # print(push[1])
                pull = self.tar_follow(gain = follow_gain, pow_tar = 0.5)
                # print('--------pull:')
                # print(pull[0])
                # print(pull[1])
                self.update_virtual(push, pull)
                
                self.send_msgs()
                
                self.recv_pose = [False]*self.drone_count
                self.recv_obst = [False]*self.drone_count
                self.rate.sleep()

                start += 1
                dir_cnt += 1          
                

if __name__ == '__main__':
    rospy.init_node('main_control_node')
    
    try:
        control = Control(sys.argv[1])
    except rospy.ROSInterruptException:  
        pass