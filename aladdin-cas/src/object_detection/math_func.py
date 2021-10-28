import numpy as np


def get_iou(boxa, boxb):
    max_x = int(max(boxa[0], boxb[0]))
    max_y = int(max(boxa[1], boxb[1]))
    min_x = int(min(boxa[2], boxb[2]))
    min_y = int(min(boxa[3], boxb[3]))
    area_i = (min_x - max_x) * (min_y - max_y)
    area_a = (boxa[2] - boxa[0]) * (boxa[3] - boxa[1])
    area_b = (boxb[2] - boxb[0]) * (boxb[3] - boxb[1])
    if min_x <= max_x or min_y <= max_y:
        return 0, area_a, area_b, area_i
    area_u = area_a + area_b - area_i
    return float(area_i) / float(area_u), area_a, area_b, area_i

def get_iou_by_min(boxa, boxb):
    max_x = int(max(boxa[0], boxb[0]))
    max_y = int(max(boxa[1], boxb[1]))
    min_x = int(min(boxa[2], boxb[2]))
    min_y = int(min(boxa[3], boxb[3]))
    area_i = (min_x - max_x) * (min_y - max_y)
    area_a = (boxa[2] - boxa[0]) * (boxa[3] - boxa[1])
    area_b = (boxb[2] - boxb[0]) * (boxb[3] - boxb[1])
    # if min_x <= max_x or min_y <= max_y:
    #     return 0, area_a, area_b, area_i
    area_u = area_a + area_b - area_i
    if area_a > area_b:
        return float(area_i)/float(area_b)
    else:
        return float(area_i)/float(area_a)

def fake_nms(box_list):
    temp_list = []
    NMS_list = [box_list[0]]
    temp_list = []
    count = 0
    while True:
        for j in range(len(box_list)):
            iou, area_a, area_b, area_i = get_iou(NMS_list[count], box_list[j])
            min_area = area_a if area_a < area_b else area_b
            if iou < 0.5 and area_i != min_area or area_i/min_area < 0.5:

                temp_list.append(box_list[j])
        if len(temp_list) == 0:
            return NMS_list
        box_list = temp_list
        temp_list = []
        NMS_list.append(box_list[0])
        count += 1
        if count > len(box_list):
            return NMS_list[:-1]


def softmax(array_list):
    exp_array_list = np.exp(array_list)
    sum_arary_exp = np.sum(exp_array_list)
    softmax = exp_array_list/sum_arary_exp
    return softmax


def hashtrick(vector, N):
    def hash_trick_core(number, n):
        return hash(number) % n

    def Xi(number):
        tmp = hash_trick_core(number, 2)
        if tmp == 0:
            return -1
        else:
            return 1

    vector = vector.tolist()[0]
    output = [0] * N
    for j in range(len(vector)):
        i = hash_trick_core(j, N)
        output[i] += Xi(j) * vector[j]
    return np.array(output).reshape((1, -1)).astype(np.float32)
