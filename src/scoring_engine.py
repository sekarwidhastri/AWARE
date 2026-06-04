from datetime import datetime

class AWAREWorkplaceScoringEngine:
    """
    Engine untuk mengukur kesiapan kerja karyawan (Fit-to-Work)
    saat melakukan absensi pagi di depan monitor AWARE.
    """
    def __init__(self):
        self.weights = {
            'visual_ear':      0.35,
            'visual_yawn':     0.25,
            'sleep_duration':  0.25,
            'overtime_hours':  0.15
        }
        self.risk_thresholds = {'low': 40, 'medium': 70}

    def calculate_ear_score(self, ear_value):
        if ear_value >= 0.30:
            return 0
        elif ear_value <= 0.20:
            return 100
        else:
            return round((0.30 - ear_value) / (0.30 - 0.20) * 100, 1)

    def calculate_yawn_score(self, yawn_count):
        if yawn_count == 0:   return 0
        elif yawn_count == 1: return 30
        elif yawn_count == 2: return 75
        else:                 return 100

    def calculate_sleep_score(self, sleep_hours):
        if sleep_hours >= 7.0:   return 0
        elif sleep_hours >= 6.0: return 25
        elif sleep_hours >= 5.0: return 60
        else:                    return 100

    def calculate_overtime_score(self, overtime_hours):
        if overtime_hours == 0:    return 0
        elif overtime_hours <= 1:  return 20
        elif overtime_hours <= 2:  return 50
        else:                      return 100

    def calculate_total_risk(self, component_scores, custom_weights=None):
        weights = custom_weights if custom_weights else self.weights
        total = 0
        for key, value in component_scores.items():
            if key in weights:
                total += value * weights[key]
        return round(total, 2)

    def get_readiness_status(self, score):
        if score < self.risk_thresholds['low']:
            return 'FIT TO WORK', 'green', '✅ Pagar absensi terbuka. Selamat bekerja dengan aman!'
        elif score < self.risk_thresholds['medium']:
            return 'AT RISK (MONITOR)', 'yellow', '⚠️ Pagar terbuka. Peringatan: Anda terdeteksi lelah ringan, harap berhati-hati.'
        else:
            return 'NOT FIT', 'red', '🚫 AKSES DITOLAK! Pagar terkunci. Notifikasi Kritis dikirim ke HRD & Supervisor.'

def assess_readiness(ear_score, yawn_count, sleep_duration, overtime_hours, w_visual=0.6, w_hist=0.4):
    engine = AWAREWorkplaceScoringEngine()
    
    custom_weights = engine.weights.copy()
    if w_visual is not None and w_hist is not None:
        custom_weights['visual_ear'] = w_visual * (0.35 / 0.60)
        custom_weights['visual_yawn'] = w_visual * (0.25 / 0.60)
        custom_weights['sleep_duration'] = w_hist * (0.25 / 0.40)
        custom_weights['overtime_hours'] = w_hist * (0.15 / 0.40)

    component_scores = {
        'visual_ear': engine.calculate_ear_score(ear_score),
        'visual_yawn': engine.calculate_yawn_score(yawn_count),
        'sleep_duration': engine.calculate_sleep_score(sleep_duration),
        'overtime_hours': engine.calculate_overtime_score(overtime_hours)
    }
    
    final_risk_score = engine.calculate_total_risk(component_scores, custom_weights)
    status, color, recommendation = engine.get_readiness_status(final_risk_score)
    
    # Sub-scores just for progress bar visual in UI
    visual_subscore = (component_scores['visual_ear'] * custom_weights['visual_ear'] + component_scores['visual_yawn'] * custom_weights['visual_yawn']) / max(w_visual, 0.01)
    historical_subscore = (component_scores['sleep_duration'] * custom_weights['sleep_duration'] + component_scores['overtime_hours'] * custom_weights['overtime_hours']) / max(w_hist, 0.01)

    return {
        'visual_score': min(100.0, visual_subscore),
        'historical_score': min(100.0, historical_subscore),
        'final_risk_score': final_risk_score,
        'status': status,
        'color': color,
        'recommendation': recommendation
    }
