import os
import sys
from unittest.mock import MagicMock

# ลบการเรียกโฟลเดอร์หลอก และใช้โค้ดจำลองระบบ (Mocking) แทน 
# เพื่อบอก Python ว่า "มีโมดูลเหล่านี้อยู่แล้ว"
sys.modules['tensorflow_decision_forests'] = MagicMock()
sys.modules['tensorflow_hub'] = MagicMock()

# แก้ปัญหาภาษาไทยใน Terminal
sys.stdout.reconfigure(encoding='utf-8')

print("⏳ กำลังโหลดโมเดล my_thai_sign_model.h5...")
try:
    import tensorflow as tf
    import tensorflowjs as tfjs
    
    # โหลดโมเดล
    model = tf.keras.models.load_model('my_thai_sign_model.h5')
    
    print("📦 กำลังแปลงไฟล์เป็น TensorFlow.js...")
    # บันทึกเป็น tfjs
    tfjs.converters.save_keras_model(model, 'tfjs_model')
    
    print("🎉 เสร็จเรียบร้อย! ไฟล์สำหรับเว็บอยู่ในโฟลเดอร์ 'tfjs_model'")
except Exception as e:
    print(f"❌ เกิดข้อผิดพลาด: {e}")
    print("💡 กรุณาตรวจสอบว่าติดตั้ง tensorflowjs แล้วหรือยัง (pip install tensorflowjs==4.17.0)")