import { Component, signal } from '@angular/core';
import { Header } from './components/header/header';
import { CameraFeed } from './components/camera-feed/camera-feed';
import { TranslationResult } from './components/translation-result/translation-result';

@Component({
  selector: 'app-root',
  imports: [Header, CameraFeed, TranslationResult],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected readonly title = signal('sign-language-app');
}
