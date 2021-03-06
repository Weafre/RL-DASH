#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ns3gym import ns3env
import matplotlib.pyplot as plt
import sys
import os
import json
os.environ['CUDA_VISIBLE_DEVICES']=''

import numpy as np
import tensorflow as tf
import time

import argparse

import itertools
import matplotlib
import numpy as np
import pandas as pd
import sys


from collections import defaultdict
import pickle
import os
from functools import partial

S_INFO = 6  # bit_rate, buffer_size, rebuffering_time, bandwidth_measurement, chunk_til_video_end
S_LEN = 8  # take how many frames in the past
A_DIM = 6
VIDEO_BIT_RATE = [300,750,1200,1850,2850,4300]  # Kbps
BITRATE_REWARD = [1, 2, 3, 12, 15, 20]
BITRATE_REWARD_MAP = {0: 0, 300: 1, 750: 2, 1200: 3, 1850: 12, 2850: 15, 4300: 20}
M_IN_K = 1000000.0
BUFFER_NORM_FACTOR = 10.0
CHUNK_TIL_VIDEO_END_CAP = 221.0
TOTAL_VIDEO_CHUNKS = 220#weafre
DEFAULT_QUALITY = 0  # default video quality without agent
REBUF_PENALTY = 4.3  # 1 sec rebuffering -> this number of Mbps
SMOOTH_PENALTY = 1
ACTOR_LR_RATE = 0.0001
CRITIC_LR_RATE = 0.001
TRAIN_SEQ_LEN = 100  # take as a train batch
MODEL_SAVE_INTERVAL = 100
RANDOM_SEED = 42
RAND_RANGE = 1000
SUMMARY_DIR = './results'
LOG_FILE = './results/log'
# in format of time_stamp bit_rate buffer_size rebuffer_time video_chunk_size download_time reward
# NN_MODEL = None
NN_MODEL = './results/pretrain_linear_reward.ckpt'

# video chunk sizes
size_video1 = [10938, 1909944, 3562992, 4145746, 2826254, 2411580, 1846876, 1458456, 1862256, 1639262, 1762162, 1728436, 1632720, 931898, 1068962, 1664806, 1860726, 2226064, 2508828, 2697114, 2778562, 3438364, 2744388, 3098524, 2781476, 2725820, 2531100, 2133572, 2153536, 2287890, 1703198, 1954122, 2221892, 1489546, 1728682, 1009416, 1235548, 967432, 994276, 991678, 1198642, 1260468, 1355492, 1216606, 769760, 998702, 1138672, 1103682, 1441186, 1162574, 701398, 267270, 1911638, 3809514, 2908998, 4124046, 3757420, 3646514, 2863936, 1413148, 2735758, 3605436, 1927798, 1810158, 2468234, 1644128, 1283582, 645554, 476182, 2849792, 3157680, 1655086, 2422030, 865194, 21740, 1672964, 3429076, 3619938, 3495936, 3793936, 3642068, 2613222, 2477740, 2844468, 2238952, 1856964, 2104104, 2565686, 3164702, 4017534, 2964310, 4405610, 3078792, 2660794, 4577932, 1670978, 3121956, 3711576, 2113830, 3165496, 3884196, 2339512, 1472964, 1552708, 1649486, 1928648, 2664290, 2382926, 2641274, 1726200, 1066390, 861156, 383238, 325736, 355820, 437786, 1120514, 1565278, 2246054, 1439812, 2092608, 1562956, 1099550, 545526, 3348426, 2548652, 2609818, 2441370, 2479116, 2120604, 1720670, 1489034, 1899890, 1716682, 1443298, 1649440, 749824, 1287512, 1621168, 1811462, 990190, 1832646, 3125862, 2439334, 2302404, 2283298, 2083042, 2638298, 1888154, 838810, 1465628, 1321054, 1531564, 1536356, 1427612, 974274, 1210618, 2505438, 2106386, 1258916, 1591920, 3256720, 2220868, 2200020, 1604814, 1672490, 2891308, 2614254, 2805362, 2344458, 2213208, 1347990, 1383444, 1657150, 1616186, 791876, 751246, 911254, 750422, 603632, 733442, 690840, 472776, 341294, 483174, 453708, 605806, 1494720, 1272124, 4046808, 3740994, 3928406, 4131498, 3843068, 4500754, 3162366, 2076624, 1308272, 1768866, 936694, 1201910, 1023084, 1361640, 830002, 654374, 569596, 820790, 764302, 787636, 910580, 152604, 547486, 784306, 730232, 1078612, 1150454, 1633210, 1790694, 42398, 707788, 869078, 1822590]
size_video2 = [6408, 1006390, 1841772, 2099710, 1531106, 1303354, 967638, 751908, 936996, 883384, 890872, 830152, 765002, 481596, 602644, 889364, 968034, 1102734, 1295478, 1338370, 1397536, 1917062, 1563234, 1655234, 1370872, 1401124, 1329350, 1168552, 1147554, 1163788, 817018, 976766, 1161540, 698234, 905140, 490738, 634470, 518874, 529286, 515898, 660316, 669498, 717700, 643228, 384562, 477904, 589022, 539598, 717554, 521114, 345114, 141080, 958252, 1787280, 1613708, 2125048, 2015250, 1814240, 1498414, 651980, 1287846, 1711582, 915990, 993484, 1352482, 848530, 585962, 383728, 287802, 1350204, 1515590, 782468, 1070150, 486094, 14296, 989948, 1776506, 2033208, 1814206, 1852666, 1996606, 1434576, 1328280, 1515308, 1278040, 1102240, 1136032, 1242512, 1601626, 1937714, 1676352, 2326452, 1536728, 1235472, 2217278, 763824, 1636062, 1881846, 1075266, 1452782, 1870676, 1264732, 819002, 794940, 821986, 989774, 1432070, 1323784, 1224324, 741860, 603878, 507256, 231316, 195314, 217788, 243370, 609564, 846388, 1241018, 849472, 1287740, 901818, 667334, 344224, 1950346, 1618930, 1583354, 1510930, 1472128, 1218834, 1009640, 832688, 1026946, 835284, 674002, 842368, 447766, 750858, 816138, 913214, 549862, 963196, 1665542, 1346368, 1341050, 1319788, 1158838, 1415672, 927420, 484348, 798722, 660962, 794788, 804462, 721140, 486548, 597914, 1368330, 1158858, 662344, 829650, 1722928, 1209426, 1046072, 860692, 861758, 1471654, 1328104, 1470408, 1155658, 923144, 636330, 700600, 718670, 696622, 414728, 384730, 457902, 355580, 267092, 330582, 309736, 201442, 169954, 276514, 239632, 304248, 654422, 595154, 2097618, 1940922, 2057210, 2078328, 2012278, 2381974, 1634170, 1083096, 655162, 892450, 523218, 632704, 544830, 785478, 503244, 388446, 321488, 471416, 424558, 449990, 500632, 80508, 294050, 405442, 364588, 568062, 637698, 848614, 942380, 20648, 331500, 370406, 850512]
size_video3 = [4496, 499214, 825296, 981130, 733942, 639638, 488296, 349962, 468860, 407504, 423708, 397076, 362400, 218644, 271614, 432530, 450424, 502640, 582204, 574158, 634288, 986196, 796780, 776022, 649422, 632654, 610536, 594824, 540494, 543780, 372834, 447436, 544846, 282550, 429728, 231128, 288106, 259568, 267158, 262252, 320112, 325766, 337610, 311068, 183118, 228512, 268660, 250930, 306064, 216892, 162990, 58192, 434928, 780428, 806510, 1049902, 905668, 845636, 712994, 286844, 566994, 699506, 385138, 488782, 658572, 398404, 243534, 213104, 166854, 599198, 630786, 338794, 429164, 218206, 9128, 487818, 887212, 988738, 831436, 927058, 954128, 728684, 677420, 767956, 711404, 599408, 545456, 607032, 803392, 888836, 833016, 1061446, 771184, 624886, 1042920, 368014, 772124, 899156, 489618, 756886, 892690, 635282, 412054, 377892, 335894, 423870, 721890, 630878, 507862, 308708, 280204, 251086, 119590, 98320, 111942, 125666, 288890, 391040, 581496, 454238, 678236, 483200, 354484, 177536, 876408, 908216, 858274, 826538, 760088, 606134, 508100, 421640, 502270, 401606, 310696, 382828, 246226, 364590, 366294, 419886, 276350, 397564, 871142, 672570, 652402, 669492, 558668, 644556, 454568, 268256, 394072, 320422, 402174, 404798, 352830, 242336, 277468, 643386, 586404, 321830, 407130, 857050, 608912, 450308, 396032, 384834, 734186, 635976, 714816, 498648, 380772, 269934, 317514, 287150, 247714, 215854, 180738, 189282, 144052, 111166, 127046, 129496, 89084, 76352, 135678, 117608, 143608, 284656, 270246, 1052512, 880550, 972786, 1041308, 889826, 1066060, 763484, 461268, 279728, 388022, 257770, 295600, 257474, 375854, 268818, 203832, 174950, 247914, 224606, 243528, 261690, 39538, 130388, 187660, 190616, 276098, 283796, 415324, 494980, 9990, 133710, 140966, 350948]
size_video4 = [3974, 243212, 402968, 457150, 347976, 312058, 231512, 171470, 222158, 192482, 213442, 184750, 163092, 101006, 118826, 208244, 226456, 242842, 275916, 268708, 311018, 489240, 412512, 367926, 309250, 287796, 288064, 280296, 259990, 260812, 180962, 219144, 260346, 116350, 198060, 100054, 125546, 125504, 130818, 124748, 146250, 139352, 159678, 144444, 82282, 107600, 130496, 114272, 136428, 89652, 72460, 22300, 169740, 338154, 397714, 467468, 467194, 396154, 346844, 139204, 275762, 309528, 181334, 228152, 291186, 195054, 112692, 112390, 96952, 279304, 276954, 163606, 192418, 104860, 6794, 235822, 471608, 504234, 394274, 421662, 434594, 390128, 333200, 395056, 392216, 312520, 292432, 263816, 348104, 384630, 401768, 536448, 364506, 298930, 506754, 153908, 381116, 430718, 217872, 382100, 439114, 282490, 214572, 138920, 143526, 187834, 359676, 333208, 248296, 149318, 134352, 116894, 59076, 50036, 55758, 61884, 130606, 176968, 297708, 250518, 353984, 253842, 185970, 95426, 445862, 460636, 465384, 417982, 378544, 301320, 254788, 218542, 252372, 206826, 146240, 188846, 128668, 186988, 171006, 206884, 134354, 205924, 431032, 339186, 318504, 317828, 265252, 290840, 197574, 131034, 202736, 165992, 209230, 211488, 184376, 124870, 132330, 302242, 294734, 159622, 193844, 419782, 302198, 210180, 181536, 172052, 349658, 321490, 341510, 237236, 160800, 125790, 149700, 136100, 92636, 100488, 85618, 77924, 56736, 45296, 53680, 53206, 40396, 36306, 66902, 53066, 64408, 132932, 118128, 475542, 450956, 437324, 502958, 437952, 502030, 355916, 213238, 108484, 170664, 120082, 138940, 120556, 190374, 137808, 107436, 88314, 125676, 117442, 132230, 139322, 19192, 57604, 87566, 96368, 137902, 130998, 204088, 248552, 5776, 62032, 61562, 132582]
size_video5 = [3254, 93058, 163088, 184294, 120228, 114716, 85260, 65960, 83530, 66028, 76042, 67382, 62090, 42838, 51568, 85324, 82874, 94430, 110584, 104602, 112556, 204056, 170788, 142026, 114824, 104946, 108484, 110226, 99396, 101116, 67794, 83276, 99018, 36942, 75570, 32924, 43240, 50264, 51086, 48716, 57456, 53162, 54614, 55394, 30372, 41060, 50072, 42254, 49934, 32318, 27812, 8220, 57908, 132460, 166780, 192670, 167894, 121326, 116214, 48080, 109116, 110272, 70822, 84180, 105136, 71566, 40222, 52800, 43902, 93854, 88366, 62454, 67110, 36762, 3824, 114990, 171732, 192844, 139044, 173528, 161996, 175128, 147730, 161990, 172352, 138154, 118588, 101082, 153670, 167472, 161560, 198274, 139164, 124784, 161960, 54998, 174302, 168968, 93616, 126708, 148610, 95462, 83590, 52654, 50824, 73528, 153224, 129158, 95846, 56610, 50946, 44076, 23104, 20568, 22040, 24454, 55826, 69968, 108398, 100606, 139476, 100874, 81024, 42872, 183654, 187280, 170708, 175712, 155286, 119708, 95028, 77210, 98160, 86178, 56280, 74100, 59754, 84992, 71436, 81260, 50676, 86028, 160358, 128552, 125230, 121230, 96776, 103386, 67572, 53752, 78554, 71286, 86924, 83790, 74348, 48266, 51718, 116614, 109474, 61126, 78338, 161928, 124958, 83558, 74708, 67126, 140636, 131860, 121860, 81668, 43740, 45724, 57410, 47622, 29324, 37482, 31204, 26378, 16998, 13782, 16728, 17554, 15500, 13632, 28896, 19802, 23810, 47304, 43434, 161956, 184748, 172478, 189518, 180516, 211928, 125598, 70186, 31330, 58454, 44908, 48772, 44564, 71230, 59212, 43556, 36388, 49546, 47296, 60528, 59694, 8604, 20652, 34230, 40842, 52144, 52720, 80096, 106706, 2778, 21566, 22260, 40074]
size_video6 = [3128, 44788, 83412, 92274, 56210, 56494, 43658, 32596, 41642, 33180, 38444, 33376, 32942, 22196, 25740, 44300, 42024, 48390, 56032, 54032, 54978, 104786, 88554, 74040, 58278, 51942, 54466, 57920, 50548, 50132, 35914, 43436, 50348, 17618, 35476, 14770, 19032, 23214, 23874, 23626, 28048, 25910, 27172, 27830, 14566, 20498, 25212, 21066, 25702, 15526, 14732, 4586, 25076, 59710, 80200, 93142, 90404, 56704, 56710, 25188, 56370, 57462, 36636, 41498, 49256, 36086, 20736, 28548, 24040, 44330, 42074, 31408, 34858, 22094, 2796, 54622, 81862, 94040, 66898, 82440, 78726, 95142, 76192, 84038, 90522, 71640, 58264, 49978, 79054, 82070, 77228, 99042, 72644, 62406, 79684, 29094, 88842, 85974, 48720, 59144, 72972, 46104, 45178, 26312, 25598, 36894, 79762, 69020, 48820, 30548, 26146, 23994, 12224, 11696, 12276, 14194, 31302, 36298, 59268, 56456, 76406, 55058, 44538, 24702, 93498, 98178, 81998, 93400, 74280, 62274, 44244, 40108, 52166, 48884, 29734, 40142, 33368, 45168, 33810, 43746, 26816, 41468, 80300, 64990, 64958, 60696, 46818, 50306, 32004, 27488, 41278, 41946, 49376, 45900, 42748, 28464, 28446, 62654, 59458, 33120, 42218, 82674, 63882, 44478, 38636, 35516, 73540, 65978, 63916, 40792, 19212, 24276, 30198, 24728, 14770, 17556, 14726, 11684, 6630, 5538, 6360, 7124, 8220, 8376, 15726, 11092, 11278, 20974, 19852, 74100, 89036, 87316, 94966, 88848, 110198, 65018, 37536, 12188, 26070, 20856, 22958, 21922, 35856, 29890, 23744, 18206, 25584, 24192, 33970, 31446, 4310, 10046, 16976, 21824, 26016, 25736, 39942, 55574, 2102, 11340, 11588, 18214]



def get_chunk_size(quality, index):
    if ( index < 0 or index > 221 ):
        return 0
    # note that the quality and video labels are inverted (i.e., quality 8 is highest and this pertains to video1)
    sizes = {5: size_video1[index], 4: size_video2[index], 3: size_video3[index], 2: size_video4[index], 1: size_video5[index], 0: size_video6[index]}
    return sizes[quality]



def env_init():
    startSim = 0
    port = 5555;
    simTime = 20 # seconds
    stepTime = 1.0  # seconds
    seed = 0
    simArgs = {"--simTime": simTime,
               "--testArg": 123}
    debug = False

    env = ns3env.Ns3Env(port=port, stepTime=stepTime, startSim=startSim, simSeed=seed, simArgs=simArgs, debug=debug)
    env.reset()

    return env

def init_action():
  return np.zeros(7)

def main(args):
    env = env_init()
    ob_space = env.observation_space
    ac_space = env.action_space
    print("INFO---------------------")
    print("Observation space: ", ob_space,  ob_space.dtype)
    print("Action space: ", ac_space, ac_space.dtype)
    
    np.random.seed(RANDOM_SEED)
    assert len(VIDEO_BIT_RATE) == A_DIM

    if not os.path.exists(SUMMARY_DIR):
        os.makedirs(SUMMARY_DIR)

    #starting coding
    #Load saved action value      
    try: 
        dic = open("./results/Q-function.pkl","rb")
        Q=pickle.load(dic)
        print("Loaded action value function")
    except:
        Q = defaultdict(partial(init_action))
    #init a policy
    #init parameter
    discount_factor=1.0
    alpha=0.5
    epsilon=0.1
    policy = make_epsilon_greedy_policy(Q, epsilon, env.action_space.n)
    
    #for learning purpose
    episodes=args.episodes
    epIdx=0
    ep_reward_statistic=[]
    while(epIdx<episodes):
        print("[INFO] Episodes: ", epIdx)
        ep_cumulative_reward = 0
        ep_start_time = time.time()
        ep_cumulative_rebuffer = 0 
        stepIdx = 0
        actionHistory = []  
        throughputHistory = []
        epIdx+=1
        #print('reset 1st time',epIdx)
        obs = env.reset()
        #print("---Initial observation:", obs)
        #print("\n")
        reward=0

        while True:

            stepIdx += 1
            if(stepIdx%50==0):
                print("     [INFO] SG",stepIdx , 'Reward: %.4f'%reward )
            #get state
            state=get_state_array(obs)
            #take an action
            action_probs = policy(state)
            action = np.random.choice(np.arange(len(action_probs)), p=action_probs)
            if ( obs['lastRequest'] == TOTAL_VIDEO_CHUNKS ):
                stepIdx = 0
                if epIdx + 1 < episodes:
                    env.reset()
                break
            #if ( stepIdx==50):
             #   stepIdx = 0
              #  if epIdx + 1 < episodes:
               #     env.reset()
                #break
            actionHistory.append(action)
            obs, reward, done, info = env.step(action)
            reward=get_reward(obs)
            ep_cumulative_reward+=reward
            next_state=get_state_array(obs)

            #update Q value 
            best_next_action = np.argmax(Q[next_state])    
            td_target = reward + discount_factor * Q[next_state][best_next_action]
            td_delta = td_target - Q[state][action]
            Q[state][action] += alpha * td_delta

        ep_reward_statistic.append(ep_cumulative_reward)
        print("Cumulative reward : " , ep_cumulative_reward , " Time : " , time.time() - ep_start_time , " Cumulative rebuffer : " , ep_cumulative_rebuffer)
        #save state-action value function to file
        #print(actionHistory)
        if(epIdx%5==0):
            fig = plt.figure()
            plt.plot(actionHistory)
            plt.ylabel('Rep Index')
            plt.savefig('./results/repValue_episode'+str(epIdx+50)+'.png')
            plt.close(fig)
        f = open("./results/Q-function.pkl","wb")
        pickle.dump(Q,f)
        print('Saved action value function to file')

    fig1 = plt.figure()
    plt.plot(ep_reward_statistic)
    plt.ylabel('Rewards over episode')
    plt.savefig('./results/reward_over'+str(episodes+50)+'episodes.png')
    plt.close(fig1)
    f = open("./results/Q-function.pkl","wb")
    pickle.dump(Q,f)
    print('Saved action value function to file')

    env.close()

def quantization(max_value,value, step):
  if (value>max_value):
    value=max_value
  index = round(value/step) 
  return index

def make_epsilon_greedy_policy(Q, epsilon, nA):

    def policy_fn(observation):
        A = np.ones(nA, dtype=float) * epsilon / nA
        best_action = np.argmax(Q[observation])
        A[best_action] += (1.0 - epsilon)
        return A
    return policy_fn

def get_state_array(obs):

    download_time = (float(obs['lastChunkFinishTime']) - float(obs['lastChunkStartTime'])) / M_IN_K
    size = float(obs['lastChunkSize']) *8000/ M_IN_K#in kbyte
    throughput = size / download_time
    buff = obs['buffer'] / M_IN_K
    left_chunks =  TOTAL_VIDEO_CHUNKS - obs['lastRequest']
    #buffer_delta = 
    rebuffer_time = obs['RebufferTime'] / M_IN_K

    buff =quantization(50,buff,10)
    throughput =quantization(1500,throughput,100) 
    next_state = (throughput,buff)#np.asarray([throughput,buff])
    #next_state = np.reshape(next_state, [1, 2])

    #next_state = np.asarray([download_time, size, throughput, buff, left_chunks, rebuffer_time])
    #next_state = np.reshape(next_state, [1, 6])
    
    return next_state    

def get_reward(obs):
    reward = obs['buffer']/M_IN_K /5+ obs['lastquality'] - 10 * ((obs['RebufferTime'] ) > 0)
    return reward
def get_args():
    parser = argparse.ArgumentParser(description='Arguments for Neural Network')
    parser.add_argument('--animate', type=str, default=None,
                       help='Create mp4 animation of result, give filename, default none')
    parser.add_argument('--episodes', type=int, default=10,
                       help='Number of episodes for training')
    return parser.parse_args()

def create_animation(args):
    os.chdir("animation")
    os.system("ffmpeg -framerate 8 -pattern_type glob -i '*.png' -c:v libx264 -r 30 -pix_fmt yuv420p " + args.animate +".mp4")
    os.system('find . -name "*.png" -type f -delete')


if __name__ == "__main__":
    try:
        args = get_args()
        main(args)
        if args.animate:
            create_animation(args)
    except (KeyboardInterrupt, SystemExit):
        print("Ctrl-C -> Exit")
    finally:
        
        print("Done")


