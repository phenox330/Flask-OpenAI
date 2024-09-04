from flask import render_template, Blueprint, request, jsonify, current_app
from app.services.assistant import AssistantService

assistant_bp = Blueprint('assistant', __name__)

@assistant_bp.route('/', methods=['GET'])
@assistant_bp.route('/assistant', methods=['GET', 'POST'])
def assistant():
    if request.method == 'POST':
        data = request.get_json()
        message = data.get('message', '')

        if not message:
            return jsonify({'error': 'No message provided'}), 400
      
        try:
            assistant_service = AssistantService()
            assistant_response = assistant_service.run_assistant(message)
            
            return jsonify({'assistant_response': assistant_response})
        except Exception as e:
            current_app.logger.error(f"Error processing assistant request: {str(e)}")
            return jsonify({'error': 'An error occurred while processing your request'}), 500
    else:
        return render_template('home.html')

@assistant_bp.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@assistant_bp.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500