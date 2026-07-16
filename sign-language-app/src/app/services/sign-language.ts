import { Injectable, signal } from '@angular/core';
import * as tf from '@tensorflow/tfjs';

export const THAI_WORDS = [
  'ใช่',
  'ขอบคุณ',
  'ขอโทษ',
  'ไม่ใช่',
  'ไม่เป็นไร',
  'ไม่สบายใจ',
  'แนะนำ',
  'สบายดี',
  'สนุก',
  'สวัสดี'
];

@Injectable({
  providedIn: 'root'
})
export class SignLanguageService {
  private model: tf.LayersModel | null = null;
  public currentWord = signal<string>('');
  public isReady = signal<boolean>(false);
  
  // ป้องกันการทายซ้ำๆ ถี่เกินไป (Smoothing)
  private predictionBuffer: number[] = [];
  private readonly BUFFER_SIZE = 10; // เพิ่มจาก 5 เป็น 10 เฟรม เพื่อให้ชัวร์ก่อนตอบ

  constructor() {
    this.loadModel();
  }

  async loadModel() {
    try {
      // โหลดโมเดลที่แปลงมา พร้อมแนบ ?v=timestamp เพื่อล้างแคชเบราว์เซอร์
      const cacheBuster = new Date().getTime();
      this.model = await tf.loadLayersModel(`/model/tfjs_model/model.json?v=${cacheBuster}`);
      console.log('Model loaded successfully');
      this.isReady.set(true);
    } catch (error) {
      console.error('Error loading model:', error);
    }
  }

  async predict(landmarks: number[]) {
    if (!this.model || landmarks.length !== 126) return; // เปลี่ยนจาก 63 เป็น 126

    // ประมวลผลโดยไม่ให้ UI กระตุก
    tf.tidy(() => {
      // แปลงเป็น Tensor shape [1, 126]
      const inputTensor = tf.tensor2d([landmarks]);
      
      // ให้โมเดลทายผล
      const prediction = this.model!.predict(inputTensor) as tf.Tensor;
      
      // หาตำแหน่งที่มีค่าความมั่นใจสูงที่สุด
      const scores = prediction.dataSync();
      const maxScore = Math.max(...Array.from(scores));
      const classId = scores.indexOf(maxScore);
      
      // ดูค่าที่โมเดลทายได้แบบ Real-time
      console.log(`Predicted: ${THAI_WORDS[classId]} (${(maxScore*100).toFixed(2)}%)`);

      // เพิ่มความเข้มงวด: ต้องมั่นใจ 95% ขึ้นไปถึงจะนับ (เดิม 70%)
      if (maxScore > 0.95) {
        this.bufferPrediction(classId);
      }
    });
  }

  private bufferPrediction(classId: number) {
    this.predictionBuffer.push(classId);
    if (this.predictionBuffer.length > this.BUFFER_SIZE) {
      this.predictionBuffer.shift();
    }

    if (this.predictionBuffer.length === this.BUFFER_SIZE) {
      const counts = this.predictionBuffer.reduce((acc, val) => {
        acc[val] = (acc[val] || 0) + 1;
        return acc;
      }, {} as Record<number, number>);

      const mostFrequent = Object.keys(counts).reduce((a, b) => counts[parseInt(a)] > counts[parseInt(b)] ? a : b);
      
      // ต้องเห็นท่าเดิมซ้ำกันอย่างน้อย 7 ใน 10 เฟรม ถึงจะมั่นใจว่าตั้งใจทำท่านี้จริงๆ
      if (counts[parseInt(mostFrequent)] >= 7) { 
        this.currentWord.set(THAI_WORDS[parseInt(mostFrequent)]);
      }
    }
  }
}
