// Trigger rebuild
import { Component, ElementRef, ViewChild, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Hands, HAND_CONNECTIONS } from '@mediapipe/hands';
import { Camera } from '@mediapipe/camera_utils';
import { drawConnectors, drawLandmarks } from '@mediapipe/drawing_utils';
import { SignLanguageService } from '../../services/sign-language';

@Component({
  selector: 'app-camera-feed',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './camera-feed.html',
  styleUrl: './camera-feed.css',
})
export class CameraFeed {
  @ViewChild('videoElement') videoElement!: ElementRef<HTMLVideoElement>;
  @ViewChild('canvasElement') canvasElement!: ElementRef<HTMLCanvasElement>;

  private signLanguageService = inject(SignLanguageService);
  
  public isCameraActive = signal<boolean>(false);
  public isLoading = signal<boolean>(false);

  async startCamera() {
    this.isLoading.set(true);
    const video = this.videoElement.nativeElement;
    const canvas = this.canvasElement.nativeElement;
    const ctx = canvas.getContext('2d')!;

    // สร้างอินสแตนซ์ของ MediaPipe Hands
    const hands = new Hands({
      locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
    });

    hands.setOptions({
      maxNumHands: 2, // ให้กล้องตรวจจับมือได้สูงสุด 2 ข้าง
      modelComplexity: 1,
      minDetectionConfidence: 0.5,
      minTrackingConfidence: 0.5
    });

    // กำหนดฟังก์ชันเมื่อตรวจจับมือได้
    hands.onResults((results) => {
      // ปรับขนาด canvas ให้เท่ากับ video
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      
      ctx.save();
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
        // วาดเส้นโครงกระดูก (UI) ให้กับมือทุกข้างที่จับได้ (สูงสุด 2 ข้าง)
        for (const landmarks of results.multiHandLandmarks) {
          drawConnectors(ctx, landmarks, HAND_CONNECTIONS, {color: '#00F2FE', lineWidth: 3});
          drawLandmarks(ctx, landmarks, {color: '#4FACFE', lineWidth: 1, radius: 3});
        }

        // เตรียม Array 126 ช่อง (ซ้าย 63, ขวา 63)
        let leftHand = new Array(63).fill(0.0);
        let rightHand = new Array(63).fill(0.0);

        for (let i = 0; i < results.multiHandLandmarks.length; i++) {
          const landmarks = results.multiHandLandmarks[i];
          
          // เนื่องจากกล้องเว็บแคมเป็นกระจกเงา (Selfie Mode)
          // สิ่งที่ MediaPipe บอกว่าเป็น 'Left' แท้จริงแล้วคือมือขวาของผู้ใช้
          // เราจึงต้องสลับค่า (Flip) ให้ตรงกับตอนเทรน AI
          const rawHandedness = results.multiHandedness[i].label;
          const actualHandedness = rawHandedness === 'Left' ? 'Right' : 'Left';
          
          // วาดข้อความบอกว่าเป็นมือซ้ายหรือขวาบนจอ (เพื่อ Debug)
          ctx.font = '24px Arial';
          ctx.fillStyle = actualHandedness === 'Left' ? '#FF5722' : '#4CAF50';
          // เนื่องจากจอถูก flip ด้วย CSS (scale-x-[-1]) เราต้อง flip กลับตอนวาด text
          ctx.save();
          ctx.translate(canvas.width, 0);
          ctx.scale(-1, 1);
          ctx.fillText(actualHandedness, canvas.width - (landmarks[0].x * canvas.width), landmarks[0].y * canvas.height - 20);
          ctx.restore();

          // แปลงเป็นพิกัดสัมพัทธ์ (Relative Coordinates) อ้างอิงจากข้อมือ
          const wrist = landmarks[0];
          const coords: number[] = [];
          for (const lm of landmarks) {
            coords.push(lm.x - wrist.x, lm.y - wrist.y, lm.z - wrist.z);
          }

          if (actualHandedness === 'Left') {
            leftHand = coords;
          } else {
            rightHand = coords;
          }
        }
        
        // นำพิกัด 126 จุด (ซ้าย 63 + ขวา 63) ส่งให้ Service ทายผล
        const finalCoords = [...leftHand, ...rightHand];
        
        // ถ้าระบบ AI พร้อมใช้งาน ให้ส่งพิกัดไปแปล
        if (this.signLanguageService.isReady()) {
          this.signLanguageService.predict(finalCoords);
        }
      }
      ctx.restore();
    });

    // เปิดกล้อง
    const camera = new Camera(video, {
      onFrame: async () => {
        await hands.send({image: video});
      },
      width: 640,
      height: 480
    });

    camera.start().then(() => {
      this.isCameraActive.set(true);
      this.isLoading.set(false);
    });
  }
}
