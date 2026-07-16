import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SignLanguageService } from '../../services/sign-language';

@Component({
  selector: 'app-translation-result',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './translation-result.html',
  styleUrl: './translation-result.css',
})
export class TranslationResult {
  public signLanguageService = inject(SignLanguageService);
}
