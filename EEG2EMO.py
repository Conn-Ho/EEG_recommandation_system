import math
from cortex import Cortex

# ========================================================================================
# PART 1: 情绪识别模块 (Emotion Recognition Module)
# 职责: 接收处理好的数据，计算并返回情绪结果。
# ========================================================================================

# Cortex API 'met' 流返回的7个数值指标的顺序
API_METRIC_ORDER = ['eng', 'exc', 'lex', 'str', 'rel', 'int', 'foc']

METRIC_RANGES = {
    'eng': (0, 1),  # Engagement
    'exc': (0, 1),  # Excitement
    'lex': (0, 1),  # Lexical Excitement
    'str': (0, 1),  # Stress
    'rel': (0, 1),  # Relaxation
    'int': (0, 1),  # Interest
    'foc': (0, 1)   # Focus (Attention)
}

# 情绪计算权重
WEIGHTS = {
    'arousal': {
        'exc': 0.4, 'str': 0.3, 'lex': 0.2, 'int': 0.15, 'eng': 0.1, 'foc': 0.05, 'rel': -0.4
    },
    'valence': {
        'rel': 0.35, 'int': 0.25, 'eng': 0.2, 'lex': 0.2, 'foc': 0.1, 'exc': 0.1, 'str': -0.5
    }
}

def normalize_to_neg_one_to_one(value, min_val, max_val):
    if max_val == min_val: return 0
    return 2 * ((value - min_val) / (max_val - min_val)) - 1

def calculate_emotion_scores(metrics, weights):
    arousal = sum(weights['arousal'][key] * metrics[key] for key in API_METRIC_ORDER)
    valence = sum(weights['valence'][key] * metrics[key] for key in API_METRIC_ORDER)
    return max(-1, min(1, valence)), max(-1, min(1, arousal))

def get_precise_emotion(valence, arousal, neutral_threshold=0.1):
    intensity_raw = math.sqrt(valence**2 + arousal**2)
    intensity_normalized = min(100, (intensity_raw / math.sqrt(2)) * 100)

    if intensity_raw < neutral_threshold:
        return "中性 (Neutral)", intensity_normalized

    angle = math.degrees(math.atan2(arousal, valence))
    if angle < 0: angle += 360

    if 22.5 <= angle < 67.5: emotion_label = "开心 (Happy)"
    elif 67.5 <= angle < 112.5: emotion_label = "惊喜 (Surprised)"
    elif 112.5 <= angle < 157.5: emotion_label = "愤怒 (Angry)"
    elif 157.5 <= angle < 202.5: emotion_label = "厌恶 (Disgust)"
    elif 202.5 <= angle < 247.5: emotion_label = "悲伤 (Sad)"
    elif 247.5 <= angle < 292.5: emotion_label = "疲倦 (Tired)"
    elif 292.5 <= angle < 337.5: emotion_label = "放松 (Relaxed)"
    else: emotion_label = "平静 (Pleased)"
    return emotion_label, intensity_normalized

def analyze_emotion_from_sample(sample_list):
    """
    情绪分析流程的入口函数。
    """
    raw_data = dict(zip(API_METRIC_ORDER, sample_list))
    
    if raw_data['foc'] <= 0.1:
        raw_data['foc'] = 0.0
    
    normalized_metrics = {}
    for key, value in raw_data.items():
        min_val, max_val = METRIC_RANGES[key]
        normalized_metrics[key] = normalize_to_neg_one_to_one(value, min_val, max_val)
    
    v, a = calculate_emotion_scores(normalized_metrics, WEIGHTS)
    emotion, intensity = get_precise_emotion(v, a)
    
    return emotion, intensity, v, a

# ========================================================================================
# PART 2: 数据获取与整合模块 (Data Acquisition and Integration Module)
# ========================================================================================

class Subcribe():
    def __init__(self, app_client_id, app_client_secret, **kwargs):
        print("正在初始化Cortex客户端...")
        self.c = Cortex(app_client_id, app_client_secret, debug_mode=False, **kwargs)
        self.c.bind(new_met_data=self.on_new_met_data)
        self.c.bind(inform_error=self.on_inform_error)
        self.c.bind(create_session_done=self.on_create_session_done)

    def start(self, streams, headset_id=''):
        self.streams = streams
        if headset_id != '':
            self.c.set_wanted_headset(headset_id)
        self.c.open()

    def sub(self, streams):
        print("发送数据订阅请求...")
        self.c.sub_request(streams)

    def on_new_met_data(self, *args, **kwargs):
        try:
            met_values = kwargs.get('data')['met']
            
            numerical_values = [
                met_values[1], met_values[3], met_values[5], met_values[7],
                met_values[9], met_values[11], met_values[13]
            ]
            
            emotion, intensity, v, a = analyze_emotion_from_sample(numerical_values)
            
            print(f"情绪: {emotion} | 强度: {intensity:.2f}/100 | (V: {v:.2f}, A: {a:.2f})")
        
        except IndexError:
            print(f"接收到的 'met' 数据格式不完整或不正确: {met_values}")
        except Exception as e:
            print(f"处理数据时发生未知错误: {e}")

    def on_create_session_done(self, *args, **kwargs):
        print("会话创建成功, 准备订阅数据。")
        self.sub(self.streams)

    def on_inform_error(self, *args, **kwargs):
        error_data = kwargs.get('error_data')
        print(f"错误: {error_data}")

# ========================================================================================
# PART 3: 主程序入口 (Main Application Entry Point)
# ========================================================================================

def main():
    # !!!重要!!!
    # 请在下方填入你的 Emotiv App Client ID 和 Client Secret
    your_app_client_id = '6OV53rWuPZiJo6419CHi4ppabSdqKpTgfYCU5mvV'
    your_app_client_secret = 'XMWhqlpRTnQfe8a0b363jYFD976u7Ar17mQw2IWJT6eS2Z5LllaMckJbfbrSEqJYZ2LBpru6cvusWDapvjPSPutglsUwgNXYUzzcLKZqIhYOV52Rcy0YilZDJwoaQWnE'

    if your_app_client_id == '你的Client ID' or your_app_client_secret == '你的Client Secret':
        print("错误：请在代码中填入你的 Emotiv App Client ID 和 Client Secret!")
        return

    streams = ['met']
    s = Subcribe(your_app_client_id, your_app_client_secret)
    s.start(streams)

if __name__ =='__main__':
    main()