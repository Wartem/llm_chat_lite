# app.py
from flask import Flask, request, jsonify, render_template, Response, jsonify
from config import get_current_theme, set_theme, load_config
import requests
from datetime import datetime
import logging
from typing import Dict, List, Optional
from translator import TranslationService
import json
import time

app = Flask(__name__)

PORT = 5012

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

with open('ollama_config.json', 'r') as f:
    config = json.load(f)
    
OLLAMA_INSTANCES = config['ollama_instances']

# Store conversation history per session
conversations: Dict[str, Dict] = {}

translator = TranslationService()

class OllamaManager:
    def __init__(self, instances):
        self.instances = sorted(instances, key=lambda x: x['priority'])
        self.current_instance = None
        self.last_health_check = {}
        self.cached_models = None
        self.last_models_check = 0
        self.models_cache_ttl = 30  # seconds
        self.failed_instances = set()  # Track failed instances
        self.failed_instance_ttl = 60  # Seconds to wait before retrying failed instance

    def _check_instance_health(self, instance_url: str) -> bool:
        """Check if an Ollama instance is healthy."""
        # Skip health check if instance recently failed
        if instance_url in self.failed_instances:
            logger.debug(f"Skipping recently failed instance: {instance_url}")
            return False

        try:
            # Reduce timeout to 2 seconds
            response = requests.get(f"{instance_url}/api/tags", timeout=2)
            logger.info(f"Health check response from {instance_url}: {response.status_code}")
            
            if response.status_code == 200:
                # Cache models when we get a successful health check
                data = response.json()
                if 'models' in data:
                    self.cached_models = [model['name'] for model in data['models']]
                    self.last_models_check = time.time()
                    logger.info(f"Cached models during health check: {self.cached_models}")
                # Clear from failed instances if it was there
                self.failed_instances.discard(instance_url)
                return True
            
            self.failed_instances.add(instance_url)
            return False
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Health check failed for {instance_url}: {str(e)}")
            self.failed_instances.add(instance_url)
            return False

    def get_healthy_instance(self) -> Optional[Dict]:
        """Get the highest priority healthy instance."""
        current_time = time.time()
        
        # If we have a current instance and it was checked recently, return it
        if self.current_instance and (current_time - self.last_health_check.get(self.current_instance['url'], 0)) <= 30:
            return self.current_instance
        
        # Clear old failed instances
        self.failed_instances = {url for url in self.failed_instances 
                               if (current_time - self.last_health_check.get(url, 0)) <= self.failed_instance_ttl}
        
        for instance in self.instances:
            # Skip recently failed instances
            if instance['url'] in self.failed_instances:
                continue
                
            # Only check health if we haven't checked in the last 30 seconds
            if (current_time - self.last_health_check.get(instance['url'], 0)) > 30:
                is_healthy = self._check_instance_health(instance['url'])
                self.last_health_check[instance['url']] = current_time
                
                if is_healthy:
                    self.current_instance = instance
                    logger.info(f"Using Ollama instance: {instance['name']} at {instance['url']}")
                    return instance
                else:
                    logger.warning(f"Instance {instance['name']} at {instance['url']} is not healthy")
        
        # If no healthy instance found, try to use the last known good instance
        if self.current_instance:
            logger.warning("No healthy instances found, using last known good instance")
            return self.current_instance
            
        logger.error("No healthy instances available")
        return None

    def get_available_models(self) -> List[str]:
        """Get list of available models from cache or current Ollama instance."""
        # First try to return cached models
        if self.cached_models:
            logger.info(f"Returning cached models: {self.cached_models}")
            return self.cached_models
            
        # If no cache, try to get fresh models
        instance = self.get_healthy_instance()
        if not instance:
            logger.error("No healthy instance available")
            return []
        
        try:
            response = requests.get(f"{instance['url']}/api/tags", timeout=2)
            
            if response.status_code == 200:
                data = response.json()
                if 'models' in data:
                    self.cached_models = [model['name'] for model in data['models']]
                    self.last_models_check = time.time()
                    logger.info(f"Found models: {self.cached_models}")
                    return self.cached_models
                    
        except Exception as e:
            logger.error(f"Error getting models: {str(e)}")
        
        return []
    
    def ensure_model_running(self) -> Optional[str]:
        """Ensure a model is running on the current instance."""
        models = self.get_available_models()
        if not models:
            instance = self.get_healthy_instance()
            if not instance:
                return None
                
            try:
                response = requests.post(
                    f"{instance['url']}/api/pull",
                    json={"name": "llama2"}
                )
                
                if response.status_code == 200:
                    logger.info(f"Successfully pulled llama2 model on {instance['name']}")
                    return "llama2"
            except requests.exceptions.RequestException as e:
                logger.error(f"Error pulling model: {str(e)}")
                return None
        
        return models[0] if models else None

    def get_chat_response(self, messages: List[Dict], stream: bool = True):
        """Get chat response from current Ollama instance."""
        instance = self.get_healthy_instance()
        if not instance:
            raise Exception("No healthy Ollama instance available")
            
        model = self.ensure_model_running()
        if not model:
            raise Exception("No model available")
            
        return requests.post(
            f"{instance['url']}/api/chat",
            json={
                "model": model,
                "messages": messages,
                "stream": stream
            },
            stream=stream
        )

class OllamaManager_Extensive:
    def __init__(self, instances):
        self.instances = sorted(instances, key=lambda x: x['priority'])
        self.current_instance = None
        self.last_health_check = {}
        self.cached_models = None
        self.last_models_check = 0
        self.models_cache_ttl = 30  # seconds

    def _check_instance_health(self, instance_url: str) -> bool:
        """Check if an Ollama instance is healthy."""
        try:
            response = requests.get(f"{instance_url}/api/tags", timeout=5)
            logger.info(f"Health check response from {instance_url}: {response.status_code}")
            
            if response.status_code == 200:
                # Cache models when we get a successful health check
                data = response.json()
                if 'models' in data:
                    self.cached_models = [model['name'] for model in data['models']]
                    self.last_models_check = time.time()
                    logger.info(f"Cached models during health check: {self.cached_models}")
                return True
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Health check failed for {instance_url}: {str(e)}")
            return False

    def get_healthy_instance(self) -> Optional[Dict]:
        """Get the highest priority healthy instance."""
        current_time = time.time()
        
        # If we have a current instance and it was checked recently, return it
        if self.current_instance and (current_time - self.last_health_check.get(self.current_instance['url'], 0)) <= 30:
            return self.current_instance
        
        for instance in self.instances:
            # Only check health if we haven't checked in the last 30 seconds
            if (current_time - self.last_health_check.get(instance['url'], 0)) > 30:
                is_healthy = self._check_instance_health(instance['url'])
                self.last_health_check[instance['url']] = current_time
                
                if is_healthy:
                    self.current_instance = instance
                    logger.info(f"Using Ollama instance: {instance['name']} at {instance['url']}")
                    return instance
                else:
                    logger.warning(f"Instance {instance['name']} at {instance['url']} is not healthy")
        
        logger.error("No healthy instances available")
        return self.current_instance  # Return current instance even if health check failed

    def get_available_models(self) -> List[str]:
        """Get list of available models from cache or current Ollama instance."""
        current_time = time.time()
        
        # Return cached models if they're still fresh
        if self.cached_models and (current_time - self.last_models_check) <= self.models_cache_ttl:
            logger.info(f"Returning cached models: {self.cached_models}")
            return self.cached_models
            
        # If no cached models or cache expired, try to get fresh models
        instance = self.get_healthy_instance()
        if not instance:
            logger.error("No healthy instance available")
            return self.cached_models or []  # Return cached models as fallback
        
        try:
            response = requests.get(f"{instance['url']}/api/tags")
            logger.info(f"Raw Ollama response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if 'models' in data:
                    self.cached_models = [model['name'] for model in data['models']]
                    self.last_models_check = current_time
                    logger.info(f"Found models: {self.cached_models}")
                    return self.cached_models
                else:
                    logger.error(f"No 'models' key in response. Response data: {data}")
            else:
                logger.error(f"Bad status code from Ollama: {response.status_code}")
        except Exception as e:
            logger.error(f"Error getting models: {str(e)}")
        
        return self.cached_models or []  # Return cached models as fallback

    def ensure_model_running(self) -> Optional[str]:
        """Get the first available model from the running Ollama instance."""
        models = self.get_available_models()
        return models[0] if models else None

    def get_chat_response(self, messages: List[Dict], stream: bool = True):
        """Get chat response from current Ollama instance."""
        instance = self.get_healthy_instance()
        if not instance:
            raise Exception("No healthy Ollama instance available")
            
        model = self.ensure_model_running()
        if not model:
            raise Exception("No model available")
            
        return requests.post(
            f"{instance['url']}/api/chat",
            json={
                "model": model,
                "messages": messages,
                "stream": stream
            },
            stream=stream
        )

# Initialize Ollama manager
ollama_manager = OllamaManager(OLLAMA_INSTANCES)

@app.route('/')
def home():
    models = ollama_manager.get_available_models()
    theme_path = get_current_theme()
    return render_template('index.html', models=models, theme_path=theme_path)

@app.route('/api/theme', methods=['GET'])
def get_theme():
    config = load_config()
    return jsonify({'theme': config['theme']})

@app.route('/api/theme/<theme_name>', methods=['POST'])
def update_theme(theme_name):
    try:
        set_theme(theme_name)
        return jsonify({'success': True, 'theme': theme_name})
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/models', methods=['GET'])
def get_models():
    models = ollama_manager.get_available_models()
    logger.info(f"Available models: {models}")  # Add logging
    return jsonify({"models": models})

@app.route('/api/chat', methods=['GET', 'POST'])
def chat():
    try:
        if request.method == 'GET':
            message = request.args.get('message')
            session_id = request.args.get('session_id', 'default')
        else:  # POST
            data = request.json
            message = data.get('message')
            session_id = data.get('session_id', 'default')

        if not message:
            return jsonify({"error": "No message provided"}), 400
        
        # Initialize conversation history if it doesn't exist
        if session_id not in conversations:
            conversations[session_id] = {
                'messages': [],
                'language': None
            }

        logger.info(f"Received message: {message}")
        
        # Detect and translate user message to English
        translated_message, detected_lang = translator.translate_to_english(message)
        logger.info(f"Translated to English: {translated_message} (from {detected_lang})")
        
        # Store the user's language preference if not already set
        if not conversations[session_id]['language']:
            conversations[session_id]['language'] = detected_lang
            logger.info(f"Set session language to: {detected_lang}")

        # Add translated user message to history
        conversations[session_id]['messages'].append({
            "role": "user",
            "content": translated_message
        })

        def generate():
            try:
                # Get response from Ollama
                response = ollama_manager.get_chat_response(
                    conversations[session_id]['messages']
                )
                
                full_response = ""
                
                # Stream the English response first
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line.decode('utf-8'))
                        if 'message' in chunk:
                            content = chunk['message'].get('content', '')
                            if content:
                                full_response += content
                                # Send the English chunk
                                yield f"data: {json.dumps({'chunk': content})}\n\n"

                if full_response:
                    # Get the target language from the session
                    target_lang = conversations[session_id]['language']
                    logger.info(f"Translating full response to {target_lang}")
                    
                    # Translate the complete response back to original language
                    if target_lang != 'en':
                        translated_response = translator.translate_from_english(
                            full_response,
                            target_lang
                        )
                        logger.info("Translation completed")
                        # Send the translated version
                        yield f"data: {json.dumps({'translation': translated_response})}\n\n"

                # Store the English version in conversation history
                conversations[session_id]['messages'].append({
                    "role": "assistant",
                    "content": full_response
                })

                # Limit conversation history
                if len(conversations[session_id]['messages']) > 20:
                    conversations[session_id]['messages'] = conversations[session_id]['messages'][-20:]

                yield f"data: {json.dumps({'done': True})}\n\n"

            except Exception as e:
                logger.error(f"Error in generate: {str(e)}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
                
        return Response(generate(), mimetype='text/event-stream')

    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/reset', methods=['POST'])
def reset_conversation():
    data = request.json
    session_id = data.get('session_id', 'default')
    if session_id in conversations:
        lang = conversations[session_id]['language']
        conversations[session_id] = {
            'messages': [],
            'language': lang
        }
    return jsonify({"status": "success"})

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get status of all Ollama instances."""
    status = []
    for instance in OLLAMA_INSTANCES:
        is_healthy = ollama_manager._check_instance_health(instance['url'])
        status.append({
            'name': instance['name'],
            'url': instance['url'],
            'status': 'healthy' if is_healthy else 'unhealthy',
            'priority': instance['priority']
        })
    return jsonify({'instances': status})

if __name__ == '__main__':
    logger.info("Starting Ollama chat application...")
    app.run(host='0.0.0.0', port=PORT, debug=True)