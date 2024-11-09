from googletrans import Translator
import logging
from typing import Tuple
from time import sleep
from functools import lru_cache

logger = logging.getLogger(__name__)

class TranslationService:
    def __init__(self):
        """Initialize the translation service with retries."""
        self.translator = None
        self.retry_count = 3
        self.retry_delay = 1  # seconds
        self._initialize_translator()

    def _initialize_translator(self):
        """Initialize translator with retry mechanism."""
        for attempt in range(self.retry_count):
            try:
                self.translator = Translator()
                logger.info("Translation service initialized successfully")
                return
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to initialize translator: {str(e)}")
                if attempt < self.retry_count - 1:
                    sleep(self.retry_delay)
                else:
                    logger.error("Failed to initialize translator after all attempts")
                    raise

    def _translate_with_retry(self, text: str, dest: str, src: str = None) -> Tuple[str, str]:
        """Perform translation with retry mechanism."""
        last_error = None
        
        for attempt in range(self.retry_count):
            try:
                if not self.translator:
                    self._initialize_translator()
                
                translation = self.translator.translate(
                    text, 
                    dest=dest,
                    src=src if src else 'auto'
                )
                
                return translation.text, translation.src
                
            except Exception as e:
                last_error = e
                logger.warning(f"Translation attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < self.retry_count - 1:
                    sleep(self.retry_delay)
                    # Reinitialize translator for next attempt
                    self._initialize_translator()
        
        logger.error(f"Translation failed after {self.retry_count} attempts")
        return text, 'en'  # Return original text if all attempts fail

    @lru_cache(maxsize=100)
    def detect_language(self, text: str) -> str:
        """Detect the language of the input text with caching."""
        try:
            if not self.translator:
                self._initialize_translator()
            
            detection = self.translator.detect(text)
            detected_lang = detection.lang
            
            # Normalize language codes
            if detected_lang.startswith('sv'):
                return 'sv'
            return 'en' if detected_lang == 'en' else detected_lang
            
        except Exception as e:
            logger.error(f"Language detection error: {str(e)}")
            return 'en'

    def translate_to_english(self, text: str, source_lang: str = None) -> Tuple[str, str]:
        """Translate text to English."""
        if not text.strip():
            return text, 'en'

        try:
            if not source_lang:
                source_lang = self.detect_language(text)
            
            if source_lang == 'en':
                return text, source_lang
            
            translated_text, detected_lang = self._translate_with_retry(text, 'en', source_lang)
            return translated_text, detected_lang
            
        except Exception as e:
            logger.error(f"Translation to English error: {str(e)}")
            return text, 'en'

    def translate_from_english(self, text: str, dest_lang: str) -> str:
        """Translate text from English to target language."""
        if not text.strip() or dest_lang == 'en':
            return text

        try:
            translated_text, _ = self._translate_with_retry(text, dest_lang, 'en')
            return translated_text
            
        except Exception as e:
            logger.error(f"Translation from English error: {str(e)}")
            return text